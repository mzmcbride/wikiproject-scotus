#! /usr/bin/env python

import datetime
import urllib

url = 'https://en.wikipedia.org/wiki/Succession_of_the_Justices_of_the_Supreme_Court_of_the_United_States?action=raw'

url_contents = urllib.urlopen(url).read()

associates = []
chiefs = []
for group in url_contents.split('|-'):
    if group.find(', ') != -1:
        if group.find('italic;') != -1:
            chief_justice = True
        else:
            chief_justice = False
        for line in group.strip().split('\n'):
            if line.startswith('| '):
                text = line.split('| ', 1)[1]
                text = text.replace('[[', '').replace(']]', '')
                if text.find('{{') == -1 and text != '\xe2\x80\x93':
                    if chief_justice:
                        chiefs.append(text)
                    else:
                        associates.append(text)

def chunkify(l, n):
    for i in range(0, len(l), n):
        yield l[i:i+n]

for i in list(chunkify(chiefs, 3)):
    print(i)

for i in list(chunkify(associates, 3)):
    print(i)
