---
title: "Set timeout for a shell command in python"
tags:
  - python
date: 2007-02-18 18:04:00
alias: /post/37471155682/set-timeout-for-a-shell-command-in-python
---

I wanted to run a shell command in python without knowing if the shell command is going to exit within reasonable time (<a href="http://adplug.sourceforge.net/">adplay</a> that was, sometimes it simply hangs).<br><br><strong>Update:</strong> <a href="http://www.python.net/crew/hooft/">the "task" module of Rob Hooft</a> seems to solve this exact problem. At the time I wrote this, the python.net website was down. I leave my solution here just for archive purpose.<br><br>

<!-- more -->

```
  def timeout_command(command, timeout):
    """call shell-command and either return its output or kill it
    if it doesn't normally exit within timeout seconds and return None"""
    import subprocess, datetime, os, time, signal
    start = datetime.datetime.now()
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    while process.poll() is None:
      time.sleep(0.1)
      now = datetime.datetime.now()
      if (now - start).seconds&gt; timeout:
        os.kill(process.pid, signal.SIGKILL)
        os.waitpid(-1, os.WNOHANG)
        return None
    return process.stdout.read()
```

Note especially lines 6, 11 and 12.<br>Usage:


```
>>> output = timeout_command(["sleep", "10"], 2)
None
>>> output = timeout_command(["sleep", "1"], 2)
```

The process can be killed when it has run for too long (the <code>os.waitpid</code> waits for the kill to end and avoids defunct-processes) and furthermore the Popen'ed process' printed is caught and returned if it doesn't timeout. However, <code>subprocess.Popen</code> is called with a list as argument. That means, that the command isn't passed to a shell and furthermore you can just call one command with options, nothing more.