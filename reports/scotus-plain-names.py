#! /usr/bin/env python
# Public domain; MZMcBride; 2012

import re
import sqlite3

import wikitools

import settings

case_name_re_1 = re.compile(r'[^\'=]\[\[([A-Za-z0-9\s\.,\-]+ v\. [A-Za-z0-9\s\.,\-]+)\]\]')

report_title = settings.rootpage + 'F'
report_template = u'''\
Cases containing non-italicized case names.

{| class="wikitable plainlinks" style="width:100%%; margin:auto;"
|- style="white-space:nowrap;"
! No.
! Page
! Match
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
    for match in case_name_re_1.finditer(page_text):
        table_row = u"""\
|-
| %d
| ''[[%s]]''
| %s""" % (i, page_title, match.group(1))
        output.append(table_row)
        i += 1

wiki = wikitools.Wiki(settings.apiurl)
wiki.login(settings.username, settings.password)
report = wikitools.Page(wiki, report_title)
report_text = report_template % ('\n'.join(output))
report.edit(report_text, summary=settings.editsumm, bot=1, skipmd5=True)
