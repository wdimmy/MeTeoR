from meteor_reasoner.materialization.t_operator import *
from meteor_reasoner.materialization.coalesce import *
from meteor_reasoner.materialization.index_build import *
from meteor_reasoner.utils.propagation import check_propagation
from meteor_reasoner.graphutil.temporal_dependency_graph import CycleFinder
import time
from meteor_reasoner.materialization.utils import no_new_facts, pre_calculate_threshold, entail_same_nonrecursive_predicates
from meteor_reasoner.utils.operate_dataset import save_dataset_to_file


def calculate_redundancy(delta, old):
    cnt = 0
    for predicate in delta:
        for entity in delta[predicate]:
            if predicate not in old or entity not in old[predicate]:  # all fact w.r.t the predicate are redundant
                cnt += len(delta[predicate][entity])
            else:
                for delta_interval in delta[predicate][entity]:
                    for old_interval in old[predicate][entity]:
                        if Interval.intersection(delta_interval, old_interval) is not None:
                            break
                    else:
                        cnt += 1
    return cnt


def seminaive_combine(D, delta_new, delta_old, D_index=None):
    for head_predicate in delta_new:
        for entity, T in delta_new[head_predicate].items():
            if head_predicate not in D or entity not in D[head_predicate]:
                D[head_predicate][entity] = D[head_predicate][entity] + T
                delta_old[head_predicate][entity] = delta_old[head_predicate][entity] + T
                # update index
                for i, item in enumerate(entity):
                    D_index[head_predicate][str(i) + "@" + item.name].append(entity)
                if len(entity) > 2:
                    for i, item1 in enumerate(entity):
                        for j, item2 in enumerate(entity):
                            if j <= i:
                                continue
                            D_index[head_predicate][str(i) + "@" + item1.name + "||" + str(j) + "@" + item2.name].append(entity)
            else:
                coalesced_T = coalescing(T + D[head_predicate][entity])
                if not Interval.compare(coalesced_T, D[head_predicate][entity]):
                    for interval1 in coalesced_T:
                        flag = True
                        for interval2 in D[head_predicate][entity]:
                            if interval1.left_value == interval2.left_value and interval1 == interval2:
                                flag = False
                                break
                            elif interval2.left_value > interval1.left_value:
                                break
                        if flag:
                            delta_old[head_predicate][entity].append(interval1)
                    D[head_predicate][entity] = coalesced_T
    fixpoint = True
    if len(delta_old) != 0:
        coalescing_d(D)
        coalescing_d(delta_old)
        fixpoint = False
    return fixpoint


def naive_combine(D, delta_new, D_index=None):
    fixpoint = True
    for head_predicate in delta_new:
        for entity, T in delta_new[head_predicate].items():
            if head_predicate not in D or entity not in D[head_predicate]:
                fixpoint = False
                try:
                    D[head_predicate][entity] = D[head_predicate][entity] + T
                except:
                    print("debug")
                    D[head_predicate][entity] = D[head_predicate][entity] + T
                # update index
                for i, item in enumerate(entity):
                    D_index[head_predicate][str(i) + "@" + item.name].append(entity)
                if len(entity) > 2:
                    for i, item1 in enumerate(entity):
                        for j, item2 in enumerate(entity):
                            if j <= i:
                                continue
                            D_index[head_predicate][str(i) + "@" + item1.name + "||" + str(j) + "@" + item2.name].append(entity)
            else:
                coalesced_T = coalescing(T + D[head_predicate][entity])
                if fixpoint:
                    if coalesced_T != D[head_predicate][entity]:
                        fixpoint = False
                D[head_predicate][entity] = coalesced_T

    if not fixpoint:
         coalescing_d(D)

    return fixpoint


def materialize(D, rules, mode="seminaive", K=100, logger=None, must_literals=None, metrics=None):
    """
    The function implements the materialization operation.
    Args:
        D (dictionary object):
        rules (list of Rule instances):
        K (int): the nunber of steps for exectuting the materialization. By default=100.
    Returns:
        The
    """
    D_index = build_index(D)
    delta_old = D
    if mode == "opt":
        return opt_materialize(D, rules, delta_old=delta_old, D_index=D_index, K=K)
    elif mode == "seminaive":
        seminaive = True
    else:
        seminaive = False

    k = 0
    if logger is not None:
        start_time = time.time()
        calc_time = 0.0

    while k < K:
        print("Iteration:", k)
        k += 1
        if seminaive:
            delta_new = seminaive_immediate_consequence_operator(rules, D, D_index, delta_old=delta_old)
        else:
            delta_new = naive_immediate_consequence_operator(rules, D, D_index)

        if seminaive:
            delta_old = defaultdict(lambda: defaultdict(list))
            fixpoint = seminaive_combine(D, delta_new, delta_old, D_index)
            if logger is not None:
                tmp_start_time = time.time()
                coalescing_d(delta_new)
                number_of_redundant_facts = calculate_redundancy(delta_new, delta_old)
                total_number = 0
                for predicate in D:
                    for entity in D[predicate]:
                        total_number += len(D[predicate][entity])
                calc_time += time.time() - tmp_start_time
                logger.info("Iteration={}, t={}, D={}, n={}".format(k, time.time() - start_time - calc_time, total_number, number_of_redundant_facts))
        else:
            if logger is not None:
                delta_old = defaultdict(lambda: defaultdict(list))
                fixpoint = seminaive_combine(D, delta_new, delta_old, D_index)
                coalescing_d(delta_new)
                number_of_redundant_facts = calculate_redundancy(delta_new, delta_old)
                total_number = 0
                for predicate in D:
                    for entity in D[predicate]:
                        total_number += len(D[predicate][entity])
                logger.info("Iteration={}, t={}, D={}, n={}".format(k, time.time() - start_time - calc_time, total_number, number_of_redundant_facts))
            else:
                fixpoint = naive_combine(D, delta_new, D_index)

        if fixpoint:
            return True

    return False


def opt_materialize(D, rules, D_index, delta_old, K=1, logger=None):
    CF = CycleFinder(program=rules)
    non_predicates = CF.get_non_recursive_predicates()
    nr_program = list()
    r_program = list()
    for rule in rules:
        for body_atom in rule.body:
            if isinstance(body_atom, BinaryLiteral):
                left_atom = body_atom.left_literal
                right_atom = body_atom.right_literal
                if left_atom.get_predicate() not in non_predicates or right_atom.get_predicate() not in non_predicates:
                    r_program.append(rule)
                    break  
            else:
                if body_atom.get_predicate() not in non_predicates:
                    r_program.append(rule)
                    break 
        else:
             nr_program.append(rule)
    flag = 0
    k = 0
    if logger is not None:
        start_time = time.time()
        calc_time = 0.0

    while k < K:
        print("Iteration:", k)
        k += 1
        delta_new = seminaive_immediate_consequence_operator(rules, D, D_index, delta_old=delta_old)
        if flag == 0:
            if entail_same_nonrecursive_predicates(D, delta_new, non_predicates):
                flag = 1
                for rule in nr_program:
                    rules.remove(rule)

                if len(r_program) != 0:
                    propagation = check_propagation(r_program)
                    if propagation == 1 or propagation == 2:
                        observed_rules = pre_calculate_threshold(rules, propagation, D, D_index, non_predicates)
                else:
                    propagation = 0

        elif flag == 1 and propagation == 1:
            if len(observed_rules) != 0:
                for i, item in enumerate(observed_rules):
                    if no_new_facts(delta_new, D, Interval(float("-inf"), item[0], True, False)):
                        for rule in item[1]:
                            try:
                                rules.remove(rule)
                            except:
                                continue
                    else:
                        observed_rules = observed_rules[i:]
                        break
                else:
                    observed_rules = observed_rules[i + 1:]

        elif flag == 1 and propagation == 2:
            if len(observed_rules) != 0:
                for i, item in enumerate(observed_rules):
                    if no_new_facts(delta_new, D, Interval(item[0], float("inf"), False, True)):
                        for rule in item[1]:
                             rules.remove(rule)
                    else:
                        observed_rules = observed_rules[i:]
                        break
                else:
                    observed_rules = observed_rules[i + 1:]
        #print("len of rules:", len(rules))
        # if len(rules) < 15:
        #    for rule in rules:
        #         print(rule)
        delta_old = defaultdict(lambda: defaultdict(list))
        fixpoint = seminaive_combine(D, delta_new, delta_old, D_index)
        if logger is not None:
            tmp_start_time = time.time()
            coalescing_d(delta_new)
            number_of_redundant_facts = calculate_redundancy(delta_new, delta_old)
            total_number = 0
            for predicate in D:
                for entity in D[predicate]:
                    total_number += len(D[predicate][entity])
            calc_time += time.time() - tmp_start_time
            logger.info("Iteration={}, t={}, D={}, n={}".format(k, time.time() - start_time - calc_time,
                                                                total_number, number_of_redundant_facts))
        if fixpoint:
            save_dataset_to_file("recursive_dataset.txt", D)
            return True

    return False


if __name__ == "__main__":
    from meteor_reasoner.utils.operate_dataset import print_dataset
    from meteor_reasoner.utils.loader import *

    # start_time = time.time()
    # raw_program = [
    #     "P(X,Y):-Diamondminus[0,1]P(X,Y)",
    #     "R(Y):-Boxminus[1,2]Q(Y),H(Z),P(X,Y)",
    #     "Q(X):-K(X,Y)"
    # ]
    # raw_data = [
    #     "P(a,b)@0",
    #     "K(b,c)@[1,2]",
    #     "H(c)@[2,5]"
    # ]
    # D = load_dataset(raw_data)
    # coalescing_d(D)
    # D_index = build_index(D)
    # program = load_program(raw_program)
    # opt_materialize(D, rules=program, D_index=D_index, delta_old=D, K=1000)
    # print("Optimized method time: ", time.time()-start_time)
    #
    # exit()
    start_time = time.time()
    raw_program = [
        "A(X):-Diamondminus[1,1]A(X)",
        "B(Y):-Diamondminus[1,1]B(Y)",
        "C(X):-A(X), B(X), D(X)"
    ]
    raw_data = [
        "A(a)@1",
        "B(a)@1",
        "D(a)@(-inf,+inf)"
    ]

    D = load_dataset(raw_data)
    coalescing_d(D)
    D_index = build_index(D)
    program = load_program(raw_program)

    materialize(D, rules=program, D_index=D_index, delta_old=D, seminaive=True, K=3)
    print_dataset(D)
    print("Seminaive method time: ", time.time() - start_time)

    start_time = time.time()
    raw_program = [
        "A(X):-Diamondminus[1,1]A(X)",
        "B(Y):-Diamondminus[1,1]B(Y)",
        "C(X):-A(X), B(X), D(X)"
    ]
    raw_data = [
        "A(a)@1",
        "B(a)@1",
        "D(a)@(-inf,+inf)"
    ]

    D = load_dataset(raw_data)
    coalescing_d(D)
    D_index = build_index(D)
    program = load_program(raw_program)
    materialize(D, rules=program, D_index=D_index, delta_old=D, seminaive=False, K=3)
    print("Naive method time: ", time.time() - start_time)
    print_dataset(D)
    exit()

    start_time = time.time()
    raw_program = [
        "P(X,Y):-Diamondminus[0,1]P(X,Y)",
        "R(Y):-Q(Y),H(Z),P(X,Y)",
        "Q(X):-K(X,Y)"
    ]
    raw_data = [
        "P(a,b)@0",
        "K(b,c)@[1,2]",
        "H(c)@[2,5]"
    ]
    D = load_dataset(raw_data)
    coalescing_d(D)
    D_index = build_index(D)
    program = load_program(raw_program)
    materialize(D, rules=program, D_index=D_index, K=1000)
    print("naive method time: ", time.time() - start_time)


    exit()
    raw_data = ["P(mike,mike)@1"]
    raw_program = ["P(X,X):- Diamondminus[1,1]P(X,X)"]
    D = load_dataset(raw_data)
    coalescing_d(D)
    D_index = build_index(D)
    Program = load_program(raw_program)

    start_time = time.time()
    materialize(D, Program, D_index, K=100)
    print_dataset(D)
    end_time = time.time()
    print("The naive mat time:", end_time-start_time)

    raw_data = ["P(mike,mike)@1"]
    raw_program = ["P(X,X):- Diamondminus[1,1]P(X,X)"]
    D = load_dataset(raw_data)
    coalescing_d(D)
    D_index = build_index(D)
    Program = load_program(raw_program)
    start_time = time.time()
    materialize(D, Program, D_index, seminaive=True, delta_old=D, K=100)
    print_dataset(D)
    end_time = time.time()
    print("The seminaive mat time:", end_time - start_time)
















