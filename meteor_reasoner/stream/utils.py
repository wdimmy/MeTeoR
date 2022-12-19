from collections import defaultdict
from meteor_reasoner.classes.interval import Interval
from meteor_reasoner.classes.atom import Atom
from meteor_reasoner.classes.literal import *
from meteor_reasoner.materialization.coalesce import coalescing, coalescing_d
import decimal


def add_fact_to_window(window_facts, delta_new, limit):
    flag = False # record whether there are new streams added to W
    for predicate in delta_new:
        for entity in delta_new[predicate]:
            tmp_interval_list = []
            if predicate in window_facts and entity in window_facts[predicate]:
                diff_interval_list = Interval.diff_list(delta_new[predicate][entity], window_facts[predicate][entity])
                if len(diff_interval_list) > 0:
                    for interval in diff_interval_list:
                        if interval.right_value == decimal.Decimal("inf"):
                            tmp_interval_list.append(interval)
                        else:
                            new_interval = Interval.intersection(limit, interval)
                            if new_interval is not None:
                                tmp_interval_list.append(new_interval)
                    if len(tmp_interval_list) != 0:
                        flag = True
                        new_interval_list = coalescing(window_facts[predicate][entity] + tmp_interval_list)
                        if len(new_interval_list) != 0:
                           window_facts[predicate][entity] = new_interval_list
                        else:
                            del window_facts[predicate][entity]
            else:
                for interval in delta_new[predicate][entity]:
                    if interval.right_value == decimal.Decimal("inf"):
                        tmp_interval_list.append(interval)
                    else:
                        new_interval = Interval.intersection(limit, interval)
                        if new_interval is not None:
                            tmp_interval_list.append(new_interval)
                if len(tmp_interval_list) != 0:
                    flag = True
                    window_facts[predicate][entity] = tmp_interval_list
    coalescing_d(window_facts)
    return flag


def trim_window(window_facts, limit):
    trimmed_delta_new = defaultdict(lambda: defaultdict(list))
    for predicate in window_facts:
        for entity in window_facts[predicate]:
            tmp_interval_list = []
            for interval in window_facts[predicate][entity]:
                if interval.right_value == decimal.Decimal("inf"):
                    tmp_interval_list.append(interval)
                else:
                    new_interval = Interval.intersection(limit, interval)
                    if new_interval is not None:
                        tmp_interval_list.append(new_interval)
            if len(tmp_interval_list) != 0:
                trimmed_delta_new[predicate][entity] = tmp_interval_list

    return trimmed_delta_new


def contain_new(delta_new, window_facts, limit):
    for predicate in delta_new:
        for entity in delta_new[predicate]:
            if predicate in window_facts and entity in window_facts[predicate]:
                diff_interval_list = Interval.diff_list(delta_new[predicate][entity], window_facts[predicate][entity])
                for interval in diff_interval_list:
                    new_interval = Interval.intersection(limit, interval)
                    if new_interval is not None:
                        return True
            else:
                for interval in delta_new[predicate][entity]:
                    new_interval = Interval.intersection(limit, interval)
                    if new_interval is not None:
                        return True
    return False


def merge_streams(window_facts, delta):
    for predicate in delta:
        for entity in delta[predicate]:
            window_facts[predicate][entity] = coalescing(window_facts[predicate][entity] + delta[predicate][entity])


def add_streams(window_facts, streams, t_next):
    for stream in streams:
        window_facts[stream.predicate][stream.entity] = coalescing(window_facts[stream.predicate][stream.entity]+[Interval(t_next, t_next, False, False)])


def get_maximum_rational_number(program):
    # assume there is no nexted operators, and only boxminus, boxplus, diamondminus and
    # diamondplus are included and no bottom and top
    maximum_val = 0
    for rule in program:
        head = rule.head
        body = rule.body
        for literal in [head]+body:
            if isinstance(literal, Atom): # no operator
                continue
            elif isinstance(literal, Literal):
                if len(literal.operators) > 0 and literal.operators[0].interval.right_value != decimal.Decimal("inf"):
                    maximum_val = max(maximum_val, literal.operators[0].interval.right_value)
    return maximum_val


