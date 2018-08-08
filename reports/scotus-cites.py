#! /usr/bin/env python
# Public domain; MZMcBride; 2012

from collections import Counter
import re
import sqlite3

import wikitools

import settings

params_re = re.compile(r"""
\s*\|\s*USVol\s*=\s*(\d{1,3})
\n\s*\|\s*USPage\s*=\s*(\d{1,4}|___)
""", re.X)

report_title = settings.rootpage + 'D'
report_template = u'''\
Case citations. Each case listed below has a citation next to it. \
This link should be blue, either as a working redirect or as a link to \
a disambiguation page.

Redirects should ideally use the {{tl|R from case citation}} template \
with a proper category sort key.

''Caveat lector'': This report is automatically generated with a script \
(examining {{tl|Infobox SCOTUS case}}'s "USVol" and "USPage" template \
parameters) and the data has not been verified. Be mindful of this \
before relying on it.

{| class="wikitable sortable"
|- style="white-space:nowrap;"
! No.
! Page
! data-sort-type="text" | Citation
%s
|}

== Anomalies ==
%s

== Counts by volume ==
{| class="wikitable sortable"
|- style="white-space:nowrap;"
! Volume
! Count
%s
|}'''

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
volume_counts_raw = []
for row in results:
    page_title = row[0]
    page_text = row[1]
    result = params_re.search(page_text)
    if result:
        us_vol = result.group(1)
        us_page = result.group(2)
        volume_counts_raw.append(int(us_vol))
        if us_page == '___':
            cite_style = '%s U.S. %s' % (us_vol, us_page)
        else:
            cite_style = '[[%s U.S. %s]]' % (us_vol, us_page)
        sort_volume = str(format(int(us_vol), '04'))
        if us_page.isdigit():
            sort_page = str(format(int(us_page), '04'))
        else:
            sort_page = '0000'
        sort_key = sort_volume + sort_page
        table_row = u"""\
|-
| %d
| ''[[%s]]''
| data-sort-value="%s" %s| %s""" % (i, page_title, sort_key, 'class="nowrap" ' if i == 1 else '', cite_style)
        output.append(table_row)
        i += 1
    else:
        anomalies.append("# ''[[%s]]''" % page_title)

volume_counts_counted = Counter(volume_counts_raw)
volume_counts_sorted = sorted(volume_counts_counted.items())
volume_counts = []
for i in volume_counts_sorted:
    volume_counts.append("""\
|-
| [[List of United States Supreme Court cases, volume %s|%s]]
| %s""" % (i[0], i[0], i[1]))

wiki = wikitools.Wiki(settings.apiurl)
wiki.login(settings.username, settings.password)
report = wikitools.Page(wiki, report_title)
report_text = report_template % ('\n'.join(output),
                                 '\n'.join(anomalies),
                                 '\n'.join(volume_counts))
report.edit(report_text, summary=settings.editsumm, bot=1, skipmd5=True)
