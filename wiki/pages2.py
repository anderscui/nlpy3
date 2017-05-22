# coding=utf-8

import glob
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


class Page(object):
    def __init__(self, ns, pid, title):
        self.ns = ns
        self.pid = pid
        self.title = title


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


def extract_page(categories, page_text):
    inst_of = []
    subcls_of = []
    redirect_to = None

    page = etree.fromstring(page_text)
    ns = page.find('ns').text
    if ns not in ns_list:
        return None

    title = page.find('title').text
    if ns == NS_CAT:
        title = extract_cat_title(title)
    # pid = page.find('id').text

    redirect = page.find('redirect')
    if redirect is not None:
        redirect_to = clean_title(redirect.attrib['title'])

    rev = page.find('revision')
    text = rev.find('text').text
    cats = RE_CAT.findall(text) if text else []
    cats = [c.split('|')[0].strip() for label, c in cats]
    if ns == NS_PAGE:
        inst_of = [c for c in cats if c in categories]
    elif ns == NS_CAT:
        subcls_of = [c for c in cats if c in categories]

    page.clear()
    page = None

    return (title, (inst_of, subcls_of, redirect_to))


def extract_title(page_text):
    page = etree.fromstring(page_text)
    ns = page.find('ns').text
    if ns not in ns_list:
        return None

    title = page.find('title').text
    if ns == NS_CAT:
        title = extract_cat_title(title)
    pid = page.find('id').text

    page.clear()

    return Page(ns, pid, title)


def extract_titles(batch=1000):
    with open(source) as f:
        batch_no = 1
        total = 0
        titles = defaultdict(dict)
        for page_lines in pages(f):
            page_text = ''.join(page_lines)

            page = extract_title(page_text)
            if page:
                titles[page.ns][page.title] = page.pid

                if len(titles[NS_PAGE]) >= batch:
                    total += len(titles[NS_PAGE])
                    print(total)
                    dump_to_json(titles, 'titles_{}.json'.format(batch_no))
                    titles = defaultdict(dict)
                    batch_no += 1

        if titles:
            total += len(titles[NS_PAGE])
            print(total)
            dump_to_json(titles, 'titles_{}.json'.format(batch_no))


def extract_pages(categories, batch=1000):
    inst_of = defaultdict(list)
    subcls_of = defaultdict(list)
    redirects = defaultdict()

    with open(source) as f:
        batch_no = 1
        total = 0

        for page_lines in pages(f):
            page_text = ''.join(page_lines)
            page_rel = extract_page(categories, page_text)
            if page_rel:
                title, rel = page_rel
                inst, subcls, redirect_to = rel
                if inst:
                    inst_of[title] = inst
                if subcls:
                    subcls_of[title] = subcls
                if redirect_to:
                    redirects[title] = redirect_to

                if len(inst_of) >= batch:
                    total += len(inst_of)
                    print(total)

                    obj = {'instance_of': inst_of,
                           'subclass_of': subcls_of,
                           'synonym_of': redirects}
                    dump_to_json(obj, 'pages_{}.json'.format(batch_no))

                    inst_of = defaultdict(list)
                    subcls_of = defaultdict(list)
                    redirects = defaultdict()
                    batch_no += 1

        if inst_of or subcls_of or redirects:
            total += len(inst_of)
            print(total)
            obj = {'instance_of': inst_of,
                   'subclass_of': subcls_of,
                   'synonym_of': redirects}
            dump_to_json(obj, 'pages_{}.json'.format(batch_no))


def check_page_count():
    with open(source) as f:
        assert len(list(pages(f))) == 65556


def combine_titles():
    all_titles = {NS_CAT: {}, NS_PAGE: {}}
    for fname in glob.glob('./titles_*.json'):
        with open(fname) as f:
            print(fname)
            titles = json.load(f)
            if NS_CAT in titles:
                all_titles[NS_CAT].update(titles[NS_CAT])
            else:
                print('cat not found')
            if NS_PAGE in titles:
                all_titles[NS_PAGE].update(titles[NS_PAGE])
            else:
                print('page not found')

    dump_to_json(all_titles, 'titles.json')


def combine_pages():
    all_pages = {"instance_of": defaultdict(list), "subclass_of": defaultdict(list), "synonym_of": defaultdict()}
    for fname in glob.glob('./pages_*.json'):
        with open(fname) as f:
            pages = json.load(f)
            all_pages['instance_of'].update(pages['instance_of'])
            all_pages['subclass_of'].update(pages['subclass_of'])
            all_pages['synonym_of'].update(pages['synonym_of'])
            print(fname)
    print(len(all_pages))
    dump_to_json(all_pages, 'pages.json')


if __name__ == '__main__':
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

    if extract_cats:
        # extract_categories(1000*10)
        extract_titles(1000 * 100)
    else:
        print('combining titles...')
        combine_titles()
        print('combining title done...')
        titles = json.load(open('titles.json'))
        categories = titles[NS_CAT]
        extract_pages(categories, batch=1000 * 100)
        # print('combining pages')
        # combine_pages()
