---
title: How to install postgres on amazon linux 2
date: 2022-05-03 17:27:10
tags:
---

This howto…

- installs postgres13
- creates a first database
- sets postgres password
- makes postgres to be reachable from outside

I assume that you…

- have an amazon linux 2 instance (ec2 or lightsail)
- opened port 5432 (I strongly recommend to open it only to a set of ip addresses)

## Install postgres

Before you can install postgres you need to "enable" it:

```
sudo amazon-linux-extras enable postgresql13
```

At the time of this blogpost version 13 was the highest one. You can try with higher versions, if you mistakenly enabled a version you can also disable it with `disable`.

To install it client+server:

```
sudo yum install postgresql postgresql-server
```

## Setup postgres

Create the initial `postgres` database:

```
sudo postgresql-setup initdb
```

Start it and tell linux to start it at boot time:

```
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

Check that postgres really started with `sudo systemctl status postgresql`

Secure the linux `postgres` user:

```
sudo passwd postgres
```

Set postgres database password:

```
su - postgres
psql -c "ALTER USER postgres WITH PASSWORD 'your-super-secret-password';"
```

## Make it reachable from outside

Because I opened port 5432 on ec2 only to a set of ip addresses I make postgres to listen to any incoming address:

Change `/var/lib/pgsql/data/postgresql.conf` and put around line 59:

```
listen_addresses = '*'
```

Likewise `/var/lib/pgsql/data/pg_hba.conf` (around line 88) add this line:

```
host  all  all 0.0.0.0/0 md5
```

Now you should be able to connect to your db from outside.