from meteor_reasoner.materialization.coalesce import *
from meteor_reasoner.materialization.index_build import *
from meteor_reasoner.utils.loader import *
from meteor_reasoner.utils.operate_dataset import print_dataset
from meteor_reasoner.materialization.materialize import opt_materialize
import time
import sys
import logging
import argparse

logger = logging.getLogger()
logger.setLevel(logging.INFO)

output_file_handler = logging.FileHandler("./log/opt.log")
stdout_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(output_file_handler)
logger.addHandler(stdout_handler)
parser = argparse.ArgumentParser()
parser.add_argument("--datapath", default="../datasets/cikm/dataset1.txt", type=str, help="Input the dataset path (json format)")
parser.add_argument("--rulepath", default="./programs/demo1.txt",  type=str, help="Input the program path")
parser.add_argument("--logpath", required=True, type=str, help="The name of logpath of the form: ./log/dataset_approach_program.txt")
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

# logger.info("Size of Dataset({}): {}".format(args.datapath, len(raw_data)))
# logger.info("".join(raw_program))
start_time = time.time()
opt_materialize(D, rules=program, D_index=D_index, delta_old=D, K=args.K, logger=logger)
#logger.info("Iteration={}, Optimized method time: {}s".format(50, time.time() - start_time))