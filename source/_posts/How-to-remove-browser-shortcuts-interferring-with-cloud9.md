---
title: How to remove browser shortcuts interferring with cloud9
date: 2018-03-11 16:31:19
tags:
---

![cloud9](/images/cloud9.png)

I just started playing around with cloud9, particularly because it looks like the ideal IDE to develop lambda functions.

One thing which bothered me from the start: Emacs keybindings such as `ctrl-n` for next line won't work because this makes the browser (in my case firefox) open a new window. Similarly, `ctrl-tab` would cycle through the browser tabs instead of cycling through cloud9 tabs. I'd like to have *all* shortcuts available for cloud9, so ideally cloud9 would run in some minimalistic browser window.

Because Firefox and also Chrome don't support *removing* shortcuts I found [this nice solution](https://stackoverflow.com/a/25995884/119861):

<!-- more -->

First, install nw.js (requires node.js)

```
sudo npm install nw -g
```

then install package.json into e.g. ~/bin/:

```
mkdir ~/bin/cloud9
wget http://howto.philippkeller.com/images/cloud9.png
vim ~/bin/cloud9/package.json
```

and put this into package.json:

```json
{
    "name": "cloud9 launcher",
    "window": {
        "fullscreen": true,
        "toolbar": false,
        "icon": "cloud9.png"
    },
    "main": "https://console.aws.amazon.com/cloud9/home"
}
```

You can directly launch that with `nw ~/bin/cloud9/`. To also have a desktop entry for Ubuntu, put this into `~/.local/share/applications/Cloud9.desktop` (replace `philipp` with your user..)

```txt
[Desktop Entry]
Type=Application
Name=Cloud9
Exec=nw /home/philipp/bin/cloud9
Icon=/home/philipp/bin/cloud9/cloud9.png
Categories=Development;IDE
Comment=Start Cloud9 in kiosk mode
Terminal=false
```