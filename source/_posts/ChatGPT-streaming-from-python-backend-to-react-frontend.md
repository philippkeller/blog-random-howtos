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

<img class="caption" alt="Streaming chatGPT API response to react frontend. GIF depicts actual speed" src="/images/chatgpt_streaming.gif"  />

ChatGPT is great, no question. But when I tried using the API, I found the speed of the response lacking.

When using OpenAIs web frontend I saw that the answer is appearing word for word.

I thought: »I might be able to stream the chatGPT api response in realtime. This way the user has immediate feedback without needing to wait for 20 seconds«.

And - lo and behold - this is possible!

**What we're building today**:

1. Call ChatGPT API
2. Stream the data with SocketIO from python (flask)
3. Receive the data in react using SocketIO and display it bit as bit in realtime

<!-- more -->

## Backend part (python/flask)

In order to stream data, HTTP does not suffice. The nature of HTTP is that a client gets the data as one response from the server and displays it. To solve streaming (or in general: realtime) needs, Websockets was invented. We could use Websockets directly but I find SocketIO is an abstraction which makes everything easier, so I'll cover SocketIO in this howto.

First, put the following dependencies into `requirements.txt`:

```
flask
flask-socketio
eventlet
gunicorn
openai
```

**Update September 2023**: Previous version of this guide needed to stick versions to past releases as eventlet, gunicorn and socketio weren't playing together otherwise. Things have improved a lot and the most recent versions are compatible to each other again. For reference, this is the versions which worked well together for me:

- gunicorn 21.2.0
- eventlet 0.33.3
- Flask-SocketIO 5.3.6

**Why eventlet? 🤔**

SocketIO is asynchronous and [flask-socketio requires an asynchronous service to run on, preferably eventlet](https://flask-socketio.readthedocs.io/en/latest/intro.html#requirements). It comes down go eventlet or gevent and I found eventlet to have more documentation / community support.

**Ah, and Gunicorn? 🧐**

Gunicorn you only need for the prod deployment. For development, the development server does suffice. Instead [you could also use the embedded server](https://flask-socketio.readthedocs.io/en/latest/deployment.html#embedded-server) but gunicorn sounded more stable for me. Bear in mind that you need to deploy it with only one worker, this is due to the »limited load balancing algorithm used by gunicorn«

**Alright, can we start now please? 🙏**

Of course, let's go to the more fun part. I assume you already have a flask project which answers to certain API requests, but no SocketIO part yet.

For the SocketIO part we first need an API key from OpenAI. Go to [User -> API Keys](https://platform.openai.com/account/api-keys) and create one. If you didn't activate payments yet you need to do so first.


The easiest way to show the setup is with this minimal example `app.py` file:


```python
# needs to be first to patch requests library for openai
import eventlet
eventlet.patcher.import_patched('requests.__init__')

from flask import Flask

from flask_socketio import SocketIO, emit
import openai

app = Flask(__name__)
socketio.init_app(app)

socketio = SocketIO(app, cors_allowed_origins='*')

openai.api_key = 'sk-my-secret-key'

@socketio.on('request_chatGPT_description')
def handle_chatgpt_description(data):
    for resp in openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[dict(
            role='user', 
            content='what does 42 signify, in brief?')],
        stream=True):

        r=resp.choices[0]
        if not 'content' in r['delta']:
            continue
        if r['finish_reason'] == 'stop':
            break
        emit('chatGPT_descripiton_chunk',
            r['delta']['content'])

if __name__ == "__main__":
    socketio.run(app)
```

But wait! ☝️ Before you just copy-paste this, here are a few explanations:

- **Line 1-2**: socketio/eventlet needs network calls to be done in an asynchronous way (using coroutines). As the `openai` module uses `requests` to run API requests we need to first import requests "patched" so that when openai uses it, it's done in a async/coroutine way.
- **Line 15**: that's where you paste your OpenAI API key
- **Line 13**: start SocketIO server:
	- `cors_allowed_origins`: for brevity I put `*` into there, best practice is to check if the code runs on production and if true, add your prod frontend urls as a list
- **Line 17**: that's how you "catch" a SocketIO message from the client and react to it. This is the counterpart of `@app.route('/path)` for HTTP
- **Lines 19-24**: OpenAI's chatGPT call. There are many possible parameters (such as `max_tokens`, `temperature`, etc.) covered in the [official doc](https://platform.openai.com/docs/api-reference/models/retrieve). The important parameter is `stream=True` which makes this call return (almost) immediately and offers us a generator to loop over.
- **Lines 26-32, processing streaming output**: The API answers with small chunks of data. Sometimes this is a word, sometimes only part of a word. Drilling down:
	- Line 27-28: I found that the first message is usually an empty "the process has started" message which can be discarded
	- Line 29-30: handling `finish_reason`. The last message has `finish_reason` different from null, which says that the stream now stops. There are also the reason `length` (ran into max_tokens limit or no tokens left in your account) and `content_filter` - blocked because OpenAIs content filters finds your request abusive. See [complete docs](https://platform.openai.com/docs/guides/chat/response-format).
- **Line 31-32**: this sends the chunk into the SocketIO stream. This is only received from the client who initiated the call (the opposite would be a `broadcast=True`)

That's it, the backend is ready. On the dev machine you need to start your app with `python app.py` (`flask run` does not work). Don't worry - it does auto-reload on save.

On the server I start it with `venv/bin/gunicorn --worker-class eventlet -w 1 app:app --access-logfile /var/log/gunicorn/access_log.log --error-logfile /var/log/gunicorn/error_log.log`

## Frontend part (React)

On the react side you first need to install the socketIO client:

```bash
npm install socket.io-client
```

Then, create `src/utils/socket.js`:

```javascript
import { io } from 'socket.io-client';

const SOCKET_URL = 'http://127.0.0.1:5000'
export const socket = io(SOCKET_URL)
```

This assumes that your flask backend runs on port 5000. Both, http and SocketIO runs on the same port.

Finally, put this into `app/chatgpt/page.jsx`:

```javascript
"use client"
import { socket } from '@/utils/socket'
import { useEffect, useState } from 'react';
 
export default function App() {
    const [isConnected, setIsConnected] = useState(false);
    const [result, setResult] = useState('')
 
    const requestAutoDescription = () => {
        socket.emit('request_chatGPT_description', 
                    { msg: 'test' })
    }
 
    useEffect(() => {
        function onChunk(value) {
            setResult(result => result + value)
        }
        function onConnect() {
            setIsConnected(true);
        }
        if (socket.connected) {
            onConnect()
        }
        socket.on('chatGPT_descripiton_chunk', onChunk)
        socket.on('connect', onConnect)
 
        return () => {
            socket.off('chatGPT_descripiton_chunk', onChunk)
        };
    }, []);
 
    return (
        <div className='m-10'>
            {isConnected ?
                <button
                    onClick={requestAutoDescription}
                >
                    Generate
                </button> : <div>Connecting to server</div>
            }
            <div className='mt-10'>{result}</div>
        </div>
    );
}
```

Explanations:

- **Line 9-11, 36**: sends the SocketIO message to the server. Here, we also send some data, which in the server side we could access using `data['test']` within the `handle_chatgpt_description` function. The function is triggered upon button click (Line 35)
- **Line 15-17 and 24**: This receives the `emit` of the backend and appends the string (without a space! because it also emits parts of words) to the `result` state which is displayed in **Line 41**
- **Line 18-23, 25**: Handling the connect to the backend. I wanted to show the button only when the connect to the backend was successful, so I added a `isConnected` state (Line 5). I found that the connection usually happens before `useEffect` is called, that's why I check for `socket.connected` and call `onConnect()` if the connect already happened.

That's it, if all works well, you should see words appearing when clicking the button. On issues, please use the comments below.