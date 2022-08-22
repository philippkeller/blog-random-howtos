---
title: Launching weegee.ch - my first side project
date: 2022-08-14 17:21:35
tags:
---

<img src="/images/weegee.png" />

During the past few months I've been busy creating my first side project. This week, I've reached a milestone - both Web and mobile apps are now available, may I present to you:

[weegee.ch](https://weegee.ch) - the biggest shared flat search in Switzerland. In Switzerland, shared flats are called WGs (for **W**ohn**G**emeinschaft), pronounced "weegee", that's where the domain name comes from.

It's available for [web](https://weegee.ch), [iOS](https://apps.apple.com/app/id1632452144) and [android](https://play.google.com/store/apps/details?id=ch.weegee).

<img src="/images/ios_store.png" onclick="window.open('https://apps.apple.com/app/id1632452144'); return false;" />

<img src="/images/play_store.png" onclick="window.open('https://play.google.com/store/apps/details?id=ch.weegee'); return false;" />

<div style="clear: both" />

The data is coming from crawling shared flats from wgzimmer, flatfox, urbanhome, ronorp and tutti - creating a shared flat search which is twice as big as any of the other portals!

<!-- more -->

The technologies I've used:

- crawling: scrapy (with python)
- data processing: python (the tricky bit here is how to detect duplicates. Often people post their room on several platforms at once, in order to not have them many times on the platform, you need to detect the tuplicates)
- website: flask
- mobile apps: flutter
- authentication: firebase
- analytics: matomo

Basically the past 8 posts on this blog are all documenting the challenges I've solved along the way.