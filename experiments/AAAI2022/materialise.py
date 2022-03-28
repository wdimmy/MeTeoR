from meteor_reasoner.graphutil.graph import *
from meteor_reasoner.materialization.build_index import *
import argparse
import sys
import json

parser = argparse.ArgumentParser()
parser.add_argument("--datapath", required=True, type=str, help="Input the dataset path (json format)")
parser.add_argument("--rulepath", required=True, type=str, help="Input the program path")
parser.add_argument("--logpath",  default="log.txt", type=str, help="Input the log path")
parser.add_argument("--predicate",  type=str, help="Input the predicate for which you save the result")
parser.add_argument("--resultpath", type=str, help="Input the result path for the given predicate")
args = parser.parse_args()

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%m-%d %H:%M', filename=args.logpath)
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
logging.info("Handle:Dataset:{} and Rule:{}".format(args.datapath, args.rulepath))

if __name__ == "__main__":
    with open(args.datapath) as file:
        D = defaultdict(lambda: defaultdict(list))
        data = json.load(open(args.datapath))
        for predicate in data:
            for entry in data[predicate]:
                for entity, interval_dict in entry.items():
                    interval = Interval(interval_dict["left_value"], interval_dict["right_value"],
                                        interval_dict["left_open"], interval_dict["right_open"])

                    D[predicate][tuple([Term(name) for name in entity.split(",")])].append(interval)

        D_index = build_index(D)

    must_literals = defaultdict(list)
    coalescing_d(D)
    with open(args.rulepath) as file:
        rules = file.readlines()
        program = load_program(rules)[:4]

    materialize(D, program, D_index)

    if args.predicate is not None and args.resultpath is not None:
        save_predicate("{}".format(args.predicate), D, outfilename=args.resultpath)

