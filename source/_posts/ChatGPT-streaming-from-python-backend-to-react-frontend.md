---
title: How to stream ChatGPT output from python backend to react frontend
date: 2023-04-03 06:16:52
tags:
scripts:
- http://cdn.jsdelivr.net/npm/highlightjs-line-numbers.js@2.8.0/dist/highlightjs-line-numbers.min.js
- /files/linenumbers.js
css:
- "pre .hljs-ln-code {padding-left: 10px}"
- "table.hljs-ln tr td {border: none}"
- "table.hljs-ln > tbody > tr:nth-child(odd) > td {background: none}"
- "td.hljs-ln-line.hljs-ln-numbers { color: #ccc !important }"
- "div.post-content > pre > code > table { margin-bottom: 0 }"
---

<img class="caption" alt="What we'll be building today" src="/images/chatgpt_streaming.gif"  />

ChatGPT is great, no question. But when I tried using the API I found the speed of the response lacking. When using OpenAIs web frontend I saw that the answer is coming word for word. I thought: »maybe that'd be possible as well with the API, and this way the user has immediate feedback without needing to wait for 20s!«. And in fact - this is possible, and that's what this howto is covering.

What we're doing today:

1. Use ChatGPT api to get generated text for a certain prompt
2. Stream the data with SocketIO from python (flask)
3. Receive the data in react using SocketIO and append bit by bit to a string

## Backend part (python/flask)

In order to stream data, HTTP does not suffice. The nature of HTTP is that a client gets the data as one response from the server and displays it. To solve streaming (or in general: realtime) needs, WebSockets was invented. We could use Websockets directly but I find SocketIO is an abstraction which makes everything easier, so I'll cover SocketIO in this howto.

To be upfront: There are quite some caveats when using SocketIO. In particular with the issues are with combining gunicorn, eventlet and SocketIO. This is the ugly part of this howto, don't worry, it's becoming bright right after it :)

First: Eventlet is compatible only with python < 3.9. On my OSX I had 3.10 running which let to the error `TypeError: cannot set 'is_timeout' attribute of immutable type 'TimeoutError'`. Apparently, Eventlet [supports only 3.9 as of today](TypeError: cannot set 'is_timeout' attribute of immutable type 'TimeoutError') (April 2023).

To solve it, create a venv with 3.9 or below: `python3.9 -m venv "venv"`

Then, we need the following dependencies in `requirements.txt`:

```
flask
flask-socketio
eventlet==0.30.2
gunicorn==20.1.0
openai
```

Eventlet added a breaking change above version 0.30 which was solving a security issue, but is still not supported on gunicorn, I was keep getting `ImportError: cannot import name 'ALREADY_HANDLED' from 'eventlet.wsgi'`. Apparently, the issue is [fixed and merged into master, just never found its way into PyPI apparently](https://github.com/benoitc/gunicorn/pull/2581#issuecomment-994198667) (latest release is from April 2021, 2 years ago!). Maybe worth finding an alternative to gunicorn.

Ok, ugly part is over, let's go to the more fun part. I assume you already have a flask project which answers to certain API requests, but no SocketIO part. The easiest way to show the setup is with a a minimal `app/__index__.py` file:


```python
from flask import Flask
from .socket import socketio

app = Flask(__name__)
socketio.init_app(app)

if __name__ == "__main__":
    socketio.run(app)
```

You might not yet work with `__init__.py` and have all in `application.py`. In this case you would not omit the import in line 2. It's kindof best practice to split the application into `app/__index__.py` and separate modules for not having all application logic in one place. All socketIO stuff lives in `app/socket.py`.

For the SocketIO part we first need an API key from OpenAI. Go to [User -> API Keys](https://platform.openai.com/account/api-keys) and create one. If you didn't activate payments yet you need to do so first.

Then, put the following code into `app/socket.py`:

```python
from flask_socketio import SocketIO, emit
import time
import openai

openai.api_key = 'sk-my-secret-key'

socketio = SocketIO(cors_allowed_origins='*', logger=True, engineio_logger=True)

@socketio.on('request_chatGPT_description')
def handle_chatgpt_description(data):
    for resp in openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[dict(role='user', content='what does 42 signify, in brief?')],
        stream=True):

        r=resp.choices[0]
        if not 'content' in r['delta']:
            continue
        if r['finish_reason'] == 'stop':
            break
        emit('chatGPT_descripiton_chunk', r['delta']['content'])
```

Wait! ☝️ Before you just copy-paste this, here are a few explanations:

- **Line 5**: that's where you paste your OpenAI API key
- **Line 7**: start SocketIO server:
	- `cors_allowed_origins`: for brevity, I put `*` into there, best practice is to check if the code runs on production and if true, add your prod frontend urls as a list
	- `logger=True, engineio_logger=True`: I wanted to see all client requests/responses in order to better understand what's happening. For prod deployment, remove this part.
- **Line 9**: that's how you "catch" a SocketIO message from the client and react to it. This is the counterpart of `@app.route('/path)` for HTTP
- **Lines 11-14**: OpenAI's chatGPT call. There are many possible parameters (such as `max_tokens`, `temperature`, etc.) covered in the [official doc](https://platform.openai.com/docs/api-reference/models/retrieve). The important parameter is `stream=True` which makes this call return (almost) immediately and offers us a generator to loop over.
- **Lines 16-20, processing streaming output**: The API answers with small chunks of data. Sometimes this is a word, sometimes only part of a word. Drilling down:
	- Line 17-18: I found that the first message is usually an empty "the process has started" message which can be discarded
	- Line 19-20: handling `finish_reason`. The last message has `finish_reason` different from null, which says that the stream now stops. There are also the reason `length` (ran into max_tokens limit or no tokens left in your account) and `content_filter` - blocked because OpenAIs content filters finds your request abusive. See [complete docs](https://platform.openai.com/docs/guides/chat/response-format).
- **Line 21**: this sends the chunk into the SocketIO stream. This is only received from the client who initiated the call (the opposite would be a `broadcast=True`)