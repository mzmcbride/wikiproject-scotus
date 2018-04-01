#! /usr/bin/env python
# Public domain; MZMcBride; 2012

import os
import re
import sqlite3
import sys
import urllib

import BeautifulSoup
import wikitools

import settings

fast = False
offset = 0
try:
    if sys.argv[-1] == '--fast':
        fast = True
except IndexError:
    pass

try:
    f = open('offset.txt', 'r')
    offset = int(f.read())
    f.close()
except (IOError, ValueError):
    offset = 0

print 'Offset: %d' % offset

params_re = re.compile(r"""
\s*\|\s*USVol\s*=\s*(\d{1,3})
\n\s*\|\s*USPage\s*=\s*(\d{1,4})
""", re.X)

def get_title_from(site, us_vol, us_page):
    #if site == 'open_jurist':
    #    url = 'http://openjurist.org/%s/us/%s' % (us_vol, us_page)
    if site == 'justia':
        url = 'http://supreme.justia.com/cases/federal/us/%s/%s/case.html' % (us_vol,
                                                                              us_page)
    if site == 'findlaw':
        url = 'http://caselaw.findlaw.com/us-supreme-court/%s/%s.html' % (us_vol,
                                                                          us_page)
    response = urllib.urlopen(url).read()
    soup = BeautifulSoup.BeautifulSoup(response)
    title = soup.html.head.title.string
    #title = title.replace(' | OpenJurist', '')
    if title:
        title = title.replace(' :: Justia US Supreme Court Center', '')
        title = title.replace('  | FindLaw', '')
    else:
        title = None
    return title

conn = sqlite3.connect(settings.dbname)
cursor = conn.cursor()

cursor.execute('''
/* scotus-cites.py */
SELECT
  page_title,
  page_text
FROM page
LIMIT 1000000
OFFSET ?;
''' , (offset,))

results = cursor.fetchall()

cursor.close()
conn.close()

wiki = wikitools.Wiki(settings.apiurl)
wiki.login(settings.username, settings.password)

all_case_citation_redirects= []
params = {
    'action': 'query',
    'list': 'categorymembers',
    'cmtitle': 'Category:Redirects from case citations',
    'cmlimit': 500,
    'cmnamespace': 0,
    'format': 'json'
}
request = wikitools.APIRequest(wiki, params)
for response in request.queryGen():
    members = response['query']['categorymembers']
    for member in members:
        all_case_citation_redirects.append(member[u'title'])

f = open('offset.txt', 'w')
i = 0
for row in results:
    i += 1
    page_title = row[0]
    page_text = row[1]
    result = params_re.search(page_text)
    if result:
        us_vol = result.group(1)
        us_page = result.group(2)
        citation = us_vol + ' U.S. ' + us_page
        if citation.decode('utf-8') in all_case_citation_redirects:
            continue
        if int(us_vol) > 567:
            continue
        print '=' * 80
        sort_key = us_vol.zfill(4) + ' U.S. ' + us_page.zfill(4)
        print page_title + '  |  ' + citation
        #print get_title_from('open_jurist', us_vol, us_page)
        print get_title_from('justia', us_vol, us_page)
        print get_title_from('findlaw', us_vol, us_page)
        redirect = '''#REDIRECT [[%s]]

{{Redirect category shell|
{{R from case citation|%s}}
{{R unprintworthy}}
}}''' % (page_title, sort_key)
        print 'Proposed: ' + redirect
        cite_redirect = wikitools.Page(wiki, citation, followRedir=False)
        try:
            cite_redirect_text = cite_redirect.getWikiText().decode('utf-8')
            print 'Current:  ' + cite_redirect_text
        except wikitools.page.NoPage:
            cite_redirect_text = False
        #print(repr(cite_redirect_text))
        #print(repr(redirect))
        if cite_redirect_text:
            cite_redirect_text = cite_redirect_text.replace(']] \n\n', ']]\n\n')
        if not cite_redirect_text:
            print 'Page does not exist (yet)!'
        else:
            continue
        if cite_redirect_text == redirect:
            print 'Identical (or really close)!'
            if fast:
                continue
        print 'Okay to edit?'
        if cite_redirect_text:
            editsumm = 'categorized'
        else:
            editsumm = 'redirect'
        try:
            response = raw_input()
        except KeyboardInterrupt:
            f.write('%s' % (i-1+offset))
            print
            break
        if response == 'y':
            cite_redirect.edit(redirect, summary=editsumm, skipmd5=True)
        elif response == 'n':
            continue
    # Clear the scrollback; Linux-only!
    os.system('clear')

f.close()
