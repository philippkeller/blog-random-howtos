---
title: 'Tags: Database schemas'
tags:
  - Tagging
  - Del.icio.us
  - MySQL
date: 2005-04-24 16:35:00
alias: /post/37027745720/tags-database-schemas
---

Recently, on the del.icio.us mailinglist, I asked the question "Does anyone know the database schema of del.icio.us?". I got a few private responses so I wanted to share the knowledge with the world.

The Problem: You want to have a database schema where you can tag a bookmark (or a blog post or whatever) with as many [tags](http://en.wikipedia.org/wiki/Tags) as you want. Later then, you want to run queries to constrain the bookmarks to a [union](http://en.wikipedia.org/wiki/Union_%28set_theory%29) or [intersection](http://en.wikipedia.org/wiki/Intersection_%28set_theory%29) of tags. You also want to exclude (say: minus) some tags from the search result.

Apparently there are three different solutions (**Attention: **If you are building a websites that allows users to tag, be sure to have a look at [my performance tests](http://howto.philippkeller.com/2005/06/19/Tagsystems-performance-tests/) as performance seems to be a problem on larger scaled sites.)<!-- more -->

## <a id="mysqlicious" name="mysqlicious"></a>"MySQLicious" solution

![mysqlicious sample data](https://lh3.googleusercontent.com/-yV7B1_K6nEM/UL0AyrAz2yI/AAAAAAAALDc/3nRpzrNXMwM/s373/mysqlicious_data.png)![mysqlicious database stucture](https://lh4.googleusercontent.com/-PSV7DWIwy0Q/UL0AyyL_z0I/AAAAAAAALDg/vUhaDRz9b-4/s128/mysqlicious_structure.png)

In this solution, the schema has got just one table, it is [denormalized](http://en.wikipedia.org/wiki/Denormalization)

I named this solution "MySQLicious solution" because [MySQLicious](http://nanovivid.com/projects/mysqlicious/) imports del.icio.us data into a table with this structure.

### Intersection (AND)

Query for `search+webservice+semweb`:

```sql
SELECT - 
FROM `delicious` 
WHERE tags LIKE "%search%" 
AND tags LIKE "%webservice%" 
AND tags LIKE "%semweb%"
```

### Union (OR)

Query for `search|webservice|semweb`

```sql
SELECT - 
FROM `delicious` 
WHERE tags LIKE "%search%" 
OR tags LIKE "%webservice%" 
OR tags LIKE "%semweb%"
```

### Minus

Query for `search+webservice-semweb`

```
SELECT - 
FROM `delicious` 
WHERE tags LIKE "%search%" 
AND tags LIKE "%webservice%" 
AND tags NOT LIKE "%semweb%"
```

### Conclusion

The advantages of this solution:

- just one table
- the queries are very straightforward
- one can also achieve results via fulltextsearch. That might be a little faster.
- queries are quite slow according to some commenters. Fulltext search would speed up a bit. I [did some performance tests](http://tagging.pui.ch/post/37027746608/tagsystems-performance-tests) to prove that.
- [In my follow up post I dealt with MySQL fulltext concerning tagging](http://tagging.pui.ch/post/37027745995/tags-with-mysql-fulltext).

Disadvantages:

- You have a limit on the number of tags per bookmark. Normally you use a 256byte field in your DB (`VARCHAR`). Otherwise, if you took a `text` field or similar, the query times would slow down, I suppose
- Patrice [noticed](http://tagging.pui.ch/post/37027745720/tags-database-schemas#comment-725379777) that `LIKE "%search"` will also find tags with "websearch". If you alter the query to `LIKE " %search% "` you end up having a messy solution: You have to add a space to the beginning of the tags value to make this work.

## <a id="scuttle" name="scuttle"></a>"Scuttle" solution

Scuttle organizes its data in two tables. That table "scCategories" is the "tag"-table and has got a foreign key to the "bookmark"-table. ![database structure of scuttle](https://lh3.googleusercontent.com/-g9_LV4z_W5Q/UL0AzhvHefI/AAAAAAAALDo/LJYhO3RlaxQ/s206/scuttle_structure.png)

### Intersection (AND)

Query for `bookmark+webservice+semweb`:

```sql
SELECT b.*
FROM scBookmarks b, scCategories c
WHERE c.bId = b.bId
AND (c.category IN ('bookmark', 'webservice', 'semweb'))
GROUP BY b.bId
HAVING COUNT( b.bId )=3
```

First, all bookmark-tag combinations are searched, where the tag is "bookmark", "webservice" or "semweb" (`c.category IN ('bookmark', 'webservice', 'semweb')`), then just the bookmarks that have got all three tags searched for are taken into account (`HAVING COUNT(b.bId)=3`).

### Union (OR)

Query for `bookmark|webservice|semweb`:

Just leave out the `HAVING` clause and you have union:

```sql
SELECT b.*
FROM scBookmarks b, scCategories c
WHERE c.bId = b.bId
AND (c.category IN ('bookmark', 'webservice', 'semweb'))
GROUP BY b.bId
```

### Minus (Exclusion)

Query for `bookmark+webservice-semweb`, that is: bookmark AND webservice AND NOT semweb.

```sql
SELECT b. *
FROM scBookmarks b, scCategories c
WHERE b.bId = c.bId
AND (c.category IN ('bookmark', 'webservice'))
AND b.bId NOT
IN (SELECT b.bId FROM scBookmarks b, scCategories c WHERE b.bId = c.bId AND c.category = 'semweb')
GROUP BY b.bId
HAVING COUNT( b.bId ) =2
```

Leaving out the `HAVING COUNT` leads to the Query for "bookmark|webservice-semweb".
Credits go to [Rhomboid](http://www.metafilter.com/user/26222) for [helping me out with this query](http://ask.metafilter.com/mefi/34897#544185).

### Conclusion

I guess the main advantage of this solution is that it is more normalized than the first solution, and that you can have unlimited number of tags per bookmark.

## <a id="toxi" name="toxi"></a>"Toxi" solution

![image](https://lh3.googleusercontent.com/-WmVNkFcCHOI/UL0A3982dZI/AAAAAAAALEI/GC0DI-wfiIU/s330/toxi_structure.png)

[Toxi](http://toxi.co.uk/) came up with a three-table structure. Via the table "tagmap" the bookmarks and the tags are n-to-m related. Each tag can be used together with different bookmarks and vice versa. This DB-schema is also used by [wordpress](http://wordpress.org/).

The queries are quite the same as in the "scuttle" solution.

### Intersection (AND)

Query for `bookmark+webservice+semweb`

```sql
SELECT b.*
FROM tagmap bt, bookmark b, tag t
WHERE bt.tag_id = t.tag_id
AND (t.name IN ('bookmark', 'webservice', 'semweb'))
AND b.id = bt.bookmark_id
GROUP BY b.id
HAVING COUNT( b.id )=3
```

### Union (OR)

Query for `bookmark|webservice|semweb`

```sql
SELECT b.*
FROM tagmap bt, bookmark b, tag t
WHERE bt.tag_id = t.tag_id
AND (t.name IN ('bookmark', 'webservice', 'semweb'))
AND b.id = bt.bookmark_id
GROUP BY b.id
```

### Minus (Exclusion)

Query for `bookmark+webservice-semweb`, that is: bookmark AND webservice AND NOT semweb.

```sql
SELECT b. *
FROM bookmark b, tagmap bt, tag t
WHERE b.id = bt.bookmark_id
AND bt.tag_id = t.tag_id 
AND (t.name IN ('Programming', 'Algorithms'))
AND b.id NOT IN (SELECT b.id FROM bookmark b, tagmap bt, tag t WHERE b.id = bt.bookmark_id AND bt.tag_id = t.tag_id AND t.name = 'Python')
GROUP BY b.id
HAVING COUNT( b.id ) =2
```

Leaving out the `HAVING COUNT` leads to the Query for `bookmark|webservice-semweb`.
Credits go to [Rhomboid](http://www.metafilter.com/user/26222) for [helping me out with this query](http://ask.metafilter.com/mefi/34897#544185).

### Conclusion

The advantages of this solution:

- You can save extra information on each tag (description, tag hierarchy, &hellip;)
- This is the most normalized solution (that is, if you go for [3NF](http://en.wikipedia.org/wiki/3NF): take this one :-)

Disadvantages:

- When altering or deleting bookmarks you can end up with tag-orphans.

If you want to have more complicated queries like (bookmarks OR bookmark) AND (webservice or WS) AND NOT (semweb or semanticweb) the queries tend to become very complicated. In these cases I suggest the following query/computation process:

1.  Run a query for each tag appearing in your "tag-query":
    ```sql
    SELECT b.id FROM tagmap bt, bookmark b, tag t 
    WHERE bt.tag_id = t.tag_id AND b.id = bt.bookmark_id AND t.name = "semweb"
    ```
2.  Put each id-set from the result into an array (that is: in your favourite coding language). You could cache this arrays if you want..
3.  Constrain the arrays with union or intersection or whatever.

In this way, you can also do queries like `(del.icio.us|delicious)+(semweb|semantic_web)-search`. This type of queries (that is: the brackets) cannot be done by using the denormalized "MySQLicious solution". 
This is the most flexible data structure and I guess it should scale pretty good (that is: if you do some caching).

**Update May, 2006**. This arcticle got quite some attention. I wasn't really prepared for that! It seems people keep referring to it and even some new sites that allow tagging give credit to my articles. I think the real credit goes to the contributers of the different schemas: [MySQLicious](http://nanovivid.com/projects/mysqlicious/), [scuttle](http://sourceforge.net/projects/scuttle/), [Toxi](http://toxi.co.uk/) and to all the contributors of the comments (be sure to read them!)

P.S. Thanks to [Toxi](http://toxi.co.uk/) for sending me the queries for the three-table-schema, Benjamin Reitzammer for pointing me to [a loughing meme article](http://laughingmeme.org/archives/002918.html) (a good reference for tag queries) and powerlinux for pointing me to [scuttle](http://sourceforge.net/projects/scuttle/).
