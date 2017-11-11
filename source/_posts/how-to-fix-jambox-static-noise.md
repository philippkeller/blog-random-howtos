---
title: How to fix Jambox’ “static noise and no bluetooth sound” problem(includes soldering)
tags:
  - jambox
date: 2012-07-21 15:07:00
alias: /post/37471161448/how-to-fix-jambox-static-noise-and-no-bluetooth
---

<img alt="fixed!" src="http://i.imgur.com/ofR49.png" style="float: right;"></div>

Jambox is a pretty cool device: The sound quality is very good, it is small, it has a battery. I liked it. Until it broke. It just didn't play music over bluetooth any more but instead uttered static noise. This seems to be a quite severe production problem as <a href="http://forums.jawbone.com/t5/JAMBOX-Troubleshooting/Static-and-dropping-bluetooth-My-customer-service-call/m-p/37461">many</a> <a href="http://forums.jawbone.com/t5/JAMBOX-Troubleshooting/jambox-static-and-airplay/td-p/6676">many</a> <a href="http://www.amazon.com/review/R3GYH7DT8H8EKR/ref=cm_cr_pr_cmt?ie=UTF8&amp;ASIN=B004E10KGU">many</a> people have devices with the exact same problem. So going down the "Jambox please replace my device" way didn't sound promising to me. The possibility that the replacement device is broken as well is just too high.

The problem lies in the aux in port. The device thinks there's an aux cable plugged in and outputs the signal from the aux input when in fact it should play the bluetooth sound.

<!-- more -->

In my <a href="http://howto.pui.ch/post/37471160886/how-to-reset-jambox-when-bluetooth-completely-stopped">last post</a> I described the different easy-to-do solutions to this problem, but today I needed to implement the soldering solution because nothing else worked. Implementing this solution means tricking the Jambox to think there's no aux cable plugged in.

<strong>Update</strong>: My initial soldering was working, but after the first recharge the fix stopped working. Might be that the soldering melted and if you are a solder pro this might work for you. Anyway. I personally ended up putting a <a href="http://howto.pui.ch/post/37471160886/how-to-reset-jambox-when-bluetooth-completely-stopped">screw into the aux port</a>

## What do you need?

- a star shaped screw driver (aka torx)
- Soldering equipment
- being ok that the aux cable will never work again
- desparation to get this machine working again (I'm not sure how safe this is, being not used to that kind of stuff)
- and of course it will void your warranty

I personally hate soldering, I'm not good at it, but still I managed to get my Jambox working agagin so I thought I'd share with the world:

### How to disassemble

There's <a href="http://www.youtube.com/watch?v=X5APtwqtEps">a good video describing how it should be done</a> (I did it just with the screwdriver. No gloves and no other equipment.)<br>
  You need to follow the video until 5:00

### What to solder?

<img class="caption" alt="the two contacts you need to bridge" src="http://i.imgur.com/cAWlo.jpg" />

<strong>Update</strong>: David Choi <a href="http://www.youtube.com/watch?v=nd5nF2hSFHw&amp;feature=youtu.be">has made a video</a> that shows very well which two contacts to solder. He claims that with good soldering skills you can achieve that both bluetooth and aux will still work.

It's pretty simple: Follow the aux port and where the end of the aux jack would be there are 2 metal contacts which need to be soldered together. Turn on the jambox and try to push the upper metal contact so the two metal pieces touch and you'll hear the bluetooth sound. Hearing the music should give you enough motivation now to go on. Now:

- Turn off the Jambox
- Try to solder (it is tricky because the spot is hard to reach)
- Try if it has worked. If it worked, wait some time. Shake the bluetooth device to really go sure the soldering joint is good (first time I was so happy that it worked, I assembled the device again and then it didn't work because the soldering joint was flaky)

### How to assemble

<img class="caption" src="http://i.imgur.com/8YeqZ.jpg" alt="I needed to bend the two metal pieces at the end of the grid to be able to assemble it" />

Again <a href="http://www.youtube.com/watch?v=X5APtwqtEps&amp;t=10m40s">follow the video starting from 10:40</a>

I found the assembling the hardest part. In the end I needed to bend the small metal pieces of the grid to be able to put it back together (although I didn't follow the video so you might be more successful).

### Happy listening

My Jambox is now up and running again since 24h. I'm very very happy that this little thing did the trick.