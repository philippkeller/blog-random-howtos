---
title: 'Python: easy way to show progress'
tags:
  - python
date: 2011-01-19 12:53:00
---

I use this quite often to indicate how long a loop takes:

<pre>for i, entry in enumerate(entries):
  # do something
  print "\r%s/%s" % (i, len(entries)),
  sys.stdout.flush()
</pre>

It shows
1/13
2/13
&hellip;
on the same line (similar to a progress bar)