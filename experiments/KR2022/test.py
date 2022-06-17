import argparse
from meteor_reasoner.materialization.coalesce import *
from meteor_reasoner.materialization.index_build import *
from meteor_reasoner.utils.loader import *
from meteor_reasoner.materialization.materialize import materialize
import time
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--datapath", default="../datasets/ISWC/lubm_sample.txt",  type=str, help="Input the dataset path (json format)")
parser.add_argument("--rulepath", default="./programs/p1.txt", type=str, help="Input the program path")
args = parser.parse_args()


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
        # raw_data.append(line)

    D = load_dataset(raw_data)
    coalescing_d(D)
    D_index = build_index(D)


for i in range(1,10):
    start_time = time.time()
    materialize(D, program, D_index=D_index, delta_old=D, K=1)
    print(time.time() - start_time)








