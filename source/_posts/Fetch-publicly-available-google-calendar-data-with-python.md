---
title: Fetch publicly available google calendar data with python
tags:
  - python
date: 2009-12-29 22:31:00
---

      I tried [accessing the google data api with python](http://code.google.com/apis/calendar/data/1.0/developers_guide_python.html) - that api seems either overly complicated or just not suited for just grabbing events from a public google calendar.
<!-- more -->

      This worked for me:

1.  find out ical address (subscribe to the calendar, other calendars-&gt;arrow down-&gt;calendar settings)
2.  install [icalendar](http://codespeak.net/icalendar/)

      Then this is possible:

<pre>      
from icalendar import Calendar
import urllib
ics = urllib.urlopen('http://www.google.com/calendar/ical/fchppllvcaupb6fgguigobkfj4@group.calendar.google.com/public/basic.ics').read()
ical=Calendar.from_string(ics)
for vevent in ical.subcomponents:
 if vevent.name != "VEVENT":
  continue
 title = str(vevent.get('SUMMARY'))
 description = str(vevent.get('DESCRIPTION'))
 location = str(vevent.get('LOCATION'))
 start = vevent.get('DTSTART').dt      # a datetime
 end = vevent.get('DTEND').dt        # a datetime
</pre>