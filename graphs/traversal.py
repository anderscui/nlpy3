# coding=utf-8
from collections import deque

import networkx as nx

# CREATE a graph
g = nx.DiGraph()

# ADD node(s)
g.add_edges_from([(1, 2), (1, 3), (2, 4), (2, 5), (3, 6), (6, 7), (7, 3)])
print(g.has_node(1))
print(g.has_node(10))
# print(g.nodes())
# print(g.edges())


def bfs(G, source, visitor):
    visited = set()
    queue = deque([(source, 0)])
    while queue:
        node, level = queue.popleft()
        visitor(G, node, level)
        visited.add(node)
        for sub_node in G.successors(node):
            if sub_node not in visited:
                queue.append((sub_node, level+1))


def tag_level(G, n, level):
    G.node[n]['L'] = level


if __name__ == '__main__':
    bfs(g, 1, tag_level)
    bfs(g, 1, lambda G, n, l: print(n, G.node[n]['L']))
