from meteor_reasoner.materialization.utils import *
from meteor_reasoner.automata.buichi_automata import *
from meteor_reasoner.utils.normalize import *
from meteor_reasoner.materialization.index_build import *
from multiprocessing.pool import ThreadPool
from automata import consistency
import argparse
import json

parser = argparse.ArgumentParser()
parser.add_argument("--datapath", required=True, type=str, help="Input the dataset path (json format)")
parser.add_argument("--rulepath", required=True,  type=str, help="Input the program path")
parser.add_argument("--fact", required=True, type=str, help="Input a fact  you wanna check the entailment for:, e.g. a1:memberOf(http://www.department0.university0.edu/undergraduatestudent19,"
                 " http://www.department0.university0.edu)@[-2,-1]")
args = parser.parse_args()

fixpoint = False
flag1, flag2 = False, False

with open(args.datapath) as file:
    D_1 = defaultdict(lambda: defaultdict(list))
    data = json.load(open(args.datapath))
    for predicate in data:
        for entry in data[predicate]:
            for entity, interval_dict in entry.items():
                interval = Interval(interval_dict["left_value"], interval_dict["right_value"],
                                    interval_dict["left_open"], interval_dict["right_open"])

                D_1[predicate][tuple([Term(name) for name in entity.split(",")])].append(interval)

    D_1_index = build_index(D_1)

with open(args.rulepath) as file:
    rules = file.readlines()
    program = load_program(rules)

must_literals = defaultdict(list)
coalescing_d(D_1)

try:
    fact = parse_str_fact(args.fact)
    F = Atom(fact[0], fact[1], fact[2])
except:
   raise ("The format you input is not correct")

def entail(fact, D):
    if fact.predicate not in D:
        return False
    else:
        if not fact.entity in D[fact.predicate]:
            return False
        else:
            intervals = D[fact.predicate][fact.entity]
            for interval in intervals:
                if Interval.inclusion(fact.interval, interval):
                    return True
            else:
                return False

def thread1():
    print("Run thread 1")
    global flag1, D_1, program, D_1_index, fixpoint, F
    if entail(F, D_1):
        flag1 = True
        return True

    elif fixpoint:
        if entail(F, D_1):
            flag1 = True
            return True
        else:
            flag1 = True
            return False
    else:
        while True:
            flag = materialize(D_1, rules=program, D_index=D_1_index)
            if flag:
                fixpoint = flag
                if entail(F, D_1):
                    flag1 = True
                    return True
                else:
                    flag1 = True
                    return False
            else:
                if entail(F, D_1):
                    flag1 = True
                    return True


def thread2():
    print("Run thread 2")
    global D_1, must_literals, F
    global program, flag2
    # make the conversion
    flag = consistency(D_1, program, F)
    flag2 = True
    if flag:
        return True
    else:
        return False


if entail(F, D_1):
    print("Materialisation: Entailed")
    exit()


CF = CycleFinder(program=program)
program = CF.get_revevant_rules(F.get_predicate())
CF = CycleFinder(program=program)
if len(CF.loop) == 0: # it is a non-recursive program
    while True:
        flag = materialize(D_1, rules=program, D_index=D_1_index)
        if entail(F, D_1):
            print("Materialisation: Entailed")
            exit()
        else:
            if flag:
                print("Materialisation: Not entailed")
                exit()
else:
    non_recursive_predicates = CF.get_non_recursive_predicates()
    involved_predicates = [predicate for predicate in CF.predicate2id if predicate not in ["Bottom", "Top"]]
    while True:
        flag = materialize_pre(D_1, rules=program, non_recursive_predicates=non_recursive_predicates,
                                         D_index = D_1_index, must_literals=must_literals)
        if entail(F, D_1):
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
    exit()







