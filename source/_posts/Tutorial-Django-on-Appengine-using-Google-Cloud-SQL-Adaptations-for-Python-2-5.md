---
title: >-
  Tutorial: Django on Appengine using Google Cloud SQL - Adaptations for Python
  2.5
tags:
  - django
  - python 2.5
  - google app engine
  - main.py
date: 2013-01-01 21:53:00
alias: /post/39406024646/tutorial-django-on-appengine-using-google-cloud
---

Google App Engine has two Python runtimes, [either 2.7.3 or 2.5.2](https://developers.google.com/appengine/docs/whatisgoogleappengine#The_Application_Environment). You should try to develop for 2.7, as it&rsquo;s the current default on GAE and all the documentations often only describe this Python version.

Additionally: If you use Python 2.5 you can only use Django up to version 1.3\. (At least I couldn&rsquo;t find out how to get version 1.4 working, `use_library('django', '1.3')` would fail if setting 1.4

If you&rsquo;re stuck with Python below 2.7 for any reason, that&rsquo;s what you need to change following [my tutorial](http://howto.philippkeller.com/2012/12/30/Tutorial-Django-on-Appengine-using-Google-Cloud-SQL/) in order to get it working for Python 2.5:

<!-- more -->

1.  If you&rsquo;re Python version is 2.6, you need to get a 2.5 enviroment: either using virtualenv: <pre>virtualenv -p /usr/bin/python2.5</pre>
  or simply change the default python version:

      OS X: <pre>defaults write com.apple.versioner.python Version 2.5</pre>
  Linux: <pre>ln -f /usr/bin/python2.6 /usr/local/bin/python</pre>

2.  In order to make oauth work you need to install ssl (which comes preinstalled with 2.7): <pre>sudo /usr/bin/python2.5 /usr/local/bin/pip install ssl</pre>
3.  Instead of `app.yaml` [defined in the tutorial](http://howto.philippkeller.com/2012/12/30/Tutorial-Django-on-Appengine-using-Google-Cloud-SQL#create_the_django_project) you need to put 2 files into your project dir: app.yaml and main.py:
`app.yaml` (replace `appproject` with the id of your appspot.com instance):
<pre>
application: appproject
version: 1
runtime: python
api_version: 1

    handlers:
- url: /static/admin
  static_dir: static/admin
  expiration: '0'
- url: /.*
  script: main.py
</pre>
`main.py` (normally those main.py snippets in the web set `DJANGO_SETTINGS_MODULE` to `mysite.settings`, but in my enviroment it only worked when omitting the project name):
<pre>
import os
import sys
import logging
# Google App Hosting imports.
from google.appengine.ext.webapp import util
from google.appengine.dist import use_library
os.environ["DJANGO_SETTINGS_MODULE"] = "settings"
use_library('django', '1.3')
# Enable info logging by the app (this is separate from appserver's
# logging).
logging.getLogger().setLevel(logging.DEBUG)
def log_exception(*args, **kwds):
  logging.exception('Exception in request:')
# Force sys.path to have our own directory first, so we can import from it.
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
# Force Django to reload its settings.
from django.conf import settings
settings._target = None
import django.core.handlers.wsgi
import django.core.signals
import django.db
# Log errors.
django.dispatch.Signal.connect(
   django.core.signals.got_request_exception, log_exception)
# Unregister the rollback event handler.
django.dispatch.Signal.disconnect(
django.core.signals.got_request_exception,
django.db._rollback_on_exception)
def main():    # Create a Django application for WSGI.
    application = django.core.handlers.wsgi.WSGIHandler()
    # Run the WSGI CGI handler with that application.
    util.run_wsgi_app(application)
if __name__ == "__main__":
    main()
</pre>

4.  That&rsquo;s it, the rest of the tutorial should work!

### Troubleshooting

**I get `pkg_resources.DistributionNotFound: pip==0.8` when trying to pip install**

Run this first:

<pre>sudo easy_install --upgrade pip</pre>