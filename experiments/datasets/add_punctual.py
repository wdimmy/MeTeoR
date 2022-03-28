import rdflib
from collections import defaultdict
import os
import random
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--path", type=str)
parser.add_argument("--outputname", type=str)
parser.add_argument("--factnum", type=int)
parser.add_argument("--intervalnum", type=int)
parser.add_argument("--min_val", type=float, default=0)
parser.add_argument("--max_val", type=float, default=1000)
args = parser.parse_args()

# python add_punctual.py --path /home/dinang/datalog_mtl/LUBM/data/lubm20 --outputname ./jsw/lubm20.txt --factnum 20000000 --intervalnum 20 --min_val 0 --max_val 300
a1 = "http://swat.cse.lehigh.edu/onto/univ-bench.owl#"
ignores = ["http://www.w3.org/2002/07/owl#imports", a1+"emailAddress", a1 + "telephone"]
POINTS = []
cur_point = args.min_val
while cur_point <= args.max_val:
    POINTS.append(round(cur_point, 1))
    cur_point += 0.5
num=args.intervalnum

prefix_id = 1
prefix = dict()

fileout = open(args.outputname, "w")
current_num = 0
for filename in os.listdir(args.path):
    g = rdflib.Graph()
    g.load(os.path.join(args.path, filename))
    degree_intervals_dict = defaultdict(dict)
    for s, p, o in g:
        if current_num == args.factnum:
            break
        s, p, o = str(s), str(p), str(o)
        if p in ignores:
          continue

        if p == "http://www.w3.org/1999/02/22-rdf-syntax-ns#type":
            _prefix, _value = o.split("#")
            if _prefix not in prefix:
                prefix[_prefix] = "a" + str(prefix_id) + ":"
                prefix_id += 1
            fact = prefix[_prefix] + _value + "(" + str(s).lower() + ")@"
            punctuals = random.sample(POINTS, num)
            punctuals.sort()
            current_num += len(punctuals)
            for punctual in punctuals:
                new_fact = fact + "[{},{}]".format(punctual, punctual)
                fileout.write(new_fact + "\n")

        else:
            _prefix, _value = p.split("#")
            if _prefix not in prefix:
                prefix[_prefix] = "a" + str(prefix_id) + ":"
                prefix_id += 1

            fact = prefix[_prefix] + _value + "(" + str(s).lower() + "," + str(o).lower() + ")@"
            punctuals = random.sample(POINTS, num)
            punctuals.sort()
            current_num += len(punctuals)
            for punctual in punctuals:
                new_fact = fact + "[{},{}]".format(punctual, punctual)
                fileout.write(new_fact + "\n")






