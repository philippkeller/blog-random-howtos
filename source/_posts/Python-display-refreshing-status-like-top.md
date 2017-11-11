---
title: 'Python: display refreshing status (like top)'
tags:
  - python
date: 2010-04-05 00:24:00
---

In scripts I often want to display some status information (e.g. progress), this can be achieved with e.g.:

<pre>print "progress: %i %%\r" % i,
sys.stdout.flush()
</pre>

but this just works for one-liners. I wanted to have what `top` or `less` do: open a new &ldquo;window&rdquo; and being able to write **everywhere** in the window, not just on the last line.<!-- more -->

Found out that [curses](http://docs.python.org/library/curses.html) does exactly that - but I didn&rsquo;t find a stripped-to-the-bare-necessities-example, so here you are:

<pre>import curses, time
from datetime import datetime
w = curses.initscr()
try:
  while True:
  w.erase()
  w.addstr("some status..\ncurrent time\n%s" % datetime.now())
  w.refresh()
  time.sleep(1)
finally:
  curses.endwin()
</pre>