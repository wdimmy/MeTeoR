from meteor_reasoner.graphutil.graph import *
from meteor_reasoner.materialization.index_build import *
from meteor_reasoner.utils.operate_dataset import save_predicate
from meteor_reasoner.materialization.materialize import materialize
import argparse
from meteor_reasoner.materialization.coalesce import coalescing_d
import json

parser = argparse.ArgumentParser()
parser.add_argument("--datapath", required=True, type=str, help="Input the dataset path (json format)")
parser.add_argument("--rulepath", required=True, type=str, help="Input the program path")
parser.add_argument("--predicate",  type=str, help="Input the predicate for which you save the result")
parser.add_argument("--resultpath", type=str, help="Input the result path for the given predicate")
args = parser.parse_args()


if __name__ == "__main__":
    with open(args.datapath) as file:
        D = defaultdict(lambda: defaultdict(list))
        data = json.load(open(args.datapath))
        for predicate in data:
            for entry in data[predicate]:
                for entity, interval_dict in entry.items():
                    interval = Interval(decimal.Decimal(interval_dict["left_value"]),
                                        decimal.Decimal(interval_dict["right_value"]),
                                        decimal.Decimal(interval_dict["left_open"]),
                                        decimal.Decimal(interval_dict["right_open"]))

                    D[predicate][tuple([Term(name) for name in entity.split(",")])].append(interval)

        D_index = build_index(D)

    coalescing_d(D)
    with open(args.rulepath) as file:
        rules = file.readlines()
        program = load_program(rules)

    materialize(D, program, D_index)

    if args.predicate is not None and args.resultpath is not None:
        save_predicate("{}".format(args.predicate), D, outfilename=args.resultpath)

