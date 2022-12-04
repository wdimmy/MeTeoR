from meteor_reasoner.materialization.coalesce import *
from meteor_reasoner.materialization.index_build import *
from meteor_reasoner.utils.loader import *
from meteor_reasoner.materialization.materialize import materialize
import time
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--datapath", required=True, type=str, help="Input the dataset path (json format)")
parser.add_argument("--rulepath", required=True, type=str, help="Input the program path")
parser.add_argument("--K", default=1, type=int, help="Default number of iterations")
args = parser.parse_args()

start_time = time.time()
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
        raw_data.append(line)
    D = load_dataset(raw_data)
    coalescing_d(D)
    D_index = build_index(D)

materialize(D, rules=program, K=args.K)

