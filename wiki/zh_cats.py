# coding=utf-8
import json as j
import re
from collections import deque

import networkx as nx
from toolz import take
from opencc import OpenCC

openCC = OpenCC('tw2sp')
RE_WHITESPACE = re.compile(r'(\s)+', re.U)


def convert(ch):
    return openCC.convert(ch)


def transform_whitespace(text):
    return RE_WHITESPACE.sub('_', text)


def preprocess(text):
    return transform_whitespace(convert(text))


cats_raw = j.load(open('zh_cats.json'))

# convert to zh_cn, remove whitespace
cats = {}
for c_id in cats_raw:
    cat = cats_raw[c_id]
    title = preprocess(cat['title'])
    sup_cats = cat.get('cats', [])
    new_sups = [preprocess(sc) for sc in sup_cats]
    cats[c_id] = {'title': title, 'cats': new_sups}
j.dump(cats, open('zh_cn_cats.json', 'w'))

# generate title_ids
title_ids = {}
for c_id in cats:
    title_ids[cats[c_id]['title']] = c_id
j.dump(title_ids, open('zh_cn_cats_title_ids.json', 'w'))

# generate graph
g = nx.DiGraph()
for c_id in cats:
    cat = cats[c_id]
    title = cat['title']
    sup_cats = cat.get('cats', [])
    for sup_cat in sup_cats:
        if sup_cat in title_ids:
            g.add_edge(sup_cat, title)

nx.write_gpickle(g, 'zh_cn_cats_edges.gpickle')

# # top nodes
# top_nodes = set()
# for n in g.nodes():
#     if len(g.predecessors(n)) == 0:
#         top_nodes.add(n)


def bfs(G, root, visitor, max_level=3):
    visited = set()
    new_g = nx.DiGraph()
    queue = deque([(root, 0)])
    while queue:
        node, level = queue.popleft()
        if node in visited:
            print('visited', node)
            continue
        if level >= max_level:
            # print('level', level)
            continue

        # visitor(G, node, level)
        visited.add(node)
        for sub_node in G.successors(node):
            if sub_node not in visited:
                new_g.add_edge(node, sub_node)
                queue.append((sub_node, level+1))
    return visited, new_g

_, ng = bfs(g, '页面分类', None, 8)
nx.write_gpickle(ng, 'zh_cn_cats_edges2.gpickle')
