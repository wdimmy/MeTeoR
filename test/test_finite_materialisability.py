from meteor_reasoner.graphutil.graph_strengthening import *
from meteor_reasoner.graphutil.multigraph import *
from meteor_reasoner.utils.loader import load_program

# MTL-acyclic must be a finitely materialisable program,but not every finitely materialisable program is MTL-acyclic


def test_finite_materialisability():
    rules = load_program("./data/finite_program.txt")
    rules = transformation(rules)
    paris = construct_pair(rules)
    G = TemporalDependencyGraph()
    for pair in paris:
        G.add_edge(pair[0], pair[1], [pair[2], pair[3]])

    print("The input program is MTL-acyclic:", G.is_cyclic())

test_finite_materialisability()

