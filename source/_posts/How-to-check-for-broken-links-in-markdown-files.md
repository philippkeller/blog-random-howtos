---
title: How to check for broken links in markdown files
date: 2018-01-26 23:49:45
tags:
---

![dead link](/images/dead.jpg)

Having blog articles up >10 years needs some kind of tool to check for dead links.

Having googled a bit I didn't find anything convincing. So I just created a very dirty solution which did the job for me.

You start it with 

```python3 link_checker.py path/to/md/files/ http://mysite.com```

and it iterates over all `.md` files in `path/to/md/files` for links and images in your articles, sends a `HTTP HEAD` request and prints everything which does not look right

<!-- more -->

### Some words of caution:

This is just a 80% solution. It will give you some false negatives:

- it does regex to find the links. It finds both markdown styled links and `a href=` styled links
- it sends a basic user-agent, but some sites such as google don't allow crawling so you'll see `405 Method not allowed`

### Screw that, I want to use it anyway

[Here's the script to download](/files/link_checker.py). And here's how it looks (it even put the <span style="color: green">✔</span> in green and the <span style="color: red">x</span> in red) (if you use Hexo you can exactly call the script like that):

```sh
$ ./link_checker.py source http://localhost:4000
How-to-set-up-raspberry-pi-headless-with-ssh-and-wifi.md ‎✔
Tagsystems-performance-tests.md x
-------------------------------
http://pastie.org/5480706 Got exception timed out
http://pastie.org/5480722 Got exception timed out
http://www.webmasterworld.com/forum23/3557.htm Got exception HTTP Error 403: Forbidden
How-to-attach-a-file-to-google-spreadsheet.md ‎✔
Django-Serve-big-files-via-fcgid.md ‎✔
Python-Print-list-of-dicts-as-ascii-table.md ‎✔
Tags-Database-schemas.md ‎✔
Tags-with-MySQL-fulltext.md ‎✔
How-to-reset-Jambox-when-bluetooth-completely-stopped-working.md ‎✔
```