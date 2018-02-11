---
title: How to mass convert mp3 files to aac (m3a)
date: 2017-11-29 16:22:14
tags:
- ffmpeg
- mp3
- aac
css:
- "pre>code.bash.hljs {font-size: 80%}"
---

<img src="/images/tape.jpg" />

Since aac has a slightly better compression rate than mp3 (and, geez, mp3 was standardized 1992, there must be better standards nowaday), I decided to mass convert my music library from mp3 to aac

### Won't the quality be just awful?

Of course, re-encoding sounds like a terrible idea. You're converting from one lossfull format to another, similar when mass-converting gifs to jpegs. But on the other hand, for my setting it was just good enough. The library I converted we listen to at home over Sonos or in the car. So in both settings there are only half-decent speakers. Also, many of the tracks I converted from audio cassettes, so they were in a bad quality already. You can certainly play with the bitrate, but if you have invested into an expensive stereo you'd be better off converting from a lossless source.

### Declutter

First things first: Almost everything in life is easier if you first reduce it to the absolute necessity. I recently spoke with a colleague who told me she has converted her whole CD stack into mp3 without first trashing the CDs she never listens to. That's insane.

First, reduce your collection to, say the albums you listened in the past 12 months. Make it 24. But anything beyond is just an overly burden you don't need to carry.

### No words! I just want to copy-paste

Here you go: Once, you haved `cd`ed into the directory with the mp3 files you want to convert, do this:

```bash
detox *.mp3
ffmpeg -i *.mp3([1]) artwork.jpg
for i in *.mp3; do ffmpeg -i $i -c:a libfdk_aac -b:a 128k -vf scale=1280:-2 ${i/mp3/m4a} done
for i in *.m4a; do AtomicParsley $i --artwork artwork.jpg --overWrite; done
rm artwork.jpg && rm *.mp3
```

<!-- more -->

### Line 1: Ascify your filenames with detox

Everything is easier on the shell if instead of having `my süpér s'öñg.mp3` having a file called `my_super_song.mp3`. Detox converts all characters which you need to somehow escape on the shell to ascii characters.

### Line 2: Extract artwork

We'll use ffmpeg to convert from mp3 to aac. Sadly the convert command does not transport your artworks, so you need to first extract the artwork. Use the correct ending (otherwise you'll have a problem in line 4). This command takes the first mp3 and extracts the artwork into artwork.jpg.

### Lines 3-5: Convert

Now, in my version of Ubuntu (Xenial, 16.04) ffmpeg does not come with the compiled in converter from mp3 to aac, so I needed to first [compile ffmpeg from source](http://trac.ffmpeg.org/wiki/CompilationGuide/Ubuntu). This was quite straightforward for me except that it kept saying I had x265 not installed even after doing `sudo apt install libx265-dev`. I needed to follow [these steps](https://bitbucket.org/multicoreware/x265/issues/125/x265-not-found-using-pkg-config#comment-17635086) to have this resolved. 

If you don't want to compile from source then [here](https://superuser.com/a/370637) is a good overview on all the options you have for doing this step. Just be sure to use the right path, `~/bin/ffmpeg` is referring to my compiled ffmpeg binary.

#### Playing with the options

- `-b:a 128k`: this sets a fixed bitrate. If you'd wish a variable bitrate (having more details for more "dynamic" sections of the track) then you can use `-vbr 4` instead, or lower it for lower quality/higher compression.
- the `-vf scale=1280:-2` bit is needed to circumvent the `height not divisible by 2` error. Taken from [here](https://stackoverflow.com/a/20848224/119861)

### Line 6: Set artwork

This just sets back the artwork you extracted in line 2. This was taken from [here](https://superuser.com/a/524120).

### Line 7: Cleanup

Yeah, finally delete all the old file and enjoy the smaller filesize :)
