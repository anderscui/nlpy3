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
RE_CATNAV = re.compile(r'{{Catnav\|(.+?)\}\}', re.U)
DISAM = ['{{disambiguation}}', '{{disambig}}', '{{dab}}', '{{disamb}}']


class Page(object):
    def __init__(self, ns, pid, title, redirect_to=None, cats=None, is_disam=False, catnavs=None):
        self.ns = ns
        self.pid = pid
        self.title = title
        self.redirect_to = redirect_to
        self.cats = cats
        self.is_disam = is_disam
        self.catnavs = catnavs

    def is_page(self):
        return self.ns == NS_PAGE

    def is_category(self):
        return self.ns == NS_CAT

    def redirected(self):
        return self.redirect_to is not None


def dump_to_json(obj, fname):
    json.dump(obj, open(fname, 'w'), ensure_ascii=False)


def extract_cat_title(cat):
    return cat.split(':')[1].strip()


def clean_title(title):
    return extract_cat_title(title) if ':' in title else title


def pages(input):
    """
    Scans input extracting pages.
    """
    page = []
    in_page = False
    for line in input:
        if not in_page:
            striped = line.strip()
            if striped == '<page>':
                in_page = True
                page.append(line)
            else:
                continue
        else:
            page.append(line)
            striped = line.strip()
            if striped == '</page>':
                yield page
                page = []
                in_page = False


def extract_item(page_text):
    page = etree.fromstring(page_text)
    ns = page.find('ns').text
    if ns not in ns_list:
        return None
    else:
        return 1


def extract_wiki_item(page_text):
    page_xml = etree.fromstring(page_text)
    ns = page_xml.find('ns').text
    if ns not in ns_list:
        return None

    title = page_xml.find('title').text
    if ns == NS_CAT:
        title = extract_cat_title(title)
    pid = page_xml.find('id').text
    redirect = page_xml.find('redirect')
    redirect_to = None
    if redirect is not None:
        redirect_to = clean_title(redirect.attrib['title'])

    rev = page_xml.find('revision')
    text = rev.find('text').text
    if text is None:
        return None

    # cats = RE_CAT.findall(text)
    # cats = [c.split('|')[0].strip() for label, c in cats]
    # is_disam = any(disam in text for disam in DISAM)

    catnavs = RE_CATNAV.findall(text)

    page_xml.clear()

    page = Page(ns, int(pid), title, redirect_to, cats=None, is_disam=None, catnavs=catnavs)
    return page


def extract_wiki_items(batch=1000):
    items = defaultdict(dict)

    with open(source) as f:
        for page_lines in pages(f):
            page_text = ''.join(page_lines)
            item = extract_wiki_item(page_text)
            if not item:
                continue

            obj = {'title': item.title}
            if item.redirected():
                obj['redirect_to'] = item.redirect_to
            if item.catnavs:
                obj['catnavs'] = item.catnavs

            items[item.ns][item.pid] = obj

            if (len(items[NS_PAGE]) + len(items[NS_CAT])) % batch == 0:
                print(len(items[NS_PAGE]) + len(items[NS_CAT]))

        print(len(items[NS_PAGE]) + len(items[NS_CAT]))
        dump_to_json(items, 'items.json')


def check_page_count():
    with open(source) as f:
        assert len(list(pages(f))) == 65556


def check_item_count():
    with open(source) as f:
        i = 0
        for page_lines in pages(f):
            page_text = ''.join(page_lines)
            page = extract_item(page_text)
            if page:
                i += 1
        # assert i == (1694+10307)
        print(i)


if __name__ == '__main__':

    # stats
    # all pages/titles: 14766698
    # main-titles: 6427217
    # synonyms: 7778441, csyn: 73

    # round 2
    # items: 14766690

    extract_cats = True
    source = 'zh_classicalwiki-20170501.xml'
    if len(sys.argv) == 2:
        source = sys.argv[1]
    elif len(sys.argv) == 3:
        source = sys.argv[1]
        extract_cats = sys.argv[2] == 'c'

    print(extract_cats)
    print(source)

    # check_page_count()
    # check_item_count()

    if extract_cats:
        # extract_titles(1000 * 100)
        extract_wiki_items(1000 * 100)
    else:
        titles = json.load(open('titles.json'))
        categories = titles[NS_CAT]
        # extract_pages(categories, batch=1000 * 100)
