---
title: 'Scan with raspberry pi, convert with aws lambda to searchable PDF'
date: 2018-01-28 21:16:13
tags:
css:
  - "pre>code.hljs.shell {font-size: 70%}"
  - "pre>code.hljs.json {font-size: 80%}"
---

![from scanner to pi3 to s3 to lambda to s3](/images/scan_flow.png)

I have long dreamed for a setup which lets me just press the scan button on my scanner and --- without any further input --- uploads it as a searchable PDF onto some cloud drive. Thanks to the good support of scanners by SANE and the ease of use of AWS lambda it's actually *quite* easy (judging to the length of this post it looks like quite a task, but in the end it is straightforwards and is --- surprisingly --- quite free of hacks).

In this solution you:

- set up **SANE** on your raspberry pi 3 so it scans your document
- set up **scanbd** to detect the scan button
- set up a S3 bucket for uploading
- set up a **lambda** function which uses **tesseract** to create a searchable PDF

What you need:

- Raspberry Pi 3 (I guess the other models serve equally well)
- Paper scanner with a "scan" button which is [supported by saned](http://www.sane-project.org/sane-mfgs.html)
- an AWS account

Personally I'm using Raspbian Stretch Lite as OS on my Raspberry and a Fujitsu S1300i.

Before you start: you might just want to wipe your pi and start fresh. Takes you about 15 minutes extra, you can [follow my howto](http://localhost:4000/2018/01/20/How-to-set-up-raspberry-pi-headless-with-ssh-and-wifi/) so you can do that headless (without attaching monitor/keyboard to the pi).

<!-- more -->

## Set up SANE

<img src="/images/sane.png" alt="Sane: Scanner Access Now Easy" class="caption" />

First I tried to compile SANE from source, believing that this is the only way to get my scanner to work. After hours of trying and simplifying this howto (And after I wiped the pi3 two times to start over!) I figured out that `apt install` works just fine! So bear in mind that this howto was done with sweat and after hours of painful try-and-error :)


Just install:

```bash
sudo apt install sane-utils -y
```

No need to install the whole `sane` package which comes with 162 packages needing 430MB of space (sic!). `sane-utils` is enough. Now, when you plug your scanner to your pi and do..

```bash
sudo sane-find-scanner -q
```

.. you should see something like this:

```shell
found USB scanner (vendor=0x04c6 [FUJITSU], product=0x128d [ScanSnap S1300i]) at libusb:001:011
found USB scanner (vendor=0x0424, product=0xec00) at libusb:001:003
```

That is, your scanner is already detected by sane. Now, throughout this howto, I'll use user `pi` to run the processes. You can choose to go for another user, but please don't use `root` for it. 

To give your user `pi` the permission to scan you'd do:

```bash
sudo usermod -a -G scanner pi
```

This works because the group `scanner` is configured in `/etc/udev/rules.d/*.conf` to access the scanner. If this step does not work then [this section](https://wiki.archlinux.org/index.php/SANE#Permission_problem) might help you to troubleshoot.


You still cannot scan though, because you need to install the firmware file for your scanner. First, find out where the firmware needs to sit: Grep for your model (in my case scansnap 1300i):

```bash
grep 1300i /etc/sane.d/*.conf
```

Shows you something like:

```shell
/etc/sane.d/epjitsu.conf:# Fujitsu S1300i
/etc/sane.d/epjitsu.conf:firmware /usr/share/sane/epjitsu/1300i_0D12.nal
```

So all you'd need to do is get this `1300i_0D12.nal` file. Get it from installation files (i.e. that old CD rom), or just google for your firmware file and hope that there's no security concerns.. In my case I found it on github and installed it with:

```
sudo mkdir /usr/share/sane/epjitsu/
sudo wget https://github.com/ckunte/sfware/raw/master/1300i_0D12.nal -O /usr/share/sane/epjitsu/1300i_0D12.nal
```

Now you should be able to insert a document into the scanner and ..

```
scanimage >/tmp/out.pnm
```

.. should produce a nice [PNM file](https://en.wikipedia.org/wiki/Image_file_formats#PPM,_PGM,_PBM,_and_PNM) ready to be further processed.

## Set up scanbd

![](/images/button.jpg)

Scanbd is [very badly documented](https://sourceforge.net/projects/scanbd/reviews/#reviews-n-ratings). It's sad, because once you get it working, it's doing its job very well. Plus: there's really no alternative to scanbd.

Scanbd is just a daemon which regularly polls the scanner to see if a button was pressed. If it was, it just starts a shell script which itself then uses sane to scan. I found [this stackoverflow answer](https://superuser.com/a/1044684/33963) a good explanation how scanbd works.

There are a few howtos on the web which are overly complicated (i.e. copying all files of sane to scanbd), after 2-3 fresh installs I found out a quite forward way to get it working.

Fist, install it via

```bash
sudo apt install scanbd -y
```

then, edit `/etc/scanbd/scanbd.conf` and set <small>(if your scanbd.conf is missing --- as it was missing for me on the first try --- take [this conf file as a start](/files/scanbd.conf))</small>:

- `debug-level = 7`: to see errors more easily while setting up
- `user = pi`: to run script and the scanning process as user `pi`

Start scanbd with 

```bash
sudo scanbd -f
```

and you'd see that scanbd is polling. When you hit the scan button then you should see output lines of scanbd trying to run `/etc/scanbd/scripts/test.script` which doesn't exist. So far, so good!

Now, we'll put our script into place: Edit `/etc/scanbd/scanbd.conf` and set:

- `script_dir=/etc/scanbd/scripts`
- in `action scan`:
  - `desc = "Scan to file and upload to s3"`
  - `script = "scan.sh"`

Now, we'll just put a little script in place which scans to `/tmp/foo.pnm`:

```bash
sudo mkdir /etc/scanbd/scripts/
echo -e '#!/bin/sh\nscanimage > /tmp/foo.pnm' | sudo tee /etc/scanbd/scripts/scan.sh
sudo chmod a+x /etc/scanbd/scripts/scan.sh
```

Replug your scanner and test it with:

```bash
sudo scanbd -f
```

Hitting the scanner button should scan. Buuut: if you now power off the scanner (close the lid on my model) or unplug it or whatever, and then replug it, then scanbd crashes spectacularly with a segmentation fault. There is [this reported bug](https://bugs.launchpad.net/ubuntu/+source/scanbd/+bug/1500095) which is solved with version 1.5.1, but instead of compiling from source it's easier to start it over systemd and tell it to restart the service after crash:

First, edit `/lib/systemd/system/scanbd.service` and in the `[Service]` section add the line `Restart=on-failure`.

Then, reload systemd and tell it to start the service on boot time:

```
sudo systemctl daemon-reload
sudo service scanbd start
sudo update-rc.d scanbd enable
```
Now, hitting the scanner button should work out of the box. Also try restarting the pi and replugging your scanner. You also may want to have a look at syslog, where all scanbds messages end up: `tail -f /var/log/syslog`

<small>If, for any reasons your service would just not start, then examine `/lib/systemd/system/scanbd.service` and check if ExecStart references your scanbd (use `which scanbd`) and your scanbd.conf, and also that `SANE_CONFIG_DIR` is set correctly.</small>

## Upload to S3


The idea is to offload as much computing as possible into the cloud. In theory you could also just run tesseract on your pi and then store it somewhere, but first I wanted to free up the pi as fast as possible for the next scan and second I was just searching for another excuse to try out lambda..

So in the next step we'll alter the script so it uploads to s3. But before we can do that we'll need to create a user on AWS which has just enough rights to do that.

### AWS: add bucket and user

![](/images/locked.jpg)

- **S3**: Create a bucket, e.g. `scanner-upload` (be sure to choose a region close to you. Upload speed is a lot faster for closer regions). Note the ARN of the bucket.
- **IAM**: create a policy `scanner-upload`, swith into JSON editor and paste this (replace the arn):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:ListBucket"],
      "Resource": ["arn:aws:s3:::scanner-upload"]
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject"
      ],
      "Resource": ["arn:aws:s3:::scanner-upload/*"]
    }
  ]
}
```

- **IAM**: Create a user with programmatic access only and attach the `scanner-upload` policy. Download the csv which contains the key and secret of this user

Back on Raspberry, first install and configure aws cli (use the key and secret from the downloaded csv):

```bash
sudo apt install python-pip -y
sudo pip install awscli
aws configure
```

It's important that you start `aws configure` as the user with which you run your script (i.e. user `pi`). 

Now, test that s3 access works: 

```bash
aws s3 ls s3://scanner-upload/
s3 cp some_file.txt s3://scanner-upload/
```

## Write the scanner script

Now -- finally.. -- all the things are in place to finish the scanner script.

The below script..

- scans in batch mode: creates multiple files until the feeder is empty
- does a duplex scan (there's no detection if both sides contain content. It means that if it's a one sided paper the second page is just empty)
- scan with `resolution 300`: this is the default. It is a pretty fast scan and the quality is good enough
- does a `.tar.gz` archive. I did some speed tests and in my case it was quicker to first gzip the file before uploading. But that greatly depends on your upload speed
- does the compression and uploading in the background so the scanner is ready to do the next scan

Take the script and save it in `/etc/scanbd/scripts/scan.sh`, the only thing you'd need to adapt is the s3 bucket name.

```bash
#!/bin/sh

set -e
export TMP_DIR=`mktemp -d`

echo 'scanning..'
scanimage --resolution 300 --batch="$TMP_DIR/scan_%03d.pnm" --format=pnm --mode Gray --source "ADF Duplex"

echo 'packaging and uploading in subshell'
(tarname=scan_$(date "+%Y-%m-%d_%H%M%S").tar.gz
cd $TMP_DIR
tar -czf $tarname *.pnm
echo 'uploading..'
aws s3 cp $TMP_DIR/$tarname s3://scanner-upload/
rm -rf $TMP_DIR
echo 'done') &
```

Now, pressing the button on your scanner should upload the file to s3.. whohoo!

If everything works then you can set `debug-level=3` in `/etc/scandb/scanbd.conf` so it does less verbose logging into syslog.

## Set up lambda

tbd