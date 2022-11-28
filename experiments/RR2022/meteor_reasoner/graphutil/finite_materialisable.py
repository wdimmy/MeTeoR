from meteor_reasoner.graphutil.graph_strengthening import *
from meteor_reasoner.graphutil.multigraph import *


def finite_materialisability(rules):
    paris = construct_pair(rules)
    G = TemporalDependencyGraph()
    for pair in paris:
        G.add_edge(pair[0], pair[1], [pair[2], pair[3]])
    return not G.is_cyclic()



