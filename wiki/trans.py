# coding=utf-8
import json


def trans_from_xlore(xlore, title):
    return xlore.get(title, '')


def trans_from_wiki_links(titles, link_langs, title):
    pid = titles.get(title, '')
    if not pid:
        return ''
    return link_langs.get(pid, '')


def trans_from_wikidata(wikidata, title):
    return wikidata.get(title, '')


def transfer_title(xlore, ptitles, ctitles, link_langs, wikidata, title):
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


def transfer(title):
    return transfer_title(xlore, ptitles, ctitles, langlinks, wikidata, title)


xlore = json.load(open('xlore.json'))
titles = json.load(open('titles.json'))
ptitles = titles['0']
ctitles = titles['14']
langlinks = json.load(open('en_to_zh_langlinks.json'))
wikidata = json.load(open('en_to_zh_wikidata.json'))

pi = 0
for k in ptitles:
    trans = transfer(k)
    if trans:
        pi += 1

ci = 0
for k in ctitles:
    trans = transfer(k)
    if trans:
        ci += 1

print(pi, ci)

# xlore: 424315 102984
# add langlinks: 577739 159577
# add wikidata: 820460 171294
