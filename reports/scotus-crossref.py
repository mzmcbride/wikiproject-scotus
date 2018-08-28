#! /usr/bin/env python
# Public domain; MZMcBride; 2012

import wikitools

import settings

report_title = settings.rootpage + 'A'
wiki = wikitools.Wiki(settings.apiurl)
wiki.login(settings.username, settings.password)

def format_line(line):
    line = line.replace('_', ' ')
    line = "# ''[[%s]]''" % line
    return line

from_cat = set() # Pages marked as US Supreme Court cases
from_talk_page = set() # Pages marked as covered by WP:SCOTUS on their talk pages
from_infobox = set() # Pages with {{Infobox SCOTUS case}}
from_stub = set() # Pages marked as {{SCOTUS-stub}}
from_court_cat = set() # Pages marked with the Court (e.g. Vinson Court) or per curium

# Retrieve US Supreme Court cases; initial fill from_cat
params = {
    'action': 'query',
    'list': 'categorymembers',
    'cmtitle': 'Category:United_States_Supreme_Court_cases',
    'cmlimit': 5000,
    'cmnamespace': 0,
    'format': 'json'
}
request = wikitools.APIRequest(wiki, params)
response = request.query(querycontinue=False)
members = response['query']['categorymembers']
for member in members:
    from_cat.add(member[u'title'])

# Retrieve WP:SCOTUS topics; initial fill from_talk_page
params = {
    'action': 'query',
    'list': 'embeddedin',
    'eititle': 'Template:WikiProject_U.S._Supreme_Court_cases',
    'eilimit': 5000,
    'einamespace' : 1,
    'format': 'json'
}
request = wikitools.APIRequest(wiki, params)
response = request.query(querycontinue=False)
transclusions = response['query']['embeddedin']
for transclusion in transclusions:
    from_talk_page.add(transclusion[u'title'].split(':', 1)[1])

# Retrieve pages with {{Infobox SCOTUS case}}; initial fill from_infobox
params = {
    'action': 'query',
    'list': 'embeddedin',
    'eititle': 'Template:Infobox_SCOTUS_case',
    'eilimit': 5000,
    'einamespace' : 0,
    'format': 'json'
}
request = wikitools.APIRequest(wiki, params)
response = request.query(querycontinue=False)
transclusions = response['query']['embeddedin']
for transclusion in transclusions:
    from_infobox.add(transclusion[u'title'])

# Retrieve pages with {{SCOTUS-stub}}; initial fill from_stub
params = {
    'action': 'query',
    'list': 'embeddedin',
    'eititle': 'Template:SCOTUS-stub',
    'eilimit': 5000,
    'einamespace' : 0,
    'format': 'json'
}
request = wikitools.APIRequest(wiki, params)
response = request.query(querycontinue=False)
transclusions = response['query']['embeddedin']
for transclusion in transclusions:
    from_stub.add(transclusion[u'title'])

# Retrieve cases marked as under a court (e.g. Vinson Court); initial fill from_court_cat
params = {
    'action': 'query',
    'list': 'categorymembers',
    'cmtitle': 'Category:United_States_Supreme_Court_cases_by_court',
    'cmlimit': 50,
    'cmnamespace': 14,
    'format': 'json'
}
request = wikitools.APIRequest(wiki, params)
for response in request.queryGen():
    members = response['query']['categorymembers']
    for member in members:
        if u'of the' in member[u'title']:
            params = {
                'action': 'query',
                'list': 'categorymembers',
                'cmtitle': member[u'title'],
                'cmlimit': 500,
                'cmnamespace': 0,
                'format': 'json'
            }
            request = wikitools.APIRequest(wiki, params)
            for response in request.queryGen():
                members = response['query']['categorymembers']
                for member in members:
                    from_court_cat.add(member[u'title'])

# Remove per curium 
params = {
    'action': 'query',
    'list': 'categorymembers',
    'cmtitle': 'Category:United_States_Supreme_Court_per_curiam_opinions',
    'cmlimit': 5000,
    'cmnamespace': 0,
    'format': 'json',
}
request = wikitools.APIRequest(wiki, params)
for response in request.queryGen():
    members = response['query']['categorymembers']
    for member in members:
        from_court_cat.discard(member[u'title'])

params = {
    'action': 'query',
    'list': 'categorymembers',
    'cmtitle': 'Category:Lists_of_United_States_Supreme_Court_cases_by_court',
    'cmlimit': 5000,
    'cmnamespace': 0,
    'format': 'json',
}
request = wikitools.APIRequest(wiki, params)
for response in request.queryGen():
    members = response['query']['categorymembers']
    for member in members:
        from_court_cat.discard(member[u'title'])

output = []
output.append('''\
<pre>{{WikiProject U.S. Supreme Court cases|class=|importance=}}</pre>

== Article categorized; talk page not tagged ==''')


for i in (from_cat - from_talk_page):
    output.append(format_line(i))

output.append('\n== Article categorized; no infobox ==\n\
[[:Category:United States Supreme Court case articles without infoboxes]]')

for i in (from_cat - from_infobox):
    output.append(format_line(i))

output.append('\n== Infobox; article not categorized ==')

for i in (from_infobox - from_cat):
    output.append(format_line(i))

output.append('\n== Infobox; talk page not tagged ==')

for i in (from_infobox - from_talk_page):
    output.append(format_line(i))

output.append('\n== Stub template; article not categorized ==')

for i in (from_stub - from_cat):
    output.append(format_line(i))

output.append(
    '\n== Article categorized in court category; '
    'not categorized in master category =='
)

for i in (from_court_cat - from_cat):
    output.append(format_line(i))


report = wikitools.Page(wiki, report_title)
report_text = '\n'.join(output)
report_text = report_text.encode('utf-8')
report.edit(report_text, summary=settings.editsumm, bot=1)

'''
with open('out.wiki', 'w') as f:
    f.write(report_text)

print sorted(list(from_cat))[:100]
print ()
print sorted(list(from_talk_page))[:100]
print ()
print sorted(list(from_cat - from_talk_page))[:100]
print sorted(list(from_cat & from_talk_page))[:100]
'''
