---
title: How to install hashicorps vault for use with python - the quick'n'easy way
date: 2022-07-21 10:46:09
tags:
---

I wanted to get rid of AWS secrets manager - both because it was eating 7% of my hosting costs (2.42$ per month, but still :) and I wanted to get a bit more independant of AWS.

The number one alternative - or let's say the quite more powerful and even free - is Hashicorp Vault - from the same company who built Terraform, Consul and Vagrant.

The learning curve is not so steep - I followed their [https://learn.hashicorp.com/collections/vault/getting-started](excellent getting started guide). But if you want to have it even quicker, then use this guide.

For the howto I chose:

- Amazon linux ec2 instance
- S3 as storage backend for 
- Nginx for ssl proxy
- Python client

Exchanging any of those is a piece of cake really… but let's stay specific:

<!--more-->


## Installing vault itself

```
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://rpm.releases.hashicorp.com/AmazonLinux/hashicorp.repo
sudo yum -y install vault
```

Voila - `vault` should be a valid command and should print out:

```
Usage: vault <command> [args]

Common commands:
    read        Read data and retrieves secrets
    write       Write data, configuration, and secrets
    delete      Delete secrets and configuration
    list        List data or secrets
…
```

## Starting vault

To play around with vault, you'd want to start it with `vault server -dev` but as this is the super expedite lane we won't do that and go right into production mode.

The install above should have created the file `/etc/vault.d/vault.hcl` - replace this file with the following:


```
ui = true

disable_mlock = true

storage "s3" {
  access_key = "ASDF123ASDF123ASDF12"
  secret_key = "8VUzCT2wjnfYDTcMD/8VUzCT2wjnfYDTcMD/8VUz"
  region     = "eu-central-1"
  bucket     = "bucket-name"
}

# HTTP listener
listener "tcp" {
  address = "127.0.0.1:8200"
  tls_disable = 1
}
```

Configuration options are documented [here](https://www.vaultproject.io/docs/configuration) - in some details, especially the disable_mlock, but in essence the above does:

1. enable the ui - which is great to quickly create and see secrets, much similar that how AWS secrets manager has it
2. configures S3 as secrets storage - that means the actual secrets are not stored on the ec2 server -> you can nuke your ec2 server and your secrets are not lost
3. create an API endpoint at 127.0.0.1:8200 - like this it's only reachable from localhost and HTTPS is not enabled yet, which we'll improve later


## S3 as storage backend

- create a new s3 bucket, enable versioning so you can roll back whenever you accidentally deleted a secret etc.
- create a new IAM user with programmatic access wo you'll get a access and secret key
- install the following policy:

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "ListObjectsInBucket",
            "Effect": "Allow",
            "Action": ["s3:ListBucket"],
            "Resource": ["arn:aws:s3:::bucket-name"]
        },
        {
            "Sid": "AllObjectActions",
            "Effect": "Allow",
            "Action": "s3:*Object",
            "Resource": ["arn:aws:s3:::bucket-name/*"]
        }
    ]
}
```

- replace `access_key`, `secret_key`, `region`, and `bucket-name` in `/etc/vault.d/vault.hcl`


That should have been it, you can test it by starting `sudo vault server -config=/etc/vault.d/vault.hcl` - if there is was an error with your s3 config you would see it right away.

## API / Nginx proxy

Vault offers an API. This is used by your python clients to retrieve secrets. Since most likely not all your python clients reside on your ec2 server (at least your dev environment is likely on your laptop), you need to expose the api to outside. No worries, this is safe, but it should be secured by HTTPS.

The Vault docs [use Kubernetes to create SSL certificates](https://www.vaultproject.io/docs/platform/k8s/helm/examples/standalone-tls) - since I first had letsencrypt SSL certificates already and second didn't want to use Kubernetes just for creating SSL certificates I chose to use nginx as a SSL proxy.

In your nginx conf create this:

```
server {
    server_name mysite.com;
    listen 8201 ssl; # managed by Certbot
    location / {
        proxy_pass         http://127.0.0.1:8200/;
        proxy_redirect     off;

        proxy_set_header   Host                 $host;
        proxy_set_header   X-Real-IP            $remote_addr;
        proxy_set_header   X-Forwarded-For      $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto    $scheme;
    }
    ssl_certificate /etc/letsencrypt/live/mysite.com/fullchain.pem; # managed by Certbot
    ssl_certificate_key /etc/letsencrypt/live/mysite.com/privkey.pem; # managed by Certbot
    include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot
}
```

This exposes the vault ui into the public IP 8201 (go sure the port is opened in your EC2 server) and secures it via SSL

## Set up Vault

If your vault server is still running then ctrl-c it, then enable the service with linux:

- `sudo systemctl enable vault.service` <-- vault is started at boot time
- `sudo systemctl start vault.service` <-- starts vault using `/etc/vault.d/vault.hcl`
- important to note: your vault is still sealed. This will **always be the case when you start vault/restart your server** - in order to unseal it you need to have one ore more unseal keys
- go to mysite.com:8201
- choose how many unseal keys you want to generate and how many are needed in minimum to unseal the vault. As I have only a one-man-project I chose 1 and 1 but you might to go for higher security standards
- store both the unseal key(s) and the root token into a secure place (e.g. 1password)
- unseal the vault with the unseal key you just generated. Now the vault is "ready to be used"
- enable the first "secrets store" under secrets -> enable new engine -> KV
- leave path as kv and everything else as well, click "enable engine"

## Set up programmatic access for python

In theory you could use your root token to read secrets with python, but of course that's not what you want, instead you create separate users/policies for your apps. Don't worry it's actually quite simple.

- go to policies -> create ACL policy -> name it after your application, I chose `flask`
- into the policy field put this:

```
path "kv/*" { capabilities = ["read"] }
```

That makes that your python client can only *read* secrets, never write them. It can read *all* secrets in the kv store you just created. You could use namespaces e.g. `kv/flask/…` and then restrict the policy to only this if you want.

- enable approle: Access -> enable new method -> AppRole
- leave the Path at `approle`, click Enable Method
- ssh into your server or open a new shell, then run the following commands:

```
export VAULT_ADDR='http://127.0.0.1:8200'
export VAULT_TOKEN="hvs.1324ASDF1324ASDF1324Aasd"
