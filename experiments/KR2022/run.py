from meteor_reasoner.utils.loader import *
from meteor_reasoner.canonical.find_common_fragment import CanonicalRepresentation, \
    find_left_right_periods, fact_entailment
from meteor_reasoner.canonical.calculate_w import get_w
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--datapath", default="./programs/case_0_dataset.txt", type=str)
parser.add_argument("--rulepath", default="./programs/case_0_program.txt", type=str)
parser.add_argument("--fact", default="", type=str)
args = parser.parse_args()


if __name__ == "__main__":
    # load the dataset and the program
    with open(args.datapath) as file:
            data = file.readlines()
    with open(args.rulepath) as file:
            program = file.readlines()
    D = load_dataset(data)
    D_index = defaultdict(lambda: defaultdict(list))
    program = load_program(program)
    if args.fact != "":
        predicate, entity, interval = parse_str_fact(args.fact)
        fact = Atom(predicate, entity, interval)
    else:
        fact = None

    # calculate w
    w = 2 * get_w(program)
    print("The w is:", w)
    # calculate the minimum value and maximum value in the dataset
    maximum_number = -10
    minimum_number = 100
    for predicate in D:
        for entity in D[predicate]:
            for interval in D[predicate][entity]:
                maximum_number = max(interval.right_value, maximum_number)
                minimum_number = min(interval.left_value, minimum_number)
    print("The maximum number:", maximum_number)
    print("The minimum number:", minimum_number)

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
