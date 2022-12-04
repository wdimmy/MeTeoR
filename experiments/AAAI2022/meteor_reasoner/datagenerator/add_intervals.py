import os
import random

import argparse

# parser = argparse.ArgumentParser(description='Process some integers.')
# parser.add_argument('integers', metavar='N', type=int, choices=[1,2,3], nargs='*',
#                     help='an integer for the accumulator')
# parser.add_argument('--sum', '-s', dest='accumulate', action='store_const',
#                     const=sum, default=max,
#                     help='sum the integers (default: find the max)')
#
# args = parser.parse_args()
# print(args.accumulate)
# print(args.accumulate(args.integers))
# exit()

parser = argparse.ArgumentParser()
parser.add_argument("--datalog_file_path", type=str, required=True)
parser.add_argument("--factnum", type=int, default=1000, required=True)
parser.add_argument("--intervalnum", type=int, default=1)
parser.add_argument("--unit", default=1, type=float)
parser.add_argument("--punctual", action="store_true", help="specify whether we only add punctual intervals")
parser.add_argument("--openbracket", action="store_true", help="specify whether we need to add open brackets")
parser.add_argument("--min_val", type=float, default=0)
parser.add_argument("--max_val", type=float, default=50)
args = parser.parse_args()


POINTS = []
cur_point = args.min_val
while cur_point <= args.max_val:
    POINTS.append(round(cur_point, 1))
    cur_point += args.unit

interval_num=args.intervalnum
current_num = 0
fileout = open(os.path.join(os.path.dirname(args.datalog_file_path), str(args.factnum)+".txt"), "w")

with open(args.datalog_file_path) as file:
    for line in file:
        if current_num == args.factnum:
            break

        elif args.factnum - current_num >= interval_num:
            current_num += interval_num
            for _ in range(interval_num):
                if args.punctual:
                    val = random.choice(POINTS)
                    left, right = val, val
                else:
                    left, right = random.sample(POINTS, 2)
                    if left > right:
                        left, right = right, left
                if args.openbracket:
                    left_bracket = random.choice(["(", "["])
                    right_bracket = random.choice([")", "]"])
                    new_fact = line.strip() + "@" + "{}{},{}{}".format(left_bracket, left, right, right_bracket)
                else:
                    new_fact = line.strip() + "@" + "[{},{}]".format(left, right)
                fileout.write(new_fact + "\n")
        else:
            current_num += args.factnum - current_num
            for _ in range(args.factnum - current_num):
                if args.punctual:
                    val = random.choice(POINTS)
                    left, right = val, val
                else:
                    left, right = random.sample(POINTS, 2)
                    if left > right:
                        left, right = right, left
                if args.openbracket:
                    left_bracket = random.choice(["(", "["])
                    right_bracket = random.choice([")", "]"])
                    new_fact = line.strip() + "@" + "{}{},{}{}".format(left_bracket, left, right, right_bracket)
                else:
                    new_fact = line.strip() + "@" + "[{},{}]".format(left, right)
                fileout.write(new_fact + "\n")