from meteor_reasoner.materialization.apply import *
from meteor_reasoner.materialization.index_build import *
from meteor_reasoner.utils.parser import *


def test_apply():
    D = defaultdict(lambda: defaultdict(list))
    D["A"][tuple([Term("mike")])] = [Interval(3, 4, False, False), Interval(6, 10, True, True)]
    D["C"][tuple([Term("mike"), Term("jack")])] = [Interval(3, 4, False, False), Interval(6, 10, True, True)]
    D["B"][tuple([Term("nan")])] = [Interval(2, 8, False, False)]
    D_index = defaultdict(lambda: defaultdict(list))
    build_index(D, D_index)

    raw_literal = "BSince[2,3]Diamondminus[1,2]Boxminus[1,2]A(mike)"
    literal = parse_literal(raw_literal)
    print(str(literal))

    T = apply(literal, D)
    print([str(interval) for interval in T])



