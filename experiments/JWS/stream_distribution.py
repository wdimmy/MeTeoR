from meteor_reasoner.utils.loader import *
import pickle
from meteor_reasoner.stream.utils import *


def generate_stream_distribution(datafiles, rulepath, output_path, relevant=False):
    with open(rulepath) as file:
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

    final_result = {}
    for i, datapath in enumerate(datafiles):
        with open(datapath) as file:
            raw_data = []
            for line in file:
                raw_data.append(line)
                if relevant:
                    for predicate in predicates:
                        if line.startswith(predicate):
                             raw_data.append(line)
                             break
            print("Lines of facts:", len(raw_data))
            D = load_dataset(raw_data)
            results = defaultdict(int)
            for predicate in D:
                for entity in D[predicate]:
                    interval_list = []
                    for item in D[predicate][entity]:
                        results[item.left_value] += 1
            streams = sorted(results.items(), key=lambda item: item[0])
            stream = [item[1] for item in streams]
            print(datapath, sum(stream))
            final_result[i] = stream

    pickle.dump(final_result, open(output_path, "wb"))




