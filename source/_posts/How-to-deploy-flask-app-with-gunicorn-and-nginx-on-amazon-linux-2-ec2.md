---
title: How to deploy flask app with gunicorn and nginx on amazon linux 2 ec2
date: 2022-05-02 18:49:13
tags:
---

This howto assumes that you
- created your ec2 already with **Amazon Linux** on it (I personally use lightsail as have great prices and IMO are a bit cheaper than ec2 instances, but there's no difference on OS level)
- opened port 80 (http) and 22 (ssh)

<!--more-->

## Flask

Deploy your flask app into `/home/ec2-user/app`. For simplicity let's put the following into `/home/ec2-user/app/app.py`:

```python
from flask import Flask
application = Flask(__name__)

@application.route("/")
def index():
    return "Nobody expects the spanish inquisition!"

if __name__ == "__main__":
    application.run(host='0.0.0.0', port='8080')
```

Let's use virtualenv (important especially if you run more than just this one webapp)

The following does:
- create the `venv` folder
- make the current shell use the venv folder (exit again with `deactivate`)
- install flask and gunicorn into venv
- store the used pip package versions into requirements.txt

 Run this in `~/app/`:

```
virtualenv -p python3 venv
source venv/bin/activate
pip install flask
pip install gunicorn
pip freeze > requirements.txt
```

Now, `python app.py` should output `* Running on http://127.0.0.1:8080`

## Gunicorn / systemd

While still in the venv, run gunicorn:

```
gunicorn app
```

This should output `[INFO] Listening at: http://127.0.0.1:8000`

You usually want your gunicorn process to start at boot time. Also you would like to be able to restart it. For this use systemd:

put this into `/etc/systemd/system/flaskapp.service`:

```
[Unit]
Description=Gunicorn daemon to serve my flaskapp
After=network.target
[Service]
User=ec2-user
Group=ec2-user
WorkingDirectory=/home/ec2-user/app
ExecStart=/home/ec2-user/app/venv/bin/gunicorn app
[Install]
WantedBy=multi-user.target
```

Note that this starts the gunicorn executable within the venv directory - which itself uses the python with all required pip packages.

To start it:

```
sudo systemctl start flaskapp
```

Check if it started without errors:

```
sudo systemctl status flaskapp
```

To start the service on linux boot time (it's started after network becomes available, because of the `After=network.target` line):

```
sudo systemctl enable flaskapp
```

gunicorn now runs at 127.0.0.1:8000 - that's where we need to point nginx to.

## Nginx

On Amazon Linux, nginx cannot be installed with `sudo yum install nginx` but instead with:


```
sudo amazon-linux-extras install nginx1
```

Now start it and make it start at linux boot time:

```
sudo systemctl start nginx
sudo systemctl enable nginx
```

To install the reverse proxy, create `/etc/nginx/conf.d/app.conf` (this is loaded because `/etc/nginx/nginx.conf` contains this line: `include /etc/nginx/conf.d/*.conf;`):

```
server {
    listen 80 default_server;
    server_name _;
    access_log  /var/log/nginx/access.log;
    error_log  /var/log/nginx/error.log;

    location / {
        proxy_pass         http://127.0.0.1:8000/;
        proxy_redirect     off;

        proxy_set_header   Host                 $host;
        proxy_set_header   X-Real-IP            $remote_addr;
        proxy_set_header   X-Forwarded-For      $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto    $scheme;
    }
}
```

The config is taken from the [flask documentation](https://flask.palletsprojects.com/en/2.1.x/deploying/wsgi-standalone/#proxy-setups) which also explains the `proxy_set_header` lines.

To test if the config is correct: `sudo nginx -t` and if there are no errors you can reload: `sudo systemctl reload nginx`.

Now, to check that nginx can connect to the gunicorn socket check error.log:

```
sudo tail -F /var/log/nginx/error.log
```

Now you should be able to see your app on http://public_ip_address

## And then…

- did changes to your app? Store the new files on ec2 and then run `sudo systemctl restart flaskapp` to make gunicorn refresh the webpage
- an alternative to the http forward would be forwarding by socket, but that proved to be more error prone. If you think that sockets are more performant, they're not, see [this stackoverflow answer](https://stackoverflow.com/a/54013893).