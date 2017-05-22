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

tagRE = re.compile(r'(.*?)<(/?\w+)[^>]*?>(?:([^<]*)(<.*?>)?)?')
keyRE = re.compile(r'key="(\d*)"')


def extract_cat_title(cat):
    return cat.split(':')[1].strip()


def clean_title(title):
    return extract_cat_title(title) if ':' in title else title


def pages_from(input):
    """
    Scans input extracting pages.
    :return: (id, revid, title, namespace key, page), page is a list of lines.
    """
    # we collect individual lines, since str.join() is significantly faster
    # than concatenation
    page = []
    id = None
    ns = '0'
    last_id = None
    revid = None
    inText = False
    redirect = False
    title = None
    for line in input:
        if '<' not in line:  # faster than doing re.search()
            if inText:
                page.append(line)
            continue
        m = tagRE.search(line)
        if not m:
            continue
        tag = m.group(2)
        if tag == 'page':
            page = []
            redirect = False
        elif tag == 'id' and not id:
            id = m.group(3)
        elif tag == 'id' and id:
            revid = m.group(3)
        elif tag == 'title':
            title = m.group(3)
        elif tag == 'ns':
            ns = m.group(3)
        elif tag == 'redirect':
            redirect = True
        elif tag == 'text':
            if m.lastindex == 3 and line[m.start(3)-2] == '/': # self closing
                # <text xml:space="preserve" />
                continue
            inText = True
            line = line[m.start(3):m.end(3)]
            page.append(line)
            if m.lastindex == 4:  # open-close
                inText = False
        elif tag == '/text':
            if m.group(1):
                page.append(m.group(1))
            inText = False
        elif inText:
            page.append(line)
        elif tag == '/page':
            if id != last_id and not redirect:
                yield (id, revid, title, ns, page)
                last_id = id
                ns = '0'
            id = None
            revid = None
            title = None
            page = []


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


def extract_category(category_page):
    page = etree.fromstring(category_page)
    ns = page.find('ns').text
    # print(ns)
    if ns not in [NS_CAT]:
        return None

    title = page.find('title').text
    pid = page.find('id').text
    page.clear()
    page = None

    return (extract_cat_title(title), int(pid))


def extract_categories(batch=1000):
    with open(source) as f:
        batch_no = 1
        total = 0
        categories = {}
        for page_lines in pages(f):
            page_text = ''.join(page_lines)

            cat = extract_category(page_text)
            if cat:
                title, cid = cat
                categories[title] = cid

                if len(categories) >= batch:
                    total += len(categories)
                    print(total)
                    json.dump(categories, open('cats_{}.json'.format(batch_no), 'w'))
                    categories = {}
                    batch_no += 1

        if categories:
            total += len(categories)
            print(total)
            json.dump(categories, open('cats_{}.json'.format(batch_no), 'w'))


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
                    break

    return {"instance_of": inst_of,
            "subclass_of": subcls_of,
            "synonym_of": redirects}


def check_page_count():
    with open(source) as f:
        assert len(list(pages(f))) == 65556


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

    # check_page_count()

    if extract_cats:
        extract_categories(1000*100)
    else:
        categories = json.load(open('cats.json'))
        pages = extract_pages(categories, batch=10 ** 10)

        instance_of = pages['instance_of']
        print(len(instance_of))
        subclass_of = pages['subclass_of']
        print(len(subclass_of))
        synonym_of = pages['synonym_of']
        print(len(synonym_of))

        json.dump(pages, open('pages.json', 'w'))
