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
DISAM = '{{disambiguation}}'


class Page(object):
    def __init__(self, ns, pid, title, redirect_to=None, cats=None):
        self.ns = ns
        self.pid = pid
        self.title = title
        self.redirect_to = redirect_to
        self.cats = cats

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


def extract_title(page_text):
    page = etree.fromstring(page_text)
    ns = page.find('ns').text
    if ns not in ns_list:
        return None

    title = page.find('title').text
    if ns == NS_CAT:
        title = extract_cat_title(title)
    pid = page.find('id').text
    redirect = page.find('redirect')
    redirect_to = None
    if redirect is not None:
        redirect_to = clean_title(redirect.attrib['title'])

    page.clear()

    return Page(ns, pid, title, redirect_to)


def extract_titles(batch=1000):
    with open(source) as f:
        titles = defaultdict(dict)
        synonyms = defaultdict(dict)
        for page_lines in pages(f):
            page_text = ''.join(page_lines)
            page = extract_title(page_text)
            if page:
                titles[page.ns][page.title] = page.pid
                if page.redirected():
                    synonyms[page.ns][page.title] = page.redirect_to

                if page.is_page() and len(titles[NS_PAGE]) % batch == 0:
                    print(len(titles[NS_PAGE]))

        print(len(titles[NS_PAGE]))
        print(len(titles[NS_CAT]))
        print(len(synonyms[NS_PAGE]))
        dump_to_json(titles, 'titles.json')
        dump_to_json(synonyms, 'synonyms.json')


def extract_page(categories, page_text):
    page_xml = etree.fromstring(page_text)
    ns = page_xml.find('ns').text
    if ns not in ns_list:
        return None

    redirect = page_xml.find('redirect')
    if redirect is not None:
        return None

    title = page_xml.find('title').text
    if ns == NS_CAT:
        title = extract_cat_title(title)
    pid = page_xml.find('id').text

    rev = page_xml.find('revision')
    text = rev.find('text').text
    cats = RE_CAT.findall(text) if text else []
    cats = [c.split('|')[0].strip() for label, c in cats]

    page_xml.clear()

    page = Page(ns, pid, title, cats=[c for c in cats if c in categories])
    return page


def extract_pages(categories, batch=1000):
    synonyms = json.load(open('synonyms.json'))
    syn_cats = synonyms[NS_CAT]
    print(len(syn_cats))

    inst_of = defaultdict(list)
    subcls_of = defaultdict(list)

    with open(source) as f:
        for page_lines in pages(f):
            page_text = ''.join(page_lines)
            page = extract_page(categories, page_text)
            if page:
                title = page.title
                cats = page.cats

                for c in cats:
                    if c in syn_cats:
                        print(c)

                if cats:
                    if page.is_page():
                        inst_of[title] = cats
                    elif page.is_category():
                        subcls_of[title] = cats

                if (len(subcls_of) + len(inst_of)) % batch == 0:
                    print(len(subcls_of) + len(inst_of))

        print(len(subcls_of) + len(inst_of))
        result = {'instance_of': inst_of,
                  'subclass_of': subcls_of}
        dump_to_json(result, 'pages.json')


def find_titles(title, batch=1000 * 100):
    with open(source) as f:
        i = 0
        for page_lines in pages(f):
            page_text = ''.join(page_lines)
            page = extract_title(page_text)
            if page and title in page.title:
                print(page)
                print(page_text)
                print('\n' * 2)

            i += 1
            if i % batch == 0:
                print(i)


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

    extract_cats = False
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
        find_titles('Calyx')
    else:
        titles = json.load(open('titles.json'))
        categories = titles[NS_CAT]
        extract_pages(categories, batch=1000 * 100)
