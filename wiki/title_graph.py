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
#
#
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
#
ptitles_main = {pitems_main[pid]['title']:pid for pid in pitems_main}
# ptitles_syn = {pitems_syn[pid]['title']:pid for pid in pitems_syn}


# graph

def generate_raw_graph():
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

    return g

# g = generate_raw_graph()
g = nx.read_gpickle('edges_01.gpickle')
print(g.number_of_nodes(), g.number_of_edges())
# nodes: 6633358, edges: 29922434


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


def bfs(G, source, visitor, max_level=16):
    visited = set()
    queue = deque([(source, 0)])
    while queue:
        node, level = queue.popleft()
        if node in visited or level > max_level:
            continue

        visitor(G, node, level)
        visited.add(node)
        for sub_node in G.successors(node):
            if sub_node not in visited:
                queue.append((sub_node, level+1))


def tag_level(G, n, level):
    G.node[n]['L'] = level


def tag_subnodes(cid, checked, tag, level=0, max_level=15):
    if cid in checked or level > max_level:
        return

    checked.add(cid)
    for n in g.successors(cid):
        g[cid][n][tag] = 1
        sn = str(n)
        if sn in citems:
            tag_subnodes(n, checked, tag, level+1, max_level)


def tag_subnodes_keep(cid, checked, tag, level=0, max_level=15):
    if cid in checked or level > max_level:
        return

    checked.add(cid)
    this_node_level = g.node[cid]['L']
    for n in g.successors(cid):
        g[cid][n][tag] = 1
        sn = str(n)
        if sn in citems:
            suc_node_level = g.node[n]['L']
            if this_node_level <= suc_node_level:
                tag_subnodes_keep(n, checked, tag, level+1, max_level)


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


# ROOT of interests
root_id = int(ctitles_main['Main topic classifications'])
# SUB NODE to keep
sci_id = int(ctitles_main['Science and technology'])
# MAX LEVEL to detect
MAX_LEVEL = 16

# tag levels of all nodes
bfs(g, root_id, tag_level, MAX_LEVEL)

# tag nodes to DELETE
excludes = [n for n in g.successors(root_id) if n != sci_id]
for cid in excludes:
    checked = set()
    tag_subnodes(cid, checked, 'D', 1, MAX_LEVEL)

# tag nodes to RESERVE/KEEP
includes = [sci_id]
for cid in includes:
    checked = set()
    tag_subnodes_keep(cid, checked, 'K', 1, MAX_LEVEL)

# collect nodes by the tags
g2 = nx.DiGraph()
checked = set()
collect_nodes(g2, root_id, checked, 0, MAX_LEVEL)
