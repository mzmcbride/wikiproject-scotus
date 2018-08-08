#! /usr/bin/env python
# Public domain; MZMcBride; 2012

import re
import sqlite3

import wikitools

import settings

report_title = settings.rootpage + 'E'
report_template = u'''\
U.S. Supreme Court cases.

%s
'''

conn = sqlite3.connect(settings.dbname)
cursor = conn.cursor()

cursor.execute('''
/* scotus-index.py */
SELECT
  page_title
FROM page;
''')

results = cursor.fetchall()

cursor.close()
conn.close()

output = []
for row in results:
    page_title = row[0]
    output.append("# ''[[%s]]''" % page_title)

wiki = wikitools.Wiki(settings.apiurl)
wiki.login(settings.username, settings.password)
report = wikitools.Page(wiki, report_title)
report_text = report_template % ('\n'.join(output))
report.edit(report_text, summary=settings.editsumm, bot=1, skipmd5=True)
