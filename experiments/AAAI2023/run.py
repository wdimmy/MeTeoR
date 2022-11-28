from meteor_reasoner.utils.loader import *
from meteor_reasoner.canonical.utils import find_periods, fact_entailment
from meteor_reasoner.canonical.canonical_representation import CanonicalRepresentation
import argparse
from meteor_reasoner.materialization.coalesce import coalescing_d
from meteor_reasoner.materialization.index_build import build_index

parser = argparse.ArgumentParser()
parser.add_argument("--datapath", default="demos/case_13_dataset.txt", type=str)
parser.add_argument("--rulepath", default="demos/case_13_program.txt", type=str)
parser.add_argument("--fact", type=str)
args = parser.parse_args()


if __name__ == "__main__":
    # load the dataset and the program
    program = load_program(args.rulepath)
    predicates = set()
    for rule in program:
        predicates.add(rule.head.get_predicate())
        for literal in rule.body:
            if isinstance(literal, BinaryLiteral):
                predicates.add(literal.left_literal.get_predicate())
                predicates.add(literal.right_literal.get_predicate())
            else:
                predicates.add(literal.get_predicate())
    D = load_dataset(args.datapath)
    coalescing_d(D)
    D_index = build_index(D)
    if args.fact is not None:
        predicate, entity, interval = parse_str_fact(args.fact)
        fact = Atom(predicate, entity, interval)
    else:
        fact = None


    CR = CanonicalRepresentation(D, program)
    CR.initilization()
    D1, common, varrho_left, left_period, left_len, varrho_right, right_period, right_len = find_periods(CR,fact)

    if varrho_left is not None:
        print("left period:", str(varrho_left))
        for key, values in left_period.items():
            print(str(key), [str(val) for val in values])
    else:
        print("left period:", "(-inf," + str(CR.base_interval.left_value), ")")

    if varrho_right is not None:
        print("right period:", str(varrho_right))
        for key, values in right_period.items():
            print(str(key), [str(val) for val in values])
    else:
        print("left period:", "(" + str(CR.base_interval.right_value), ", +inf)")

    if fact is not None:
       print("Entailment:", fact_entailment(D1, fact, common, left_period, left_len, right_period, right_len))
