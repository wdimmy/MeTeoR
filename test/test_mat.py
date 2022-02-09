from meteor_reasoner.utils.operate_dataset import *
from meteor_reasoner.materialization.materialize import *
import time

def test_naive_mat():
    D = defaultdict(lambda: defaultdict(list))
    D["A"][tuple([Term("mike")])] = [Interval(3, 4, False, False), Interval(6, 10, True, True)]
    D["C"][tuple([Term("mike"), Term("jack")])] = [Interval(3, 4, False, False), Interval(6, 10, True, True)]
    D["B"][tuple([Term("nan")])] = [Interval(2, 8, False, False)]
    D_index = defaultdict(lambda: defaultdict(list))
    build_index(D, D_index)

    head = Atom("C", tuple([Term("nan")]))
    literal_a = Literal(Atom("A", tuple([Term("X", "variable")])), [Operator("Boxminus", Interval(1, 2, False, False))])
    literal_b = Literal(Atom("B", tuple([Term("nan")])), [Operator("Diamondminus", Interval(0, 1, False, False))])
    body = [literal_a, literal_b]
    rule = Rule(head, body)
    Program = [rule]

    start_time = time.time()
    flag,_ = materialize(D, Program, K=10)
    end_time = time.time()
    print("flag:", flag)
    print("naive run time:", end_time-start_time)
    print("Naive:")
    print_dataset(D)


def test_seminaive_mat():
    D = defaultdict(lambda: defaultdict(list))
    D["A"][tuple([Term("mike")])] = [Interval(3, 4, False, False), Interval(6, 10, True, True)]
    D["C"][tuple([Term("mike"), Term("jack")])] = [Interval(3, 4, False, False), Interval(6, 10, True, True)]
    D["B"][tuple([Term("nan")])] = [Interval(2, 8, False, False)]
    D_index = defaultdict(lambda: defaultdict(list))
    build_index(D, D_index)

    head = Atom("C", tuple([Term("nan")]))
    literal_a = Literal(Atom("A", tuple([Term("X", "variable")])), [Operator("Boxminus", Interval(1, 2, False, False))])
    literal_b = Literal(Atom("B", tuple([Term("nan")])), [Operator("Diamondminus", Interval(0, 1, False, False))])
    body = [literal_a, literal_b]
    rule = Rule(head, body)
    Program = [rule]

    start_time = time.time()
    flag, _ = materialize(D, Program, seminaive=True, K=10)
    end_time = time.time()
    print("flag:", flag)
    print("seminaive run time:", end_time - start_time)
    print("Naive:")
    print_dataset(D)
