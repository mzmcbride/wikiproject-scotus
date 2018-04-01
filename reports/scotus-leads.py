#! /usr/bin/env python
# Public domain; MZMcBride; 2012

import sqlite3
import re

import wikitools

import settings

lead_re = re.compile("""'''''.+''''', """)

report_title = settings.rootpage + 'B'
report_template = u'''\
Case article leads by [[WP:SCOTUS/SG|style guide]] status.
__TOC__
== Not formatted (%s) ==
{| class="wikitable plainlinks" style="width:100%%; margin:auto;"
|- style="white-space:nowrap;"
! No.
! Page
%s
|}

== Formatted (%s) ==
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
/* scotus-leads.py */
SELECT
  page_title,
  page_text
FROM page;
''')

results = cursor.fetchall()

cursor.close()
conn.close()

i = 1
j = 1
good_cases = []
bad_cases = []
for row in results:
    page_title = row[0]
    page_text = row[1]
    found = False
    for line in page_text.split('\n'):
        if lead_re.search(line):
            found = True
    if found:
        table_row = u"""\
|-
| %d
| ''[[%s]]''""" % (i, page_title)
        good_cases.append(table_row)
        i += 1
    else:
        table_row = u"""\
|-
| %d
| ''[[%s]]''""" % (j, page_title)
        bad_cases.append(table_row)
        j += 1

wiki = wikitools.Wiki(settings.apiurl)
wiki.login(settings.username, settings.password)
report = wikitools.Page(wiki, report_title)
report_text = report_template % (len(bad_cases),
                                 '\n'.join(bad_cases),
                                 len(good_cases),
                                 '\n'.join(good_cases))
report.edit(report_text.encode('utf-8'), summary=settings.editsumm, bot=1)
