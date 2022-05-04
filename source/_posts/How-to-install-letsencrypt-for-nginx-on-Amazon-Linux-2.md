---
title: How to install letsencrypt for nginx on Amazon Linux 2
date: 2022-05-04 17:43:20
tags:
---

For a Flask app I'm running nginx on an Amazon Linux 2. To install letsencrypt (auto renewing SSL certificate):

<!--more-->

Verify that nginx' `server` config contains the domain name (www and blank), e.g.

```
server {
    server_name example.ch www.example.ch
    … 
```

Then, install certbot for root (needs to be root because nginx config files are writable by root only)

```
sudo pip3 install certbot certbot-nginx
```

Now, run certbot the first time which does some domain name verification to go sure you really own the domain:

```
sudo /usr/local/bin/certbot --nginx -d example.com -d www.example.com
```

This command creates the SSL certifications and alters the nginx config so that the server listens on port 443 and uses the just generated certs.

Because the certificates expire in 90 days you need to cronjob them, easiest is to run this command (taken from [official doc](https://eff-certbot.readthedocs.io/en/stable/using.html#setting-up-automated-renewal)):

```
SLEEPTIME=$(awk 'BEGIN{srand(); print int(rand()*(3600+1))}'); echo "0 0,12 * * * root sleep $SLEEPTIME && /usr/local/bin/certbot renew -q" | sudo tee -a /etc/crontab > /dev/null
```

