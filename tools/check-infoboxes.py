#! /usr/bin/env python
# Public domain; MZMcBride; 2018

import subprocess

import wikitools

import settings

wiki = wikitools.Wiki(settings.apiurl)
wiki.login(settings.username, settings.password)


def get_intro_section_wikitext(wiki, page):
    params = {
        'action': 'parse',
        'page': page,
        'section': '0',
        'format': 'json',
        'prop': 'wikitext',
    }
    request = wikitools.APIRequest(wiki, params)
    og_wikitext = request.query()[u'parse'][u'wikitext'][u'*']
    return og_wikitext


def manipulate_intro_section_wikitext(og_wikitext):
    sb_wikitext = og_wikitext.replace(
        'Infobox SCOTUS case',
        'Infobox SCOTUS case/sandbox',
    ).replace(
        'SCOTUSCase',
        'Infobox SCOTUS case/sandbox',
    )
    return sb_wikitext


def parse_wikitext_to_html(wiki, title, wikitext):
    params = {
        'action': 'parse',
        'text': wikitext,
        'title': title,
        'format': 'json',
        'prop': 'text',
        'disablelimitreport': '1',
    }
    request = wikitools.APIRequest(wiki, params)
    html = request.query()[u'parse'][u'text'][u'*']
    return html


def get_category_members(wiki, category):
    from_cat = set()
    params = {
        'action': 'query',
        'list': 'categorymembers',
        'cmtitle': category,
        'cmlimit': 500,
        'cmnamespace': 0,
        'format': 'json',
    }
    request = wikitools.APIRequest(wiki, params)
    for response in request.queryGen():
        members = response['query']['categorymembers']
        for member in members:
            from_cat.add(member[u'title'])
    return from_cat


cases = get_category_members(wiki, 'Category:United_States_Supreme_Court_cases')
for case in cases:
    print(case)
    og_wikitext = get_intro_section_wikitext(wiki, case)
    sb_wikitext = manipulate_intro_section_wikitext(og_wikitext)
    og_html = parse_wikitext_to_html(wiki, case, og_wikitext)
    sb_html = parse_wikitext_to_html(wiki, case, sb_wikitext)
    with open('sb', 'w') as f_:
        f_.write(sb_html.encode('utf-8') + '\n')
    with open('og', 'w') as f_:
        f_.write(og_html.encode('utf-8') + '\n')
    args = [
        '/usr/bin/git',
        'diff',
        '--color=always',
        '--no-index',
        '--word-diff-regex=.',
        'og',
        'sb',
    ]
    f = subprocess.Popen(args, stdout=subprocess.PIPE)
    (out, error) = f.communicate()
    print(out)
