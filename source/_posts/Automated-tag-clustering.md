---
title: Automated tag clustering
tags:
  - RawSugar
  - Clustering
  - Del.icio.us
date: 2006-07-11 09:03:00
alias: /post/37027750128/automated-tag-clustering
---

[Grigory Begelman](http://www.cs.technion.ac.il/%7Egbeg/) ([Technion - Israel Institute of Technology Computer Science Dpt)](http://www.cs.technion.ac.il/), [Frank Smadja](http://smadja.us/) ([RawSugar](http://www.rawsugar.com/)) and I did a paper for [www2006](http://www2006.org) called "automated tag clustering". It deals with why clustering the tag space makes sense and how this could be done.

After the presentation at the [tagging workshop](http://blog.rawsugar.com/wikka/wikka.php?wakka=HomePage) at www2006 we felt the need to give our paper a more www-friendly, I-don't-want-to-read-through-those-theoretical-equation-flooded-papers face.

[![clustering the tag space](http://i.imgur.com/40BW8.png "clustering the tag space")](http://tagging.pui.ch/automated_tag_clustering/#cluster)

So, here you go: [Automated Tag Clustering: Improving search and exploration in the tag space](http://tagging.pui.ch/automated_tag_clustering/).<!-- more -->

To read this document you should have a clue what tags are about, you should also know some tag services as [delicious](http://del.icio.us) or [flickr](http://www.flickr.com) so you can understand the limitations these services currently have. If you don't want to read through the whole papers, the numerous figures give you a good summary. Finally, to wet your appetite, here a few excerpts of the document:

> Currently tagging services still provide a relatively marginal value for information discovery and we claim that with the use of clustering techniques this can be greatly improved [from [introduction](http://tagging.pui.ch/automated_tag_clustering/#p_motivation)]
> The whole promise of collaborative tagging is that by exploring the tag space you can discover a lot of useful information you would not find with traditional search engines. When your information need is not well defined, the idea that you can explore and see what other people tagged with certain tags is very attractive. We believe that tagging will be able to reach a very wide audience only when exploration techniques will be effective. [from [limited exploration](http://tagging.pui.ch/automated_tag_clustering/#p_exploration)]
> Although a great visualization paradigm, we believe that with today's tagclouds it is hard to find more than one or two tags to click on. Tags are not grouped, there is too much information, so that you find lot of related tags scattered on the tag cloud. One or two popular topics and all their related tags tend to dominate the whole cloud. For example, looking at the del.icio.us tagcloud, one would mostly see tags related to web design and technologies. This is because these topics are overwhelmingly more frequent than anything else. [from [limited exploration](http://tagging.pui.ch/automated_tag_clustering/#p_exploration)]
> Tag _web2.0_ nowadays is so popular and is combined wildly with anything. In fact this tag is so overused that if you look at [tag _bookmarks_ in the del.icio.us dataset](http://del.icio.us/tag/bookmarks), the most used cotag is _web2.0_[&hellip;]. Basing tag similarity on these numbers often doesn't make sense at all. The similarity measure should be chosen so the popularity of a tag doesn't affect the set of a tags related tags. Don't cut the [long tail](http://en.wikipedia.org/wiki/Long_tail). The success of blogs is driven by the importance of the long tail. We all know that it is crucial to support the niches. Tagging applications should empower the long tail too. If you just sort by popularity, you'd loose all those niches. [from [choosing a similarity measure](http://tagging.pui.ch/automated_tag_clustering/#p_similarity)]

We'd be happy to get any kind of feedback on the article. Just post a comment to this blog post.

**Edit (4 years later!)**: A few guys asked me about the source code: [Source code with syntax highlighting](http://pastie.org/1098455).
You need [kmetis](http://people.sc.fsu.edu/~jburkardt/c_src/kmetis/kmetis.html) to make this run, see `usage()` to see how it should be used.

**Edit**: Robin sent me [this fixed source code](http://pastie.org/3549928), didn't test it though:

<div class="blogger-post-footer">![](https://blogger.googleusercontent.com/tracker/2748783673844839576-786221472892263493?l=theneachwenttohisownhome.blogspot.com)</div>