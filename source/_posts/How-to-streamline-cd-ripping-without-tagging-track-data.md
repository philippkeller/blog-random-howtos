---
title: How to streamline cd ripping without tagging track data
date: 2017-12-02 16:23:53
tags:
- ripping
- music
css:
- "pre>code.bash.hljs {font-size: 80%}"

---

![CD tower to rip](/images/automate.jpg)

Since we recently stopped using Spotify, we switched to borrowing CDs from the local library (which, in our case is only 200m away from our house).

Now, because the kids get CDs at least once a week, I needed a way to quickly import those CDs into our Sonos system without too much hassle. Since the kids only borrow children stories (spoken audio) which often are not on MusicBrainz, I needed an easy way to tag them myself. Because I don't care about tagging every single track (because you usually listen to a story start to end anyway), I wanted to have a streamlined process. The following script does:

- Rip the CD and convert it to m4a (AAC encoding, slightly better compression than mp3)
- Eject the CD
- Ask me for the album and artist name
- Opens chrome so I can choose an artwork
- Convert the artwork to JPG in a reasonable size
- Copies the music to the directory on my NAS
- Triggers Sonos to update the music library

<!-- more -->

You may take it as a starting point, you'd want to adapt:

- the paranoia level. `-Y` is only basic checking which is enough for me. You can remove the `-Y` to increase the error handle
- the bitrate (line 7). 96k is enough for me
- the genre (line 8)
- the handling of special characters for the album directory name (line 15)
- the hostname/directory of your NAS
- the updating of the music library (line 23. For Sonos there's [soco](https://github.com/SoCo/SoCo), an awesome python library. If you want to use that you'd need to `pip install soco` first)

Btw: the script can be run in parallel, i.e. when the first cd is finished ripping and the aac encoding runs you can insert the next disc and start the script again.

## OSX

The below script is for Linux. After brew installing cdparanoia, [ffmpeg with aac flags](https://trac.ffmpeg.org/wiki/CompilationGuide/macOS#Specifyingadditionaloptions), AtomicParsley, wget and imagemagick, you need to replace `eject` by `drutil eject` and `firefox` by `open -a firefox -g https://...`. You'd also need to `pip3 install soco` to make the sonos update work


## Linux

To make the following script work, you'll need to [compile ffmpeg with aac](http://trac.ffmpeg.org/wiki/CompilationGuide/Ubuntu), and install AtomicParsley, wget and imagemagick. Also you'd need to `pip3 install soco` to make the third last row working which updates the sonos library.

```bash
#!/bin/bash

set -e
tmp_dir=$(mktemp -d)
cd $tmp_dir
cdparanoia -BY
eject

for i in *.wav; do 
	ffmpeg -i $i -c:a libfdk_aac -b:a 96k ${i/cdda.wav/m4a}
done

total=$(ls *.m4a | wc -l)
for i in *.m4a; do 
	number=$(echo $i | sed 's/^track\([0-9]*\).*/\1/')
	AtomicParsley $i --tracknum "$number/$total" --title "Track $number" --genre "<my genre>" --overWrite
done

echo -n "Album name>" && read album
echo -n "Artist name>" && read artist
search_term="$(perl -MURI::Escape -e 'print uri_escape($ARGV[0]);' "$album $artist cd")"
chrome "https://www.google.ch/search?&q=$search_term&tbm=isch" >/dev/null 2>/dev/null &
echo -n "Artwork url>" && read artwork_url
wget -q "$artwork_url" -O artwork.orig
convert artwork.orig -resize "250x" artwork.jpg
for i in *.m4a; do 
	AtomicParsley $i --artwork artwork.jpg --artist "$artist" --album "$album" --overWrite
done
dir_name=$(echo "${artist// /_}_${album// /_}" | sed 's/Ö/oe/g; s/Ä/ae/g; s/Ü/ue/g; s/ä/ae/g; s/ö/oe/g; s/ü/ue/g' | tr '[:upper:]' '[:lower:]')
mkdir $dir_name
mv *.m4a $dir_name
scp -rp $dir_name user@nas:/directory/of/my/music
python3 -c "import soco; soco.music_library.MusicLibrary().start_library_update()"
cd -
rm -rf $tmp_dir
```