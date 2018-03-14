---
title: How to extract text from pdf in python
date: 2018-03-13 21:04:48
tags:
---

![xpdf](/images/xpdf.jpg)

I'm trying to get text extraction from pdfs working on lambda for a little fun project of mine.

Now, there are [a lot of possibilities how to extract text from pdfs using python](https://stackoverflow.com/questions/34837707/extracting-text-from-a-pdf-file-using-python) but nothing really worked for me:

- pypdf2 just returned newlines for my test pdfs
- tika (which calls apache tika) was too slow (needs to start a java server first on localhost)

Finally I ended up using xpdfs pdftotext. Sadly I couldn't install xpdf on AWS EC2 (Amazon Linux), so I needed to compile it, but turned out it is quite straigtforward:

<!-- more -->

```
sudo yum install -y cmake freetype-devel clang
cmake -DCMAKE_BUILD_TYPE=Release
make
```

There will be warnings about qt missing, but this is not relevant as we're only interested in the xpdf tools.

Make produces `xpdf/pdftotext` which has only one shared lib dependency (`/usr/lib64/libstdc++.so.6`) you'd need to fix in order to make it work on AWS lambda:

Copy `pdftotext` into your lambda root and `/usr/lib64/libstdc++.so.6` into `lib/libstdc++.so.6` and then you can call pdftotext like this:

```python
	import os, subprocess
	SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
	LIB_DIR = os.path.join(SCRIPT_DIR, 'lib')

    args = ["{}/pdftotext".format(SCRIPT_DIR), 
            '-enc',
            'UTF-8',
            "my.pdf",
            '-']
    env = os.environ.copy()
    env.update(dict(LD_LIBRARY_PATH=LIB_DIR))
    res = subprocess.run(args, 
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env)
    if res.returncode > 0:
        print("pdftotext exited with {}:\n{}".format(res.returncode, res.stderr))
        raise Exception
	output = res.stdout.decode('utf-8')
```

In my case I was only interested in non-whitespace characters so I added `words = re.sub("\W+", " ", output)`