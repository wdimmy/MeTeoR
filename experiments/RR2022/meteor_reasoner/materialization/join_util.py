from meteor_reasoner.classes.interval import *
import copy


def contain_variable(entity):
    for term in entity:
        if term.type == "variable":
            return True
    return False


def contain_variable_after_replace(entity, context):
    for term in entity:
        if term.type == "variable" and term.name not in context:
            return True
    return False


def boundary_check(p, max_p):
    for i, _ in enumerate(p):
        if p[i] < max_p[i]:
            continue
        else:
            return False

    return True


def interval_merge(T):
    """
    A novel merging algorithm is implemented.
    Args:
        T (A list of list of Interval instances):

    Returns:
        A list of Interval instances.

    """

    T = list(copy.deepcopy(T))
    for i in range(len(T)):
        intervals = T[i]
        intervals = sorted(intervals, key=lambda t: t.left_value)
        T[i] = intervals

    T.sort(key=lambda item: item[0].left_value, reverse=True) # sorted by reverse according to the first interval's value

    max_pointers = [len(item) for item in T]
    pointers = [0] * len(T)
    result = set()
    while boundary_check(pointers, max_pointers):
        flag = True
        mover = T[0][pointers[0]]
        for i, _ in enumerate(pointers):
            while pointers[i] < max_pointers[i]:
                tmp = Interval.intersection(mover, T[i][pointers[i]])
                if tmp is None:
                    if T[i][pointers[i]].left_value == mover.right_value and mover.right_open and T[i][pointers[i]].left_open:
                        mover = tmp
                        for j in range(0, i):
                            while True:
                                if Interval.intersection(T[j][pointers[j]], T[i][pointers[i]]) is None and T[j][pointers[j]].left_value < T[i][pointers[i]].right_value:
                                    pointers[j] = pointers[j] + 1
                                    if pointers[j] == max_pointers[j]:
                                        break
                                else:
                                    break

                        flag = False
                        break

                    elif T[i][pointers[i]].left_value == mover.right_value and mover.right_open != T[i][pointers[i]].left_open:
                        mover = tmp
                        for j in range(0, i):
                            while True:
                                if Interval.intersection(T[j][pointers[j]], T[i][pointers[i]]) is None and T[j][pointers[j]].left_value < T[i][pointers[i]].right_value:
                                    pointers[j] = pointers[j] + 1
                                    if pointers[j] == max_pointers[j]:
                                        break
                                else:
                                    break

                        flag = False
                        break

                    elif T[i][pointers[i]].left_value > mover.right_value:
                        mover = tmp
                        for j in range(0, i):
                            while True:
                                if Interval.intersection(T[j][pointers[j]], T[i][pointers[i]]) is None and T[j][pointers[j]].left_value < T[i][pointers[i]].right_value:
                                    pointers[j] = pointers[j] + 1
                                    if pointers[j] == max_pointers[j]:
                                        break
                                else:
                                    break
                        flag = False
                        break

                    else:
                        if pointers[i] != max_pointers[i] - 1:
                            pointers[i] = pointers[i] + 1
                        else:
                            pointers[i] = pointers[i] + 1
                            flag = False
                            mover = None
                            break
                else:
                    mover = tmp
                    break

            if flag is False:
                break

        if mover is None:
            continue

        for i, _ in enumerate(pointers):
                if mover.right_value < T[i][pointers[i]].right_value:
                    T[i][pointers[i]].left_value = mover.right_value
                    T[i][pointers[i]].left_open = False
                elif mover.right_value == T[i][pointers[i]].right_value and mover.right_open and not T[i][pointers[i]].right_open:
                    T[i][pointers[i]].left_value = mover.right_value
                    T[i][pointers[i]].left_open = False
                else:
                    pointers[i] = pointers[i] + 1
        result.add(mover)
    return list(result)

