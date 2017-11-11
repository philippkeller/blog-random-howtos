---
title: 'Django: Serve big files via fcgid'
tags:
  - python
  - django
date: 2007-10-03 10:14:00
alias: /post/37471157406/django-serve-big-files-via-fcgid
---

I&rsquo;ve got a [django project](http://extranet.icoc.ch) running which requires you to login to access files.

That means that I have to serve the files via python, like this:
<pre>
  @login_required
  def download(request, filename):
    # ... some code specific to my site ...
    response = HttpResponse(mimetype=postUpload.mimetype)
    response['Content-Disposition'] = "attachment; filename=" + original_filename
    response['Content-Length'] = os.path.getsize(filename_path)
    response.write(open(filename_path).read())
    return response
</pre>
<!-- more -->

The problem: If the download of a file exceeded 5 minutes (big files and/or low
bandwidth) the download was canceled on the server side by a timeout. This Apache
configuration for mod_fcgid solved the problem (see [mod_fcgid documentation for BusyTimeout](http://fastcgi.coremail.cn/doc.htm))

<pre>
&lt;IfModule mod_fcgid.c&gt;
 BusyTimeout 1200
&lt;/IfModule&gt;
</pre>

The problem was that the apache module scanned every minute for processes that run for
more than BusyTimeout seconds. These processes are potentially in bad health (infinite
loop et al.) and have to be killed. Not so with my processes (since I know what I&rsquo;m
doing..). The setting of the busy timeout to 1200 seconds now lets my processes run for
a maximum of one hour.

As this setting can&rsquo;t by overwritten in a htaccess file by default I needed to bug
[my web hosting provider](http://www.citrin.ch/) with the request, which was
handled in 24 hours, so thanks for that one!

PS: If you know of another way how to serve protected static files via a single sign on
(no HTTP basic auth), please let me know.