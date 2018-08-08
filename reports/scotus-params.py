#! /usr/bin/env python
# Public domain; MZMcBride; 2013

import sqlite3
import wikitools

import settings

report_title = settings.rootpage + 'G'
report_template = u'''\
Cases containing a deprecated template parameter.

== [[Template:Infobox SCOTUS case|Infobox SCOTUS case]]'s "CitationNew" ==
{| class="wikitable plainlinks" style="width:100%%; margin:auto;"
|- style="white-space:nowrap;"
! No.
! Page
%s
|}
'''

conn = sqlite3.connect(settings.dbname)
cursor = conn.cursor()

cursor.execute('''
/* scotus-cites.py */
SELECT
  page_title,
  page_text
FROM page;
''')

results = cursor.fetchall()

cursor.close()
conn.close()

i = 1
output = []
anomalies = []
for row in results:
    page_title = row[0]
    page_text = row[1]
    if page_text.find('CitationNew') != -1:
        table_row = u"""\
|-
| %d
| ''[[%s]]''""" % (i, page_title)
        output.append(table_row)
        i += 1

wiki = wikitools.Wiki(settings.apiurl)
wiki.login(settings.username, settings.password)
report = wikitools.Page(wiki, report_title)
report_text = report_template % ('\n'.join(output))
report.edit(report_text, summary=settings.editsumm, bot=1, skipmd5=True)
