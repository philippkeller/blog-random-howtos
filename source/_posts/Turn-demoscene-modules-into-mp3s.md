---
title: Turn demoscene modules into mp3s
tags:
  - demoscene
  - music
  - python
  - modules
date: 2007-02-10 19:39:00
alias: /post/37471155417/turn-demoscene-modules-into-mp3s
---

**Update 2018** (11 years later): I fixed the python scripts below, so they should still work! If not, then please add a comment below. Btw: Isn't it **amazing** that modland is still up and running after all these years?

![iTunes screenshot of purple motions tracks](/images/purple_motion.png)

If you were part of the demoscene in your former life, if you were and still are fond of modules (those sound files with the mod, xm, s3m, it, &hellip; ending), if you are a linux user and if you still want to listen to this music on your computer without doing all the tweaks of installing (or even compiling) music player plugins for itunes or amarok or if you simply want to listen to Purple Motions tunes on your mp3 player then this little tutorial is for you. If not, then you won't have read that far anyway..

<!-- more -->

## short version for the impatient

Download [downloadmod.py](/files/downloadmod.py) and [mod2mp3.py](/files/mod2mp3.py) and start then with python2 (the command may be just `python` on your machine).

```bash
sudo apt-get install xmp adplay unrar lame
mkdir ~/modules/
python2 downloadmod.py ~/modules/ "Purple Motion"
python2 mod2mp3.py ~/modules/
```

### First, get those modules

The first task is to get those modules onto your computer (as you most certainly deleted them - either per accident or when you were in needed of some space on your hard drive back when hard drives where small and expensive)

Afaik the most complete module resource is [modland](ftp://ftp.modland.com). The crux is that it's just an ftp site with deep directory structure and without a search facility. All it has got is a complete list of all the modules in a RAR file (which is kept up to date by a cron job) that holds a text file with all the available modules and their path.

To download all modules of a certain artist, I wrote a little [python script](/files/downloadmod.py) that downloads the module list, unrars it, caches it for further search requests, searches for the artist and downloads all modules of that particular artist.

`downloadmod.py ~/modules/ "Michael Land"` downloads all Adlib songs of Michael Land and places them into ~/modules/Michael Land/ and writes some artist/album meta information into those newly created directories.

### Then, convert those modules into mp3 files

To convert the modules into mp3 files you usually take a module player and call with some special parameters in order to "play" the module into a wav-File and convert that wav into an mp3 file.

On linux, I'd suggest to install this module players (both exist as debian packages and work without hassle on my ubuntu installation)

- [xmp](http://xmp.sourceforge.net/) is *nix "native"
- [adplay](http://adplug.sourceforge.net/) supports many adlib formats

I wrote a [python script](/files/mod2mp3.py) that converts the downloaded modules into mp3s using the just mentioned module players. You need at least xmp or adplay. If you install both, you'd be able to play about 90% of all modules.

Just call `mod2mp3.py` with your root module directory as argument and the script creates a mp3 file for each module that is convertible and isn't already converted. If you downloaded the modules with my download script, this script will use the meta information of the first script to write the id3 tags of the mp3s.

If everything worked, you now should have mp3 files with correct id3 tags that can be imported into your amarok/itunes library.