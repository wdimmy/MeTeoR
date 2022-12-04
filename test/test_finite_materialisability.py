from meteor_reasoner.graphutil.graph_strengthening import *
from meteor_reasoner.graphutil.multigraph import *
from meteor_reasoner.classes import *
from meteor_reasoner.utils.loader import load_program


def test_finite_materialisability():

    rules = load_program(["A(X):-Boxplus[4]C(X)", "Boxplus[5]C(X):- A(X)"])
    rules = transformation(rules)
    print(rules[0])
    paris = construct_pair(rules)
    G = TemporalDependencyGraph()
    for pair in paris:
        G.add_edge(pair[0], pair[1], [pair[2], pair[3]])
    print(rule, ":")
    print(G.is_cyclic())


test_finite_materialisability()

