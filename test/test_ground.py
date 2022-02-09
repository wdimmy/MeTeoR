from collections import defaultdict
from meteor_reasoner.classes.term import *
from meteor_reasoner.classes.literal import *
from meteor_reasoner.classes.atom import *
from meteor_reasoner.materialization.ground import *


def test_ground():
    D = defaultdict(lambda: defaultdict(list))
    D["A"][tuple([Term("mike")])] = [Interval(3, 4, False, False), Interval(6, 10, True, True)]
    D["C"][tuple([Term("mike"), Term("jack")])] = [Interval(3, 4, False, False), Interval(6, 10, True, True)]
    D["B"][tuple([Term("nan")])] = [Interval(2, 8, False, False)]

    literal_a = Literal(Atom("A", tuple([Term("X", "variable")])), [Operator("Boxminus", Interval(1, 2, False, False))])

    for entity, intervals, delta in ground_unary_literal(literal=literal_a, context=dict(), D=D):
        assert ["mike"] == [str(item) for item in entity]
        assert ['[3,4]', '(6,10)'] == [str(item) for item in intervals]

    literal_b = Literal(Atom("B", tuple([Term("nan")])), [Operator("Diamondminus", Interval(0, 1, False, False))])
    for entity, intervals, delta in ground_unary_literal(literal=literal_b, context=dict(), D=D):
        assert ["nan"] == [str(item) for item in entity]
        assert ['[2,8]'] == [str(item) for item in intervals]

    literal_c = Literal(Atom("A", tuple([Term("mike")])), [Operator("Diamondminus", Interval(0, 1, False, False))])
    for entity, intervals, delta in ground_unary_literal(literal=literal_c, context=dict(), D=D):
        assert ["mike"] == [str(item) for item in entity]
        assert ['[3,4]', '(6,10)'] == [str(item) for item in intervals]

    literal_d = Literal(Atom("C", tuple([Term("mike"), Term("X", "variable")])), [Operator("Diamondminus", Interval(0, 1, False, False))])
    for entity, intervals, delta in ground_unary_literal(literal=literal_d, context=dict(), D=D):
        assert ['mike', 'jack'] == [str(item) for item in entity]
        assert ['[3,4]', '(6,10)'] == [str(item) for item in intervals]

