# coding=utf-8

import networkx as nx

# CREATE a graph
g = nx.Graph()

# ADD node(s)
g.add_node(1)
g.add_nodes_from([2, 3])
print(g.nodes())

# h = nx.path_graph(10)
# g.add_nodes_from(h)
# # or
# g.add_node(h)

# ADD edge(s)
g.add_edge(1, 2)
e = (2, 3)
g.add_edge(*e)

print(g.edges())

# REMOVE nodes or edges by g.remove_*, or g.clear
g.clear()

g.add_edges_from([(1, 2), (1, 3)])
g.add_node(1)
g.add_edge(1, 2)
g.add_node("spam")
g.add_nodes_from("spam")

print(g.number_of_nodes(), g.number_of_edges())
print(g.neighbors(1))

