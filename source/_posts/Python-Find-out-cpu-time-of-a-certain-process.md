---
title: "Python: Find out cpu time of a certain process"
tags:
  - python
date: 2007-06-08 06:52:00 
alias: /post/37471156554/python-find-out-cpu-time-of-a-certain-process
---

<p>
  To find out how many percentage a certain process uses the cpu:
</p>
<!-- more -->
<pre>
  import os, time

  # find out the pid by username.
  # "-o pid h" omits the header and just prints the pid
  pid = os.popen('ps -U my_user_name -o pid h').read().strip()

  # 14th column is utime, 15th column is stime:
  # The time the process has been scheduled in user/kernel mode
  # The time value is in jiffies. One jiffie is appox 1/100 second
  # see man proc for more info
  stat = os.popen('cat /proc/%s/stat' % pid).read().strip()
  cpu_time1=int(stat.split()[14]) + int(stat.split()[15])
  time1=time.time()

  time.sleep(1)
  stat = os.popen('cat /proc/%s/stat' % pid).read().strip()
  cpu_time2=int(stat.split()[14]) + int(stat.split()[15])
  time2=time.time()

  print str(float(cpu_time2 - cpu_time1) / (time2 - time1)) + "%"
</pre>
<p>
  I don't know though if the number is accurate.<br>
  What is "cpu time" anyway? It's the time the process is running (using the cpu for 100%) divided by the time the process is laid asleep by the scheduler.<br>
  Then, <a href="http://www.ecos.sourceware.org/ml/systemtap/2005-q4/msg00185.html">jiffies seem to be not a safe number</a> for time measurements.<br>
  But for relative measurements it should do the trick.
</p>