from meteor_reasoner.graphutil.temporal_dependency_graph import CycleFinder
from meteor_reasoner.utils.loader import load_program
from meteor_reasoner.classes.literal import BinaryLiteral

def test_cycle():
    rulepath = "/Users/dimmy/Desktop/MeTeoR/experiments/ISWC/programs/test.txt"
    with open(rulepath) as file:
        raw_program = file.readlines()
        program = load_program(raw_program)
        predicates = set()
        for rule in program:
            predicates.add(rule.head.get_predicate())
            for literal in rule.body:
                if isinstance(literal, BinaryLiteral):
                    predicates.add(literal.left_literal.get_predicate())
                    predicates.add(literal.right_literal.get_predicate())
                else:
                    predicates.add(literal.get_predicate())

    print("Number of predicates:", len(predicates))
    CF = CycleFinder(program=program)
    non_predicates = CF.get_non_recursive_predicates()

    print("Number of non-predicates:", len(non_predicates))
    for predicate in predicates:
        if predicate not in non_predicates:
              print(predicate)
