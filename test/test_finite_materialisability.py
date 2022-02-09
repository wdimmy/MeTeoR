from meteor_reasoner.graphutil.graph_strengthening import *
from meteor_reasoner.graphutil.multigraph import *
from meteor_reasoner.classes import *
import copy


def test_finite_materialisability():
    head = Atom("C", tuple([Term("nan")]))
    literal_a = Literal(Atom("A", tuple([Term("X", "variable")])), [Operator("Boxminus", Interval(1, 2, False, False)),
                                                                    Operator("Boxminus", Interval(1, 2, False, False))])
    literal_b = Literal(Atom("B", tuple([Term("nan")])), [Operator("Diamondminus", Interval(0, 1, False, False))])
    literal_c = BinaryLiteral(copy.deepcopy(literal_a), copy.deepcopy(literal_b),
                              Operator("Until", Interval(4, 5, False, False)))

    body = [literal_a, literal_b, literal_c]
    rule = Rule(head, body)
    rules = transformation([rule])
    print(rules[0])
    paris = construct_pair(rules)
    G = TemporalDependencyGraph()
    for pair in paris:
        G.add_edge(pair[0], pair[1], [pair[2], pair[3]])
    print(rule, ":")
    print(G.is_cyclic())


test_finite_materialisability()

