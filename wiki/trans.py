# coding=utf-8
import json
import re


def capitalized(s):
    return s == s.capitalize()


def titled(s):
    return s == s.title()


def dump_to_json(obj, fname):
    json.dump(obj, open(fname, 'w'), ensure_ascii=False)


def trans_from_xlore(xlore, title):
    return xlore.get(title, '')


def trans_from_wiki_links(titles, link_langs, title):
    pid = titles.get(title, '')
    if not pid:
        return ''
    return link_langs.get(pid, '')


def trans_from_wikidata(wikidata, title):
    return wikidata.get(title, '')


def translate_title(xlore, ptitles, ctitles, link_langs, wikidata, title):
    trans = trans_from_xlore(xlore, title)
    if trans:
        return trans

    ptitle = trans_from_wiki_links(ptitles, link_langs, title)
    if ptitle:
        return ptitle

    ctitle = trans_from_wiki_links(ctitles, link_langs, title)
    if ctitle:
        return ctitle

    return trans_from_wikidata(wikidata, title)


def translate(title):
    return translate_title(xlore, ptitles, ctitles, langlinks, wikidata, title)


xlore = json.load(open('xlore.json'))
items = json.load(open('items.json'))
pitems = items['0']
citems = items['14']
ptitles = {}
for pid in pitems:
    ptitles[pitems[pid]['title']] = pid
ctitles = {}
for pid in citems:
    ctitles[citems[pid]['title']] = pid

langlinks = json.load(open('en_to_zh_langlinks.json'))
wikidata = json.load(open('en_to_zh_wikidata.json'))

# translate page items
for i in pitems:
    item = pitems[i]
    title = item['title']
    trans = translate(title)
    if trans:
        item['zh'] = trans

# translate category items
for i in citems:
    item = citems[i]
    title = item['title']
    trans = translate(title)
    if trans:
        item['zh'] = trans

# item_trans contains translation from xlore, langlinks and wikidata
items_trans = {'0': pitems, '14': citems}
dump_to_json(items_trans, 'items_trans.json')

# xlore: 424315 102984
# add langlinks: 577739 159577
# add wikidata: 820460 172964

re_cn = re.compile("[\u4E00-\u9FD5]+", re.U)


def filter_zh(enks):
    return [enk for enk in enks if not re_cn.search(enk)]


mba = json.load(open('mba_zh-CN_en.json'))
# mba2 = {}
# for k in mba:
#     enks = filter_zh(mba[k])
#     enks = [enk.replace('－', '-') for enk in enks]
#     if enks:
#         mba2[k] = enks

for k in mba:
    enks = mba[k]
    for enk in enks:
        if enk in ptitles:
            pid = ptitles[enk]
            item = pitems[pid]
            if 'zh' not in item:
                item['zh'] = k
                print(k, item['title'])
        if enk in ctitles:
            cid = ctitles[enk]
            item = citems[cid]
            if 'zh' not in item:
                item['zh'] = k
                print(k, item['title'])

for k in mba:
    enks = mba[k]
    for enk in enks:
        if enk not in ptitles and enk not in ctitles:
            enk = enk.capitalize()
            if enk in ptitles:
                pid = ptitles[enk]
                item = pitems[pid]
                if 'zh' not in item:
                    item['zh'] = k
                    print(k, item['title'])
            if enk in ctitles:
                cid = ctitles[enk]
                item = citems[cid]
                if 'zh' not in item:
                    item['zh'] = k
                    print(k, item['title'])
