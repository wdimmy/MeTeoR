from meteor_reasoner.graphutil.graph_strengthening import *
from meteor_reasoner.classes import *
import copy


def test_strengthening():
    head = Atom("C", tuple([Term("nan")]))
    literal_a = Literal(Atom("A", tuple([Term("X", "variable")])), [Operator("Boxminus", Interval(1, 2, False, False)),Operator("Boxminus", Interval(1, 2, False, False))])
    literal_b = Literal(Atom("B", tuple([Term("nan")])), [Operator("Diamondminus", Interval(0, 1, False, False))])
    literal_c = BinaryLiteral(copy.deepcopy(literal_a), copy.deepcopy(literal_b), Operator("Since", Interval(4, 5, False, False)))
    body = [literal_a, literal_b, literal_c]
    rule = Rule(head, body)
    print(rule)
    new_rule = transformation([rule])
    print(new_rule[0])


test_strengthening()