# coding=utf-8

import networkx as nx

g = nx.read_gpickle('graph.gpickle')
print(len(g.nodes()))
