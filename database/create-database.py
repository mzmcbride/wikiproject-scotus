#! /usr/bin/env python
# Public domain; MZMcBride; 2012

import sqlite3
import os
from datetime import datetime

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

    members = list()
    for result in request.queryGen(): #a generator of all the results
        for member in result['query']['categorymembers']: #each JSON result has params
            members.append(member['title']) #Get the title from inside member
    return members
        

#Archive the database if it exists
if os.path.exists(settings.dbname):
    print(dir(datetime))
    archive_name = settings.dbname + ' ' + str(datetime.now())
    archive_name = archive_name.replace(' ', '_')
    os.rename(settings.dbname, archive_name)

#Connect to database
conn = sqlite3.connect(settings.dbname)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE page (
  page_title text,
  page_text blob
); """)
cursor.execute('CREATE UNIQUE INDEX page_title ON page (page_title);')

#Connect to wiki
wiki = wikitools.Wiki(settings.apiurl)
wiki.login(settings.username, settings.password)

# Get the case data
cases = get_category_members('United States Supreme Court cases')
print("Number of cases:", len(cases)) 

for i, case_title in enumerate(cases):
    print("{}/{}".format(i, len(cases)))
    case = wikitools.Page(wiki, case_title)
    case_text = case.getWikiText().decode('utf-8')
    cursor.execute('''
    INSERT OR REPLACE INTO page VALUES (?, ?);
    ''' , (case_title, case_text))
    conn.commit()

cursor.close()
conn.close()
