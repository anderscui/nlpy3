# coding=utf-8
import json

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
#
#
# pitems_main = {}
# pitems_syn = {}
# pitems_disam = {}
# for pid in pitems:
#     item = pitems[pid]
#     if 'redirect_to' in item:
#         pitems_syn[pid] = item
#     elif 'is_disam' in item:
#         pitems_disam[pid] = item
#     else:
#         pitems_main[pid] = item

ctitles = {citems[cid]['title']:cid for cid in citems}


ptitles = {pitems[pid]['title']:pid for pid in pitems}

ctitles_main = {citems_main[pid]['title']:pid for pid in citems_main}
ctitles_syn = {citems_syn[pid]['title']:pid for pid in citems_syn}
#
# ptitles_main = {pitems_main[pid]['title']:pid for pid in pitems_main}
# ptitles_syn = {pitems_syn[pid]['title']:pid for pid in pitems_syn}

# graph
g = nx.DiGraph()
# add sub class edges
for cid in citems:
    item = citems[cid]
    if is_main_item(item):
        sup_classes = item.get('subcls_of', [])
        for sup_cls in sup_classes:
            if sup_cls in ctitles_main:
                g.add_edge(int(ctitles_main[sup_cls]), int(cid))

# add inst edges
for pid in pitems:
    item = pitems[pid]
    if is_main_item(item):
        classes = item.get('inst_of', [])
        for cls in classes:
            if cls in ctitles_main:
                g.add_edge(int(ctitles_main[cls]), int(pid))

# nodes: 6738454, edges: 28375220
# nodes: 6507250, edges: 27857208

to_remove_cats = ['Reference works', 'Library science', 'Places', 'Events',
                  'People', 'Personal life', 'Self', 'Surnames',
                  'Thought', ]


def tag_del_cls_node(graph, cid, level=0):
    if level > 100:
        print('overflow...')
        return
    print(citems[str(cid)])

    if graph.has_node(cid):
        for i in graph.successors(cid):
            e = graph.edge[cid][i]
            # not tagged
            if 'D' not in e:
                e['D'] = 1
                si = str(i)
                if si in citems:
                    tag_del_cls_node(graph, i, level + 1)


def tag_del_cls_node_by_title(graph, ctitles, title):
    if title in ctitles:
        tag_del_cls_node(graph, int(ctitles[title]))


i = 0
for n in g.nodes():
    if len(g.predecessors(n)) == 0 and len(g.successors(n)) == 0:
        i += 1

i = 0
for e in take(10, g.edges_iter()):
    edge = g[e[0]][e[1]]
    if 'D' in edge:
        i += 1
