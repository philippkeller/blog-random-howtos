---
title: How to stream chatGPT from Flask to react (using only HTTP)
date: 2023-10-14 12:56:53
tags:
- flask
- chatGPT
- react
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

ChatGPT's UI (and most of the 3rd party tools) have streaming output. This is not just a gimmick but follows the way LLMs generate the output: word for word.

So you usually also want to output to the user: word for word.

Turns out this is very simple to achieve. 

[My first attempt was using web sockets](http://howto.philippkeller.com/2023/04/03/ChatGPT-streaming-from-python-backend-to-react-frontend/) - which turned out to be unstable and needs lots of overhead. In came [Ilias](https://typefully.com/illyism), who created a [ChatGPT to Telegram Bot](https://magicbuddy.chat/) that streams responses to users. He was like: »man, why are you using sockets for this!?« And enlightened me that the same thing is possible with good ol' http requests.

Plus: This method uses *zero* additional dependencies.

Hope that I've wet your appetite.

So enough of those introductory bubbles, let's talk tech.

The whole idea is that the frontend (react) `POST`s a JSON to backend (flask) which then "streams" the data back by outputting line by line, leaving the HTTP connection open until all is done.

<!-- more -->

## Backend: Flask

Because I hate those "step by step" tutorial blog posts which make me scroll down to copy-paste their final code let's start with the final code right away and I explain you what's happening **under** it. Of course you're fine to just copy-paste and leave, like you would do anyway when asking chatGPT.

```python
from flask import request, Flask
import openai

openai.api_key = 'sk-my-secret-key'

app = Flask(__name__)

@app.route("/message/stream", methods=["POST"])
def chatgpt_message_stream():
    j = request.get_json()

    def generate():
        for resp in openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[dict(role="user", content="what does 42 signify, in brief?")],
            stream=True):
            r = resp.choices[0]
            if not "content" in r["delta"]:
                continue
            if r["finish_reason"] == "stop":
                break
            chunk = r["delta"]["content"]
            chunk = chunk.replace("\n", "<br />")
            yield f"{chunk}\n"

    return generate(), {"Content-Type": "text/plain"}
```

Explanations:

- **Line 4**: that's where you paste your OpenAI API key
- **Lines 13-16**: OpenAI's chatGPT call. There are many possible parameters (such as `max_tokens`, `temperature`, etc.) covered in the [official doc](https://platform.openai.com/docs/api-reference/models/retrieve). The important parameter is `stream=True` which makes this call return (almost) immediately and offers us a generator to loop over.
- **Lines 17-21, processing streaming output**: The API answers with small chunks of data. Sometimes this is a word, sometimes only part of a word. Drilling down:
	- Line 27-28: I found that the first message is usually an empty "the process has started" message which can be discarded
	- Line 29-30: handling `finish_reason`. The last message has `finish_reason` different from null, which says that the stream now stops. There are also the reason `length` (ran into max_tokens limit or no tokens left in your account) and `content_filter` - blocked because OpenAIs content filters finds your request abusive. See [complete docs](https://platform.openai.com/docs/guides/chat/response-format).
- **Lines 23-24, streaming and newline handling**: to make flask send a line to the frontend you need to finish the line with newline. `yield` sends this via the generator (see [Flask documentation](https://flask.palletsprojects.com/en/2.3.x/patterns/streaming/#basic-usage)). As chatGPT *also* outputs newlines, we need to "escape" chatGPT's newlines. I find replacing them with `<br />` is the clearest way to do so.


## React

For the frontend we need to tell react to not wait for the whole response to finish but to update chunk by chunk. This is done by the function `streamPost` which takes a callback function as argument. All credits go to copilot. I literally only wrote the function header 🤘

```javascript
BACKEND_URL = 'http://127.0.0.1:5000'
export async function streamPost(url, payload, update) {
    const url = BACKEND_URL + path
    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify(payload)
    })
    const reader = response.body.getReader()
    const decoder = new TextDecoder('utf-8')
    let partial = ''
    while (true) {
        const { done, value } = await reader.read()
        if (done) {
            break
        }
        partial += decoder.decode(value)
        const lines = partial.split('\n')
        partial = lines.pop()
        for (const line of lines) {
            update(line)
        }
    }
    if (partial) {
        update(partial)
    }
}
```

Explanations:

- **Line 12-13: Streamed reader init**: With fetch you usually would call `response.json()` which reads the whole response and parses the json output into a js object. Of course we don't use JSON as it would only be valid once the whole output is through. Instead we now get hold of the reader object and tell it that the output will be `utf8`.
- **Line 16: read line by line**: `read()` reads from the http connection until the first newline arrives (which makes me doubt the meaningfulness of Line 21 - but let's trust copilot here).
- **Line 24+28: callback** for every line the callback function is called, that's how you call it:

```javascript
"use client"
import { useState } from 'react';
 
export default function App() {
    const [result, setResult] = useState('')
 
    const requestAutoDescription = () => {
        setResult('')
        streamPost('/message/stream', { test: 1 }, (value) => {
            value = value.replace(/<br \/>/g, '\n')
            setResult(chatgptOutput => chatgptOutput + value)
        })
    }
 
    return (
        <div className='m-10'>
            <button onClick={requestAutoDescription}>
                Generate
            </button>
            <div className='mt-10'>{result}</div>
        </div>
    );
}
```

Line 10 is where the `<br />` is turned back into newlines. Rest is straight forward react code.

## Nginx

On my dev machine the setup above worked out of the box. On the server with gunicorn / nginx it turns out that nginx holds back the response until the full response is done, I needed to add into my `location` direction additionally `proxy_buffering off;` and just to be sure I pushed up the timeout of a http connection to an hour. Here's the full location block I'm using:

```nginx
location / {
    proxy_pass         http://127.0.0.1:8000/;
    proxy_redirect     off;

    proxy_set_header   Host                 $host;
    proxy_set_header   X-Real-IP            $remote_addr;
    proxy_set_header   X-Forwarded-For      $proxy_add_x_forwarded_for;
    proxy_set_header   X-Forwarded-Proto    $scheme;

    proxy_read_timeout 3600;
    proxy_buffering off;
}
```

That's it! As always - if I missed something please use the comments (not that anyone would do that anyway - but just in case 😅)