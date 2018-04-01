#! /usr/bin/env python
# Public domain; MZMcBride; 2012

import hashlib
import sqlite3

import wikitools

import settings

def get_hashes_from_category(category):
    hashes = {}
    params = {
        'action': 'query',
        'generator' : 'categorymembers',
        'gcmtitle': 'Category:' + category,
        'gcmnamespace': 0,
        'gcmlimit': 5000,
        'prop' : 'revisions',
        'rvprop': 'sha1',
        'format': 'json',
    }
    request = wikitools.APIRequest(wiki, params)
    response = request.query(querycontinue=False)
    members = response['query']['pages']
    for page_id, dict_ in members.iteritems():
        page_title = dict_[u'title'].encode('utf-8')
        hashes[page_title] = dict_[u'revisions'][0][u'sha1'].encode('utf-8')
    return hashes

def get_hashes_from_local_store(cursor):
    hashes = {}
    cursor.execute('''
    /* update-scotus-db.py */
    SELECT
      page_title,
      page_text
    FROM page;
    ''')
    results = cursor.fetchall()
    for row in results:
        page_title = row[0].encode('utf-8')
        page_text = row[1].encode('utf-8')
        hash = hashlib.sha1(page_text).hexdigest()
        hashes[page_title] = hash
    return hashes

conn = sqlite3.connect(settings.dbname)
cursor = conn.cursor()

wiki = wikitools.Wiki(settings.apiurl)
wiki.login(settings.username, settings.password)

case_hashes = get_hashes_from_category('United States Supreme Court cases')
stored_hashes = get_hashes_from_local_store(cursor)

for case_title, sha1 in case_hashes.iteritems():
    if sha1 not in stored_hashes.values():
        case = wikitools.Page(wiki, case_title, followRedir=False)
        case_title = case_title.decode('utf-8')
        case_text = case.getWikiText().decode('utf-8')
        cursor.execute('''
        INSERT OR REPLACE INTO page VALUES (?, ?);
        ''' , (case_title, case_text, ))
        conn.commit()

# Get these hashes again as they may have changed!
stored_hashes = get_hashes_from_local_store(cursor)
for stored_title, stored_hash in stored_hashes.iteritems():
    if stored_hash not in case_hashes.values():
        cursor.execute('''
        DELETE FROM page WHERE page_title = ?;
        ''' , (stored_title, ))
        conn.commit()

cursor.close()
conn.close()
