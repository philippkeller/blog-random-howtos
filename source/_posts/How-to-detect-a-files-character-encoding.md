---
title: How to detect a files character encoding
tags:
  - python
date: 2012-07-17 09:59:00
---

iconv is alright - except it&rsquo;s sometimes hard to know in which encoding the file is I just got.

There is [enca](http://freecode.com/projects/enca) which promises to work, but I couldn&rsquo;t get it working. I was looking for a simple tool that just outputs the encoding without the need of any parameters

Now the python module [chardet](https://github.com/dcramer/chardet) comes to the rescue. Once you have git forked you can write this boilerplate python script &ldquo;detect.py&rdquo;:

<pre>#!/usr/bin/python
import sys, chardet
a = open(sys.argv[1]).read()
print chardet.detect(a)
</pre>

after
`chmod a+x detect.py`
you can write:
`./detect.py my_strange_file.txt`

<div class="blogger-post-footer">![](https://blogger.googleusercontent.com/tracker/290349385069691835-984568850343921941?l=coderandomm.blogspot.com)</div>