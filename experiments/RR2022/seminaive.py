from meteor_reasoner.materialization.coalesce import *
from meteor_reasoner.materialization.index_build import *
from meteor_reasoner.utils.loader import *
from meteor_reasoner.utils.operate_dataset import print_dataset, print_predicate
from meteor_reasoner.materialization.materialize import materialize
import time
import logging
import sys
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--datapath", default="../datasets/ISWC/lubm_sample.txt",  type=str, help="Input the dataset path (json format)")
parser.add_argument("--rulepath", default="./programs/p1.txt", type=str, help="Input the program path")
parser.add_argument("--predicate", default="a1:GoodUniversity", type=str, help="Input the predicate you want to print")
parser.add_argument("--K", default=1, type=int, help="Default number of iterations")
parser.add_argument("--logpath", required=True, type=str, help="The name of logpath of the form: ./log/dataset_approach_program.txt")
args = parser.parse_args()

logger = logging.getLogger()
logger.setLevel(logging.INFO)

output_file_handler = logging.FileHandler(args.logpath)
stdout_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(output_file_handler)
logger.addHandler(stdout_handler)


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
        # for predicate in predicates:
        #     if line.startswith(predicate):
        #          raw_data.append(line)
        #          break
    D = load_dataset(raw_data)
    coalescing_d(D)
    D_index = build_index(D)

logger.info("Size of Dataset({}): {}".format(args.datapath, len(raw_data)))
start_time = time.time()
materialize(D, rules=program, D_index=D_index, seminaive=True, delta_old=D, K=args.K, logger=logger)
logger.info("======END=========\n")
