from meteor_reasoner.classes.interval import *


def coalescing(old_intervals):
    if len(old_intervals) == 0:
        return old_intervals
    new_intervals = []
    old_intervals = sorted(old_intervals, key=lambda t: (t.left_value, t.left_open))
    i = 1
    mover = old_intervals[0]
    while i <= len(old_intervals)-1:
        tmp_interval = Interval.union(mover, old_intervals[i])
        if tmp_interval is None:
            # no intersection
            new_intervals.append(mover)
            mover = old_intervals[i]
        else:
            mover = tmp_interval
        i += 1
    new_intervals.append(mover)
    return new_intervals


def coalescing_d(D):
    """
    Merge two overlapped intervals into one interval.
    Args:
        D (a dictionary object): store facts.
    Returns:
    """
    for predicate in D:
        for entity, old_intervals in D[predicate].items():
                old_intervals = D[predicate][entity]
                if len(old_intervals) == 0:
                    continue
                new_intervals = coalescing(old_intervals)
                D[predicate][entity] = new_intervals