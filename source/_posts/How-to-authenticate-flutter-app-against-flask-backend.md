---
title: How to authenticate flutter app against flask backend (using Firebase)
date: 2022-06-25 08:18:39
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

![Flutter meets Flask meets Firebase](/images/flutter_flask_firebase.png)

Over the past 2 weeks I struggled quite a bit to come up with a setup to make my flutter app work together with my flask web app. There's not much documentation online, I'm wondering if I'm the only one with that setup. I doubt that, as Flutters web capabilities are still somehow limited and you'd normally want to have a "full blown" flask web app alongside your flutter app.

What I wanted is to have a login possibility with social login providers (Google, Facebook, Apple ID, via Oauth) both on Flutter and on my Flask app and when a user uses both web and app they would use the same profile and settings.

Where I was mentally stuck was this: How do I guarantee that the OAuth identity which the flutter app would send to my flask api backend can be trusted? Every app can be decompiled, you can put a [proxy in front of it](https://www.charlesproxy.com/) or whatever other hacks the internet provides. So flask needs a mechanism to double-check what flutter just sent. 

<!-- more -->

There are different solutions to that. [auth0 has a good post on that](https://auth0.com/docs/get-started/authentication-and-authorization-flow/which-oauth-2-0-flow-should-i-use), in essence there are two options

- [Resource Owner Password Flow](https://auth0.com/docs/get-started/authentication-and-authorization-flow/resource-owner-password-flow) - use this if you totally trust your app, e.g. when you deploy it to a closed group of users for which you have device management in place. This situation doesn't apply for me and also Auth0 doesn't recommend it. Still, it would have been relatively easy to implement.
- [PCKE (Proof Key for Code Exchange)](https://auth0.com/docs/get-started/authentication-and-authorization-flow/authorization-code-flow-with-proof-key-for-code-exchange-pkce) - use this when the client cannot be trusted (IMO 99.9% of mobile apps). But this needs some fancy protocol between the mobile app and the server and alone by [looking at the flowchart diagram](https://auth0.com/docs/get-started/authentication-and-authorization-flow/authorization-code-flow-with-proof-key-for-code-exchange-pkce#how-it-works) I got headaches

I am a flutter noob. And I already had my issues getting the OAuth flow working on my app in a standalone manner. So I didn't trust myself getting PCKE implemented. I then realized that **this is exactly the raison d'être of auth providers**: These things are so complex, you would not want to code this on your own. That's why there is Auth0, Cognito or Firebase. As there is a lot of documentation and libraries how to get Flutter to work with Firebase, and there's a free pricing as long as you don't have too many users (10K signups per month), I decided to go with Firebase.

## How does it work?

The whole thing works like this:

1. flutter triggers the oauth flow for e.g. google
2. flutter gets back the auth details, including email address, name, etc. (depends on oauth provider)
3. the auth details are sent to firebase which creates the user if it doesn't exist yet, enriches it with a user id and packs it into an encrypted token
4. the token is sent to flask, which verifies the token against firebase
5. flask logs the user in (via flask_login) and returns a session cookie
6. the session cookie is stored in flutter (using [requests](https://pub.dev/packages/requests)) and used for subsequent api calls
7. to preserve the user logged in even after app close, the session is stored in apps preferences (using [shared_preferences](https://pub.dev/packages/shared_preferences))

Wow, that sounds complicated when written out like this, but in code it's fairly simple, given you have both your flutter app and flask hooked up with firebase, which are the first two preparation steps:

## Preparation step 1: Flutter and firebase

1. Create a firebase project
2. add firebase-core as a dependency to flutter and add the configuration to have it talk to your just created firebase project: [follow this howto](https://firebase.google.com/docs/flutter/setup)
3. add firebase-auth, that's basically `flutter pub add firebase_auth`
4. add the social login providers you want. Follow [this howtos](https://firebase.google.com/docs/auth/flutter/federated-auth) - they are very well made. This is probably the most complicated step as there are a lot of hoops you need to jump through, especially for Facebook. Be sure to not skip any step when following the howto and test it all both on Android and iOS

## Preparation step 2: Flask and firebase

As this is not well documented, I created a [separate blog post](http://howto.philippkeller.com/2022/06/16/How-to-use-Firebase-Auth-in-Flask/) for it. Trust me, it's worth it. Before I switched to firebase I used [flask-dance](https://flask-dance.readthedocs.io/). This was already quite efficient but still it needs quite a lot of boilerplate code around it. After I switched to firebase I could delete about 40% of all my python code and around 20% of template code.

## Marry flutter and flask so they can live happily ever after

Now to the interesting part: The matrimony of flutter and flask.

Here's an example how you would trigger the google login flow and send the token to flask.

The example uses the [requests package](https://pub.dev/packages/requests) (install it with `flutter pub add requests`) - this saves the returned login session cookie behind the scenes and adds it to every subsequent http request. You could use any other package to achieve that but requests looks well maintained.

```dart
import 'package:google_sign_in/google_sign_in.dart';
import 'package:requests/requests.dart';

…

Future<String?> signInWithGoogle() async {
  final GoogleSignInAccount? googleUser = await GoogleSignIn().signIn();
  final GoogleSignInAuthentication? googleAuth =
      await googleUser?.authentication;
  final credential = GoogleAuthProvider.credential(
    accessToken: googleAuth?.accessToken,
    idToken: googleAuth?.idToken,
  );
  UserCredential userCredentials =
      await FirebaseAuth.instance.signInWithCredential(credential);
  return userCredentials.user?.getIdToken();
}

var cookies = await Requests.getStoredCookies('mysite.com');
if (!cookies.keys.contains('session')) {
  print('cookie missing triggering signin flow');
  String? idToken = await signInWithGoogle();
  if (idToken != null) {
    await Requests.post('https://mysite.com/auth/sign-in',
        body: idToken,
        headers: {'Content-Type': 'application/jwt'},
        bodyEncoding: RequestBodyEncoding.PlainText);
  }
}

var r = await Requests.get('https://mysite.com/api/something_which_requires_login');
```

The important lines are 24-27 where the idToken (encrypted by firebase) is sent to `/auth/sign-in`. This is an endpoint of [flask_firebase](https://github.com/klokantech/flask-firebase) ([see code](https://github.com/klokantech/flask-firebase/blob/master/flask_firebase/__init__.py#L103)) which, after verifying the token, calls the callback you registered, e.g.

```python
from flask_login import login_user

@auth.production_loader
def production_sign_in(token):
    account = Account.query.filter_by(firebase_user_id=token['sub']).one_or_none()
    if account is None:
        account = Account(firebase_user_id=token['sub'])
        db.session.add(account)
    account.email = token['email']
    account.email_verified = token['email_verified']
    account.name = token.get('name')
    account.photo_url = token.get('picture')
    db.session.flush()
    login_user(account)
    db.session.commit()
```

Lines 5-13 stores the user in your own database (something you'd want to do if you want to store e.g. the name of the user).
Then in line 14 `login_user` sets the cookie session, returns and makes `flask_firebase` return code 200 with payload `OK`, which in flutter you discard. But the session cookie is stored by `requests`, so when you do the api call in line 31 (flutter code above) this includes the required cookie. `/api/something_which_requires_login` now knows which user is calling, so you can use e.g. `current_user.name`.

The last thing you need to do is to store the session cookie, so that when the user quits the app, the app stays logged in. For this, add [shared_preferences](https://pub.dev/packages/shared_preferences) with `flutter pub add shared_preferences` and then hook it into your flutter code into two places:

Before line 19 add this, in order to load the cookie from the shared_preferences:

```dart
var cookies = await Requests.getStoredCookies('mysite.com');
SharedPreferences? prefs;
if (!cookies.keys.contains('session')) {
  prefs = await SharedPreferences.getInstance();
  if (prefs.containsKey('session')) {
    print('cookie not set, load session from prefs');
    await Requests.addCookie(
        'mysite.com', 'session', prefs.getString('session')!);
  }
}
``` 

and after line 28 add this to store it:

```dart
var cookies = await Requests.getStoredCookies('mysite.com');
        prefs?.setString('session', cookies['session']!.value);
```

That's all there's to it. I hope you'll get it working! 🤞
