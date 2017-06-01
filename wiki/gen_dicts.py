# coding=utf-8
import json
from collections import deque

import networkx as nx
from toolz import take


def dump_to_json(obj, fname):
    json.dump(obj, open(fname, 'w'), ensure_ascii=False)


def is_main_item(item):
    return 'is_disam' not in item and 'redirect_to' not in item


items = json.load(open('items_trans.json'))
pitems = items['0']
citems = items['14']

citems_main = {}
citems_syn = {}
citems_disam = {}
for cid in citems:
    item = citems[cid]
    if 'redirect_to' in item:
        citems_syn[cid] = item
    elif 'is_disam' in item:
        citems_disam[cid] = item
    else:
        citems_main[cid] = item

pitems_main = {}
pitems_syn = {}
pitems_disam = {}
for pid in pitems:
    item = pitems[pid]
    if 'redirect_to' in item:
        pitems_syn[pid] = item
    elif 'is_disam' in item:
        pitems_disam[pid] = item
    else:
        pitems_main[pid] = item

# ctitles = {citems[cid]['title']:cid for cid in citems}
# ptitles = {pitems[pid]['title']:pid for pid in pitems}

ctitles_main = {citems_main[pid]['title']:pid for pid in citems_main}
# ctitles_syn = {citems_syn[pid]['title']:pid for pid in citems_syn}
ptitles_main = {pitems_main[pid]['title']:pid for pid in pitems_main}
# ptitles_syn = {pitems_syn[pid]['title']:pid for pid in pitems_syn}

g = nx.read_gpickle('edges.gpickle')
# g = nx.DiGraph()


def gen_zh_inst_dict():
    insts = {}
    for pid in pitems:
        sid = pid
        item = pitems[sid]
        if 'redirect_to' in item:
            redirect_to = item['redirect_to']
            if redirect_to in ptitles_main:
                sid = ptitles_main[redirect_to]
                item = pitems[sid]

        iid = int(sid)
        # is a core article
        if g.has_node(iid) and 'zh' in item:
            insts[item['zh'].lower()] = iid

    return insts


def gen_en_inst_dict():
    insts = {}
    for pid in pitems:
        sid = pid
        item = pitems[sid]
        if 'redirect_to' in item:
            redirect_to = item['redirect_to']
            if redirect_to in ptitles_main:
                sid = ptitles_main[redirect_to]
                item = pitems[sid]

        iid = int(sid)
        # is a core article
        if g.has_node(iid):
            insts[item['title'].lower()] = iid

    return insts


def gen_zh_cats_dict():
    cats = {}
    for cid in citems:
        sid = cid
        item = citems[sid]
        if 'redirect_to' in item:
            redirect_to = item['redirect_to']
            if redirect_to in ctitles_main:
                sid = ctitles_main[redirect_to]
                item = citems[sid]

        iid = int(sid)
        # is a core category
        if g.has_node(iid) and 'zh' in item:
            cats[item['zh'].lower()] = iid

    return cats


def gen_en_cats_dict():
    cats = {}
    for cid in citems:
        sid = cid
        item = citems[sid]
        if 'redirect_to' in item:
            redirect_to = item['redirect_to']
            if redirect_to in ctitles_main:
                sid = ctitles_main[redirect_to]
                item = citems[sid]

        iid = int(sid)
        # is a core article
        if g.has_node(iid):
            cats[item['title'].lower()] = iid

    return cats


def gen_zh_dict():
    zh_inst = gen_zh_inst_dict()
    zh_cats = gen_zh_cats_dict()
    # (545091, 97598)
    zh_dict = {'cat': zh_cats, 'inst': zh_inst}
    dump_to_json(zh_dict, 'zh_dict.json')


def gen_en_dict():
    en_inst = gen_en_inst_dict()
    en_cats = gen_en_cats_dict()
    en_dict = {'cat': en_cats, 'inst': en_inst}
    # (3827096, 837550)
    dump_to_json(en_dict, 'en_dict.json')
