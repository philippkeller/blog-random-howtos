---
title: How to authenticate flutter app against flask backend (using Firebase)
date: 2022-06-25 08:18:39
tags:
---

![Flutter meets Flutter meets Firebase](/images/flutter_flask_firebase.png)

Over the past 2 weeks I struggled quite a bit to come up with a setup to make my flutter app work together with my flask web app. There's not much documentation online, I'm wondering if I'm the only one on the web to do so. I doubt that, as Flutters web capabilities are still somehow limited and you'd normally want to have a "full blown" flutter web app alongside your flutter app.

What I wanted is to have login possibility with social login providers (Google, Facebook, Apple ID, via Oauth) both on Flutter and on my Flask app and when a user uses both web and the app they would use the same profile and settings.

Where I was mentally stuck was this: How do I guarantee that the OAuth identity which the flutter app would send to my flask server can be trusted? Every app can be decompiled, you can put a [proxy in front of it](https://www.charlesproxy.com/) or whatever other hacks the internet provides. So flask needs a mechanism to double-check what flutter just sent. 

<!-- more -->

There are different solutions to that. [auth0 has a good post on that](https://auth0.com/docs/get-started/authentication-and-authorization-flow/which-oauth-2-0-flow-should-i-use), in essence there are two options

- [Resource Owner Password Flow](https://auth0.com/docs/get-started/authentication-and-authorization-flow/resource-owner-password-flow) - you can do that if you totally trust your app, e.g. when you deploy it to the closed group of users for which you have device management in place. This situation doesn't apply for me and also Auth0 doesn't recommend it. Still, it would have been relatively easy to implement
- [PCKE (Proof Key for Code Exchange)](https://auth0.com/docs/get-started/authentication-and-authorization-flow/authorization-code-flow-with-proof-key-for-code-exchange-pkce) - for when the client cannot be trusted. But this needs some fancy protocol between the mobile app and the server and alone by [looking at the flowchart diagram I got headaches](https://auth0.com/docs/get-started/authentication-and-authorization-flow/authorization-code-flow-with-proof-key-for-code-exchange-pkce#how-it-works).

I am a beginner in flutter development. And I already had my issues getting the OAuth flow working on my app in a standalone manner. So I didn't trust myself getting PCKE implemented. I then realized that this is exactly the point of having auth providers: These things are so complex, you would not want to code this on your own. That's why there is Auth0, Cognito or Firebase. As there is a lot of documentation and libraries how to get Flutter to work with Firebase, and there's a free pricing as long as you don't have too many users (10K signups per month), I decided to take this path.

## How does it work?

The whole thing works like this:

1. flutter triggers the oauth flow for e.g. google
2. flutter gets back the auth details, including email address, name, etc. (depends on oauth provider)
3. the auth details are sent to firebase which enriches it with an encrypted token
4. the token is sent to flask, which verifies the token against firebase
5. flask logs the user in (via flask_login) and sends back a session cookie
6. the session cookie is stored in flask (using [requests](https://pub.dev/packages/requests)) and used for subsequent api calls
7. so you don't need to login after you force close your app you store the session also in the apps preferences (using [shared_preferences](https://pub.dev/packages/shared_preferences)
Wow, that sounds complicated when written out like this, but in code it's fairly simple…

## Preparation step 1: Flutter and firebase

1. Create a firebase project
2. add firebase-core as a dependency to flutter and add the configuration to have it talk to your just created firebase project: [follow this howto](https://firebase.google.com/docs/flutter/setup)
3. add firebase-auth, that's basically `flutter pub add firebase_auth`
4. add the social login providers you want. Follow [this howtos](https://firebase.google.com/docs/auth/flutter/federated-auth) - they are very well made. This is probably the most complicated step as there are a lot hoops you need to jump through, especially for Facebook. Be sure to not skip any step when following the howto and test it all both on Android and iOS

## Preparation step 2: Flask and firebase

As this is not well documented, I created a [separate blog post](http://howto.philippkeller.com/2022/06/16/How-to-use-Firebase-Auth-in-Flask/) for it. Trust me, it's worth it. Before I switched to firebase I used [flask-dance](https://flask-dance.readthedocs.io/). This was already quite efficient but still it needs quite a lot of boilerplate code around it. After I switched to firebase I could delete about 40% of all my python code and around 20% of template code.

## Marry flutter and flask so they can live happily ever after


