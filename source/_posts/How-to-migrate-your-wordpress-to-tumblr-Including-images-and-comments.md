---
title: How to migrate your wordpress to tumblr. Including images and comments.
tags:
  - wordpress-to-tumblr
  - wordpress
  - tumblr
  - migration
date: 2012-12-14 11:37:00
alias: /post/37850192094/how-to-migrate-your-wordpress-to-tumblr-including
---

![](https://lh3.googleusercontent.com/-Pn-aBqMjq9g/UMpMLdyLsgI/AAAAAAAALe0/zbopqqnD77M/s300/wordpresstumblr.jpg)So I've decided to move my wordpress blogs to tumblr. Although apparently TechCrunch [thinks that's a bad idea](http://techcrunch.com/2010/09/18/stuff-white-person-doesnt-like/). And although [Moritz Adler](https://twitter.com/moritzadler) would kill me for that. (Although: He doesn't have a personal blog and hence has no licence to kill me). Anyway. With tumblr I don't need to host a blog software myself. And I don't end up having my blog hacked and then seeing my blog being displayed as a malware site in Chrome/Firefox (happened to me twice). And then with tumblr I create new blogs with subdomains within minutes. Cool stuff. Hail to the cloud, baby!

So here you go: A complete guide how to fully migrate your wordpress blog to tumblr. Including comments and pictures. And still supporting your old url scheme.

**Update:** I ran into a tool that claims to do a lot for you: [import2.com/tumblr](http://www.import2.com/tumblr). It doesn't migrate images and 302 redirects. Not sure about comments migration. And it costs 24$. Still, if you can leave out some of the steps below that'd be worth the money. [Comments of the author on quora](http://www.quora.com/Mark-Kofman/answers/Tumblr)

<!-- more -->

## Before you start

Before you start to actually move your blog, you need to consider a few things:

### Where do you move your **DNS** to?

If you have a wordpress webhost, then this webhost most probably also does DNS for you. You need to replace that by a third party solution. I think these are good services:

*   [he.net](https://dns.he.net/). Free service. No strings attached. The one I've chosen. The interface is nice and very easy to add new CNAMES, MX records, etc. The uptime was [reported to be not so good](http://www.lowendtalk.com/discussion/262/which-dns-site-to-use-for-domains#Comment_3800), but I don't really care about uptime of my blogs. To host your tumblr blog on your domain, you add a `CNAME` to `domains.tumblr.com` and then configure your tumblr blog to listen to that domain. Very simple.
*   [Amazon Route 53](http://aws.amazon.com/route53/): They charge you $0.50 per hosted zone per month. That's a fair price and probably has a better uptime then he.net

### What do you want to do with your **images**?

At default they're all located under `[www.yourolddomain.com/wp-content/img1.jpg](http://www.yourolddomain.com/wp-content/img1.jpg)`. To completely get rid of your old web host you need to move those to a different image hoster. I don't advice you to upload it to tumblr because if in future you want to move away from tumblr you run into the same problem again.

### Would you like to keep your **comments**?

Do you have comments at all? Tumblr doesn't support comments by itself. Most themes have disqus support. Moving comments to disqus is no big deal, but still it's some work, so you may decide to just not migrate comments.

### Are you keen to not break your **old blog urls**?

Wordpress' url scheme generally is e.g. `code.pui.ch/2007/01/05/print-hello-world/`.
That same post ends up at this tumblr url: `howto.pui.ch/post/37471154429/print-hello-world`. Note that the last part of the url is optional, i.e. `howto.pui.ch/post/37471154429` works as well.
If you care about incoming links to your blog not to break and if you care about your google ranking (I guess 302 redirects inherit the google ranking), there are two possibilities:

1.  Stay on the same domain, handle the redirects in tumblr (tumblr supports that with the pages' type "redirect")
2.  Move to a different domain and put up e.g. `redirect permanent` in a .htaccess file on your web server

## A rough outline of what you're up to

At a glance, that what you'll do:

1.  Upload your images to a different hoster (if you want to get rid of your old webhost)
2.  Extract all blog posts+comment from wordpress
3.  Fix the export.xml: Replace images, more-tags and fix some additional stuff
4.  Migrate your wordpress blog to blogger
5.  Migrate your blogger blog to tumblr
6.  Install http redirects (on old webhost or on tumblr)
7.  Migrate your comments to disqus
8.  Clean up blog posts (might be a biggie if you're a perfectionist)

Alright, let's specify those 8 steps.

## Step 1: Upload your images to a different hoster

If you're ok with keeping your old webhost you can skip this point. Easiest thing to do would be to copy your wp-content directory one to one to a different hoster so `[www.yourolddomain.com/wp-content/img1.jpg](http://www.yourolddomain.com/wp-content/img1.jpg)` turns into `[www.imagehoster.com/my_user_name/img1.jpg](http://www.imagehoster.com/my_user_name/img1.jpg)`.

I don't have experience with image hosting providers so I just uploaded my images to picasa, but that meant I needed to update every single image in all my blog posts to the new image url of picasa. That was quite a pain. I couldn't find a image hoster yet who meets the criterias above. Photobucket doesn't, Dropbox doesn't, Google Drive doesn't. Maybe Amazon S3

## Step 2: Extract your blog posts+comment from wordpress

1.  In your wordpress admin go to Tools → Export. On my blog that was `code.pui.ch/wp-admin/export.php`.
2.  Choose `All content`, `Download Export File`.

## Step 3: Fix the export.xml

You have just downloaded an xml file, in my case the name was `coderandom.wordpress.2012-12-13.xml`. Open that file with your favourite text editor. Now you need to do a few things before you can go on:

1.  Replace all &lt;!&ndash;more&ndash;&gt; by <span>[[</span>MORE<span>]]</span>. The uppercase actually matters. <span>[[</span>MORE<span>]]</span> is the divider that tumblr actually understands as the place where you want your excerpt to stop in the blog overview view.
2.  Replace all images by the new urls you got by uploading the images to the image hoster in step 1\. It's much easier to do this at this stage than to replace the images once you've migrated your blog to tumblr.
3.  You may have more wordpress plugins you used in your posts. I used `[python]...[/python]` to syntax highlight my python markup. I've moved to [google code prettify](http://code.google.com/p/google-code-prettify/) which needs `&lt;pre class="prettyprint"&gt;...&lt;/pre&gt;` as a syntax. So I needed to replace all occurrences by the new markup. Obviously, regex is your friend at this stage.

## Step 4: Migrate your wordpress blog to blogger

Unfortunately there's no direct way to directly import this xml file into tumblr. Instead, that's what you need to do:

1.  **Convert** your xml file [on this website](http://wordpress2blogger.appspot.com/) to a file fit for importing into blogger.

      This doesn't work for files bigger than 1MB. If that's the case then you can either convert the file on your own machine using [this sourcecode on google code](http://code.google.com/p/google-blog-converters-appengine/). Or you can follow the [instructions under step 3 on this blog post.](http://julioinprogress.com/2011/09/10/guide-to-moving-from-wordpress-to-tumblr/)
2.  **Create a new blog** on [blogger.com](http://www.blogger.com).
3.  In blogger navigate to your new blog and do settings → other settings → **import blog**
4.  **Publish** all blog posts: Posts → All → Select all → Publish

If you have difficulties in this step you might try a different solution (didn't try any of these):

*   [ideashowers PHP script on github](https://github.com/ideashower/Export-Wordpress-posts-to-Tumblr)
*   [Dave Lartigues php script (plus explanations)](http://www.daveexmachina.com/wordpress/?p=5974)
*   [Darshan Bavarians PHP script](http://dbavaria.tumblr.com/post/28193913/wp2tumblr-transfer-your-blog-from-wordpress-to-tumblr)
*   [shakefons php script](http://snipplr.com/view/14609/migrate-wordpress-to-tumblr/)

## Step 5: Migrate your blogger blog to tumblr

1.  Go to [bloggertotumblr.com](http://www.bloggertotumblr.com/) and enter your url for your newly created blogger and tumblr blogs. The conversion is very straight forward.
2.  Delete your blogger blog
3.  Enjoy. Your blog posts are now on tumblr. Still missing: Support of the old url scheme and comments

## Step 6: Install http redirects (on old webhost or on tumblr)

In the section [before you start](#beforeyoustart) I asked you to decide if you're ok to break your old urls. If you don't care, then skip this step. Although: if you care about keeping your comments then you still might to do this step, as it makes migrating comments to disqus a lot easier

If you do care, then:

*   If you keep the domain of your blog: You need to install tumblr redirect pages. See below.
*   If you changed the domain of your blog: You need to install redirects on your former wordpress webhost. I describe how this is done via .htaccess config below

### Install tumblr redirect pages

1.  go to your new tumblr blog
2.  click customize top right
3.  add a page (left column)
4.  instead of "Standard Layout" choose "Redirect" and add a posts' old url on top, and the new url on bottom. Repeat this for every blog posts (yeah, lots of work here)

### Install .htaccess on your old webhost

IMO that's a bit simpler than installing a tumblr redirect for every blog post. Still it's a lot of work since you need to come up with a map of old_url → new_url for every blog post. If your webhost supports .htaccess then go for this method. Most probably you have such a file already for your wordpress installation.

An example of a .htaccess file:

```apache
RewriteEngine On
Redirect permanent /page/2/ [http://howto.pui.ch/page/2](http://howto.pui.ch/page/2)
Redirect permanent /feed/ [http://howto.pui.ch/rss](http://howto.pui.ch/rss)
RewriteRule ^$ [http://howto.pui.ch/](http://howto.pui.ch/) [R=301,L]
Redirect permanent /2007/02/25/add-bandwidth-to-a-file-download-in-python/ [http://howto.pui.ch/post/37471156141/add-bandwidth-to-a-file-download-in-python](http://howto.pui.ch/post/37471156141/add-bandwidth-to-a-file-download-in-python)
Redirect permanent /2007/06/08/python-find-out-cpu-time-of-a-certain-process/ [http://howto.pui.ch/post/37471156554/python-find-out-cpu-time-of-a-certain-process](http://howto.pui.ch/post/37471156554/python-find-out-cpu-time-of-a-certain-process)
Redirect permanent /2007/07/23/python-sort-a-list-of-dicts-by-dict-key/ [http://howto.pui.ch/post/37471157116/python-sort-a-list-of-dicts-by-dict-key](http://howto.pui.ch/post/37471157116/python-sort-a-list-of-dicts-by-dict-key)
Redirect permanent /2009/12/30/dealing-with-mysql-backend-does-not-support-timezone-aware-datetimes/ [http://howto.pui.ch/post/37471158729/dealing-with-mysql-backend-does-not-support](http://howto.pui.ch/post/37471158729/dealing-with-mysql-backend-does-not-support)
Redirect permanent /2011/01/19/python-easy-way-to-show-progress/ [http://howto.pui.ch/post/37471159741/python-easy-way-to-show-progress](http://howto.pui.ch/post/37471159741/python-easy-way-to-show-progress)
Redirect permanent /2012/07/17/how-to-detect-a-files-character-encoding/ [http://howto.pui.ch/post/37471161169/how-to-detect-a-files-character-encoding](http://howto.pui.ch/post/37471161169/how-to-detect-a-files-character-encoding)
Redirect permanent /2010/04/04/python-display-refreshing-status-like-top/ [http://howto.pui.ch/post/37471159398/python-display-refreshing-status-like-top](http://howto.pui.ch/post/37471159398/python-display-refreshing-status-like-top)
Redirect permanent /2011/11/03/how-to-switch-gnu-screen-windows-in-iterm2-via-keyboard-shortcuts/ [http://howto.pui.ch/404](http://howto.pui.ch/404)
Redirect permanent /2007/01/19/sched-20-pizza-is-ready/ [http://howto.pui.ch/post/37471155110/sched-20-pizza-is-ready](http://howto.pui.ch/post/37471155110/sched-20-pizza-is-ready)
```

Note the first 3 lines, you will need the same for your redirects. Note the special syntax of line 3\. That is important to not redirect a non existing url to the new domain.

#### Wait! I just moved my blog away from my old webhost, and now I need to keep it to have http redirects in place?

Uh, yes. Alternatively, you can move to a free hoster like google apps engine and e.g. [use this](http://blog.dantup.com/2010/01/generic-redirection-script-for-google-app-engine) to redirect. Or you just wait a few months and wait until all search engines have digested your redirects and kill your old webhost only then (that's what I'm probably gonna do).

## Step 7: Migrate your comments to disqus

Because tumblr doesn't offer comments by itself you need to migrate your comments to disqus:

1.  [Register](http://disqus.com/admin/register/) your new tumblr blog url at disqus
2.  On disqus go to `Admin` → `Tools` → `Import/Export` → `Upload WXR`. Choose the XML file you downloaded from your wordpress installation (not that got converted for blogger). Upload that
3.  On the same page go to `Migrate Threads`. Choose "Redirect crawler" if you installed the redirects in step 6\. Otherwise you need to use the "Upload a URL map" option

Voilà! After a few minutes your comments should appear in your new tumblr blog.

## Step 8: Clean up your tumblr posts

Might be that the html markup of my wordpress posts were so bad, but I needed to fix a lot of spacing between paragraphs. I also had some CSS tweaks to right align the images which I needed to fix.

Lastly, blogger adds these paragraphs to the end of every blog post:

```html
<div class="blogger-post-footer">
  <img alt="" height="1" src="https://blogger.googleusercontent.com/tracker/290349385069691835-5946149615494229188?l=coderandomm.blogspot.com" width="1">
</div>
```

If you are a perfectionist you may want to remove this markup from every blog post.

A word of caution: You can spend a lot of time at this step if you overdo it.

## Thanks

- Thanks to **MG Siegler** (one of my favourite bloggers, although he is an Apple fanboy and I am a google disciple): He showed me that you can [perfectly write long blog posts on tumblr](http://parislemon.com/post/15604811641/why-i-hate-android) (that linked article is actually a must read about Android vs. iPhone)
- **Julio Angel Ortiz**, who's [article](http://julioinprogress.com/2011/09/10/guide-to-moving-from-wordpress-to-tumblr/) served as the base for this howto.
- **TextMate** for making html editing so easy. Just found out that it's actually a pretty decent HTML editor. I'll write my blog posts in here and only then past them into the tiny tumblr HTML editor popup.