#! /usr/bin/env python
# Public domain; MZMcBride; 2012

"""
CREATE TABLE page (
  page_title text,
  page_text blob
);
CREATE UNIQUE INDEX page_title ON page (page_title);
"""

import sqlite3

import wikitools

import settings

def get_category_members(category):
    category_members = []
    params = {
        'action': 'query',
        'list': 'categorymembers',
        'cmtitle': 'Category:' + category,
        'cmlimit': 5000,
        'cmnamespace': 0,
        'format': 'json',
    }
    request = wikitools.APIRequest(wiki, params)
    response = request.query(querycontinue=False)
    members = response['query']['categorymembers']
    for member in members:
        category_members.append(member[u'title'])
    return category_members

conn = sqlite3.connect(settings.dbname)
cursor = conn.cursor()

wiki = wikitools.Wiki(settings.apiurl)
wiki.login(settings.username, settings.password)

cases = get_category_members('United States Supreme Court cases')
print(len(cases))

for case_title in cases:
    print(case_title)
    case = wikitools.Page(wiki, case_title)
    case_text = case.getWikiText().decode('utf-8')
    cursor.execute('''
    INSERT OR REPLACE INTO page VALUES (?, ?);
    ''' , (case_title, case_text))
    conn.commit()

cursor.close()
conn.close()
