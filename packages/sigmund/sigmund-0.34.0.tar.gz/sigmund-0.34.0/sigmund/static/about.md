Sigmund is a powerful, privacy-focused AI assistant (or chatbot). It is a web app that is built on state-of-the-art large language models (LLMs).


[TOC]


## Sigmund is an OpenSesame expert

If OpenSesame-expert mode is enabled (in the menu), Sigmund searches for relevant sections in the documentation of [OpenSesame](https://osdoc.cogsci.nl/), a program for developing psychology and cognitive-neuroscience experiments. Sigmund also receives a set of fixed instructions designed to enhance its general knowledge of OpenSesame. Sigmund subsequently uses this information to answer questions, and to provide links to relevant pages from the documentation. This technique, which is a variation of so-called [Retrieval-Augmented Generation](https://en.wikipedia.org/wiki/Retrieval-augmented_generation), allows Sigmund to answer questions about OpenSesame much better than other chatbots.

Sigmund is especially good at generating code for (Python) inline_script or inline_javascript items. Try it!

<blockquote style="white-space:pre-wrap;">
I want to create a stimulus display in OpenSesame, using a canvas in a Python inline script. It's a bit complex, so please read carefully! There should be:

- A central fixation dot.
- Six shapes in a circular arrangement around the central dot.
- One of these shapes, randomly selected, should be a square. The other shapes should be circles.
- One of these shapes, again randomly selected, should be green. The other shapes should be red.
- Inside each shape there should be a line segment that is tilted 45 degrees clockwise or counterclockwise.
</blockquote>


## Sigmund respects your privacy

Your messages and attachments are encrypted based on a key that is derived from your password. This means that no-one, not even the administrators of Sigmund, are able to access your data. 

Sigmund uses large-language-model APIs provided by third parties. You can choose which model you want to use in the menu. Importantly, none of these third parties uses data that is sent through the API for any purposes other than replying to the request. Specifically, your data will *not* be used to train their models. For more information, see the terms of service of [OpenAI](https://openai.com/enterprise-privacy), [Anthropic](https://www.anthropic.com/legal/commercial-terms), and [Mistral](https://mistral.ai/terms/).


## Tools that Sigmund can use

The following tools are only available when Research-assistant mode is disabled. (This is to avoid overwhelming the model with instructions in OpenSesame-expert mode.)

### Search Google Scholar

Sigmund can search Google Scholar for scientific literature. Try it!

> Do your pupils constrict when you think of something bright, such as a sunny beach? Please base your answer on scientific literature.

Limitation: Sigmund reads abstracts, titles, author lists, etc. but does not spontaneously reads complete articles. To have Sigmund read complete articles, you can either encourage Sigmund to download the article (see below) or upload the article as an attachment yourself.

Limitation: Google Scholar occasionally blocks searches from autonomous agents such as Sigmund, which results in an error message. When this happens, try again later.


### Execute Python and R code

Sigmund can not only write Python and R code, but also execute it. Try it!

> Can you write a Python function that returns the number of words in a sentence? Please also write some test cases and execute them to make sure that the function is correct.

Limitation: Sigmund cannot use or generate attachments during code execution and cannot display figures. This will be improved in future versions.


### Generate images

Sigmund can also generate images using OpenAI's Dall-E 3 model. Try it!

> Can you generate an image that represents yourself?


## Sigmund is open source

The source code of Sigmund is available on GitHub:

- <https://github.com/open-cogsci/sigmund-ai>


## How can I get an account?

There are two ways to log-in to Sigmund:

- With your Google Account. This also includes organizational accounts that use Google Log-in.
- With your CogSci forum account. If you do not already have a forum account, create one <https://forum.cogsci.nl/>. Next, use this account to login to Sigmund.
