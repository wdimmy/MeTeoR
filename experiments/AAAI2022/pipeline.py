from meteor_reasoner.automata.buichi_automata import *
from meteor_reasoner.materialization.index_build import *
from meteor_reasoner.materialization.materialize import materialize
from multiprocessing.pool import ThreadPool
from meteor_reasoner.automata.automaton import consistency
import argparse
import json
from meteor_reasoner.utils.entail_check import entail
parser = argparse.ArgumentParser()
parser.add_argument("--datapath",  required=True, type=str, help="Input the dataset path")
parser.add_argument("--rulepath", required=True, type=str, help="Input the program path")
parser.add_argument("--fact", default="a1:ResearchAssistant(http://www.department0.university0.edu/graduatestudent117)@[4,8]",  type=str, help="Input a fact  you wanna check the entailment")

args = parser.parse_args()
fixpoint = False

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
coalescing_d(D)
D_index = build_index(D)

with open(args.rulepath) as file:
    rules = file.readlines()
    program = load_program(rules)

try:
    fact = parse_str_fact(args.fact)
    F = Atom(fact[0], fact[1], fact[2])
except:
   raise ("The format you input is not correct")


def thread1():
    print("Run thread 2")
    global D, F
    global program, flag2
    # make the conversion
    D1 = copy.deepcopy(D) #copying is time-consuming which can be further optimized
    flag = consistency(D1, program, F)
    flag2 = True
    if flag:
        return True
    else:
        return False


def thread2():
    print("Run thread 1")
    global flag1, D, program, D_index, fixpoint, F
    if entail(F, D):
        return True

    elif fixpoint:
        if entail(F, D):
            return True
        else:
            return False
    else:
        while True:
            fixpoint = materialize(D, rules=program, D_index=D_index, K=1)

            if fixpoint:
                fixpoint = flag
                if entail(F, D):
                    return True
                else:
                    return False
            else:
                if entail(F, D):
                    return True

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
    pool1 = ThreadPool(processes=1)
    async_result1 = pool1.apply_async(thread1)

    pool2 = ThreadPool(processes=1)
    async_result2 = pool2.apply_async(thread2)
    try:
        result = async_result1.get(timeout=120) # setting 120 as the timeout time
        if result:
            print("Automata: Not entailed")
        else:
            print("Automata: Entailed")
    except:
        try:
            result = async_result1.get(timeout=1)
            if result:
                print("Materialisation: Entailed")
            else:
                print("Materialisation: Not Entailed")
        except:
            print("Time out")





