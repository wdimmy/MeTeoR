from meteor_reasoner.materialization.seminaive_join import *
from meteor_reasoner.materialization.naive_join import *
from collections import defaultdict


def naive_immediate_consequence_operator(rules, D, D_index):
    delta_new = defaultdict(lambda: defaultdict(list))
    for i, rule in enumerate(rules):
        naive_join(rule, D, delta_new, D_index)
    return delta_new


def seminaive_immediate_consequence_operator(rules, D, D_index, delta_old=None):
    delta_new = defaultdict(lambda: defaultdict(list))
    for i, rule in enumerate(rules):
        seminaive_join(rule, D, delta_old, delta_new, D_index=D_index)

    return delta_new
