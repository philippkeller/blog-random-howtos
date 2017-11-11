---
title: 'Python: Print list of dicts as ascii table'
tags:
  - python
date: 2010-02-27 12:55:00
---

Sometimes I want to print list of dicts as an ascii table, like this:

<pre>  | Programming Language | Language Type | Years of Experience |
  +----------------------+---------------+---------------------+
  | python               | script        |                    4 |
  | php                  | script        |                    5 |
  | java                 | compiled      |                   11 |
  | assember             | compiled      |                   15 |
</pre>

I searched on Google - but without luck.<!-- more -->

 That&rsquo;s what I came up with - it&rsquo;s not particularly nice but it does the job:

<pre>  def table_print(data, title_row):
    """
    data: list of dicts,
    title_row: e.g. [('name', 'Programming Language'), ('type', 'Language Type')]
    """
    max_widths = {}
    data_copy = [dict(title_row)] + list(data)
    for col in data_copy[0].keys():
      max_widths[col] = max([len(str(row[col])) for row in data_copy])
    cols_order = [tup[0] for tup in title_row]

    def custom_just(col, value):
      if type(value) == int:
        return str(value).rjust(max_widths[col])
      else:
        return value.ljust(max_widths[col])

    for row in data_copy:
      row_str = " | ".join([custom_just(col, row[col]) for col in cols_order])
      print "| %s |" % row_str
      if data_copy.index(row) == 0:
        underline = "-+-".join(['-' * max_widths[col] for col in cols_order])
        print '+-%s-+' % underline

  </pre>

Use it like that:

<pre>  data = [dict(name='python', type='script', years_experience=4),
    dict(name='php', type='script', years_experience=5),
    dict(name='java', type='compiled', years_experience=11),
    dict(name='assember', type='compiled', years_experience=15)
    ]
  titles = [('name', 'Programming Language'),
    ('type', 'Language Type'),
    ('years_experience', 'Years of Experience')]
  table_print(data, titles)
  </pre>

It will produce the table printed above. It&rsquo;s not fancy - the only &lsquo;smart&rsquo; thing it does is **right-adjusting integers, strings are left-adjusted**.

 P.S. no, I don&rsquo;t have 15 years of experience of Assembler - I just know it since 15 years - it&rsquo;s one of the first programming languages I learned - and I even wrote a text editor with it - then I learned that&rsquo;s probably not the best language to write an editor :-)