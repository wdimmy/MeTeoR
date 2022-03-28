from meteor_reasoner.materialization.seminaive_join import *
from meteor_reasoner.materialization.naive_join import *
from meteor_reasoner.materialization.optimized_seminaive_join import *
from collections import defaultdict


def naive_immediate_consequence_operator(rules, D, D_index, recorder=None):
    delta_new = defaultdict(lambda: defaultdict(list))
    for i, rule in enumerate(rules):
        naive_join(rule, D, delta_new, D_index, recorder=recorder)
    return delta_new


def seminaive_immediate_consequence_operator(rules, D, D_index, delta_old=None):
    delta_new = defaultdict(lambda: defaultdict(list))
    for i, rule in enumerate(rules):
        seminaive_join(rule, D, delta_old, delta_new, D_index)

    return delta_new


def optimize_seminaive_immediate_consequence_operator(rules, D, D_index, delta_old=None, non_predicates=[], records={}):
    delta_new = defaultdict(lambda: defaultdict(list))
    for i, rule in enumerate(rules):
        optimized_seminaive_join(rule, D, delta_old, delta_new, D_index, records=records, non_predicates=non_predicates)

    return delta_new