# coding=utf-8

import re
import xml.etree.ElementTree as etree

nsmap = {'': 'http://www.mediawiki.org/xml/export-0.10/',
         'xsi': 'http://www.w3.org/2001/XMLSchema-instance'}
ns_list = ['0', '14']
ns_list = ['14']
# [[Category:自然科學]]
RE_CAT = re.compile(r'\[\[(Category|分類):(.+)\]\]', re.U | re.MULTILINE)


def fixtag(tag, ns=''):
    return '{' + nsmap[ns] + '}' + tag


def xpath(tags):
    if not isinstance(tags, (list, tuple)):
        tags = [tags]

    prefix_added = [fixtag(tag) for tag in tags]
    return '/'.join(prefix_added)


def extract_pages(fname):
    i = 0
    categories = set()
    for event, elem in etree.iterparse(fname, events=('end',)):
        i += 1
        # print(event, elem)
        if elem.tag == fixtag('page'):
            ns = elem.find(xpath('ns')).text
            if ns not in ns_list:
                continue

            title = elem.find(xpath('title')).text
            pid = elem.find(xpath('id')).text

            rev = elem.find(xpath('revision'))
            text = rev.find(xpath('text')).text

            if ns == '0':
                if text:
                    cats = RE_CAT.findall(text)
                    if cats:
                        print(title, pid, ns)
                        print(cats)
            elif ns == '14':
                # print(title, pid, ns)
                # if text:
                #     cats = RE_CAT.findall(text)
                #     print(cats)
                categories.add(title)

            # print('\n' * 1)

        # if i >= 10000:
        #     break
    return categories


if __name__ == '__main__':
    source = 'zh_classicalwiki-20170501.xml'
    categories = extract_pages(source)
    for c in categories:
        print(c)
