---
title: How to reset Jambox when bluetooth completely stopped working
tags:
  - gadgets
date: 2012-07-14 19:26:00
alias: /post/37471160886/how-to-reset-jambox-when-bluetooth-completely
---

  I bought a Jambox about half a year ago. Sound wise it is great, but apparently it is not very stable, especially after recharging it falls into some state where it only utters static noise. In this state it still plays music over the aux cable, but not any more over bluetooth.<!-- more -->

Apparently the issue is the aux port which has two contacts that should touch each other when there is no aux cable inserted. But, because of manufacture problems these two contacts don't touch on some device, even though there is no aux cable inserted. So: The jambox thinks there is an aux cable, but there is none. That's why it utters static noise

  So, because I have a device with such problems I needed to hard reset my jambox half a dozen. That's why I thought I finally write it down.

*   **Soft reset**: Holding down the circle button (talk button) and plugging it into the charger and then releasing. You will see the red flash
*   Unpair / Pair again; being deleting it from every device, restarting all of them and pairing once more
*   **Hard reset**: Turn off bluetooth on all devices in reach, then turn on the jambox and press the circle button six times, when you see the light flash red, press the circle once more and hold it and it will go into pairing mode
*   Update the software to &gt;=2.1 using [mytalk.jawbone.com](http://mytalk.jawbone.com)
*   Insert an **aux cable** and removing it again (worked a few times for me)
*   Insert a small **screw driver** (this is scary, more detailed instructions [here](http://forums.jawbone.com/t5/JAMBOX-Troubleshooting/jambox-static-and-airplay/m-p/14882/highlight/true#M748)). This connects the two metal contacts which should touch each other to make the Jambox believe there is no AUX cable inserted
*   If the screw driver thing is working for you, you might consider putting a screw into the aux port: [![](http://i.imgur.com/udCI5.jpg)](http://i.imgur.com/udCI5.jpg)
*   If nothing of the above works, you can [solder a bypass of the aux port](http://howto.philippkeller.com/2012/07/21/how-to-fix-jambox-static-noise/) (which is what I finally did)

  I don't recommend buying a Jambox to anyone, I completely agree with [this review on Amazon](http://www.amazon.com/review/R3GYH7DT8H8EKR/ref=cm_cr_pr_cmt?ie=UTF8&amp;ASIN=B004E10KGU)