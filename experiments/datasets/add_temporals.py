import rdflib
from collections import defaultdict
import os
import random
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--start", type=float)
parser.add_argument("--end", type=float)
parser.add_argument("--num", type=int, default=1)
parser.add_argument("--factnum", type=int, default=-1)
parser.add_argument("--path", type=str)
parser.add_argument("--outputdir", type=str, default="./")
parser.add_argument("--outputprefix", type=str, default="lubm5")
args = parser.parse_args()


if not os.path.exists(args.outputdir):
   os.mkdir(args.outputdir)


pattern1 = "({},{})"
pattern2 = "[{},{}]"
pattern3 = "({},{}]"
pattern4 = "[{},{})"
patterns = [pattern1, pattern2, pattern3, pattern4]


def make_interval(start, end):
    start = round(start, 1)
    end = round(end, 1)
    if start == end:
        return pattern2.format(start, end)
    elif start < end:
        return random.choice(patterns).format(start, end)
    else:
        raise Exception("the left point  should be lower than the right point.")


a1 = "http://swat.cse.lehigh.edu/onto/univ-bench.owl#"
ignores = ["http://www.w3.org/2002/07/owl#imports", a1+"emailAddress", a1 + "telephone"]

gap_range = [1, 2, 3, 1.5, 2.5]


POINTS = []
cur_point = args.start
while cur_point <= args.end:
    POINTS.append(cur_point)
    cur_point += random.choice([0.5, 1])

prefix_id = 1
prefix = dict()

outputfilename = os.path.join(args.outputdir, "{}_{}.txt".format(args.outputprefix,  str(args.num)))
print("Outputfilename:", outputfilename)

fileout = open(outputfilename, "w")
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

        current_num += args.num

        if p == "http://www.w3.org/1999/02/22-rdf-syntax-ns#type":
            _prefix, _value = o.split("#")
            if _prefix not in prefix:
                prefix[_prefix] = "a" + str(prefix_id) + ":"
                prefix_id += 1

            fact = prefix[_prefix] + _value + "(" + str(s).lower() + ")@"
            cnt = 0
            start = random.choice(POINTS)
            while cnt < args.num:
                end = random.choice(POINTS[POINTS.index(start):])
                end = round(end, 1)
                new_fact = fact + make_interval(start, end)
                fileout.write(new_fact + "\n")
                start = min(POINTS[-1], round(end + random.choice(gap_range),1))
                cnt += 1
                if end == POINTS[-1]:
                    break
        else:
            _prefix, _value = p.split("#")
            if _prefix not in prefix:
                prefix[_prefix] = "a" + str(prefix_id) + ":"
                prefix_id += 1

            fact = prefix[_prefix] + _value + "(" + str(s).lower() + "," + str(o).lower() + ")@"
            cnt = 0
            start = random.choice(POINTS)
            while cnt < args.num:
                end = random.choice(POINTS[POINTS.index(start):])
                end = round(end, 1)
                new_fact = fact + make_interval(start, end)
                fileout.write(new_fact + "\n")
                start = min(POINTS[-1], round(end + random.choice(gap_range), 1))
                cnt += 1
                if end == POINTS[-1]:
                    break






