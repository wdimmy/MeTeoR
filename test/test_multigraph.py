from meteor_reasoner.graphutil.multigraph import TemporalDependencyGraph


def test_multigraph():
    G = TemporalDependencyGraph()
    G.add_edge("Vaccinated", "Immune", [21,28])
    G.add_edge("NoSympt", "Immune", [0, 10])
    G.add_edge("Infected", "Immune", [10, 183])
    G.add_edge("NegTest", "Immune", [0, 0])
    G.add_edge("Immune", "NegTest", [0, 5])

    print(G.is_cyclic())

    G = TemporalDependencyGraph()
    G.add_edge("NotInf", "Susc", [0,183])
    G.add_edge("NotVacc", "Susc", [0, 365])
    G.add_edge("FirstSympt", "GetsInf", [5, 5])
    G.add_edge("GetsInf", "FirstSympt", [-5, -5])
    G.add_edge("Over65", "FirstSympt", [0, 0])
    G.add_edge("NoMask", "GetsInf", [1/12, 1/12])
    print(G.is_cyclic())



test_multigraph()