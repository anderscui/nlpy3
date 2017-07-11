# coding=utf-8
import networkx as nx

g = nx.DiGraph()
g.add_edge(1, 2)
g.add_edge(1, 3)
g.add_edge(2, 3)
g.add_edge(3, 4)

print(g.nodes())
print(g.edges())

print(g.predecessors(1))
print(g.predecessors(3))

# parent nodes
print(nx.ancestors(g, 1))
# child nodes
print(nx.neighbors(g, 1))

print(nx.ancestors(g, 2))
print(nx.neighbors(g, 2))

print(nx.ancestors(g, 3))
print(nx.neighbors(g, 3))

g.remove_node(1)
print(g.nodes())
print(g.edges())
