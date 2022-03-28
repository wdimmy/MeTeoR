from meteor_reasoner.materialization.index_build import build_index
from meteor_reasoner.utils.loader import *
from meteor_reasoner.utils.operate_dataset import get_min_max_rational
from meteor_reasoner.materialization.coalesce import coalescing_d, coalescing
from meteor_reasoner.materialization.t_operator import naive_immediate_consequence_operator
import time
import pickle
import sys
import decimal
import argparse
from meteor_reasoner.utils.operate_dataset import print_dataset
from meteor_reasoner.stream.utils import *
from meteor_reasoner.stream.stream_generator import Stream_Generator
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

output_file_handler = logging.FileHandler("./log/mock.log")
stdout_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(output_file_handler)
logger.addHandler(stdout_handler)

parser = argparse.ArgumentParser()
parser.add_argument("--datapath", default="../datasets/jsw/onlane.txt",  type=str, help="Input the dataset path (json format)")
parser.add_argument("--rulepath", default="./programs/traffic_shortbreak.txt", type=str, help="Input the program path")
parser.add_argument("--datasetname", default="traffic_shortbreak", type=str, help="Input the save path")
parser.add_argument("--target", default="ShortStop", type=str, help="Input the program path")
args = parser.parse_args()

target_predicate = args.target
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
                value = (item.left_value + item.right_value) * 10 / 2
                interval_list.append(Interval(value, value, False, False))
            D[predicate][entity] = interval_list
    coalescing_d(D)
    D_index = build_index(D)

min_val, max_val = get_min_max_rational(D)
max_val = 2000
print("Min_value={}, Max_value={} in the given dataset".format(min_val, max_val))

time_points = []
point = min_val - decimal.Decimal(10)
while point <= max_val:
    point += decimal.Decimal(10)
    time_points.append(point)

print("Loading ends!={}s".format(time.time()-start_time))
t_program = decimal.Decimal(get_maximum_rational_number(program))
step = 1

coalescing_d(D)

t = -1
window = [decimal.Decimal(-1 - t_program), decimal.Decimal(-1)]
window_facts = defaultdict(lambda: defaultdict(list))

print("============Stream Reasoning Starts============\n")
start_time = time.time()
run_times = []
window_size = []
window_size_raw = []
in_streams_num = []
out_streams_num = []
rule_fired = []
apply_num = []

stream_generator = Stream_Generator(time_points, Data=D)

for streams, t_next in stream_generator.generator():
    # keep the window unchange
    if len(streams) == 0:
        continue
    logger.info("Streams in at the time point {}".format(t_next))
    logger.info("Number of streams: {}".format(len(streams)))

    in_streams_num.append(len(streams))
    # calculate the number of facts in the window
    # end of the calculation
    add_streams(window_facts, streams, t_next) # add the stream to window_facts

    window_index = build_index(window_facts)
    new_area = Interval(window[1], t_next, True, False)

    stream_out_cnt = 0
    iteration_step = 0

    raw_point_size = 0
    point_size = 0
    while True:
        #print_dataset(window_facts)
        print("Iteration_step:", iteration_step)
        iteration_step += 1
        one_start_time = time.time()
        delta_new = naive_immediate_consequence_operator(D=window_facts, rules=program, D_index=window_index)

        # stream_out
        streams_out = trim_delta(window_facts, delta_new, new_area)
        one_time = time.time() -one_start_time
        if len(streams_out) == 0:
            # trim to the window size
            window = [t_next-t_program, t_next]
            next_window = Interval(t_next-t_program, t_next, False, False)
            window_facts = trim_window(window_facts, next_window)
            logger.info("Streams out at the time point {}".format(t_next))
            logger.info("Number of out streams: {}".format(stream_out_cnt))
            out_streams_num.append(stream_out_cnt)
            logger.info("Run time is:{}".format(time.time() - start_time-one_time))
            run_times.append(time.time()-start_time)
            break
        for point in time_points:
            if target_predicate in streams_out:
                for entity in streams_out[target_predicate]:
                    for interval in streams_out[target_predicate][entity]:
                        if interval.left_value < point < interval.right_value or (interval.left_value == point
                                                                                  and not interval.left_open) or\
                                (interval.right_value == point and not interval.right_open):
                                stream_out_cnt += 1
                                break

        # === before coalescing =====
        raw_fact_num = 0
        for predicate in window_facts:
            for entity in window_facts[predicate]:
                raw_fact_num += len(window_facts[predicate][entity])

        for predicate in streams_out:
            for entity in streams_out[predicate]:
                raw_fact_num += len(streams_out[predicate][entity])

        raw_point_size = max(raw_fact_num, raw_point_size)

        # === before coalescing ========

        merge_streams(window_facts, streams_out)
        window_index = build_index(window_facts)
        fact_num = 0
        for predicate in window_facts:
            for entity in window_facts[predicate]:
                fact_num += len(window_facts[predicate][entity])
        point_size = min(fact_num, point_size) if point_size != 0 else fact_num

    window_size_raw.append(raw_point_size)
    window_size.append(point_size)
    logger.info("Number of window facts: uncoalesced={}, coalesced={}".format(raw_point_size, point_size))
    print("Iteration_step:", iteration_step)


results = {
    "run_times": run_times,
    "window_size": window_size,
    "window_size_raw": window_size_raw,
    "stream_in": in_streams_num,
    "stream_out": out_streams_num,
    "min_value": min_val,
    "max_value": max_val
}

logger.info(results)
from datetime import datetime
now = datetime.now()

output_path = "./results/sr_" + args.datasetname + ".pkl"
pickle.dump(results, open(output_path , "wb"))
print("============Stream Reasoning Ends============\n")



