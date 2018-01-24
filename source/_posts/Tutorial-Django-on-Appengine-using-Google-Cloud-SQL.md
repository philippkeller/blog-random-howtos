---
title: 'Tutorial: Django on Appengine using Google Cloud SQL'
tags:
  - django
  - appengine
  - google cloud sql
  - python
  - mysql
date: 2012-12-30 22:47:00
css:
  - "pre>code.hljs.python {font-size: 80%}"
alias: /post/39245389801/tutorial-django-on-appengine-using-google-cloud
---

![](https://lh5.googleusercontent.com/-lX6aq3qvV50/UOC0ONuosVI/AAAAAAAAMUE/Q_occPtbmnQ/s230/Untitled-1.png)
Google is running an [introductory trial for Cloud SQL that runs since Nov 2012 until June 1, 2013](https://developers.google.com/cloud-sql/docs/billing#intro_trial). That's the right hour to test Django on Google App Engine. No need to mess around with their non relational datastore. Just use their MySQL 5.5 in the cloud.

Hence I decided to give it a try and documented all into a very complete tutorial how to start a Django 1.4 project running on "Google App Engine".
<!-- more -->

If you run into exceptions, check the troubleshooting part at the bottom

## Requirements

- **Python 2.7**: If you can't use 2.7 for any reason, no worries. [Here are the adaptions](http://howto.philippkeller.com/2013/01/01/Tutorial-Django-on-Appengine-using-Google-Cloud-SQL-Adaptations-for-Python-2-5/) you need to make for this tutorial to work
- **OS X or Linux**: I'm on OS X 10.8.2, I marked the steps that are OS X specific. For Linux users it's most probably very easy to adapt those. For Windows you certainly need to do some bigger adaptations.
- **MySQL** and its python bindings (for local development)

### What about Django > 1.4?

Appengine supports the versions 0.96, 1.2, 1.3 and 1.4\. This tutorial should work with all those versions. I only tested 1.3 and 1.4 though.
All you need to do with this tutorial is to change 1.4 to 1.3 and keep in mind that the [Django directory structure slightly changed](https://docs.djangoproject.com/en/dev/releases/1.4/#updated-default-project-layout-and-manage-py) in version 1.4 so you need to adapt some of the shell commands.

## Create a Google App Engine Instance

Create new instance on [appengine](https://appengine.google.com/).

Your instance will be located in the US unless you're willing to pay [500$ a month to register for a premium account](https://cloud.google.com/pricing/) (Europe hosting is [for premium accounts only](https://developers.google.com/appengine/docs/premier/location))

## Install Google App Engine (OS X specific)

1.  Download the [GoogleAppEngineLauncher-x.x.x.dmg](https://developers.google.com/appengine/downloads#Google_App_Engine_SDK_for_Python)
2.  Open the dmg, move `GoogleAppEngineLauncher` to Applications
3.  Open GoogleAppEngineLauncher, say yes to the symlinks
4.  Add `$PATH` and `$PYTHONPATH` to shell environment: Add these lines to `.bash_profile` (`.bashrc` on Linux):
    ```bash
    export GAE="/usr/local/google_appengine"
    export PYTHONPATH="$PYTHONPATH:$GAE:$GAE/lib/django_1_4"
    export PATH=${PATH}:$GAE/lib/django_1_4/django/bin/
    ```

    Load these settings into the current session with `source ~/.bash_profile` and make the django binaries executable: `chmod a+x $GAE/lib/django_1_4/django/bin/[a-z]*.py`

## Create the django project

1.  run this in a directory of your choice (I chose `~/python/`). This generates a stub django project. Replace mysite with the name of your django project. `django-admin.py startproject mysite`. Switch into mysite (where `manage.py` resides, only do this if you run Django 1.4): `cd mysite`
2.  create the file `mysite/app.yaml` with this content (replace `appproject` with the id of your appspot.com instance):
    ```
    application: appproject
    version: 1
    runtime: python27
    api_version: 1
    threadsafe: true

    libraries:
    - name: django
      version: "1.4"

    builtins:
    - django_wsgi: on

    handlers:
    - url: /static/admin
      static_dir: static/admin
      expiration: '0'
    ```

3.  edit `mysite/settings.py`: Change the value of `ROOT_URLCONF` from `mysite.urls` to `urls` (else you run into an exception in your live instance)
4.  also in `settings.py` add these 2 lines anywhere at the top:
    ```
    import os
    BASE_DIR = os.path.abspath(os.path.dirname(__file__)) + os.sep
    ```
This is the path prefix you'll put before all the `xyz_ROOT` settings later.
5.  run this one level up of your python project directory: `dev_appserver.py mysite`

Congrats! Your [local instance](http://localhost:8080) now shows [this](http://i.imgur.com/rXh74.png) - hopefully :-)

# Set up Google Cloud SQL

1.  Register Cloud SQL in the [Google API Console](https://code.google.com/apis/console/) (I think you need to add billing, but currently there's a free plan until June 1, 2013)
2.  create a new instance in the **United States** (even when you're located in Europe). The reason is that your Cloud SQL instance needs to be at the same location as your GAE instance. Put your ID of your appspot.com instance to the Authorized Applications.
3.  create a new database using the SQL Prompt: `CREATE DATABASE my_database;`
4.  replace the `DATABASES` section of your `settings.py` with the snippet below: (Replace `my_project:instance1` with your Cloud SQL Instance id and `my_database` with your created database name).

    ```python
    import os
    if (os.getenv('SERVER_SOFTWARE', '').startswith('Google App Engine') or
        os.getenv('SETTINGS_MODE') == 'prod'):
        # Running on production App Engine, so use a Google Cloud SQL database.
        DATABASES = {
            'default': {
                'ENGINE': 'google.appengine.ext.django.backends.rdbms',
                'INSTANCE': 'my_project:instance1',
                'NAME': 'my_database',
            }
        }
    else:
        # Running in development, so use a local MySQL database
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.mysql',
                'USER': 'root',
                'PASSWORD': '',
                'HOST': 'localhost',
                'NAME': 'my_db',
            }
        }
    ```

    These settings configure django to use a local MySQL storage for development. That's very close to the cloud setup, as Google Cloud SQL is [powered by Mysql (currently 5.5)](https://developers.google.com/cloud-sql/faq#databaseengine)

    I highly recommend this as on my machine every SQL query took about 1 second when run against Google Cloud SQL.

    That comes from the fact as first the SQL queries run over HTTP and second the Cloud SQL Instance [runs in California](https://ipdb.at/ip/74.125.132.95).

5.  To trigger the oauth authorization (stored in `~/.googlesql_oauth2.dat`) run this:`SETTINGS_MODE='prod' python manage.py syncdb`

If that last command worked that proves that your Cloud SQL worked so far. Congrats!

Your local MySQL instance is now ready as well. You should check if `MySQLdb` is installed: `python -c "import MySQLdb"`. To test the Django↔MySQL connection run `python mysite/manage.py syncdb`

Whenever you want to sync your django models to:

a) the _live_ db: `SETTINGS_MODE='prod' python manage.py syncdb`
b) the _local mysql_ db: `python manage.py syncdb`

## Deploy your stub app to appspot

Ready to deploy your fresh app to the cloud?

Run this (replace mysite with your project name): 

```bash
appcfg.py --oauth2 update mysite
```

After about 1 minute your fresh Django project should run perfectly on [http://your-id.appspot.com/](http://your-id.appspot.com/)

### Why not sqlite?

Sqlite would be a lot easier to set up, actually there is nothing to install and no server to start, no passwords, etc.

Apart from the fact that I couldn't get it working (details see [here](http://stackoverflow.com/questions/14080430)) it's certainly not a smart idea to run sqlite locally and MySQL (as used by Cloud SQL) in production, [it's very likely that you'll run into issues](http://stackoverflow.com/questions/2306048/django-sqlite-for-dev-mysql-for-prod).

## Serving static files

Django [supports serving static files](https://docs.djangoproject.com/en/dev/howto/static-files/) via `django.contrib.staticfiles`. However, I didn't get this to work. And since serving these files directly via GAE is faster anyways, add this to your `app.yaml`:

```
- url: /media
  static_dir: media
  expiration: '0'
```

This assumes your static files are under `mysite/media`. Your static files now serve under [/media/](http://localhost:8080/media/)

## Enable Admin (optional)

You probably want to enable the admin interface (Steps 2-4 are actually all about getting the static admin files to serve. Full discussion see [here](http://stackoverflow.com/questions/9860610).)

1.  Uncomment all admin specific lines in `settings.py` (in `INSTALLED_APPS`) and `urls.py` (header and urlpatterns). Go sure you don't miss any of these lines by double checking [here, under "Activate the admin site"](https://docs.djangoproject.com/en/1.3/intro/tutorial02/#activate-the-admin-site).
2.  Sync the new models agains live `SETTINGS_MODE='prod' python mysite/manage.py syncdb` and local MySQL `python mysite/manage.py syncdb`
3.  in `settings.py` replace the `STATIC_ROOT` line with (you defined BASE_DIR [above](#create_the_django_project)): `STATIC_ROOT = BASE_DIR + 'static'`
4.  To copy all the admin media assets into `mysite/static` run:
    `python mysite/manage.py collectstatic`
5.  now, [/admin](http://localhost:8080/admin/) should show your admin site, with CSS.

## And now?

*   If you're new to Django or if you want to be 100% sure everything works as expected follow the [django tutorial](https://docs.djangoproject.com/en/1.4/intro/tutorial01/)
*   Want to port your Django app to Google App Engine? I'll likely come up with another article about that.

## Troubleshooting

### On my development machine the web app is _veeery_ slow

Chances are high that you're not using the local MySQL. Start dev_appserver.py with the `--debug` flag and see if it does any RPC calls (SQL queries wrapped into HTTP)

If that isn't the issue you might want to [track performance with appstats](https://developers.google.com/appengine/docs/python/tools/appstats#EventRecorders).

### I wanted to use sqlite instead of mysql as a backend, but I run into `ImportError`, `cannot import name utils`

So did I. I don't know how to solve it. See [here](http://stackoverflow.com/questions/14080430) for details.

### I get an `unknown locale` exception when running syncdb against MySQL

I personally got `ValueError: unknown locale: UTF-8`. There is a [solution for that](http://patrick.arminio.info/blog/2012/02/fix-valueerror-unknown-locale-utf8/)

### I get a `DoesNotExist` exception when accessing /admin/

At one point I got this exception: `DoesNotExist at /admin/`, `Site matching query does not exist`

Solution is [described here](http://stackoverflow.com/questions/9736975/django-admin-doesnotexist-at-admin)

### I get an ImportError for mysite.urls

I got the exception `No module named mysite.urls` before I replaced

`ROOT_URLCONF = 'mysite.urls'` with `ROOT_URLCONF = 'urls'`.

I didn't really understand why that error occurs.

### Further reading

- Official doc: [Official Google Documentation on how to use Django with Google Cloud SQL](https://developers.google.com/appengine/docs/python/cloud-sql/django)
- Tutorial: Google App Engine, Django and Cloud SQL [Part 1](http://bjornalycke.se/articles/google-app-engine-django-and-cloud-sql) and [2](http://bjornalycke.se/articles/google-app-engine-django-and-cloud-sql-part-ii) (Björnalycke)
- Tutorial: [Running Django 1.3 in Google App Engine with Google Cloud SQL (Joemar Taganna)](http://www.joemartaganna.com/web-development/running-django-13-in-google-app-engine-with-google-cloud-sql/)

**Outdated tutorials (based on Datastore, e.g. django-nonrel)**

- [Django on Google App Engine in 13 simple steps (by Thomas Brox Røst)](http://thomas.broxrost.com/2008/04/08/django-on-google-app-engine/)
- [Using Django with Appengine (2 tutorials by Shabda Raaj)](http://agiliq.com/blog/2008/04/two-djangoappengine-tutorials/)