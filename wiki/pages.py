# coding=utf-8

import json
import re
import xml.etree.ElementTree as etree
import sys

from collections import defaultdict

nsmap = {'': 'http://www.mediawiki.org/xml/export-0.10/',
         'xsi': 'http://www.w3.org/2001/XMLSchema-instance'}

NS_CAT = '14'
NS_PAGE = '0'
ns_list = [NS_PAGE, NS_CAT]

# [[Category:自然科學]]
RE_CAT = re.compile(r'\[\[(Category|分類):(.+?)\]\]', re.U)


def fixtag(tag, ns=''):
    return '{' + nsmap[ns] + '}' + tag


def xpath(tags):
    if not isinstance(tags, (list, tuple)):
        tags = [tags]

    prefix_added = [fixtag(tag) for tag in tags]
    return '/'.join(prefix_added)


def extract_cat_title(cat):
    return cat.split(':')[1].strip()


def clean_title(title):
    return extract_cat_title(title) if ':' in title else title


def extract_categories(fname, n=10000):
    categories = {}
    i = 0
    for event, elem in etree.iterparse(fname, events=('end',)):
        i += 1
        if elem.tag == fixtag('page'):
            ns = elem.find(xpath('ns')).text
            if ns not in [NS_CAT]:
                continue

            title = elem.find(xpath('title')).text
            print(title)
            pid = elem.find(xpath('id')).text
            categories[extract_cat_title(title)] = pid

            # THIS is REQUIRED
            elem.clear()

        if i >= n:
            break

    return categories


def extract_pages(fname, categories, n=10000):
    inst_of = defaultdict(list)
    subcls_of = defaultdict(list)
    redirects = defaultdict()

    i = 0
    for event, elem in etree.iterparse(fname, events=('end',)):
        i += 1
        if elem.tag == fixtag('page'):
            ns = elem.find(xpath('ns')).text
            if ns not in ns_list:
                continue

            title = elem.find(xpath('title')).text
            if ns == NS_CAT:
                title = extract_cat_title(title)
            # pid = elem.find(xpath('id')).text

            redirect = elem.find(xpath('redirect'))
            if redirect is not None:
                redirects[title] = clean_title(redirect.attrib['title'])

            rev = elem.find(xpath('revision'))
            text = rev.find(xpath('text')).text
            cats = RE_CAT.findall(text) if text else []
            cats = [c.split('|')[0].strip() for label, c in cats]
            if ns == NS_PAGE:
                for c in cats:
                    if c in categories:
                        inst_of[title].append(c)
            elif ns == NS_CAT:
                for c in cats:
                    if c in categories:
                        subcls_of[title].append(c)

            # THIS is REQUIRED
            elem.clear()

        if i >= n:
            break

    return {"instance_of": inst_of,
            "subclass_of": subcls_of,
            "synonym_of": redirects}


if __name__ == '__main__':
    extract_cats = True
    source = 'zh_classicalwiki-20170501.xml'
    if len(sys.argv) == 2:
        source = sys.argv[1]
    elif len(sys.argv) == 3:
        source = sys.argv[1]
        extract_cats = sys.argv[2] == 'c'

    print(extract_cats)
    print(source)

    if extract_cats:
        categories = extract_categories(source, n=10**10)
        print(len(categories))
        json.dump(categories, open('cats.json', 'w'))
    else:
        categories = json.load(open('cats.json'))
        pages = extract_pages(source, categories, n=10**10)

        instance_of = pages['instance_of']
        print(len(instance_of))
        subclass_of = pages['subclass_of']
        print(len(subclass_of))
        synonym_of = pages['synonym_of']
        print(len(synonym_of))

        json.dump(pages, open('pages.json', 'w'))
