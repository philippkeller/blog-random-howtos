---
title: How to install matomo for nginx on amazon linux 2
date: 2022-07-27 16:04:16
tags:
---

![](/images/matomo.png)

Matomo is a replacement for google analytics which is free when you self-host it. Honestly, I underestimated the effort it takes. Turns out it needs php, mysql and fastcgi running, since I'm running a python/postgres stack it adds quite a bit of clutter onto the server…

But anyway: here you are, the following guide installs Matomo with…

- php8
- mysql 8.0
- nginx / letsencrypt
- php-fpm (fastcgi)

<!--more-->

## Install php8.0

```
sudo yum -y update
sudo yum -y install yum-utils
sudo  amazon-linux-extras | grep php
```

Check if php8.0 is there, my output:
```
  _  php7.4         available    [ =stable ]
 51  php8.0=latest  enabled      [ =stable ]
 ```

Continue:

```
sudo yum-config-manager --disable 'remi-php*'
sudo amazon-linux-extras enable php8.0
sudo yum clean metadata
sudo yum install -y php-cgi php-gd php-xml php-mbstring php-opcache php-soap php-fpm
```

Now, `php --version` should print something like this:

```
PHP 8.0.20 (cli) (built: Jun 23 2022 20:34:07)
…
```


## Install mysql

Same as php, mysql does not come as a first citizen package in amazon linux 2.

1. Check with `rpm -E %{rhel}` what what centos version you're on -> 7 is for amazon linux 2
2. go to https://dev.mysql.com/downloads/repo/yum/ and look up the current download link for your version number (7 for amazon linux 2)
3. click and then on the following page right click "No thanks, just start my download" -> copy url
4. Run `sudo yum install https://dev.mysql.com/get/mysql80-community-release-el7-6.noarch.rpm` - replace url with the url you just got
5. Check with `ls /etc/yum.repos.d` that the new repo mentioning mysql is there
6. Run `sudo amazon-linux-extras install epel -y`
7. Run sudo `rpm --import https://repo.mysql.com/RPM-GPG-KEY-mysql-2022`  (I needed this, otherwise I got `GPG key retrieval failed: [Errno 14] curl#37 - "Couldn't open file /etc/pki/rpm-gpg/RPM-GPG-KEY-mysql-2022"`)
8. Now you finally can install mysql with `sudo yum -y install mysql-community-server`
9. Start mysql and make it run at boot time: `sudo systemctl enable --now mysqld`
10. Check that it is running with `systemctl status mysqld`
11. Grab the temporary root password with `sudo grep 'temporary password' /var/log/mysqld.log`

Now you need to secure the mysql installation with `sudo mysql_secure_installation -p`. Type in initial password and then set the new root password and some other settings:

- Change the password for root > n
- Remove anonymous users? > y
- Disallow root login remotely? > y
- Remove test database and access to it? > y
- Reload privilege tables now? > y

Finally: start mysql `sudo systemctl start mysqld.service`

To reduce memory consumption: Change `/etc/my.cnf` and add the following lines:

```
performance_schema_max_table_instances=150
table_definition_cache=150
table_open_cache=64
secure-file-priv=
```

The last line is needed for the archive command to work.

Restart: `sudo systemctl restart mysqld.service`

## Install matomo

```
cd /opt/
sudo wget https://builds.matomo.org/matomo-latest.zip
sudo unzip matomo-latest.zip
sudo chown -R nginx:nginx /opt/matomo
```

Matomo also needs mysqli so install it with `yum install php-mysqli`

## Add Nginx config

Matomo has [an official github project](https://github.com/matomo-org/matomo-nginx ) where they give guidance how to install matomo behind nginx. The following guide…

1. takes their nginx conf as a base
2. tweaks it to our setup
3. runs letsencrypt to secure it behind SSL. I assume that you already have letsencrypt running, otherwise head over to [my howto](http://howto.philippkeller.com/2022/05/04/How-to-install-letsencrypt-for-nginx-on-Amazon-Linux-2/) and install it first

`cd` into the directory where you have your nginx config files. Mine are at `/etc/nginx/conf.d`

Now, download matomos nginx.conf as a base:

```
wget https://raw.githubusercontent.com/matomo-org/matomo-nginx/master/sites-available/matomo.conf
```

Changes needed:

- remove the first `server {}` directive which redirects port 80 to 443, letsencrypt will add this section again
- replace all `server_name` by your subdomain, e.g. matomo.mydomain.com (subdomain needs to be an A record pointing to your public IP address)
- put `/opt/matomo/` into the `root` line
- remove all lines which listen to port `443` and all which start with `ssl_certificate` (letsencrypt will add those later)
- remove `include ssl.conf`
- remove the last line with `# vim: filetype=nginx` - letsencrypt had issues with this line
- replace the fastcgi block (curly braces after `location ~ ^/(index|matomo|…`) with the following (taken from [here](https://rootritesh.medium.com/configure-php7-1-nginx-on-amazon-linux-2-ami-b545047911))

        fastcgi_pass   unix:/var/run/php-fpm/www.sock;
        fastcgi_index  index.php;
        fastcgi_param  SCRIPT_FILENAME  $document_root$fastcgi_script_name;
        include        fastcgi_params;


Run letsencrypt: `sudo /usr/local/bin/certbot --nginx -d matomo.mydomain.com`. This creates the ssl certificates and puts the ssl config lines into `matomo.conf`. Load the new conf with `sudo systemctl reload nginx`

## Install/configure php-fpm

php-fpm is the fastcgi service which connects nginx with php. You've installed it already earlier with `sudo yum install -y … php-fpm`

Change `/etc/php-fpm.d/www.conf`: First, comment out `user=apache`, `group=apache` and `listen.acl_users=…`, then add the following lines directly under `www`:

```
listen = /var/run/php-fpm/www.sock
listen.owner = nginx
listen.group = nginx
listen.mode = 0664
user = nginx
group = nginx
```

In order to not have php-fpm eats tons of memory, limit the number of processes to 1 (search for the appropriate lines and replace the settings)
```
pm = static
pm.max_children = 1
pm.start_servers = 1
```

- Run `sudo systemctl enable php-fpm` to start php-fpm at boot time
- Run `sudo systemctl start php-fpm` to start the service

Now, https://matomo.mydomain.com/ should show a running matomo! If all goes well… 🤞 

Now, before you start that setup process, go sure to create a mysql database and user for matomo, see [this official documentation](https://matomo.org/faq/how-to-install/faq_23484/). Please not that you need `mysql -u root -p` to start the mysql shell.

## Crontab for log archival

Finally you need this cronjob to archive the logs:

5 * * * * nginx /usr/bin/php /opt/matomo/console core:archive --url=https://matomo.myserver.com/ >> /var/tmp/matomo-archive.log

I hope I covered everything. The installation was not super straight forward for me (that's why I created this howto!), if I forgot something, please put a comment.
