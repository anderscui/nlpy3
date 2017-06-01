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

# ctitles = {citems[cid]['title']:cid for cid in citems}

# ptitles = {pitems[pid]['title']:pid for pid in pitems}

ctitles_main = {citems_main[pid]['title']:pid for pid in citems_main}
# ctitles_syn = {citems_syn[pid]['title']:pid for pid in citems_syn}
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

g = nx.read_gpickle('edges_01.gpickle')
print(g.number_of_nodes(), g.number_of_edges())

# nodes: 6507250, edges: 27857208
# nodes: 6633360, edges: 29922434


def show_cat_parents(title):
    if title in ctitles_main:
        cid = int(ctitles_main[title])
        for n in g.predecessors(cid):
            print(citems[str(n)])


def show_cat_children(g, title):
    if title in ctitles_main:
        cid = int(ctitles_main[title])
        for n in g.successors(cid):
            sn = str(n)
            if sn in citems:
                print(citems[sn])
            else:
                print(pitems[sn])


def gather_cats_contents(titles):
    contents = set()
    for title in titles:
        if title in ctitles_main:
            cid = int(ctitles_main[title])
            gather_cat_contents(cid, contents)
    return contents


def gather_cat_contents(cid, checked, level=0, max_level=3):
    # already checked.
    if level > max_level:
        return

    checked.add(cid)
    for n in g.successors(cid):
        sn = str(n)
        if sn in citems:
            gather_cat_contents(n, checked, level+1, max_level)
        else:
            checked.add(n)


def show_cat_contents(cid, checked, excluded, level=0, max_level=15):
    # already checked.
    if cid in checked or level > max_level:
        return

    checked.add(cid)
    for n in g.successors(cid):
        sn = str(n)
        if sn in citems:
            show_cat_contents(n, checked, excluded, level+1, max_level)
        else:
            checked.add(n)


def show_cat_by_title(title):
    found = set()
    excluded = set()
    if title in ctitles_main:
        cid = int(ctitles_main[title])
        show_cat_contents(cid, found, excluded)
    return found


root_id = int(ctitles_main['Main topic classifications'])
sci_id = int(ctitles_main['Science and technology'])


def bfs(G, source, visitor, max_level=16):
    visited = set()
    queue = [(source, 0)]
    while queue:
        node, level = queue.pop(0)
        if level > max_level:
            continue

        visitor(G, node, level)
        visited.add(node)
        for sub_node in G.successors(node):
            if (sub_node not in visited) and (sub_node not in queue):
                queue.append((sub_node, level+1))

    visited = None


def tag_level(G, n, level):
    G.node[n]['L'] = level


bfs(g, root_id, tag_level)


def tag_subnodes(cid, checked, tag, level=0, max_level=15):
    if cid in checked or level > max_level:
        return

    checked.add(cid)
    for n in g.successors(cid):
        g[cid][n][tag] = 1
        sn = str(n)
        if sn in citems:
            tag_subnodes(n, checked, tag, level+1, max_level)


excludes = [n for n in g.successors(root_id) if n != sci_id]
for cid in excludes:
    checked = set()
    tag_subnodes(cid, checked, 'D', 0, 15)


includes = [sci_id]
for cid in includes:
    checked = set()
    tag_subnodes(cid, checked, 'K', 0, 15)


def collect_nodes(g2, cid, checked, level=0, max_level=16):
    # already checked.
    if cid in checked or level > max_level:
        return

    checked.add(cid)
    for n in g.successors(cid):
        if 'D' not in g[cid][n] or 'K' in g[cid][n]:
            g2.add_edge(cid, n)

        sn = str(n)
        if sn in citems:
            collect_nodes(g2, n, checked, level + 1, max_level)


g2 = nx.DiGraph()
checked = set()
collect_nodes(g2, root_id, checked, 0, 16)
