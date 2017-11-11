---
title: Streaming audio from Mac to Sonos
tags:
  - sonos
  - airsonos
  - osx
  - yosemite
date: 2015-08-22 14:45:32
---

About a year ago when we moved from a flat into a house we needed a sound system that supported multiple floors and is compatible with non-Apple-devices, so we chose Sonos.

The Sonos-App is kindof ok, but there are situations I want to stream music directly from my mac to Sonos (e.g. using the spotify app which is like 1325 times more exciting to use than the Sonos app).

After trying for hours I finally got a working system with [AirSonos](https://github.com/stephen/airsonos). Only issue I still have is that the audio is about 2 seconds delayed, which makes this unusable for video playback.

<!-- more -->

## How to install

1.  install node and npm either via [installer](http://nodejs.org/download/) or via [homebrew](https://changelog.com/install-node-js-with-homebrew-on-os-x/)
2.  install airsonos via `npm install -g airsonos` (although on some forums users say you need an older node version I got it running with version 0.12.7)
3.  turn off ipv6 via `networksetup -setv6off Wi-Fi`: this is the hacky part: apparently on yosemite this is needed, otherwise every time you try to connect to your Sonos device you get `Could not connect to "&lt;speaker&gt; (AirSonos)"`. I found this trick in [this thread](https://github.com/stephen/airsonos/issues/80)
4.  start `airsonos`
5.  start streaming your audio by pressing `alt(option)` and clicking the volume symbol top right: ![stream music to sonos](https://docs.google.com/uc?id=0B0uw1JCogWHucUJfLXhHVTMyMlk)

## Troubleshooting

*   I had issues with AirSonos after upgrading (error text: `Error: Module did not self-register`) my node version. I needed to `npm uninstall airsonos` and `npm install airsonos` to make it recompile for the new node version
*   when playing music through vlc the music is stuttering (choppy playback), this is due to VLC, see [this thread for details](https://www.reddit.com/r/sonos/comments/2ssi3g/pushing_audio_from_video_from_pc_to_sonos_devices/)
*   audio is about 2 seconds delayed, that is a [known issue](https://github.com/stephen/airsonos/issues/65) which - unfortunately - doesn&rsquo;t look to be solved soon.

## About AirSonos

AirSonos is independent from Sonos, and is a one-man project which kindof fell asleep beginning of 2015 but which might see another update soon, looking at [a dev branch](https://github.com/stephen/airsonos/compare/lib).