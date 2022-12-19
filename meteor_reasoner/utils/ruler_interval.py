from meteor_reasoner.classes.literal import *
from functools import reduce
from meteor_reasoner.classes.atom import *
from meteor_reasoner.classes.interval import *
import math
from decimal import Decimal


def construct_left_right_pattern(points, gcd):
    """
    This function build two dictionaries used for finding the next interval when
    executing the left or right moving operation.
    Args:
        points (list of distinct points in the dataset):
        gcd (the great common divisor in the program):

    Returns:
        two dictionary objects
    """
    points = list(points)
    points.sort()

    left_end_point = points[0]
    right_end_point = points[0] + gcd

    pattern = set()
    pattern.add(left_end_point)
    pattern.add(right_end_point)
    # the pattern's range [x, x+gcd], all other points will fall into this range
    for item in points:
        a, b = divmod(item-left_end_point, gcd)
        if a == 0:
            continue
        else:
            pattern.add(b)

    pattern = list(pattern)
    pattern.sort()

    intervals = []
    for i in range(len(pattern) - 1):
        item = pattern[i + 1] - pattern[i]
        intervals.append(item)

    right_interval_search_dict = dict()
    pattern = []
    for i in range(len(intervals)):
        pattern.append(str(intervals[i]))
        if i == len(intervals) - 1:
            right_interval_search_dict["#".join(pattern)] = intervals[0]
        else:
            right_interval_search_dict["#".join(pattern)] = intervals[i + 1]

    left_interval_search_dict = dict()
    pattern = []
    for i in range(len(intervals) - 1, -1, -1):
        pattern = [str(intervals[i])] + pattern
        if i == 0:
            left_interval_search_dict["#".join(pattern)] = intervals[len(intervals) - 1]
        else:
            left_interval_search_dict["#".join(pattern)] = intervals[i - 1]

    if len(left_interval_search_dict) == 0:
        left_interval_search_dict["1.0"] = 1
    if len(right_interval_search_dict) == 0:
        right_interval_search_dict["1.0"] = 1
    return left_interval_search_dict, right_interval_search_dict



def interval_intesection_intervallist(target, interval_list):
    """
    Check whether an Interval instance has an intersection with one of the interval_list
    Args:
        target (an Interval instance):
        interval_list (a list of Interval instances):

    Returns:
        Boolean

    """
    for interval in interval_list:
        if Interval.intersection(target, interval) is not None:
            return True
    return False


def interval_inclusion_intervallist(target, interval_list):
    """
    Check whether an Interval instance has an intersection with one of the interval_list
    Args:
        target (an Interval instance):
        interval_list (a list of Interval instances):

    Returns:
        Boolean

    """
    for interval in interval_list:
        if Interval.inclusion(target, interval):
            return True
    return False


def get_conditions(literals, d):
    """
    This function return the accepting conditions according to the direction ``d''.
    Args:
        literals ( list of Literal instances):
        d (the direction):

    Returns:
        list of accepting conditions .

    """
    F = list()
    for literal in literals:
        if d == "left":
            if isinstance(literal, BinaryLiteral):
                if literal.operator.right_value == Decimal("inf") and literal.operator.name == "Since":
                    F.append(literal)
            else:
                if isinstance(literal, Literal) and len(literal.operators) == 1 and (
                        literal.operators[0].right_value == Decimal("inf")) and literal.operators[0].name == "Boxminus":
                    F.append(literal)

        else:
            if isinstance(literal, BinaryLiteral):
                if literal.operator.left_value == Decimal("inf") and literal.operator.opName == "U":
                    F.append(literal)
            else:
                if isinstance(literal, Literal) and len(literal.operators) == 1 and (
                        literal.operators[0].right_value == Decimal("inf")) and literal.operators[0].name == "Boxplus":
                    F.append(literal)
    return F


def get_initial_ruler_intervals(points, left_border, right_border, gcd):
    """
    This function build initial intervals used for creating a AutomataWindow instance.
    Args:
        left_border (float): the most left minimum value  of the Window
        right_border(float):  the most right maximum value  of the Window
        gcd (float):
    Returns:
    """

    points = list(points)
    points.sort()

    left_end_point = points[0]
    right_end_point = points[0] - gcd

    pattern = set()
    pattern.add(left_end_point)
    pattern.add(right_end_point)
    # the pattern's range [x, x+gcd], all other points will fall into this range
    for item in points:
        a, b = divmod(item-left_end_point, gcd)
        if b == 0:
            continue
        else:
            pattern.add(item-gcd * (a+1))

    pattern = list(pattern)
    pattern.sort()
    left_initial_intervals = []
    for i in range(len(pattern)):
        if i == len(pattern) - 1:
            left_initial_intervals.append(
                Interval(pattern[i], pattern[i], False, False))
        else:
            left_initial_intervals.append(
                Interval(pattern[i], pattern[i], False, False))
            left_initial_intervals.append(
                Interval(pattern[i], pattern[i + 1], True, True))

    left_end_point = points[-1]
    right_end_point = points[-1] + gcd

    pattern = set()
    pattern.add(left_end_point)
    pattern.add(right_end_point)
    # the pattern's range [x, x+gcd], all other points will fall into this range
    for item in points:
        a, b = divmod(right_end_point - item, gcd)
        if b == 0:
            continue
        else:
            pattern.add(item + gcd * a)

    pattern = list(pattern)
    pattern.sort()
    pattern_len = [pattern[i] - pattern[i - 1] for i in range(1, len(pattern))]
    pattern_num = len(pattern_len)

    right_initial_intervals = []
    for i in range(len(pattern)):
        if i == len(pattern) - 1:
            right_initial_intervals.append(
                Interval(pattern[i], pattern[i], False, False))
        else:
            right_initial_intervals.append(
                Interval(pattern[i], pattern[i], False, False))
            right_initial_intervals.append(
                Interval(pattern[i], pattern[i + 1], True, True))

    return left_initial_intervals, right_initial_intervals, pattern_num, pattern_len


def get_dataset_points_x(D, min_x_flag=False):
    """
    This function return all distinct points and the maximum point.
    Args:
        D (dictionary of dictionary):  contain all facts.

    Returns:
         (set, int)
    """
    max_x = decimal.Decimal("-inf")
    min_x = decimal.Decimal("+inf")
    points = set()
    for predicate in D:
        if type(D[predicate]) == list:
            for interval in D[predicate]:
                if interval.left_value not in [Decimal("inf"), Decimal("-inf")]:
                    points.add(interval.left_value)
                    max_x = max(max_x, interval.left_value)
                    min_x = min(min_x, interval.left_value)
                if interval.right_value not in [Decimal("inf"), Decimal("-inf")]:
                    points.add(interval.right_value)
                    max_x = max(max_x, interval.right_value)
                    min_x = min(min_x, interval.right_value)
        else:
            for entity in D[predicate]:
                for interval in D[predicate][entity]:
                    if interval.left_value not in [Decimal("inf"), Decimal("-inf")]:
                        points.add(interval.left_value)
                        max_x = max(max_x, interval.left_value)
                        min_x = min(min_x, interval.left_value)
                    if interval.right_value not in [Decimal("inf"), Decimal("-inf")]:
                        points.add(interval.right_value)
                        max_x = max(max_x, interval.right_value)
                        min_x = min(min_x, interval.left_value)

    points = list(points)
    points.sort()
    if min_x_flag:
        return points, min_x, max_x
    else:
        return points, max_x


def get_gcd(program):
    """
    This function calculate the maximum value in the program and  the great common divisor.
    Args:
        program (list of Rule instances):

    Returns:
       (float, float)
    """
    numbers = set()
    for rule in program:
        body = rule.body
        for literal in body + [rule.head]:
            if isinstance(literal, Atom):
                continue

            elif isinstance(literal, BinaryLiteral):
                if literal.operator.interval.left_value not in [Decimal("inf"), Decimal("-inf")]:
                    numbers.add(literal.operator.interval.left_value)
                if literal.operator.interval.right_value not in [Decimal("inf"), Decimal("-inf")]:
                    numbers.add(literal.operator.interval.right_value)

            else:
                for operator in literal.operators:
                    if operator.interval.left_value not in [Decimal("inf"), Decimal("-inf")]:
                        numbers.add(operator.interval.left_value)
                    if operator.interval.right_value not in [Decimal("inf"), Decimal("-inf")]:
                        numbers.add(operator.interval.right_value )

    precisions = [len(str(item).split(".")[1]) for item in numbers if len(str(item).split(".")) == 2]
    if len(precisions) == 0 and len(numbers) != 0:
        return max(numbers), reduce(lambda x, y: math.gcd(int(x), int(y)), numbers)
    elif len(precisions) == 0 and len(numbers) == 0:
        return 1, 1
    else:
        aug = 10 ** max(precisions)
        aug_numbers = [item*aug for item in numbers]
        gcd = reduce(lambda x, y: math.gcd(int(x), int(y)), aug_numbers) / aug
        gcd = decimal.Decimal(gcd)
        return max(numbers), gcd


def window_contain_accepting_conditions(F, W, subset_conditions, d):
    """
    This function judge whether the given AutomataWindow instance contains some accepting conditions
    Args:
        F (list of Literal instances):
        W (AutomtataWindow instance):
        subset_conditions:
        d:
    Returns:
    """
    ruler_intervals = W.ruler_intervals
    ruler_intervals_literals = W.ruler_intervals_literals

    for ruler_interval in ruler_intervals:
       for condition in F:
          if condition in ruler_intervals_literals[ruler_interval]:
             subset_conditions.add(condition)

          elif isinstance(condition, Literal):
             if condition.atom not in ruler_intervals_literals[ruler_interval]:
                if d == "left":
                   operator1 = Operator("Boxminus", Interval(0, Decimal("inf"), False, True))
                   literal1 = Literal(condition.atom, [operator1])
                   operator2 = Operator("Boxminus", Interval(0, Decimal("inf"), True, True))
                   literal2 = Literal(condition.atom, [operator2])
                   if literal1 in F:
                      subset_conditions.add(literal1)
                   if literal2 in F:
                      subset_conditions.add(literal2)
                else:
                    operator1 = Operator("Boxplus", Interval(0, Decimal("inf"), False, True))
                    literal1 = Literal(condition.atom, [operator1])
                    operator2 = Operator("Boxplus", Interval(0, Decimal("inf"), True, True))
                    literal2 = Literal(condition.atom, [operator2])
                    if literal1 in F:
                       subset_conditions.add(literal1)
                    if literal2 in F:
                       subset_conditions.add(literal2)

          elif isinstance(condition, BinaryLiteral):
               if condition.right.atom in ruler_intervals_literals[ruler_interval]:
                    subset_conditions.add(condition)

       if len(subset_conditions) != 0:
           return True
       else:
           return False


def extract_dataset(D, involved_predicates, automata_predicates=[]):
    """
    Extract Atom instances from the dataset and construct the corresponding unbounded literals.
    Args:
        D (dictionary of dictionary):
        automata_predicates (list of str): store predicates needed for Automata
        exclude (list of str): contain some predicat names that are not needed to construct unbounded literals.

    Returns:
        (list, list)
    """
    atoms = []
    unbounded_literals = []
    for predicate in involved_predicates:
        if predicate in D:
            if type(D[predicate]) == list:
                atom = Atom(predicate)
                atoms.append(atom)
                if predicate in automata_predicates:
                    literal = Literal(Atom(predicate),
                                       [Operator("Boxminus", Interval(0, Decimal("inf"), False, True))])
                    unbounded_literals.append(literal)
                    # literal = Literal(Atom(predicate),
                    #                    [Operator("Boxminus", Interval(0, Decimal("inf"), True, True))])
                    # unbounded_literals.append(literal)

                    literal = Literal(Atom(predicate),
                                      [Operator("Boxmplus", Interval(0, Decimal("inf"), False, True))])
                    unbounded_literals.append(literal)
                    # literal = Literal(Atom(predicate),
                    #                   [Operator("Boxmplus", Interval(0, Decimal("inf"), True, True))])
                    # unbounded_literals.append(literal)
            else:
                for entity in D[predicate]:
                    atom = Atom(predicate, entity)
                    atoms.append(atom)
                    if predicate in automata_predicates:
                        literal = Literal(Atom(predicate, entity),
                                          [Operator("Boxminus", Interval(0, Decimal("inf"), False, True))])
                        unbounded_literals.append(literal)
                        # literal = Literal(Atom(predicate, entity),
                        #                   [Operator("Boxminus", Interval(0, Decimal("inf"), True, True))])
                        # unbounded_literals.append(literal)

                        literal = Literal(Atom(predicate, entity),
                                          [Operator("Boxplus", Interval(0, Decimal("inf"), False, True))])
                        unbounded_literals.append(literal)
                        # literal = Literal(Atom(predicate, entity),
                        #                   [Operator("Boxplus", Interval(0, Decimal("inf"), True, True))])
                        # unbounded_literals.append(literal)

    return atoms, unbounded_literals


def extract_program(program, involved_predicates):
    atoms = set()
    literals = set()
    for rule in program:
        head = rule.head
        if head.get_predicate() in involved_predicates:
            continue
        for literal in rule.body():
            if isinstance(literal, BinaryLiteral):
                if literal.left_atom.get_predicate() in involved_predicates or literal.right_atom.get_predicate() in involved_predicates:
                    literals.add(literal)
            elif isinstance(literal, Literal):
                if literal.get_predicate() in involved_predicates:
                    literals.append(literal)
            else:
                if literal.get_predicate() in involved_predicates:
                    atoms.add(literal)
    return literals