from meteor_reasoner.materialization.index_build import build_index
from meteor_reasoner.utils.loader import *
from meteor_reasoner.utils.operate_dataset import get_min_max_rational
from meteor_reasoner.materialization.coalesce import coalescing_d, coalescing
from meteor_reasoner.materialization.t_operator import naive_immediate_consequence_operator
import time
from meteor_reasoner.materialization.materialize import naive_combine
import pickle
import sys
import decimal
import argparse
from meteor_reasoner.stream.utils import *
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

output_file_handler = logging.FileHandler("./log/mock.log")
stdout_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(output_file_handler)
logger.addHandler(stdout_handler)

parser = argparse.ArgumentParser()
parser.add_argument("--datapath", default="../datasets/jsw/traffic.txt",  type=str, help="Input the dataset path (json format)")
parser.add_argument("--rulepath", default="./programs/traffic_1", type=str, help="Input the program path")
parser.add_argument("--datasetname", default="local_lubm5_program_1", type=str, help="Input the save path")
parser.add_argument("--target", default="a1:Scientist", type=str, help="Input the program path")
args = parser.parse_args()

target_predicate = args.target
time_points = [decimal.Decimal(i) for i in range(1001)]
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

start_time = time.time()
with open(args.datapath) as file:
    raw_data = []
    for line in file:
        for predicate in predicates:
            if line.startswith(predicate):
                 raw_data.append(line)
                 break
    print("Lines of facts:", len(raw_data))
    D = load_dataset(raw_data)
    for predicate in D:
        for entity in D[predicate]:
            interval_list = []
            for item in D[predicate][entity]:
                value = (item.left_value + item.right_value) / 2
                interval_list.append(Interval(value, value, False, False))
            D[predicate][entity] = interval_list

    coalescing_d(D)
    D_index = build_index(D)

print("Loading ends={}s".format(time.time()-start_time))
coalescing_d(D)
min_val, max_val = get_min_max_rational(D)
limit = Interval(min_val, max_val, False, False)
print("Min_value={}, Max_value={} in the given dataset".format(min_val, max_val))

start_time = time.time()
cnt = 0
window_sizes = []
window_sizes_raw = []
while True:
    cnt += 1
    print("cnt={}, {}s".format(cnt, time.time()-start_time))
    delta_new = naive_immediate_consequence_operator(D=D, rules=program, D_index=D_index)

    # drop facts out of the range
    delta_new_prime = trim_delta(D, delta_new, limit=limit)

    if len(delta_new_prime) != 0:
        num_facts_raw = 0

        # before coalescing
        for predicate in D:
            for entity in D[predicate]:
                num_facts_raw += len(D[predicate][entity])
        for predicate in delta_new_prime:
            for entity in delta_new_prime[predicate]:
                num_facts_raw += len(delta_new_prime[predicate][entity])

        window_sizes_raw.append(num_facts_raw)
        logger.info("Number of window facts: {}".format(num_facts_raw))
        # before coalescing

        fixpoint = naive_combine(D, delta_new_prime, D_index)

        num_facts = 0
        for predicate in D:
            for entity in D[predicate]:
                num_facts += len(D[predicate][entity])
        window_sizes.append(num_facts)

        logger.info("Number of window facts: uncoalesced={}, coalesced={}".format(num_facts_raw, num_facts))
        if fixpoint:
            break
    else:
        break

time_points = []
point = min_val - decimal.Decimal(0.5)
while point <= max_val:
    point += decimal.Decimal(0.5)
    time_points.append(point)

streams_out = 0
for point in time_points:
    for entity in D[target_predicate]:
        for interval in D[predicate][entity]:
            if interval.left_value < point < interval.right_value or (interval.left_value == point
                                                                      and not interval.left_open) or \
                    (interval.right_value == point and not interval.right_open):
                streams_out += 1
                break

run_times = time.time() - start_time
results = {
    "run_times": run_times,
    "window_size": window_sizes,
    "window_size_raw": window_sizes_raw,
    "stream_out": streams_out,
    "min_value": min_val,
    "max_value": max_val
}

logger.info(results)
from datetime import datetime
now = datetime.now()
output_path = "./results/meteor_" + args.datasetname + ".pkl"
pickle.dump(results, open(output_path, "wb"))
print("============Stream Reasoning Ends============\n")



