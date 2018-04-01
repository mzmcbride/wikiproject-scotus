#!/usr/bin/env python

import wikitools

import settings

wiki = wikitools.Wiki(settings.apiurl)

report_title = settings.rootpage + 'J'
report_template = u'''\
Category comparisons.
Cases containing non-italicized case names.

{| class="wikitable plainlinks" style="width:100%%; margin:auto;"
|- style="white-space:nowrap;"
! No.
! Page
! Match
%s
|}
'''

category = wikitools.Category(wiki, 'United States Supreme Court cases by court')
members = category.getAllMembersGen(titleonly=True)

courts = []
for member in members:
    if 'of the ' in member:
        courts.append(member)

all_cases = []
category = wikitools.Category(wiki, 'United States Supreme Court cases')
members = category.getAllMembersGen(titleonly=True, namespaces=[0])
for member in members:
    all_cases.append(member)

all_cases_by_court = []
for court in courts:
    category = wikitools.Category(wiki, court)
    members = category.getAllMembersGen(titleonly=True, namespaces=[0])
    for member in members:
        all_cases_by_court.append(member)

for case in all_cases:
    if case not in all_cases_by_court:
        print('* [[' + case + ']]')

print('\n')
print('=' * 80)
print('THESE CASES ARE MISSING THE MASTER CATEGORY:')
print('=' * 80)
print('\n')

for case in all_cases_by_court:
    if case not in all_cases and "per curiam opinions of the Supreme Court of the United States" not in case and \
        "List of United States Supreme Court cases" not in case:
        print('* [[' + case + ']]')

wiki.login(settings.username, settings.password)
report = wikitools.Page(wiki, report_title)
report_text = report_template % ('\n'.join(output))
report.edit(report_text, summary=settings.editsumm, bot=1)
