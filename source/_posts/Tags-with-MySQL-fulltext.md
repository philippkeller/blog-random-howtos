---
title: Tags with MySQL fulltext
tags:
  - Tags
  - MySQL
date: 2005-05-05 19:09:00
alias: /post/37027745995/tags-with-mysql-fulltext
---

While setting up the promised performance test in my [last post](http://tagging.pui.ch/post/37027745720/tags-database-schemas), I did some tests with the [MySQL fulltext features](http://dev.mysql.com/doc/mysql/en/fulltext-search.html) and it seems that they are built for tagging systems. Take a look at the queries (if it is not clear for you what is done here, please read [my previous post](http://tagging.pui.ch/post/37027745720/tags-database-schemas)).<!-- more -->

I took the [MySQLicious](http://nanovivid.com/projects/mysqlicious/) schema and added `ALTER TABLE `delicious` ADD FULLTEXT (`tags`)`. 
The full schema:

> <div>
> <div>`CREATE TABLE `delicious` (
>  `id` int(11) NOT NULL auto_increment,
>  `url` text,
>  `description` text,
>  `extended` text,
>  `tags` text,
>  `date` datetime default NULL,
>  `hash` varchar(255) default NULL,
>  PRIMARY KEY (`id`),
>  KEY `date` (`date`),
>  FULLTEXT KEY `tags` (`tags`)
> ) ENGINE=MyISAM`</div>
> </div>

## Queries

### Intersection

Intersections can be done using [boolean fulltext search](http://dev.mysql.com/doc/mysql/en/fulltext-boolean.html) (since MySQL 4.01):
Query for semweb+search:

`SELECT * FROM delicious WHERE MATCH (tags) AGAINST ('+semweb +search' IN BOOLEAN MODE)`

Now this was easy. And, you guess it, Minus is very similar:

### Minus

<span>Query for search+webservice-search:</span>

<span></span>`SELECT * FROM delicious WHERE MATCH (tags) AGAINST ('+search +webservice -search' IN BOOLEAN MODE)`

### Brackets

<span>Even brackets are possible:</span>
Query for (del.icio.us|delicious)+(webservice|project):

`SELECT * FROM delicious WHERE MATCH (tags) AGAINST ('+(del.icio.us delicious) +(webservice project)' IN BOOLEAN MODE)`

### Union

![union DB result](https://lh5.googleusercontent.com/-KI8lkatasrA/UL0A4ABDj4I/AAAAAAAALEY/X2i8ehJDAiE/s508/union_result.png)

<span>For union you could use the already mentioned boolean mode, but if you want to have the results ordered so that the bookmark with the most &ldquo;hits&rdquo; is the first entry of the result try this sort of query:</span>

`SELECT * FROM delicious WHERE MATCH (tags) AGAINST ('delicious clone project webservice')`

If you take a look at the screenshot of the first 7 results of the query run on my DB, you can see that the first hit has got all four tags we searched for, the second has got two and the rest has got just one of them. Like this you can do a &ldquo;find similar entries&rdquo; very easily.

## Downsides and problems

<span>There are two points where difficulties can accur: When MySQL builds its index out of the tags and when searching for specific tags. I stumbled on three problems:</span>

### Stopcharacters

<span>If you insert tags with characters like &ldquo;-&rdquo; (as in &ldquo;my-comment&rdquo;), then MySQL will make two index entries: One for &ldquo;my&rdquo; and one for &ldquo;comment&rdquo;. Vice versa if you search for &ldquo;my-comment&rdquo; you&rsquo;ll find bookmarks with tag &ldquo;my&rdquo; and those with tag &ldquo;comment&rdquo;. It seems that this problem can be eliminated by </span>[setting the character set of the column &ldquo;tags&rdquo; to `latin1_bin`](http://dev.mysql.com/doc/mysql/en/fulltext-search.html)<span> but this feature is not available before MySQL 4.1.</span>
But nontheless this shouldn&rsquo;t be a showstopper. You could replace &ldquo;-&rdquo; with a string, say &ldquo;_minus_&rdquo;. This is ugly but should do it..

### Stopwords

When searching for or indexing tags like &ldquo;against&rdquo; or &ldquo;brief&rdquo; ([full list of stopwords](http://www.databasejournal.com/features/mysql/article.php/1578331)), these tags will not be regarded. 
Since MySQL 4.0.10 you can [customize your stopwordlist](http://dev.mysql.com/doc/mysql/en/fulltext-fine-tuning.html).

### Minimum length of a tag

Per default, the minimal length of a word indexed by MySQL fulltext is 4 characters. You should therefor [edit `my.cnf`](http://dev.mysql.com/doc/mysql/en/fulltext-fine-tuning.html) in order to set the minimal tag length to 1.

## Performance

This solution scales ok. I did tests with tables from 1000 to 1 million bookmarks.
The time for inserting a bookmark is the same for small as for big tables. The time for an intersection query was 0.001 (finding 0.7 urls averaged) in the 1000-table and 0.1 seconds in the 1 million-table(finding 70 bookmarks averaged). There are some [discussions about if MySQLs fulltext search is fast or not (have a look at the user comments)](http://dev.mysql.com/doc/mysql/en/fulltext-search.html). Quick performance tests showed that it is about 10 times as fast as the LIKE-queries mentioned in [my previous post](http://tagging.pui.ch/post/37027745720/tags-database-schemas). But I guess it is not fast enough for webservices like [del.icio.us](http://del.icio.us), I guess this services have to run more than 10 queries a second and then this solution is too slow..
Update: [I tested the performance of this setup](http://tagging.pui.ch/post/37027746608/tagsystems-performance-tests).