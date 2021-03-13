---
title: 'How to root Samsung A50 with TWRP, Magisk, LineageOS and Magisk'
date: 2021-03-13 10:57:33
---

I've rooted many smartphones before. Probably about 6. But I never had so much problems as with Samsung A50. To spare you the frustrations I went through, I did a little writeup.

The exact phone model I have is `SM-A505FN` but I guess it work with any A50 model.

<!-- more -->

## Download needed files

- get latest TWRP *with* Magisk patched from [here](https://forum.xda-developers.com/f/samsung-galaxy-a50-guides-news-discussion.8682/) I got version 3.5.0 from [here](https://forum.xda-developers.com/t/guide-recovery-unofficial-twrp-v3-5-0-for-samsung-galaxy-a50.4216765/). If you want root this is crucial because Samsung A50 has no ramdisk and that means you cannot flash Magisk later on, you *need* to start with a patched TWRP
- get Lineage version of your wishes. I *think* the only version existing is from AndyYan. For Samsung A50 choose the `treble_a64_bv` version:
	- [17.1](https://sourceforge.net/projects/andyyan-gsi/files/lineage-17.x/) is Android 10 based (worked for me well)
	- [18.1](https://sourceforge.net/projects/andyyan-gsi/files/lineage-18.x/) is Android 11 based (didn't get gapps to work with this version)
	- [16.0](https://sourceforge.net/projects/andyyan-gsi/files/lineage-16.x/) is Android 9. If you need Family Link to work, see [this thread](https://gitlab.com/LineageOS/issues/android/-/issues/1839) about the discussion why the setup of Family Link needs 16 (but you probably can update to 17/18 later)
- Get [google apps of your wishes](https://opengapps.org/). Personally I went for pico which didn't have google search but google app store. But depends on your use case of course. Important is that you choose the right Android version. Platform for A50 is ARM64.

## Prepare phone

- enable developer options (click many times on the build number)
- enable OEM options
- power off
- press volume up and down at same time and plug in USB -> shows a dialogue
- hold volume up long to really unlock

## How to start Samsung A50 into recovery

You need this step several times. It's important that you get it right!

- press volume down and power at the same time (this works in any case, if phone is turned on, booting, whatever. But it did **not** work for me when phone was plugged in via USB)
- when the phone vibrates immediately press volume up and power at the same time **before** any logo appears
- keep the keys pressed until the recovery screen appears

## Install TWRP, Lineage and Google Apps

- put phone into download mode (for me I needed to either do via `adb reboot-bootloader` or via recovery)
- install TWRP using ODIN (AP -> choose TWRP you downloaded, in options uncheck reboot)
- Enter TWRP Recovery Mode (see above)
- Select Wipe - Format Data - type "yes" and confirm
- Copy lineage ROM to your phone via `adb push xxx.img /`
- Install -> Install Image -> select img -> select System Image and Confirm to flash
- Copy gapps on your phone with `adb push gapps-xxx.img /`
- Select Wipe - Advanced Wipe - select "System" - Repair or Change File System - Resize File System - Confirm to Resize (this step is needed, otherwise gapps would fail on install with "not enough space")
- Select Install - select gapps.zip file and Confirm Flash

## Root phone with Magisk

Important: if you want to start the phone in rooted magisk mode, then you **must** do either:

- reboot into recovery from TWRP
- press power and volume down, wait for splash screen and then release (see [here](https://topjohnwu.github.io/Magisk/install.html#magisk-in-recovery) for details)

If you start your phone normal, then it is **not** rooted.

You don't need to flash any magisk.zip in recovery. This is needed for other phone types but as you started with patched TWRP this step is not needed.

After booting and setting up phone, you will see a magisk app, which is only a stub. Open, install the real magisk app and let it download some additional stuff.

To try if it works, install "root checker". If everything is well, then when checking root there's a magisk dialogue asking you if you want to grant root. 