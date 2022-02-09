from meteor_reasoner.materialization.join import *
from meteor_reasoner.materialization.coalesce import *
from meteor_reasoner.materialization.index_build import *
from meteor_reasoner.utils.loader import load_program, load_dataset
from meteor_reasoner.utils.operate_dataset import *
import time


def materialize(D, rules, common_fragment=None, K=100):
    """
    The function implements the materialization operation.
    Args:
        D (dictionary object):
        rules (list of Rule instances):
        K (int): the nunber of steps for exectuting the materialization. By default=100.
    Returns:
        The
    """
    k = 0
    while k < K:
        coalescing_d(D)
        D_index = defaultdict(lambda: defaultdict(list))
        build_index(D, D_index)
        k += 1
        if k == 1:
            delta_old = D
            delta_new = defaultdict(lambda: defaultdict(list))
        else:
            coalescing_d(delta_new)
            delta_old = delta_new
            delta_new = defaultdict(lambda: defaultdict(list))

        for i, rule in enumerate(rules):
            join(rule, D, delta_old, delta_new, common_fragment, D_index)

        if not delta_new:
            return True, delta_new

        if common_fragment is None:
            #add to D later
            for predicate in delta_new:
                for entity in delta_new[predicate]:
                    if predicate not in D:
                        D[predicate][entity] = delta_new[predicate][entity]
                    elif predicate in D and entity not in D[predicate]:
                        D[predicate][entity] = delta_new[predicate][entity]
                    elif predicate in D and entity in D[predicate]:
                        D[predicate][entity] += delta_new[predicate][entity]

    if common_fragment is None:
         coalescing_d(D)

    return False, delta_new


if __name__ == "__main__":
    raw_data = ["P(mike,mike)@1"]
    raw_program = ["P(X,X):- Diamondminus[0,1]P(X,X)"]
    D = load_dataset(raw_data)
    Program = load_program(raw_program)
    start_time = time.time()
    flag = materialize(D, Program, K=1)
    end_time = time.time()
    print("The mat time:", end_time-start_time)

    #print_dataset(D)











