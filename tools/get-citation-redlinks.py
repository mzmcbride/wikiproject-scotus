#! /usr/bin/env python
# CC0; lethargilistic; 2018

# Unlike the other tools, this uses Python 3, bs4, and requests.

'''
Check Report D and list all case citations that don't currently redirect to
articles and provide boilerplate code for those redirects.
'''

from bs4 import BeautifulSoup as bs
import requests
import re

def make_redirect(cite, title):
    search = re.search(r'(\d+) U.S. (\d+)', cite)
    vol = search.group(1).zfill(4)
    page = search.group(2).zfill(4)

    redirect = f'#REDIRECT [[{title}]]\n\n'
    redirect += '{{Redirect category shell|\n{{R from case citation|'
    redirect += f'{vol} U.S. {page}' + '}}\n'
    redirect += '{{R unprintworthy}}\n}}'
    return redirect

def main():
    BASE_URL = 'https://en.wikipedia.org'

    html = requests.get(BASE_URL + '/wiki/Wikipedia:WikiProject_U.S._Supreme_Court_cases/Reports/D').text

    soup = bs(html, 'html.parser')
    new_cites = soup.find_all('a', class_='new')

    for i, cite in enumerate(new_cites):
        print(i)
        print(BASE_URL + cite['href'])
        title = cite.parent.parent.contents[3].a['title']
        print(make_redirect(cite.string, title))
        print()

if __name__ == '__main__':
    main()
