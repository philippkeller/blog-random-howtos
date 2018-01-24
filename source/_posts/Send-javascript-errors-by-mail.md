---
title: Send javascript errors by mail
tags:
  - python
  - django
  - javascript
date: 2007-10-06 15:33:00
alias: /post/37471157855/send-javascript-errors-by-mail
css:
  - "pre>code.hljs.javascript {font-size: 80%}"

---

I'm running [a Django-powered site for a closed user group](http://extranet.icoc.ch) and added a bit of JavaScript magic here and there (mainly [Prototype](http://www.prototypejs.org/) and [Tooltip](http://codylindley.com/Javascript/219/finding-a-javascript-tool-tip-script)).

<!-- more -->

Now Django sends me a mail whenever a 404 or 500 error occurs. But when one of my users encounters a JavaScript-Error, I'm not informed. I thought anyone in the web has solved this problem but didn't find anything, so here's my take: Just send any error using Ajax (here: using [Prototypes Ajax abstraction](http://www.prototypejs.org/learn/introduction-to-ajax)) to the server

```javascript
onerror = Extranet.mailError;
function mailError(msg, url, line) {
   var postBody = 'url=' + url + '&amp;line=' + line + '&amp;message=' + escape(msg)
   + '&amp;useragent=' + escape(navigator.userAgent) + '&amp;user=' + escape(user_name);
   var myAjax = new Ajax.Request('/api/jserror/', {method: 'post', postBody: postBody});
}
```

  `user_name` is a JavaScript variable holding the Django username (so I know whom I can inform when the error is fixed).

  On the server side, I just send me mails containing the JavaScript error message, the username and the user agent:

```python
def jserror(request):
   from django.core.mail import mail_admins
   omit_messages = ['pointerobj is not defined', 
     'tipobj is not defined', 
     'ns6 is not defined', 'enabletip is not defined']
    if request.POST.get('message', '') not in omit_messages:
    message = """url: %s (%s) %s
    user-agent: %s
    username: %s""" % (request.POST.get('url', ''), 
        request.POST.get('line', ''),
        request.POST.get('message', ''),
        request.POST.get('useragent', ''),
        request.POST.get('user', ''))
    mail_admins("javascript error", urldecode(message))
    return HttpResponse()
```

Yeah, that's all very trivial but I wonder what other solutions exist for this problem...