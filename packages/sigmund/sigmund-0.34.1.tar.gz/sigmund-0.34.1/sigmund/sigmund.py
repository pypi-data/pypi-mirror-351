import logging
import json
from types import GeneratorType
from . import config
from .reply import Reply, ActionReply
from .documentation import Documentation, FAISSDocumentationSource
from .messages import Messages
from .model import model    
from .database.manager import DatabaseManager
from . import prompt, tools, utils
logger = logging.getLogger('sigmund')


class Sigmund:
    """The main chatbot class.
    
    Parameters
    ----------
    user_id: A user name
    persistent: Indicates whether the current session should be persistent in
        the sense of using the database.
    search_first: Indicates whether the answer phase should be preceded by a
        documentation search phase. If None, the config default will be used.
    model_config: Indicates the model configuration. If none, the config
        default will be used.
    search_tools: A list of tools to be used by the documentation search (if
        enabled). Values are class names from sigmund.tools. If None, the
        config default will be used.
    answer_tools: A list of tools to be used during the answer phase (if
        enabled). Values are class names from sigmund.tools. If None, the
        config default will be used.
    """
    def __init__(self, user_id: str, persistent: bool = False,
                 encryption_key: str = None,
                 search_first: bool = None,
                 model_config: str = None,
                 search_tools: list = None,
                 answer_tools: list = None):
        self.user_id = user_id
        self.database = DatabaseManager(self, user_id, encryption_key)
        # Search first is stored as a str but should be a bool here
        self.search_first = (
            self.database.get_setting('mode') == 'opensesame'
            if search_first is None else search_first)
        self.model_config = config.model_config[
            self.database.get_setting('model_config')
            if model_config is None else model_config
        ]
        self.documentation = Documentation(
            self, sources=[FAISSDocumentationSource(self)])
        self.messages = Messages(self, persistent)
        if search_tools is None:
            search_tools = config.search_tools
        if answer_tools is None:
            if self.search_first:
                answer_tools = config.answer_tools_with_search
            else:
                answer_tools = [
                    t for t in config.answer_tools_without_search
                    if self.database.get_setting(f'tool_{t}') == 'true'
                ]
        # Tools are class names from the tools module, which need to be
        # instantiated with sigmund (self) as first argument
        self.search_tools = [getattr(tools, t)(self) for t in search_tools]
        self.answer_tools = [getattr(tools, t)(self) for t in answer_tools]
        # If there are search tools, the first one should always be used
        if search_tools:
            search_tool_choice = search_tools[0]
        else:
            search_tool_choice = None
        # If there are answer tools, the mode can choose freely
        if answer_tools:
            answer_tool_choice = 'auto'
        else:
            answer_tool_choice = None
        self.search_model = model(self, self.model_config['search_model'],
                                  tools=self.search_tools, 
                                  tool_choice=search_tool_choice)
        self.answer_model = model(self, self.model_config['answer_model'],
                                  tools=self.answer_tools,
                                  tool_choice=answer_tool_choice)
        self.condense_model = model(self, self.model_config['condense_model'])
        self.public_model = model(self, self.model_config['public_model'])
    
    def send_user_message(self, message: str, workspace_content: str = None,
                          workspace_language: str = 'text',
                          attachments: list = None,
                          message_id: str = None) -> GeneratorType:
        """The main function that takes a user message and returns one or 
        replies. This is a generator function where each yield gives a tuple.
        
        This tuple can be (dict, dict, str) in which case the first dict 
        contains an action and a message key. This communicates to the client 
        that an action should be taking, such that the loading indicator should
        change. This tuple can also be (str, dict, str) in which case the first
        str contains an AI message and the dict contains metadata for the 
        message. The third element corresponds to the content of the workspace,
        and can be None if empty.
        """
        # A temporary hack to prune messages for accounts
        if message == 'prune_detached_messages()':
            yield ActionReply(
                f'{config.ai_name} is pruning detached messages ')
            self.database.prune_detached_messages()
            return Reply('Done', None, None, None)
        if config.log_replies:
            logger.info(f'[user message] {message}')
        if self._rate_limit_exceeded():
            yield Reply(config.max_tokens_per_hour_exceeded_message,
                        self.messages.metadata())
            return
        self.messages.workspace_content = workspace_content
        self.messages.workspace_language = workspace_language
        self.messages.append('user', 
                             message=message,
                             workspace_content=workspace_content,
                             workspace_language=workspace_language,
                             message_id=message_id)
        if self.search_first:
            for reply in self._search(message):
                yield reply
        for reply in self._answer(attachments):
            yield reply
            
    def _rate_limit_exceeded(self):
        tokens_consumed_past_hour = self.database.get_activity()
        logger.info(
            f'tokens consumed in past hour: {tokens_consumed_past_hour}')
        return tokens_consumed_past_hour > config.max_tokens_per_hour
    
    def _search(self, message: str) -> GeneratorType:
        """Implements the documentation search phase."""
        yield ActionReply(f'{config.ai_name} is searching ')
        logger.info('[search state] entering')
        self.documentation.clear()
        # First seach based on the user question
        logger.info('[search state] searching based on user message')
        self.documentation.search([message])
        # Then search based on the search-model queries derived from the user
        # question
        reply = self.search_model.predict(self.messages.prompt(
            system_prompt=prompt.SYSTEM_PROMPT_SEARCH))
        if config.log_replies:
            logger.info(f'[search state] reply: {reply}')
        if callable(reply):
            reply()
        else:
            logger.warning('[search state] did not call search tool')
        self.documentation.strip_irrelevant(message)
        logger.info(
            f'[search state] {len(self.documentation._documents)} documents, {len(self.documentation)} characters')
    
    def _answer(self, attachments: [] = None,
                state: str = 'answer') -> GeneratorType:
        """Implements the answer phase."""
        yield ActionReply(f'{config.ai_name} is thinking and typing ')
        logger.info(f'[{state} state] entering')
        # We first collect a regular reply to the user message. While doing so
        # we also keep track of the number of tokens consumed.
        tokens_consumed_before = self.answer_model.total_tokens_consumed
        reply = self.answer_model.predict(self.messages.prompt(),
                                          attachments=attachments)
        tokens_consumed = self.answer_model.total_tokens_consumed \
            - tokens_consumed_before
        logger.info(f'tokens consumed: {tokens_consumed}')
        self.database.add_activity(tokens_consumed)        
        if config.log_replies:
            logger.info(f'[{state} state] reply: {reply}')
        # If the reply is a callable, then it's a tool that we need to run
        if callable(reply):
            tool_message, tool_result, tool_language, needs_feedback = reply()
            if needs_feedback:
                logger.info(f'[{state} state] tools need feedback')
                if not self.answer_model.supports_tool_feedback:
                    logger.info(
                        f'[{state} state] model does not support feedback')
                    needs_feedback = False
            tool_message, workspace_content, workspace_language = \
                utils.extract_workspace(tool_message)
            # If the tool has a result and no workspace content was included in
            # the message itself, use the result as the workspace message. Also
            # remember the tool result it in the mssage history.
            if tool_result:
                if workspace_content is None:
                    workspace_content = tool_result['content']
                    workspace_language = tool_language
                metadata = self.messages.append(
                    'assistant', message=tool_message,
                    workspace_content=workspace_content,
                    workspace_language=workspace_language)
                self.messages.append('tool', message=json.dumps(tool_result))
            else:
                metadata = self.messages.append('assistant', tool_message)
            yield Reply(tool_message, metadata, workspace_content,
                        workspace_language)
        # Otherwise the reply is a regular AI message
        else:
            reply, workspace_content, workspace_language = \
                utils.extract_workspace(reply)
            metadata = self.messages.append(
                'assistant',
                message=reply,
                workspace_content=workspace_content,
                workspace_language=workspace_language)
            yield Reply(reply, metadata, workspace_content, workspace_language)
            # If the reply contains a NOT_DONE_YET marker, this is a way for the AI
            # to indicate that it wants to perform additional actions. This makes 
            # it easier to perform tasks consisting of multiple responses and 
            # actions. The marker is stripped from the reply so that it's hidden
            # from the user. We also check for a number of common linguistic 
            # indicators that the AI isn't done yet, such "I will now". This is
            # necessary because the explicit marker isn't reliably sent.
            if self.answer_model.supports_not_done_yet and \
                    prompt.NOT_DONE_YET_MARKER in reply:
                reply = reply.replace(prompt.NOT_DONE_YET_MARKER, '')
                logger.info(f'[{state} state] not-done-yet marker received')
                needs_feedback = True
            else:
                needs_feedback = False
        # If feedback is required, either because the tools require it or 
        # because the AI sent a NOT_DONE_YET marker, go for another round.
        if needs_feedback and not self._rate_limit_exceeded():
            if workspace_content is not None:
                logger.info('workspace content has been updated for feedback')
                self.messages.workspace_content = workspace_content
                self.messages.workspace_language = workspace_language
            for reply in self._answer(attachments, state='feedback'):
                yield reply
