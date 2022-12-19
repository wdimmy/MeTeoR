from meteor_reasoner.materialization.index_build import build_index
from meteor_reasoner.utils.loader import *
from meteor_reasoner.utils.operate_dataset import get_min_max_rational
from meteor_reasoner.materialization.t_operator import naive_immediate_consequence_operator
import time
import sys
import argparse
from meteor_reasoner.stream.utils import *
from meteor_reasoner.stream.stream_generator import Stream_Generator
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
#output_file_handler = logging.FileHandler("./meteor_str_mock.log")
stdout_handler = logging.StreamHandler(sys.stdout)
#logger.addHandler(output_file_handler)
logger.addHandler(stdout_handler)


parser = argparse.ArgumentParser()
parser.add_argument("--datapath", default="./data/s1.txt",  type=str, help="Input the dataset path")
parser.add_argument("--rulepath", default="./data/short_stop.txt", type=str, help="Input the program path")
parser.add_argument("--target", default="ShortStep", type=str, help="Input the target predicate")
parser.add_argument("--input_detail", action="store_true")
parser.add_argument("--output_detail", action="store_true")
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

with open(args.datapath) as file:
    lines = file.readlines()
    # raw_data = []
    # if len(lines) > args.limit:
    #     for line in lines:
    #         for predicate in predicates:
    #             if line.startswith(predicate):
    #                  raw_data.append(line)
    #                  break
    # else:
    #     raw_data = lines[:]
    raw_data = lines[:]

    D = load_dataset(raw_data)
    for predicate in D:
        for entity in D[predicate]:
            interval_list = []
            for item in D[predicate][entity]:
                value = (item.left_value + item.right_value) // 2
                interval_list.append(Interval(value, value, False, False))
            D[predicate][entity] = interval_list
    coalescing_d(D)
    D_index = build_index(D)

min_val, max_val = get_min_max_rational(D)
logger.info("Min_value={}, Max_value={} in the given dataset".format(min_val, max_val))

time_points = set()
for predicate in D:
    for entity in D[predicate]:
        for interval in D[predicate][entity]:
            time_points.add(interval.left_value)

time_points = sorted(list(time_points))

output_points = time_points[:]
t_program = decimal.Decimal(get_maximum_rational_number(program))
step = 1

coalescing_d(D)

t = -step
window = [decimal.Decimal(-1 - t_program), decimal.Decimal(-1)]
window_facts = defaultdict(lambda: defaultdict(list))
H = dict() # the key is the predicate name and the value the set of ground relational atoms

logger.info("============Stream Reasoning Starts (MeTeoR-Str) ============\n")
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
    # keep the window unchanged
    if len(streams) == 0:
        continue
    logger.info("Streams in at the time point {}".format(t_next))
    logger.info("Number of streams (in): {}".format(len(streams)))
    if args.input_detail:
        for stream in streams:
            logger.info(str(stream) + "@{}".format(t_next))

    # calculate the number of facts in the window
    # end of the calculation
    add_streams(window_facts, streams, t_next) # add the stream to window_facts
    window_index = build_index(window_facts)
    new_area = Interval(t, t_next, True, False)

    # Apply Rules
    delta_new = naive_immediate_consequence_operator(D=window_facts, rules=program, D_index=window_index)
    flag = add_fact_to_window(window_facts, delta_new, new_area)

    while flag:
        delta_new = naive_immediate_consequence_operator(D=window_facts, rules=program, D_index=window_index)
        # stream_out
        flag = add_fact_to_window(window_facts, delta_new, new_area)

    # Stream Out
    # The time range within which Streams should be out
    stream_window = Interval(t, t_next, True, False)
    # ==== calculate the time point whose stream need to stream out ===
    points_needed_to_out = []
    for point in output_points:
        if point <= stream_window.right_value:
            points_needed_to_out.append(point)
        else:
            break
    for point in points_needed_to_out:
        output_points.remove(point)

    # ==== end ================

    # Being to stream out
    out_streams = []
    number_of_streamout = 0
    if target_predicate in window_facts:
        for entity in window_facts[target_predicate]:
            for interval in window_facts[target_predicate][entity]:
                for point in points_needed_to_out:
                    if interval.left_value < point < interval.right_value:
                        out_streams.append(str(Atom(target_predicate, entity)) + "@{}".format(point))
                        number_of_streamout += 1
                    elif interval.left_value == point and interval.left_open is False:
                        out_streams.append(str(Atom(target_predicate, entity)) + "@{}".format(point))
                        number_of_streamout += 1
                    elif interval.right_value == point and interval.right_open is False:
                        out_streams.append(str(Atom(target_predicate, entity)) + "@{}".format(point))
                        number_of_streamout += 1
                    else:
                        continue
    logger.info("Stream out at the time point " + ",".join([str(item) for item in points_needed_to_out]))
    logger.info("Number of streams (out) " + str(number_of_streamout))
    if args.output_detail:
        for stream in out_streams:
            logger.info(stream)

    # Forget
    t = t_next
    next_window = Interval(t - t_program, t, True, False)
    window_facts = trim_window(window_facts, next_window)

logger.info("\n============Stream Reasoning Ends (MeTeoR-Str) ============\n")
