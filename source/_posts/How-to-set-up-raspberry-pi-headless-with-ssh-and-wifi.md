---
title: How to set up raspberry pi headless with ssh and wifi
date: 2018-01-20 09:32:44
tags:
---

![raspberry pi 3](/images/pi.jpg)

Setting up raspberry pi is a bit tedious when doing it over attached monitor, keyboard and mouse (I usually don't have those around anyway, being laptop only at the moment), so here's a good and easy way to get an installation directly from your laptop, making the pi automatically join your wifi and enable ssh:

# Flash

![etcher](/images/etcher.png)

I found that etcher.io is a very easy way to flash, in order to do so:

- **Install [etcher](https://etcher.io/)** (available for linux/osx/windows)
- **Download image:** I chose the raspbian lite version from [official](https://www.raspberrypi.org/downloads/raspbian/)
- **Open etcher** etcher (on linux just unzip the etcher.zip and open the executable therein)
- **Insert sd card** (don't mount it yet!), watch that etcher now detects that new card in the middle
- **Select image** e.g. `~/Downloads/2017-11-29-raspbian-stretch-lite.zip` and **flash** <small>(for linux i3 users: you'll get a polkit error. You'll need to start a polkit agent, e.g. `/usr/lib/policykit-1-gnome/polkit-gnome-authentication-agent-1` before flashing)</small>

<!-- more -->

# Enable ssh and wlan on the image

Etcher just created two partitions: a boot partition and a data partition. First, find out the device files of the two partitions using `sudo fdisk -l`. In my case I found:

```
Disk /dev/mmcblk0: 14.9 GiB, 15931539456 bytes, 31116288 sectors
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes
Disklabel type: dos
Disk identifier: 0x37665771
Device         Boot Start     End Sectors  Size Id Type
/dev/mmcblk0p1       8192   93236   85045 41.5M  c W95 FAT32 (LBA)
/dev/mmcblk0p2      94208 3629055 3534848  1.7G 83 Linux
```

The relevant lines are 8 (boot partition) and 9 (data partition).

## Enable ssh

- create the mount point e.g. `mkdir /var/tmp/sdcard`
- mount the boot partition with `sudo mount -t vfat /dev/mmcblk0p1 /var/tmp/sdcard` whereas you specify the file system using `-t vfar` (corresponds to W95 FAT32) and the device `/dev/mmcblk0p1` is what you take from above (be sure to take the first one, that with the lower start number)
- `sudo touch /var/tmp/sdcard/ssh` to enable ssh on the first boot
- `sudo umount /var/tmp/sdcard`

## Enable wireless

- mount the data partition with `sudo mount -t ext4 /dev/mmcblk0p2 /var/tmp/sdcard`, be sure to take the correct `/dev/`, `-t ext4` corresponds to the `Linux` fs type
- run `wpa_passphrase <ssid> <password>` to create the wireless config config
- edit `/var/tmp/sdcard/etc/wpa_supplicant/wpa_supplicant.conf` and add the config you just got from `wpa_passphrase`. Be sure to delete the plain text psk line
- `sudo umount /var/tmp/sdcard`

# Profit!

That's it, boot your pi, check your router for the ip address it just got and ssh in with `ssh pi@192.168.x.x` using `raspberry` as password.

A good first step is to start `sudo raspi-config` in order to:

- change password
- generate the locale (get rid of the `warning: setlocale: LC_ALL: cannot change locale (en_US.UTF-8)`)
- set the correct timezone

And, of course add your public key to authorized_keys:

```
cat ~/.ssh/id_rsa.pub | ssh pi@192.168.x.x "mkdir -p ~/.ssh && chmod 700 ~/.ssh && cat >>  ~/.ssh/authorized_keys"
```