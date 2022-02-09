from meteor_reasoner.materialization.utils import *
from multiprocessing.pool import ThreadPool
from meteor_reasoner.automata.consistency_check import consistency
from meteor_reasoner.utils.entail_check import entail
from meteor_reasoner.materialization.materialize import *
import argparse
import json

parser = argparse.ArgumentParser()
parser.add_argument("--datapath", required=True, type=str, help="Input the dataset path (json format)")
parser.add_argument("--rulepath", required=True,  type=str, help="Input the program path")
parser.add_argument("--fact", required=True, type=str, help="Input a fact  you wanna check the entailment for")
args = parser.parse_args()

fixpoint = False
flag1, flag2 = False, False

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

with open(args.rulepath) as file:
    rules = file.readlines()
    program = load_program(rules)

must_literals = defaultdict(list)
coalescing_d(D)

try:
    fact = parse_str_fact(args.fact)
    F = Atom(fact[0], fact[1], fact[2])

except ValueError:
    raise ValueError("The format you input is not correct")


def thread1():
    print("Run thread 1")
    global flag1, D, program, D_index, fixpoint, F
    if entail(F, D):
        flag1 = True
        return True

    elif fixpoint:
        if entail(F, D):
            flag1 = True
            return True
        else:
            flag1 = True
            return False
    else:
        while True:
            flag = materialize(D, rules=program, K=1)
            if flag:
                fixpoint = flag
                if entail(F, D):
                    flag1 = True
                    return True
                else:
                    flag1 = True
                    return False
            else:
                if entail(F, D):
                    flag1 = True
                    return True


def thread2():
    print("Run thread 2")
    global D, F
    global program, flag2
    # make the conversion
    flag = consistency(D, program, F)
    flag2 = True
    if flag:
        return True
    else:
        return False


if entail(F, D):
    print("Materialisation: Entailed")
    exit()


CF = CycleFinder(program=program)
program = CF.get_revevant_rules(F.get_predicate())
CF = CycleFinder(program=program)
if len(CF.loop) == 0: # it is a non-recursive program
    while True:
        flag = materialize(D, rules=program, D_index=D_index)
        if entail(F, D):
            print("Materialisation: Entailed")
            exit()
        else:
            if flag:
                print("Materialisation: Not entailed")
                exit()

else:
    non_recursive_predicates = CF.get_non_recursive_predicates()
    involved_predicates = [predicate for predicate in CF.predicate2id if predicate not in ["Bottom", "Top"]]
    part_of_rules = []
    for rule in program:
        if rule.head.get_predicate() in non_recursive_predicates:
            part_of_rules.append(rule)
            break
        for body_literal in rule.body:
            if not isinstance(body_literal, BinaryLiteral):
                if body_literal.get_predicate() in non_recursive_predicates:
                    part_of_rules.append(rule)
                    break
            else:
                if body_literal.left_atom.get_predicate() in non_recursive_predicates or body_literal.right_atom.get_predicate() in non_recursive_predicates:
                    part_of_rules.append(rule)
                    break

    while True:
        flag, delta_new = materialize(D, rules=part_of_rules, K=1)
        if entail(F, D):
            print("Materialisation: Entailed")
            exit()
        if flag:
            break

    pool1 = ThreadPool(processes=1)
    async_result1 = pool1.apply_async(thread1)

    pool2 = ThreadPool(processes=1)
    async_result2 = pool2.apply_async(thread2)

    while True:
        if flag1:
            result = async_result1.get()
            pool2.terminate()
            if result:
                print("Materialisation: Entailed")
            else:
                print("Materialisation: Not entailed")
            break
        if flag2:
            result = async_result2.get()
            pool1.terminate()
            if not result:
                print("Automata: Entailed")
            else:
                print("Automata: Not entailed")
            break






