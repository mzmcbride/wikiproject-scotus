#! /usr/bin/env python
# Public domain; MZMcBride; 2012

import re
import sqlite3

import wikitools

import settings

params_re = re.compile(r"""
\s*\|\s*USVol\s*=\s*(\d{1,3})
\n\s*\|\s*USPage\s*=\s*(\d{1,4}|___)
""", re.X)
scite_re = re.compile(r'\{\{scite\|\d{1,3}\|_{3}\|\d{4}\}\}')

report_title = settings.rootpage + 'D'
report_template = u'''\
Case citations. Each case listed below has two citations next to it \
(one "U.S." version and one "US" version) and both should be blue \
links (working redirects or links to disambiguation pages).

Redirects should ideally use the {{tl|R from case citation}} template \
with a proper category sort key.

''Caveat lector'': This report is automatically generated with a script \
(examining {{tl|Infobox SCOTUS case}}'s "USVol" and "USPage" template \
parameters) and the data has not been verified. Be mindful of this \
before relying on it.

{| class="wikitable plainlinks" style="width:100%%; margin:auto;"
|- style="white-space:nowrap;"
! No.
! Page
! Canonical citation
! Alternate citation
%s
|}

== Anomalies ==
%s
'''

conn = sqlite3.connect(settings.dbname)
cursor = conn.cursor()

cursor.execute('''
/* scotus-cites.py */
SELECT
  page_title,
  page_text
FROM page
ORDER BY page_title ASC;
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
    result = params_re.search(page_text)
    if result:
        if result.group(2) == '___':
            cite_style_1 = '%s U.S. %s' % (result.group(1),
                                           result.group(2))
        else:
            cite_style_1 = '[[%s U.S. %s]]' % (result.group(1),
                                               result.group(2))
        cite_style_2 = cite_style_1.replace('U.S.', 'US')
        table_row = u"""\
|-
| %d
| ''[[%s]]''
| %s
| %s""" % (i, page_title, cite_style_1, cite_style_2)
        output.append(table_row)
        i += 1
    else:
        anomalies.append("# ''[[%s]]''" % page_title)

wiki = wikitools.Wiki(settings.apiurl)
wiki.login(settings.username, settings.password)
report = wikitools.Page(wiki, report_title)
report_text = report_template % ('\n'.join(output),
                                 '\n'.join(anomalies))
report.edit(report_text, summary=settings.editsumm, bot=1, skipmd5=True)
