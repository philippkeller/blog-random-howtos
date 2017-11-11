---
title: 'Tagsystems: performance tests'
tags:
  - Performance
  - Tags
  - Del.icio.us
  - MySQL
date: 2005-06-19 17:09:00
alias: /post/37027746608/tagsystems-performance-tests
---

In my [previous article named &ldquo;Tags: database schemas&rdquo;](http://tagging.pui.ch/post/37027745720/tags-database-schemas "Tags: database schemas") we analysed different database schemas on how they could meet the needs of tag systems. In this article, the focus is on performance (speed). That is: if you want to build a tagsystem that performs good with about 1 million items (bookmarks for instance), then you may want to have a look at the following result of my performance tests.
In this article I tested tagging of bookmarks, but as you can tag pretty much anything, this goes for tagging systems in general.<!-- more -->

I tested the following schemas (I keep the naming from the previous article):

*   **mysqlicious**: One table. Tags are space separated in column &ldquo;tags&rdquo;; [as introduced](http://tagging.pui.ch/post/37027745720/tags-database-schemas#mysqlicious)
*   **mysqlicious fulltext**: Same schema but with [mysql fulltext](http://dev.mysql.com/doc/mysql/en/fulltext-search.html) on the tag column; [as introduced](http://tagging.pui.ch/post/37027745995/tags-with-mysql-fulltext)
*   **scuttle**: Two tables: One for bookmarks, one for tags. Tag-table has foreign key to bookmark table; [as introduced](http://tagging.pui.ch/post/37027745720/tags-database-schemas#scuttle)
*   **toxi**: Three tables: One for bookmarks, one for tags, one for junction; [as introduced](http://tagging.pui.ch/post/37027745720/tags-database-schemas#toxi)

<span>You may want to have a close watch at the details of the schemas when having a look at the </span>[sql-create-table-queries](http://pastie.org/5480706)<span>.</span>

<span></span>But let&rsquo;s go directly to the results. The details about the setup of this tests are mentioned at the [end of this article](#setup). The x-axis depicts the number of bookmarks in the corresponding database, on the y-axis you see how much time each query took to execute.<!-- more -->

### <a name="#results" id="#results"></a>Results

#### Intersection: 250 tag set

![Intersection test with 300 queries, up to three tags in query, 250 tags in small dataset](https://lh4.googleusercontent.com/-3MTMt9iTACc/UL0Axe4hHMI/AAAAAAAALDM/cGcmhMoMo20/s400/intersection_250_3_i300.png "Intersection test with 300 queries, up to three tags in query, 250 tags in small dataset")

The first two tests are done with 250 tags in the small dataset ([see below](#setup) for explanation). I think the queries in the &ldquo;1 million bookmarks database&rdquo; are the only size we should pay attention to. I mean if you have a small number of bookmarks, performance isn&rsquo;t really a thing to bother..

We run intersection queries, like

> <div>I want to search for bookmarks tagged with &ldquo;design&rdquo; and &ldquo;html&rdquo;</div>

You see that, not surprisingly, mysqlicious with its `WHERE tag LIKE "% tag %"` is very slow. That is, MySQL has to go through the whole dataset and test each bookmark against the query.
What actually **is** surprising me, is that the fulltext search of mysql is not that high-performance. In fact it is not faster then the `LIKE`-query in the MySQLicious DB. This really disappointed me. I tried to do any quirks possible to make this faster as [I think, a tag-database-system with mysql fulltext would be very easy and like the only thing you should head to..](http://tagging.pui.ch/post/37027745995/tags-with-mysql-fulltext).
What is surprising me too, is that the queries on the 3 table schema are about double as fast the the ones on the two-table ones([take a look at the queries](http://pastie.org/5480722) if you think you could give me a hint on this). Noticeable is, that in the scuttle and toxi-variant, the more queries were run, the faster they were. I didn&rsquo;t do any tests with queries and inserts mixed so this may be coming from just plain good caching and this effect possible doesn&rsquo;t show up on live bookmark management systems.

#### Intersection: 999 tag set

![Intersection test with 300 queries, up to three tags in query, 250 tags in small dataset](https://lh4.googleusercontent.com/-4awEHoQC8w8/UL0Ax6ZbRNI/AAAAAAAALDY/rSvIp_iaqGA/s400/intersection_999_3_300.png "Intersection test with 300 queries, up to three tags in query, 250 tags in small dataset")
Now have a look to what happens if we broaden our small tag set: MySQLicious with fulltext suddenly gets the performance leader. That means, if you have a bookmark management system with diverse tags (this most probably comes from the fact that there are many users), the fulltext solution is possibly the way to go.
So now, as you see, choosing the right schema is all about tag distribution. In my previous post about guessing the overall tag distribution on [del.icio.us](http://del.icio.us), I came to the conclusion, that delicious&rsquo; most popular tag &ldquo;design&rdquo; is showing up in 3.2% of all bookmarks on [del.icio.us](http://del.icio.us). So then, what is the mean tag distribution?

*   If we say 1% (a tag shows up in 1/100 of all bookmarks on an average) that makes our small tag set 250 tags big
*   If we say 0.25%, the small tag set grows to a size of 1000
*   If we say 0.1%, the small set will contain 2500 tags

<span>So I&rsquo;d suggest that if your average distribution is 1%, take &ldquo;toxi&rdquo;, if the distribution is broader, take &ldquo;MySQLicious fulltext&rdquo;.</span>

<span></span>If you take a closer look, you can see that the fulltext schema stayed as fast as when queried in the 250 tag set. That means, if you want to go sure your tag system responds ok in every situation, you should go with the &ldquo;mysql fulltext&rdquo; schema.
[Hannes has done some further investigation on mysql fulltext running on MySQL 4.1](http://hannes.magiccards.info/get/results.html) (my tests were on MySQL 4.0.21)

#### Union

![Union test with 250 tags in small dataset](https://lh5.googleusercontent.com/-Ze5AtV5GPMQ/UL0A35Lc2aI/AAAAAAAALEQ/Y9b0Qs9daAU/s400/union_full_250_3.png)
When doing a union query we say

> <div>I want to search for all the bookmarks that are tagged either with &ldquo;delicious&rdquo; or &ldquo;del.icio.us&rdquo;</div>

This queries, you guessed, are handled the fastest by &ldquo;MySQLicious schema&rdquo; with its `LIKE`-queries: MySQL seeks through the bookmarks, harvesting all bookmarks with one of the given tags and says &ldquo;I&rsquo;m finished!&rdquo; when it was at bookmark number #968, because it found 50 bookmarks. Whereas in the other schemas, MySQL has to join the tags with the bookmarks first and only then could search though it..

#### Insert

![Setup database schemas with the data: 250 tags in small dataset](https://lh5.googleusercontent.com/-0HAVj_cQ5dM/UL0A2DwvC5I/AAAAAAAALDw/X4DmJIwk8nk/s400/setup_250.png)
When comparing the different schemas on the time of the insert-&ldquo;statements&rdquo; of one bookmark, the result isn&rsquo;t very surprising (notice that I&rsquo;ve changed the scale of the y-axis).
Mysqlicious with it&rsquo;s 1 table is very fast indeed, its variation with fulltext had to create the fulltext index and therefore is a bit slower. Scuttle, with its 2 tables and toxi with its 3 tables are at least two respectively three times as slow. I have to remark, that I used quite a bit of caching for the toxi schema, as I didn&rsquo;t want hours to have the data ready..

I guess it doesn&rsquo;t really make sense to base your decision, which schema to take on the time for an insert: Bookmark inserts are about 100 times as fast as the intersection queries..

#### «What? That slow??»

You said it. You don&rsquo;t want your intersection queries take 0.2 seconds each. That would bring your system to its knees.

<span>There are some recipes to avoid that:</span>

##### Caching

I think, you don&rsquo;t come around good old caching. I think that you could cache results to a query like &ldquo;mysql+tagging&rdquo; for about an hour or so. If a user queries his own items, I would lower the cache time (as up-to-dateness is more important with his own items).
Then, I expect if you for instance cache items per tag and intersection them with a decent algorithm, that could be faster..

##### The Best Of Both Worlds

I think you could have &ldquo;mysqlicous fulltext&rdquo; and &ldquo;toxi&rdquo; running at the same time. That means you have to update/insert in both schemas but when you have to query, you could take the one you think is faster: For simple union the mysqlicious without fulltext search, for intersection queries with common tags the toxi, and for those with uncommon tags the mysqlicious fulltext variant.

##### Slicing and dicing

You could &ldquo;slice and dice&rdquo; data (as Nitin proposed it in [two](http://tagschema.com/blogs/tagschema/2005/06/slicing-and-dicing-data-20-part-1.html) of his [posts](http://tagschema.com/blogs/tagschema/2005/06/slicing-and-dicing-data-20-part-2.html)): That is: you slice your user/tag/item-room and build fact tables. You &ldquo;prebuild&rdquo; your results in a way. This way, inserts take long but queries themself should be much faster. In our examples, you would for instance first query the tag-intersections on &ldquo;toxi&rdquo; and then get the facts about each bookmark out of the &ldquo;mysqlicious&rdquo;-fact-table. But you really should read Nitins posts, as they give a lot of insight.

##### Using a non RDBMS system

**Update:** It&rsquo;s been about a year since I wrote that article, and during that year I came to the conclusion that [RDBMS](http://en.wikipedia.org/wiki/RDBMS) systems don&rsquo;t scale good in systems that have more than 1 million items. Yes, this is a warning: If you are planning to build a large scale system then look for alternatives to [RDBMS](http://en.wikipedia.org/wiki/RDBMS) systems. To quote Joshua Schachter, founder of [delicious](http://del.icio.us):
«tags doesn&rsquo;t map to sql at all. so use partial indexing.»[[Joshua Schachter at Carson Summit](http://www.redmonk.com/jgovernor/2006/02/08/things-weve-learned-josh-schachter-quotes-of-the-day/)]
I didn&rsquo;t try any of the non-RDBMS system but it looks like [Apache Lucene](http://lucene.apache.org/java/docs/) and [Hadoop](http://lucene.apache.org/hadoop/). There has been [a discussion on the Tagdb Mailing list](http://nelson.textdrive.com/pipermail/tagdb/2006-March/thread.html#164) about these solutions.

#### «I don&rsquo;t believe you! I want to try it at home»

[Download the source code (PHP)](https://docs.google.com/file/d/0B0uw1JCogWHubEJhdFhub0VjbkE/edit) I used to run the queries and test yourself, extend them as you like. The source is published as [LGPL](http://en.wikipedia.org/wiki/LGPL).

### <a id="setup" name="setup"></a>Performance Tests Setup

<span>Now, if you have read that far, you probably want to know some background information: As you noticed, for each schema, I set up 4 databases, one database holding 1000 bookmarks, the next 10'000, then 100'000 and the fourth 1 million bookmarks. The inserted tags (as well as urls) are random English words taken from two sets of tags:</span>

*   the large set containing about 44'000 tags (that are simple English words)
*   the small set is varying in size (the results shown here are taken from 250 and 999 tag sets)

Every bookmark gets one to ten tags attached. Every odd tag is from the large set, alternately taken from small and large set. Every schema got exactly the same bookmarks and tag data.

Then every schema got queried with an alternately 1-3 tag query. So the first query is for instance just &ldquo;blog&rdquo;, the second &ldquo;design+css&rdquo;, the third &ldquo;webdesign+music+software&rdquo;, the fourth again with just one tag an so forth..
All the tags for the queries are taken from the small set so that the queries don&rsquo;t all end in empty results..
All the queries are tested and work. The outcome of each query on the three schemas is exactly the same.

#### Mysql Setup

I used mysql 4.0.21.
An excerpt from `/etc/my.cnf` (I think these are the relevant settings to this performance test)

<pre>key_buffer=300M
query_cache_size=30M
query_cache_limit=30M
table_cache = 64
ft_min_word_len = 2
ft_stopword_file = ''</pre>

#### System

> <div>CPU: 3GHz Dual Xeon
> Cache: 1MB
> Harddisk: SCSI Ultra 320 Atlas 10K, no RAID
> RAM: 3GB</div>

#### Assumptions

*   Queries select just the id of a bookmark. I assume that you have to do a second query to get all the wished data to display. I know that this is not fair towards the mysqlicious schema.
*   I left out user data, as I assume, user data columns wouldn&rsquo;t change the outcome of this tests. I wanted to keep the schemas as simple as possible.
*   Each query is done with `LIMIT 50` as I assume that a normal application doesn&rsquo;t want to get all bookmarks. I assume nobody wants to `order` bookmarks by any dimension, because this would be **very** expensive (ever wondered why you cannot sort bookmarks on [del.icio.us](http://del.icio.us) by date or similar? You get it..)

### Acknowledgements

Thanks to [Citrin](http://www.citrin.ch), the company I work, to let me use our new server to run the queries. The server didn&rsquo;t have much anything else to do so the results should be accurate.
The graphs are done using [JpGraph](http://www.aditus.nu/jpgraph/). Very easy to use and produces beautiful images.

### Further reading

*   [Flickr architecture](http://www.niallkennedy.com/blog/archives/2004/10/flickr_architec.html)
*   [Lab notes: Fulltext not so fast](http://labnotes.blogsome.com/2005/06/06/lab-notes-5-fulltext-not-so-fast/): Fulltext performance issues
*   [WebmasterWorld forum: mysql fulltext performance issues](http://www.webmasterworld.com/forum23/3557.htm)
*   [Mysql Supersmack: Mysql performance tool](http://vegan.net/tony/supersmack/)
*   [Mysql Benchmark](http://dev.mysql.com/doc/mysql/en/mysql-benchmarks.html)
*   [Powerpoint article of jeremy zawodny](http://jeremy.zawodny.com/mysql/mysql-optimization.html)on Mysql optimisation
*   [Pete Freitag did a sort of review of this article](http://www.petefreitag.com/item/389.cfm)<div class="blogger-post-footer">![](https://blogger.googleusercontent.com/tracker/2748783673844839576-5133448602510209729?l=theneachwenttohisownhome.blogspot.com)</div>