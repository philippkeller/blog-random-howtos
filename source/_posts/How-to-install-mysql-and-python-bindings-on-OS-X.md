---
title: How to install mysql and python bindings on OS X
tags:
  - mysql
  - python
  - MySQLdb
date: 2012-12-30 14:45:00
---

For my upcoming post [&ldquo;how to create a Django project on Google App Engine&rdquo;](http://howto.pui.ch/post/39245389801/tutorial-django-on-appengine-using-google-cloud-sql) I needed to install a MySQL instance and configure python to do so.
MySQL is a little beast, and it is not so straight forward to install it on OS X&hellip;

<!-- more -->

1.  Install mysql. Find good instructions [here](http://www.djangoapp.com/blog/2011/07/24/installation-of-mysql-server-on-mac-os-x-lion/). I also did the optional step to install the MySQL startup scripts and preference pane. I know I&rsquo;ll forget how to start the mysql server manually after 2 months, so the entry in `System Preferences` is handy.
2.  create your database: <pre>mysql -u root -e "CREATE DATABASE my_db;"</pre>
3.  Optionally set a password for root (I left it blank as my local mysql server only serves to localhost):
<pre>
      $ mysql -u root
      mysql&gt; use mysql;
      mysql&gt; update user set password=PASSWORD("NEWPASSWORD") where User='root';
      mysql&gt; flush privileges;
      mysql&gt; quit
    </pre>
4.  Install MySQLdb (the mysql python binding): <pre>sudo pip install MySQL-python</pre> If you haven&rsquo;t yet installed `pip`: <pre>sudo easy_install pip</pre>
5.  Test it: <pre>python -c "import MySQLdb"</pre> should output no error.

### Troubleshooting

*   `Library not loaded: libmysqlclient.18.dylib`, `Reason: image not found`. Solution: <pre>sudo ln -s /usr/local/mysql/lib/libmysqlclient.18.dylib /usr/lib/libmysqlclient.18.dylib</pre> as described [here](http://stackoverflow.com/questions/6383310)
*   `IOError: [Errno 13] file not accessible: '/Library/Python/2.7/site-packages/MySQL_python-1.2.3-py2.7-macosx-10.8-intel.egg'`. I ran into this problem when building `MySQL-python` myself. <pre>pip install MySQL-python</pre> solved this problem
*   on `pip install MySQL-python` I got `EnvironmentError: mysql_config not found`

      Before running pip, run this
  <pre>export PATH=$PATH:/usr/local/mysql/bin</pre>