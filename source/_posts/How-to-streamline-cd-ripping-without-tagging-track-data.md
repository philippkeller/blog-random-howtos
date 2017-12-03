---
title: How to streamline cd ripping without tagging track data
date: 2017-12-02 16:23:53
tags:
- ripping
- music
---

![CD tower to rip](/images/cd_tower.jpg)

I wanted to rip a couple of children CDs (spoken stories) which often are not on MusicBrainz -> I need to tag them myself. Because I don't care about tagging every single track (because you usually listen to a story start to end anyway), I wanted to have a streamlined process. The following script does:

- Rip the CD and convert it to m4a (AAC encoding, slightly better compression than mp3)
- Eject the CD
- Ask me for the album and artist name
- Opens chrome so I can choose an artwork (be sure to take a jpg image)
- Copies the music to the directory on my NAS

<!-- more -->

You may take it as a starting point, you'd want to adapt:

- the paranoia level. `-Y` is only basic checking which is enough for me. You can remove the `-Y` to increase the error handle
- the bitrate (line 7). 96k is enough for me
- the genre (line 8)
- the handling of special characters for the album directory name (line 15)
- the hostname/directory of your NAS

Btw: the script can be run in parallel, i.e. when the first cd is finished ripping and the aac encoding runs you can insert the next disc and start the script again.

```
#!/bin/bash
set -e
tmp_dir=$(mktemp -d)
cd $tmp_dir
cdparanoia -BY
eject
for i in *.wav; do ffmpeg -i $i -c:a libfdk_aac -b:a 96k ${i/cdda.wav/m4a}; done
total=$(ls *.m4a | wc -l); for i in *.m4a; do number=$(echo $i | sed 's/^track\([0-9]\+\).*/\1/'); AtomicParsley $i --tracknum "$number/$total" --title "Track $number" --genre "Kinder Geschichten" --overWrite; done
echo -n "Album name>" && read album
echo -n "Artist name>" && read artist
chrome "https://www.google.ch/search?&q=${album// /+}+${artist// /+}+cd&tbm=isch" 2>/dev/null
echo -n "Artwork url>" && read artwork_url
wget -q "$artwork_url" -O artwork.jpg
for i in *.m4a; do AtomicParsley $i --artwork artwork.jpg --artist "$artist" --album "$album" --overWrite; done
dir_name=$(echo "${artist// /_}_${album// /_}" | sed 's/Ö/oe/g; s/Ä/ae/g; s/Ü/ue/g; s/ä/ae/g; s/ö/oe/g; s/ü/ue/g' | tr '[:upper:]' '[:lower:]')
mkdir $dir_name
mv *.m4a $dir_name
scp -rp $dir_name root@wdmycloud:/DataVolume/shares/Public/Shared\\\ Music/kinder
cd -
rm -rf $tmp_dir
```
