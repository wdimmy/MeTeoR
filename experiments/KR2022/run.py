from meteor_reasoner.utils.loader import *
from meteor_reasoner.canonical.find_common_fragment import CanonicalRepresentation, find_left_right_periods, fact_entailment
from meteor_reasoner.canonical.calculate_w import get_w
import argparse
from meteor_reasoner.materialization.coalesce import coalescing_d
from meteor_reasoner.materialization.index_build import build_index
from meteor_reasoner.entailment import entail
import time
from meteor_reasoner.utils.operate_dataset import print_dataset

parser = argparse.ArgumentParser()
parser.add_argument("--datapath", default="programs/case_12_dataset.txt", type=str)
parser.add_argument("--rulepath", default="programs/case_12_program.txt", type=str)
parser.add_argument("--fact", type=str)
args = parser.parse_args()


if __name__ == "__main__":
    # load the dataset and the program
    with open(args.rulepath) as file:
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

    with open(args.datapath) as file:
        raw_data = []
        for line in file:
            for predicate in predicates:
                if line.startswith(predicate):
                     raw_data.append(line)
                     break
        D = load_dataset(raw_data)
        coalescing_d(D)
        D_index = build_index(D)

    # with open(args.datapath) as file:
    #         data = file.readlines()
    #
    # with open(args.rulepath) as file:
    #         program = file.readlines()
    #
    # D = load_dataset(data)
    # D_index = defaultdict(lambda: defaultdict(list))
    # program = load_program(program)
    if args.fact is not None:
        predicate, entity, interval = parse_str_fact(args.fact)
        fact = Atom(predicate, entity, interval)
    else:
        fact = None

    start_time = time.time()
    # calculate w
    # will change the program, so we need to make a copy
    t_program = copy.deepcopy(program)
    w = 2 * get_w(t_program)
    print("The w is:", w)
    # calculate the minimum value and maximum value in the dataset
    maximum_number = 0
    minimum_number = 100
    for predicate in D:
        for entity in D[predicate]:
            for interval in D[predicate][entity]:
                maximum_number = max(interval.right_value, maximum_number)
                minimum_number = min(interval.left_value, minimum_number)
    # calculate the canonical representation
    CR = CanonicalRepresentation(D, program)
    D1, common, varrho_left, left_period, left_len, varrho_right, right_period, right_len = find_left_right_periods(CR, w, fact)

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
