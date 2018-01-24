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

![iTunes screenshot of purple motions tracks](https://lh3.googleusercontent.com/-31kHXDajZUM/UMZL5kXClbI/AAAAAAAALXE/S26QsfTYpHs/s498/itunes_purple_motion.png)

If you were part of the demoscene in your former life, if you were and still are fond of modules (those sound files with the mod, xm, s3m, it, &hellip; ending), if you are a linux user and if you still want to listen to this music on your computer without doing all the tweaks of installing (or even compiling) music player plugins for itunes or amarok or if you simply want to listen to Purple Motions tunes on your mp3 player then this little tutorial is for you. If not, then you won't have read that far anyway..

<!-- more -->

## short version for the impatient

download [downloadmod.py](https://docs.google.com/uc?export=download&amp;id=0B0uw1JCogWHucXNKdUVlUGsyaGs) and [mod2mp3.py](https://docs.google.com/uc?export=download&amp;id=0B0uw1JCogWHubk9CdDFCdnJXNkE) into /usr/local/bin/

```bash
sudo apt-get install xmp adplay unrar lame
mkdir ~/modules/
downloadmod.py ~/modules/ "Purple Motion"
mod2mp3.py ~/modules/
```

### First, get those modules

The first task is to get those modules onto your computer (as you most certainly deleted them - either per accident or when you were in needed of some space on your hard drive back when hard drives where small and expensive)

Afaik the most complete module resource is [modland](ftp://ftp.modland.com). The crux is that it's just an ftp site with deep directory structure and without a search facility. All it has got is a complete list of all the modules in a RAR file (which is kept up to date by a cron job) that holds a text file with all the available modules and their path.

To download all modules of a certain artist, I wrote a little [python script](https://docs.google.com/uc?export=download&amp;id=0B0uw1JCogWHucXNKdUVlUGsyaGs) that downloads the module list, unrars it, caches it for further search requests, searches for the artist and downloads all modules of that particular artist.

`downloadmod.py ~/modules/ "Michael Land"` downloads all Adlib songs of Michael Land and places them into ~/modules/Michael Land/ and writes some artist/album meta information into those newly created directories.

Alternatively you can adapt a quick and dirty [bash function](http://pastie.org/private/nszifsjxnw5obz8bai3ng). It uses wget and is quite messy but it should do the task as well. You have to download and unpack the module list before you call the shell function.

### Then, convert those modules into mp3 files

To convert the modules into mp3 files you usually take a module player and call with some special parameters in order to "play" the module into a wav-File and convert that wav into an mp3 file.

On linux, I'd suggest to install this module players (both exist as debian packages and work without hassle on my ubuntu installation)

- [xmp](http://xmp.sourceforge.net/) is *nix "native"
- [adplay](http://adplug.sourceforge.net/) supports many adlib formats

I wrote a [python script](https://docs.google.com/uc?export=download&amp;id=0B0uw1JCogWHubk9CdDFCdnJXNkE) that converts the downloaded modules into mp3s using the just mentioned module players. You need at least xmp or adplay. If you install both, you'd be able to play about 90% of all modules.

Just call `mod2mp3.py` with your root module directory as argument and the script creates a mp3 file for each module that is convertible and isn't already converted. If you downloaded the modules with my download script, this script will use the meta information of the first script to write the id3 tags of the mp3s.

If everything worked, you now should have mp3 files with correct id3 tags that can be imported into your amarok/itunes library.

### What about us windows users?

Sorry guys. I've got to let you down. One whole evening I tried to get any module player writing it's output to a wave file from the command line. I tried [modplug](http://www.modplug.com/playerinfo.html) and [Winamp](http://www.winamp.com) with a [module player plugin](http://www.winamp.com/plugins/details.php?id=132367) but without luck. If you succeed, let me know. Up to then, just take a linux box, copy/download all modules there and let the box convert your modules over night and import it back into your iTunes player. That's what I did.