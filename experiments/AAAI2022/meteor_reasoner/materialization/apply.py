from meteor_reasoner.classes.literal import *
from meteor_reasoner.classes.interval import *
from meteor_reasoner.classes.atom import *
import copy


def since_deduce(literal, left_interval, right_interval):
    """
    Calculate the ``Since'' operator .
    Args:
        literal (a BinarayLiteral instance):
        left_interval (an Interval instance):
        right_interval (an Interval instance):
    Returns:
        a Interval instance or None
    """
    if not literal.operator.interval.left_open and literal.operator.interval.left_value == 0:
        return Interval.add(right_interval, literal.operator.interval)

    # calculate S
    closed_left_interval = copy.copy(left_interval)
    closed_left_interval.left_open = False
    closed_left_interval.right_open = False

    s_interval = Interval.intersection(closed_left_interval, right_interval)
    if s_interval is None:
        return None

    # calculate T satisfying the right literal
    t_interval = Interval.add(s_interval, literal.operator.interval)

    # calculate T satisfying the left literal
    interval = Interval.intersection(t_interval, closed_left_interval)
    if interval is None:
        return None
    else:
        return interval


def until_deduce(literal, left_interval, right_interval):
    """
    Calculate the ``Until'' operator .
    Args:
        literal (a BinarayLiteral instance):
        left_interval (an Interval instance):
        right_interval (an Interval instance):

    Returns:
        a Interval instance or None
    """
    if not literal.operator.interval.left_open and literal.operator.interval.left_value == 0:
        return Interval.sub(right_interval, literal.operator.interval)

    # calculate S
    closed_left_interval = copy.copy(left_interval)
    closed_left_interval.left_open = False
    closed_left_interval.right_open = False

    s_interval = Interval.intersection(closed_left_interval, right_interval)
    if s_interval is None:
        return None

    # calculate T satisfying the right literal
    t_interval = Interval.sub(s_interval, literal.operator.interval)

    # calculate T satisfying the left literal
    interval = Interval.intersection(t_interval,closed_left_interval)
    if interval is None:
        return None
    else:
        return interval


def apply(literal, D, delta_old=None):
    """
    Apply MTL operator(s) to a literal.
    Args:
        literal (Literal BinaryLiteral Instance):
        D (defaultdict):

    Returns:
        A list of Interval instances.
    """
    if not isinstance(literal, BinaryLiteral) and (isinstance(literal, Atom) or
                                                   len(literal.operators) == 0):

        predicate = literal.get_predicate()
        entity = literal.get_entity()
        if entity: # not None
            if predicate in D and entity in D[predicate]:
                if delta_old is not None and predicate in delta_old and entity in delta_old[predicate]:
                    full_intervals = copy.deepcopy(D[predicate][entity])
                    for remove_interval in delta_old[predicate][entity]:
                        full_intervals.remove(remove_interval)
                    return full_intervals
                else:
                    return D[predicate][entity]
            else:
                return []

        else:
            if predicate in D:
                return D[predicate]
            else:
                return []
    else:
        op_name = literal.get_op_name()
        if op_name in ["Until", "Since"]:
            left_literal = literal.left_literal
            right_literal = literal.right_literal

            if left_literal.get_predicate() == "Bottom" or right_literal.get_predicate() == "Bottom":
                raise ValueError("It is not allowed to have the bottom predicate in the left side "
                                 "or the right side of a binary literal ")
            if left_literal.get_predicate() == "Top":
                T1 = [Interval(float('-inf'), float('inf'), True, True)]
            else:
                T1 = apply(left_literal, D)

            if right_literal.get_predicate() == "Top":
                T2 = [Interval(float('-inf'), float('inf'), True, True)]
            else:
                T2 = apply(right_literal, D)

            T = []
            if op_name == "Until":
                if T1 and T2:
                    for t1 in T1:
                        for t2 in T2:
                            t = until_deduce(literal, t1, t2)
                            if t:
                                T.append(t)
            else:
                if T1 and T2:
                    for t1 in T1:
                        for t2 in T2:
                            t = since_deduce(literal, t1, t2)
                            if t:
                                T.append(t)
            return T

        else:
            pop_operator = literal.operators.pop(0)
            T0 = apply(literal, D)
            literal.operators.insert(0, pop_operator)
            T = []
            if op_name == "Diamondminus":
                for t0 in T0:
                  interval = Interval.add(t0, literal.operators[0].interval)
                  if Interval.is_valid_interval(interval.left_value, interval.right_value,
                                                interval.left_open, interval.right_open):
                      T.append(interval)
            elif op_name == "Boxminus":
                for t0 in T0:
                  interval = Interval.circle_add(t0, literal.operators[0].interval)
                  if Interval.is_valid_interval(interval.left_value, interval.right_value,
                                                interval.left_open, interval.right_open):
                      T.append(interval)
            elif op_name == "Diamondplus":
                for t0 in T0:
                  interval = Interval.sub(t0, literal.operators[0].interval)
                  if Interval.is_valid_interval(interval.left_value, interval.right_value,
                                                interval.left_open, interval.right_open):
                      T.append(interval)
            elif op_name == "Boxplus":
                for t0 in T0:
                  interval = Interval.circle_sub(t0, literal.operators[0].interval)
                  if Interval.is_valid_interval(interval.left_value, interval.right_value,
                                                interval.left_open, interval.right_open):
                      T.append(interval)
            else:
                raise ValueError("{} is an illegal MTL operator name!".format(op_name))

            return T


def reverse_apply(literal, D):
    """
    Apply MTL operator(s) to a literal.

    Args:
        literal (Literal BinaryLiteral Instance):
        D (defaultdict):

    Returns:
        A list of Interval instances.
    """
    if isinstance(literal, Atom) or len(literal.operators) == 0:
        predicate = literal.get_predicate()
        entity = literal.get_entity()

        if entity: # not None
            if predicate in D and entity in D[predicate]:
                return D[predicate][entity]
            else:
                return []

        else:
            if predicate in D:
                return D[predicate]
            else:
                return []
    else:
        op_name = literal.get_op_name()
        pop_operator = literal.operators.pop(0)
        T0 = reverse_apply(literal, D)
        literal.operators.insert(0, pop_operator)
        T = []
        if op_name == "Boxplus":
            for t0 in T0:
              interval = Interval.add(t0, literal.operators[0].interval)
              if Interval.is_valid_interval(interval.left_value, interval.right_value,
                                            interval.left_open, interval.right_open):
                  T.append(interval)

        elif op_name == "Boxminus":
            for t0 in T0:
              interval = Interval.sub(t0, literal.operators[0].interval)
              if Interval.is_valid_interval(interval.left_value, interval.right_value,
                                            interval.left_open, interval.right_open):
                  T.append(interval)
        else:
            raise ValueError("{} is an illegal MTL operator name!".format(op_name))

        return T


if __name__ == "__main__":
    from collections import defaultdict
    from meteor_reasoner.classes import Term
    from meteor_reasoner.materialization.index_build import build_index

    D = defaultdict(lambda: defaultdict(list))
    D["A"][tuple([Term("mike"), Term("nick")])] = [Interval(3, 4, False, False), Interval(6, 10, True, True)]
    D["B"][tuple([Term("nan")])] = [Interval(2, 8, False, False)]
    D_index = build_index(D)
    literal_a = Literal(Atom("A", tuple([Term("mike"), Term("nick")])), [Operator("Boxminus", Interval(1, 2, False, False))])
    literal_b = Literal(Atom("A", tuple([Term("mike"), Term("nick")])), [Operator("Diamondminus", Interval(1, 2, False, False))])
    bi_literal_a = BinaryLiteral(Atom("A", tuple([Term("mike"), Term("nick")])),
                               Atom("B", tuple([Term("nan")])), Operator("Since", Interval(1, 2, False, False)))
    bi_literal_b = BinaryLiteral(literal_a, literal_b, Operator("Since", Interval(1, 2, False, False)))

    t1 = apply(literal_a, D)
    for t in t1:
        print(t)
    print("end")
    t2 = reverse_apply(literal_a, D)
    for t in t2:
        print(t)
    print("end")
    t3 = apply(bi_literal_a, D)
    for t in t3:
        print(t)
    print("end")
    t4 = apply(bi_literal_b, D)
    for t in t4:
        print(t)
    print("end")



