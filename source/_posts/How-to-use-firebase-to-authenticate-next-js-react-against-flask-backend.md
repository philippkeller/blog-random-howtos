---
title: How to use firebase to authenticate next.js/react against flask backend
date: 2023-03-11 07:09:18
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

<img class="caption" alt="What you'll have at the end of this howto" src="/images/firebaseui.png" width="368" />

I'm migrating my frontend away from Flask to next.js, reducing my flask app to only backend apis.

This blogpost explains how a next.js app authenticates against flask backend using flask-login.

It assumes that you have in your flask backend:

- an endpoint `auth/sign-in` which…
	- accepts a POST request with the firebase idToken
	- checks the token against firebase
	- when successful, logs it in with flask_login's `login_user`
- your api routes secured with @login_required

<!-- more -->

If you don't have this yet you can follow [this blogpost](/2022/06/16/How-to-use-Firebase-Auth-in-Flask/)

It also assumes you have…

- a firebase project set up
- some authentication providers (google, facebook, …) already set up.

## next.js / react: configure firebase

First, you need to install the needed npm packages:

```
npm i firebase firebaseui
```

Then, you'd need to tell next.js/react your firebase API secrets. I created a separate file `firebaseConfig.js`:

```javascript
import { initializeApp, getApps } from "firebase/app";

const firebaseConfig = {
    apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
    authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
    projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
    storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET,
    messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID,
    appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID,
    measurementId: process.env.NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID,
};

// Initialize Firebase
let firebase_app = getApps().length === 0 ? initializeApp(firebaseConfig) : getApps()[0];

export default firebase_app;
```

For this to work you'd need to add the actual values in your `.env` file (get the values from your firebase project in "Project Overview" -> "Your apps", you might need to create your app first.)

## Firebaseui

Sadly, there is no up-to-date react component for firebaseui, at this moment (March 2023), the best solution is to copy-paste `StyledFirebaseAuth.tsx` [from here](https://github.com/firebase/firebaseui-web-react/pull/173#issuecomment-1215648239) into your project (go sure you have typescript enabled).

## Setting it all together

I find the easiest way to explain how it all works is to show a minimal example and explain the different parts:

```javascript
import firebase_app from 'firebaseConfig';
import { getAuth } from "firebase/auth";
import { useEffect, useState } from "react";
import StyledFirebaseAuth from "@/components/StyledFirebaseAuth";
import firebase from 'firebase/compat/app';
import "firebase/compat/auth";
import { fetchJson, postJwt } from "api/api";

export default function FirebaseExample() {
    const [isSignedIn, setIsSignedIn] = useState(false);
    const uiConfig = {
        signInFlow: 'popup',
        signInOptions: [
            firebase.auth.GoogleAuthProvider.PROVIDER_ID,
            firebase.auth.FacebookAuthProvider.PROVIDER_ID,
            firebase.auth.EmailAuthProvider.PROVIDER_ID,
        ],
        callbacks: {
            // Avoid redirects after sign-in.
            signInSuccessWithAuthResult: () => false,
        },
    }

    useEffect(() => {
        const unregisterAuthObserver = getAuth(firebase_app).onAuthStateChanged(user => {
            if (user != null) {
                postJwt('/auth/sign-in', user.accessToken).then((res) => {
                    fetchJson('/api/forcelogin')
                })
            }
            setIsSignedIn(!!user);
        });
        // Make sure we un-register Firebase observers when the component unmounts.
        return () => unregisterAuthObserver();
    }, [])
    return (
        <>
            <Head>
                <title>Firebase Example</title>
            </Head>
            <Header />
            <main>
                {!isSignedIn && (
	                <div id="firebase">
	                    <StyledFirebaseAuth
	                      uiConfig={uiConfig}
	                      firebaseAuth={getAuth(firebase_app)} />
	                </div>
                )}
            </main>
        </>
    )
}
```

## FirebaseUI config (Lines 11-22)

That's where you configure what buttons will be shown in your  app, what happens after the sign-in etc. Check [the configuration options in the firebaseui github documentation](https://github.com/firebase/firebaseui-web#configuration).

In this example I didn't want any redirect but handle all myself in next.js directly (as I need to send the token to the backend in order to sign in).

## Sending the token to the backend (Lines 24-35)

Firebase uses the `onAuthStateChanged` event whenever a user is logged in or logged out. When this is called you'd need to check if there's a `user` object (the user really logged in) and if yes, send a post to the backend. I extracted this part into a separate function `postJwt`:

```javascript
export async function postJwt(path, payload) {
    const url = BACKEND_URL + path
    const res = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/jwt'
        },
        credentials: 'include',
        body: payload
    })
    return res
}
```

Then, on the other end, python processes the post with (this is just an excerpt, I'm using `flask-firebase` package, see [the full code with more context](https://github.com/klokantech/flask-firebase/blob/master/flask_firebase/__init__.py))

```python
@app.route('/auth/sign-in')
def sign_in(self):
    header = jwt.get_unverified_header(request.data)
    with self.lock:
        self.refresh_keys()
        key = self.keys[header['kid']]
    token = jwt.decode(
        request.data,
        key=key,
        audience=self.project_id,
        algorithms=['RS256'])
    account = Account.query.filter_by(firebase_user_id=token['sub']).one_or_none()
    # handle account creation/update
    login_user(account)
    return 'OK'
```

After the JWT token is verified against Firebase, the user is logged in with `login_user`. This sets a cookie which is returned with the `OK` response.

One tricky part is to appease CORS: Cookies are only set if you add `credentials: 'include'` in the POST to the backend. Then, you also need to tell Flask to return the cookies using `support_credentials`, example:

```
from flask_cors import CORS

cors = CORS(app, resources={
  r"/api/*": {"origins": ["http://127.0.0.1:3000"], "supports_credentials": True},
  r"/auth/sign-in": {"origins": ["http://127.0.0.1:3000"], "supports_credentials": True},
 39 })
 ```
 
I only have to allow it for my dev environment, as on prod, both frontend and backend runs on the same port.

 
**Also: Be sure to both run your backend and your frontend on 127.0.0.1**. I had one running on localhost and the other on 127.0.0.1 and wondered why no cookie was stored in the browser!


## Subsequent calls (Line 28)

To show how subsequent calls works I added a get request to `/api/forcelogin` on line 28.

The nice thing is that next.js/react stores the cookie it got in the `sign-in` POST into the browsers' cookies which are automagically sent in any subsequent requests, **if** you also explicitly say so with `credentials: 'include',`. Here's my `fetchJson` function definition:

```javascript
export async function fetchJson(path) {
    const url = BACKEND_URL + path
    const response_raw = await fetch(url, {
      credentials: 'include'
    })
    return await response_raw.json()
}
```

That's it! I hope I didn't forget any caveat in my howto, otherwise, please leave a comment below and I'll add the missing part.


## Styling

I was not too happy with the default styling of firebaseui, so I  included custom styling. See [firebaseui documentation](https://github.com/firebase/firebaseui-web-react#styling) on more details, basically it needs importing a css file in `_app.jsx`:

```
import '@/styles/firebaseui.global.css'
```

Into the css file I put this to make the buttons bigger:

```css

#firebase .firebaseui-container {
    max-width: 50em;
}

#firebase .firebaseui-idp-button,
#firebase .firebaseui-tenant-button {
    max-width: none;
    padding-top: 1em;
    padding-bottom: 1em;
}

#firebase .firebaseui-idp-text {
    font-size: 18px;
}
```