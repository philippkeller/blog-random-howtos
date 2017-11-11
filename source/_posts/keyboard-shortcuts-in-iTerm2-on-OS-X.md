---
title: keyboard shortcuts in iTerm2 on OS X
tags:
  - os x
  - bash
date: 2012-06-25 15:46:00
---

<span>I love having my terminal completely on the server, so I can connect from everywhere and just resume with all my windows.</span>

<span></span><span>That&rsquo;s why I always work on tmux and my iTerm just has one tab.</span>

<span></span><span>That&rsquo;s why I remapped e.g. cmd-t to &ldquo;new tmux tab&rdquo; and cmd-w to &ldquo;close tmux tab&rdquo;.<!-- more --></span>

<span></span><span>To achieve this, in tmux&rsquo; preferences in keys you need to add global shortcut keys. I&rsquo;m using ctrl-z as prefix, if you use ctrl-a use 0x01 instead. These are the combinations for ctrl-z (L</span><span>ist items are: Key combinations - Hex Codes - Comment):</span>

*   <span>⌘0 - _0x1a 0x22_ - switch to window 0\. Other window suffixes (replace 22 by that): 1=31,2=32,3=33,4=34,5=35,6=36,7=37,8=38,9=39</span>
*   <span>⌘r - _0x1a 0x2c 0x08 0x08 0x08 0x08 0x08_ - rename current window (0x08 sends backspace)</span>
*   <span>⌘t - _0x1a 0x63 - _new &ldquo;tab&rdquo; (=new tmux window)</span>
*   <span>⌘w - 0x04 - sends ctrl-d</span>
*   <span>⌥⌘← - 0x1a 0x1b 0x5b 0x44 - jump to plane to the left (ctrl-z &ldquo; or ctrl-z % to split windows into panes in tmux). Replace 0x44 by 0x41 (up), 0x42 (down), 0x43 (right)</span>
*   <span>⌘↑ - 0x1a 0x5b - jump to tmux history</span>

<span>Use </span>`showkey --ascii`<span> on the shell to inspect the hex keys of key strokes.</span>