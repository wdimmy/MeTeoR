from meteor_reasoner.utils.loader import *
from meteor_reasoner.materialization.index_build import *
from meteor_reasoner.materialization.coalesce import *
from meteor_reasoner.utils.operate_dataset import *
from meteor_reasoner.materialization.materialize import materialize
from meteor_reasoner.utils.ruler_interval import *

class CanonicalRepresentation:
    def __init__(self, D, Program):
        self.D = D
        self.D_index = defaultdict(lambda : defaultdict(list))
        self.Program = Program
        self.initilization()

    def initilization(self):
        coalescing_d(self.D)
        build_index(self.D,  self.D_index )
        self.points, self.min_x, self.max_x = get_dataset_points_x(self.D, min_x_flag=True)
        self.z, self.gcd = get_gcd(self.Program)
        _, self.initial_ruler_intervals = get_initial_ruler_intervals(self.points, left_border= self.min_x,
                                                                      right_border=self.max_x, gcd=self.gcd)
        self.left_dict, self.right_dict = construct_left_right_pattern(self.points, self.gcd)


def find_common_fragment(D1, D2, rules, varrho):
    points, min_x, max_x = get_dataset_points_x(D2, min_x_flag=True)
    _, gcd = get_gcd(rules)
    _, initial_window_ruler_intervals = get_initial_ruler_intervals(points, left_border=min_x, right_border=max_x, gcd=gcd)
    left_point = Interval(varrho.left_value, varrho.left_value, False, False)
    right_point = Interval(varrho.right_value, varrho.right_value, False, False)
    left_i = initial_window_ruler_intervals.index(left_point)
    right_i = initial_window_ruler_intervals.index(right_point)

    # check whether in the interval [t_D^{-}, t_D^{+}], D' and D'' are the same
    middle_i = left_i
    while middle_i <= right_i:
        flag = False
        ruler_interval = initial_window_ruler_intervals[middle_i]
        for predicate in D2:
            for entity in D2[predicate]:
                if interval_intesection_intervallist(ruler_interval, D2[predicate][entity]):
                    if predicate not in D1 or entity not in D1[predicate] or not \
                            interval_intesection_intervallist(ruler_interval, D1[predicate][entity]):
                        flag = True
                        break
            if flag:
                return None, None
        middle_i += 1

    left_border = None
    while left_i > 0:
        left_i -= 1
        ruler_interval = initial_window_ruler_intervals[left_i]
        for predicate in D2:
            flag = False
            for entity in D2[predicate]:
                if interval_intesection_intervallist(ruler_interval, D2[predicate][entity]):
                    if predicate not in D1 or entity not in D1[predicate] or not \
                            interval_intesection_intervallist(ruler_interval, D1[predicate][entity]):
                        left_border = ruler_interval
                        flag = True
                        break
            if flag:
                break

    right_border = None
    while right_i < len(initial_window_ruler_intervals)-1:
        right_i += 1
        ruler_interval = initial_window_ruler_intervals[right_i]
        flag = False
        for predicate in D2:
            for entity in D2[predicate]:
                if interval_inclusion_intervallist(ruler_interval, D2[predicate][entity]):
                    if predicate in D1 and entity in D1[predicate] and interval_inclusion_intervallist(
                            ruler_interval, D1[predicate][entity]):
                        continue
                    else:
                        if ruler_interval.left_open:
                            right_border = Interval(ruler_interval.left_value, ruler_interval.left_value, False, False)
                        else:
                            right_border = Interval(ruler_interval.left_value, ruler_interval.left_value, True, True)
                        flag = True
                        break
            if flag:
                break
        if flag:
            break

    if left_border is None:
        left_value, left_open = decimal.Decimal("-inf"), True
    else:
        left_value, left_open = left_border.left_value, left_border.left_open

    if right_border is None:
        right_value, right_open = decimal.Decimal("inf"), True
    else:
        right_value, right_open = right_border.left_value, right_border.left_open

    varrho_left_range = None
    if Interval.is_valid_interval(left_value, varrho.left_value, left_open, True):
        varrho_left_range = Interval(left_value, varrho.left_value, left_open, True)
    varrho_right_range = None
    if Interval.is_valid_interval(varrho.right_value, right_value, True, right_open):
        varrho_right_range = Interval(varrho.right_value, right_value, True, right_open)

    return varrho_left_range, varrho_right_range


def has_same_pattern(ruler_intervals1, ruler_intervals2):
    """
    Check whether the give two ruler interval lists have the same pattern
    Args:
        ruler_intervals1: a list of ruler-intervals
        ruler_intervals2: a list of ruler-intervals

    Returns:
        True or False
    """
    if len(ruler_intervals1) != len(ruler_intervals2):
        return False
    if ruler_intervals1[0].left_open != ruler_intervals2[0].left_open or ruler_intervals1[-1].right_open != ruler_intervals2[-1].right_open:
        return False
    for ruler1, ruler2 in zip(ruler_intervals1, ruler_intervals2):
        if abs(ruler1.right_value-ruler1.left_value) != abs(ruler2.right_value - ruler2.left_value):
            return False
    return True


def has_same_facts(ruler_intervals1, ruler_intervals2, D):
    """
    Check whether the two same-pattern ruler lists have the same facts at each corresponding ruler-interval
    Args:
        ruler_intervals1: a list of ruler-intervals
        ruler_intervals2: a list of ruler-intervals
        D: contain all relational facts
    Returns:
        True or False
    """

    for ruler1, ruler2 in zip(ruler_intervals1, ruler_intervals2):
        for predicate in D:
            for entity in D[predicate]:
                if interval_inclusion_intervallist(ruler1, D[predicate][entity]) and \
                        not interval_inclusion_intervallist(ruler2, D[predicate][entity]):
                    return False
    return True


def find_left_period(D, left_interval_range, CR, w):
    if left_interval_range.left_value != decimal.Decimal("-inf"):
        big_ruler_intervals = CR.initial_ruler_intervals[:]
        starting_ruler_interval = None
        while big_ruler_intervals[0].left_value >= left_interval_range.left_value:
            ruler_interval_len = []
            cnt = 0
            if big_ruler_intervals[0].left_open:
                new_ruler_interval = Interval(big_ruler_intervals[0].left_value, big_ruler_intervals[0].left_value,
                                              False, False)
                if starting_ruler_interval is None:
                    starting_ruler_interval = new_ruler_interval
                if new_ruler_interval.left_value > left_interval_range.left_value:
                   big_ruler_intervals = [new_ruler_interval] + big_ruler_intervals
                   continue
                elif new_ruler_interval.left_value == left_interval_range.left_value and new_ruler_interval.left_open == left_interval_range.left_open:
                    big_ruler_intervals = [new_ruler_interval] + big_ruler_intervals
                    continue
                else:
                    break

            for i in range(len(big_ruler_intervals)):
                if big_ruler_intervals[i].left_open:
                    ruler_interval_len.append(
                        str(abs(big_ruler_intervals[i].right_value - big_ruler_intervals[i].left_value)))
                    cnt += 1
                if cnt >= len(CR.left_dict):
                    break
            tmp_pattern = "#".join(ruler_interval_len)
            current_the_most_left_ruler_interval = big_ruler_intervals[0]
            next_ruler_interval_len = CR.left_dict[tmp_pattern]
            new_ruler_interval = (Interval(current_the_most_left_ruler_interval.left_value - next_ruler_interval_len,
                                           current_the_most_left_ruler_interval.left_value, True, True))
            if new_ruler_interval.left_value > left_interval_range.left_value:
                big_ruler_intervals = [new_ruler_interval] + big_ruler_intervals
                continue
            elif new_ruler_interval.left_value == left_interval_range.left_value and new_ruler_interval.left_open == left_interval_range.left_open:
                big_ruler_intervals = [new_ruler_interval] + big_ruler_intervals
                continue
            else:
                break

        big_ruler_intervals = big_ruler_intervals[0: big_ruler_intervals.index(starting_ruler_interval) + 1]

        len_big_ruler_intervals = len(big_ruler_intervals)
        for i in range(len_big_ruler_intervals - 1, -1, -1):
            if big_ruler_intervals[i].left_open:
                continue
            j = i
            first_interval = []
            tmp_w = w
            first_flag = False
            while tmp_w >= 0:
                next_ruler_interval_len = abs(big_ruler_intervals[j].right_value - big_ruler_intervals[j].left_value)
                tmp_w -= next_ruler_interval_len
                if tmp_w >= 0:
                    first_interval = [big_ruler_intervals[j]] + first_interval
                j -= 1
                if j < 0:
                    first_flag = True
                    break
            if first_flag:
                break

            for k in range(i - 1, -1, -1):
                if big_ruler_intervals[k].left_open:
                    continue
                j = k
                second_interval = []
                tmp_w = w
                second_flag = False
                while tmp_w >= 0:
                    next_ruler_interval_len = abs(
                        big_ruler_intervals[j].left_value - big_ruler_intervals[j].right_value)
                    tmp_w -= next_ruler_interval_len
                    if tmp_w >= 0:
                        second_interval = [big_ruler_intervals[j]] + second_interval
                    j -= 1
                    if j < 0:
                        second_flag = True
                        break
                if second_flag:
                    break

                if has_same_pattern(second_interval, first_interval) and has_same_facts(second_interval, first_interval,
                                                                                        D):
                    varrho_left_dict = defaultdict(list)
                    for ruler in first_interval:
                        for predicate in D:
                            for entity in D[predicate]:
                                if interval_inclusion_intervallist(ruler, D[predicate][entity]):
                                    varrho_left_dict[ruler].append(Atom(predicate, entity))
                    return first_interval, second_interval, varrho_left_dict

        return None, None, None

    else:
        threshold = 100
        big_ruler_intervals = CR.initial_ruler_intervals[:]
        starting_ruler_interval = None
        for _ in range(threshold+len(CR.initial_ruler_intervals)+1):
            ruler_interval_len = []
            cnt = 0
            if big_ruler_intervals[0].left_open:
                new_ruler_interval = Interval(big_ruler_intervals[0].left_value, big_ruler_intervals[0].left_value, False, False)
                if starting_ruler_interval is None:
                    starting_ruler_interval = new_ruler_interval
                big_ruler_intervals = [new_ruler_interval] + big_ruler_intervals
                continue

            for i in range(len(big_ruler_intervals)):
                if big_ruler_intervals[i].left_open:
                    ruler_interval_len.append(str(abs(big_ruler_intervals[i].right_value - big_ruler_intervals[i].left_value)))
                    cnt += 1
                if cnt >= len(CR.left_dict):
                    break
            tmp_pattern = "#".join(ruler_interval_len)
            current_the_most_left_ruler_interval = big_ruler_intervals[0]
            next_ruler_interval_len = CR.left_dict[tmp_pattern]
            new_ruler_interval = (Interval(current_the_most_left_ruler_interval.left_value - next_ruler_interval_len,
                                           current_the_most_left_ruler_interval.left_value, True, True))
            big_ruler_intervals = [new_ruler_interval] + big_ruler_intervals

        big_ruler_intervals = big_ruler_intervals[0: big_ruler_intervals.index(starting_ruler_interval)+1]

        len_big_ruler_intervals = len(big_ruler_intervals)
        for i in range(len_big_ruler_intervals-1, -1, -1):
            if big_ruler_intervals[i].left_open:
                continue
            j = i
            first_interval = []
            tmp_w = w
            while tmp_w >= 0:
                next_ruler_interval_len = abs(big_ruler_intervals[j].right_value - big_ruler_intervals[j].left_value)
                tmp_w -= next_ruler_interval_len
                if tmp_w >= 0:
                    first_interval = [big_ruler_intervals[j]] + first_interval
                j -= 1

            for k in range(i - 1, -1, -1):
                if big_ruler_intervals[k].left_open:
                    continue
                j = k
                second_interval = []
                tmp_w = w
                while tmp_w >= 0:
                    next_ruler_interval_len = abs(big_ruler_intervals[j].left_value - big_ruler_intervals[j].right_value)
                    tmp_w -= next_ruler_interval_len
                    if tmp_w >= 0:
                        second_interval = [big_ruler_intervals[j]] + second_interval
                    j -= 1

                if has_same_pattern(second_interval, first_interval) and has_same_facts(second_interval, first_interval,D):
                     varrho_left_dict = defaultdict(list)
                     for ruler in first_interval:
                         for predicate in D:
                             for entity in D[predicate]:
                                 if interval_inclusion_intervallist(ruler, D[predicate][entity]):
                                     varrho_left_dict[ruler].append(Atom(predicate, entity))
                     return first_interval, second_interval,  varrho_left_dict


def find_right_period(D, right_interval_range, CR, w):
    if right_interval_range.right_value != decimal.Decimal("inf"):
        big_ruler_intervals = CR.initial_ruler_intervals[:]
        starting_ruler_interval = None
        while big_ruler_intervals[-1].right_value <= right_interval_range.right_value:
            ruler_interval_len = []
            cnt = 0
            if big_ruler_intervals[-1].left_open:
                new_ruler_interval = Interval(big_ruler_intervals[-1].right_value, big_ruler_intervals[-1].right_value,
                                              False, False)
                if starting_ruler_interval is None:
                    starting_ruler_interval = new_ruler_interval

                if new_ruler_interval.right_value < right_interval_range.right_value:
                   big_ruler_intervals = big_ruler_intervals + [new_ruler_interval]
                   continue
                elif new_ruler_interval.right_value == right_interval_range.right_value and new_ruler_interval.right_open == right_interval_range.right_open:
                    big_ruler_intervals = big_ruler_intervals + [new_ruler_interval]
                    continue
                else:
                    break

            for i in range(len(big_ruler_intervals)-1, -1, -1):
                if big_ruler_intervals[i].left_open:
                    ruler_interval_len.append(
                        str(abs(big_ruler_intervals[i].right_value - big_ruler_intervals[i].left_value)))
                    cnt += 1
                if cnt >= len(CR.right_dict):
                    break
            tmp_pattern = "#".join(ruler_interval_len)
            current_the_most_right_ruler_interval = big_ruler_intervals[-1]
            next_ruler_interval_len = CR.right_dict[tmp_pattern]
            new_ruler_interval = (Interval(current_the_most_right_ruler_interval.right_value,
                                           current_the_most_right_ruler_interval.right_value + next_ruler_interval_len, True, True))
            if new_ruler_interval.right_value < right_interval_range.right_value:
                big_ruler_intervals = big_ruler_intervals + [new_ruler_interval]
            elif new_ruler_interval.right_value == right_interval_range.right_value and new_ruler_interval.right_open == right_interval_range.right_open:
                big_ruler_intervals = big_ruler_intervals + [new_ruler_interval]
            elif new_ruler_interval.right_value == right_interval_range.right_value and not right_interval_range.right_open:
                big_ruler_intervals = big_ruler_intervals + [new_ruler_interval]
            else:
                break
        big_ruler_intervals = big_ruler_intervals[big_ruler_intervals.index(starting_ruler_interval):]

        len_big_ruler_intervals = len(big_ruler_intervals)
        for i in range(0, len_big_ruler_intervals-1):
            if big_ruler_intervals[i].left_open:
                continue
            j = i
            first_interval = []
            tmp_w = w
            first_flag = False
            while tmp_w >= 0:
                next_ruler_interval_len = abs(big_ruler_intervals[j].right_value - big_ruler_intervals[j].left_value)
                tmp_w -= next_ruler_interval_len
                if tmp_w >= 0:
                    first_interval =first_interval + [big_ruler_intervals[j]]
                j += 1
                if j >= len(big_ruler_intervals):
                    first_flag = True
                    break
            if first_flag:
                break

            for k in range(i+1,len_big_ruler_intervals):
                if big_ruler_intervals[k].left_open:
                    continue
                j = k
                second_interval = []
                tmp_w = w
                second_flag = False
                while tmp_w >= 0:
                    next_ruler_interval_len = abs(
                        big_ruler_intervals[j].left_value - big_ruler_intervals[j].right_value)
                    tmp_w -= next_ruler_interval_len
                    if tmp_w >= 0:
                        second_interval = second_interval + [big_ruler_intervals[j]]
                    j += 1
                    if j >= len(big_ruler_intervals):
                        second_flag = True
                        break
                if second_flag:
                    break

                if has_same_pattern(second_interval, first_interval) and has_same_facts(second_interval, first_interval,D):
                    varrho_right_dict = defaultdict(list)
                    for ruler in first_interval:
                        for predicate in D:
                            for entity in D[predicate]:
                                if interval_inclusion_intervallist(ruler, D[predicate][entity]):
                                    varrho_right_dict[ruler].append(Atom(predicate, entity))
                    return first_interval, second_interval,  varrho_right_dict
        return None, None, None
    else:
        threshold = 100
        big_ruler_intervals = CR.initial_ruler_intervals[:]
        starting_ruler_interval = None
        for _ in range(threshold + len(CR.initial_ruler_intervals) + 1):
            ruler_interval_len = []
            cnt = 0
            if big_ruler_intervals[-1].left_open:
                new_ruler_interval = Interval(big_ruler_intervals[-1].right_value, big_ruler_intervals[-1].right_value,
                                              False, False)
                if starting_ruler_interval is None:
                    starting_ruler_interval = new_ruler_interval
                if new_ruler_interval.right_value < right_interval_range.right_value:
                    big_ruler_intervals = big_ruler_intervals + [new_ruler_interval]
                elif new_ruler_interval.right_value == right_interval_range.right_value and new_ruler_interval.right_open == right_interval_range.right_open:
                    big_ruler_intervals = big_ruler_intervals + [new_ruler_interval]
                continue

            for i in range(len(big_ruler_intervals)-1, -1, -1):
                if big_ruler_intervals[i].left_open:
                    ruler_interval_len.append(
                        str(abs(big_ruler_intervals[i].right_value - big_ruler_intervals[i].left_value)))
                    cnt += 1
                if cnt >= len(CR.left_dict):
                    break
            tmp_pattern = "#".join(ruler_interval_len)
            current_the_most_right_ruler_interval = big_ruler_intervals[-1]
            next_ruler_interval_len = CR.left_dict[tmp_pattern]
            new_ruler_interval = (Interval(current_the_most_right_ruler_interval.right_value,
                                           current_the_most_right_ruler_interval.right_value + next_ruler_interval_len, True, True))
            if new_ruler_interval.right_value < right_interval_range.right_value:
                big_ruler_intervals = big_ruler_intervals + [new_ruler_interval]
            elif new_ruler_interval.right_value == right_interval_range.right_value and new_ruler_interval.right_open == right_interval_range.right_open:
                big_ruler_intervals = big_ruler_intervals + [new_ruler_interval]

        big_ruler_intervals = big_ruler_intervals[big_ruler_intervals.index(starting_ruler_interval):]

        len_big_ruler_intervals = len(big_ruler_intervals)
        for i in range(0, len_big_ruler_intervals - 1):
            if big_ruler_intervals[i].left_open:
                continue
            j = i
            first_interval = []
            tmp_w = w
            while tmp_w >= 0:
                next_ruler_interval_len = abs(big_ruler_intervals[j].right_value - big_ruler_intervals[j].left_value)
                tmp_w -= next_ruler_interval_len
                if tmp_w >= 0:
                    first_interval = first_interval + [big_ruler_intervals[j]]
                j += 1

            for k in range(i + 1, len_big_ruler_intervals):
                if big_ruler_intervals[k].left_open:
                    continue
                j = k
                second_interval = []
                tmp_w = w
                while tmp_w >= 0:
                    next_ruler_interval_len = abs(
                        big_ruler_intervals[j].left_value - big_ruler_intervals[j].right_value)
                    tmp_w -= next_ruler_interval_len
                    if tmp_w >= 0:
                        second_interval = second_interval + [big_ruler_intervals[j]]
                    j -= 1

                if has_same_pattern(second_interval, first_interval) and has_same_facts(second_interval, first_interval, D):
                    varrho_right_dict = defaultdict(list)
                    for ruler in first_interval:
                        for predicate in D:
                            for entity in D[predicate]:
                                if interval_inclusion_intervallist(ruler, D[predicate][entity]):
                                    varrho_right_dict[ruler].append(Atom(predicate, entity))
                    return first_interval, second_interval, varrho_right_dict


def main(CR, w):
    while True:
        D1 = copy.deepcopy(CR.D)
        materialize(CR.D, rules=CR.Program, K=1)
        D2 = copy.deepcopy(CR.D)
        varrho_left_range, varrho_right_range = find_common_fragment(D1, D2, CR.Program, Interval(CR.min_x, CR.max_x, False, False))
        if varrho_left_range is None or varrho_right_range is None:
            continue
        varrho_left_1, varrho_left_2, varrho_left_dict = find_left_period(D1, varrho_left_range, CR, w)
        if varrho_left_1 is not None:
            varrho_right_1, varrho_right_2, varrho_right_dict = find_right_period(D1, varrho_right_range, CR, w)
            if varrho_right_1 is not None:
                return D1, varrho_left_1, varrho_left_2, varrho_left_dict,  varrho_right_1, varrho_right_2, varrho_right_dict


if __name__ == "__main__":
    raw_data = ["P(mike,mike)@[0,1]"]
    raw_program = ["ALWAYS[0,1]P(X,X):- P(X,X)"]
    w = 1

    raw_data = [
        "P(a,a)@(0,5)",
        "P(a,a)@6",
        "Q(b)@[1,5]",
        "Q(a)@(1,4)",
        "R(a,b)@(0,4)",
        "R(a,b)@(4,7]", "R(b,b)@1",
        "S(a)@0", "S(a)@1", "S(b)@[1,5)"
    ]

    raw_program = [
        "P(X,Y):- Boxminus[0,1]Q(Y), Diamondplus[1,2]S(X)",
        "Boxplus[2,3]R(X,X):-P(X,Y), S(Y)",
        "S(X):-Diamondminus[1,2]Q(y), Diamondminus[3,4]S(X)"
    ]
    w = 8

    raw_data = [
        "P(a,a)@[0,4)", "P(a,a)@(4,5]", "P(a,b)@(3,6]",
        "Q(b)@1", "Q(a)@2",
        "R(a,b)@(0,5]", "R(b,b)@0", "R(b,b)@[5,7)",
        "S(a)@[0,3)", "S(a)@(3,7)", "S(b)@0"
    ]
    raw_program = [
        "P(X,Y):-Boxminus(0,1]Q(Y), Diamondplus[1,2)R(X)",
        "Boxminus(1,2)R(X,X):- P(X,Y), S(Y)",
        "S(X,Y):- Diamondminus(1,2)Q(Y), Diamondminu(2,4]S(X)"
    ]
    w = 8

    raw_data = [
        "P(a,a)@(-2,3]", "P(a,a)@4", "P(a,b)@(-1,3)",
        "A(b)@[-1,4)", "Q(a)@(4,7)", "Q(a)@7",
        "R(a,a)@0", "R(a,b)@[-2,3)", "R(b,b)@(-1,3]",
        "S(a)@2", "S(a)@(-2,5]", "S(b)@[0,5)"
    ]

    raw_program = [
        "P(X,Y):- Boxminus[2]Q(Y), Diamondplus[2]S(X)",
        "Boxminus(1,2)R(X,X):- Diamondplus[1]P(X,Y), S(Y)",
        "S(X):- Diamondminus(1,2)Q(Y), Diamondminus[2]S(X)"
    ]
    w = 6

    raw_data = [
        "P(a,a)@0", "P(a,a)@6", "P(b,b)@(0,6)", "P(a,b)@(0,6)",
        "Q(b)@(-1,3)", "Q(a)@4", "Q(a)@5",
        "R(a,b)@(0,4)", "R(a,b)@(-4,0)", "R(b,b)@(0,4)", "R(b,b)@(4,5)",
        "S(a)@(-2,2)", "S(a)@3", "S(b)@[2,3]"
    ]
    raw_program = [
        "P(X,Y):- Boxplus[1,4]Q(Y), Diamondplus[2,3]S(X), Boxplus[3]P(X,Y)",
        "Boxminus[1]R(X,X):- Diamondplus[1]P(X,Y),Boxplus(1,2)@S(Y)",
        "S(X):- Diamondminus(1,2)Q(Y), Diamondminus[2]@S(X), Diamondminus(2,3)Q(Y)"
    ]
    w = 8

    D = load_dataset(raw_data)
    print("Dataset:")
    print_dataset(D)
    D_index = defaultdict(lambda: defaultdict(list))
    Program = load_program(raw_program)
    print("Program:")
    print([str(rule) for rule in Program])
    print("===========")
    CR = CanonicalRepresentation(D, Program)
    D, varrho_left1, varrho_left2, varrho_left_dict,  varrho_right1, varrho_right2, varrho_right_dict = main(CR,  w)
    print("D^{'}:")
    print("===========")
    print_dataset(D)
    print("Varrho Left:")
    print("===========")
    print([str(interval) for interval in varrho_left1])
    print([str(interval) for interval in varrho_left2])
    for key, value in varrho_left_dict.items():
        print(str(key), [str(item) for item in value])
    print("Varrho Right:")
    print("===========")
    print([str(interval) for interval in varrho_right1])
    print([str(interval) for interval in varrho_right2])

    for key, value in varrho_right_dict.items():
        print(str(key), [str(item) for item in value])








