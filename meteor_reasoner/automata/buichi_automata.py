from itertools import chain, combinations
from meteor_reasoner.automata.window import *
from meteor_reasoner.automata.satisfy import *
from meteor_reasoner.materialization.coalesce import *
from meteor_reasoner.automata.guess import *
from meteor_reasoner.materialization.apply import *


class BuchiAutomata:
    def __init__(self, D, program, unbounded_literals, p_literals, involved_predicates, automata_predicates,left_dict,
                 right_dict, x, z, gcd, points):
        self.D = D
        self.program = program
        self.x = x
        self.z = z
        self.gcd = gcd
        self.points = points
        self.p_literals = p_literals

        self.unbounded_literals = unbounded_literals
        self.window_ruler_interval_list = []

        self.involved_predicates = involved_predicates
        self.automata_predicates = automata_predicates

        self.left_window_pattern_dict = left_dict
        self.right_window_pattern_dict = right_dict

        self.window_must_include_static = defaultdict(list)
        self.variable_literals = set()

        self.left_conditions = self.get_conditions("left")
        self.right_conditions = self.get_conditions("right")

    def get_conditions(self, d):
        F = set()
        for literal in self.unbounded_literals:
            if d == "left":
                if isinstance(literal, BinaryLiteral):
                    if literal.operator.interval.right_value == float("inf") and literal.operator.name == "Since":
                        F.add(literal)
                else:
                    if isinstance(literal, Literal) and len(literal.operators) == 1 and (
                            literal.operators[0].interval.right_value == float("inf")) and literal.operators[0].name == "Boxminus":
                        F.add(literal)

            else:
                if isinstance(literal, BinaryLiteral):
                    if literal.operator.interval.right_value == float("inf") and literal.operator.name == "Until":
                        F.add(literal)
                else:
                    if isinstance(literal, Literal) and len(literal.operators) == 1 and (
                            literal.operators[0].interval.right_value == float("inf")) and literal.operators[0].name == "Boxplus":
                        F.add(literal)
        return F

    def build_prior(self, must_literals):
        initial_window_len, initial_window_ruler_intervals = get_initial_ruler_intervals(self.points,
                                                                                         left_border=-2 * self.x - 2 * self.z,
                                                                                         right_border=2 * self.x + 2 * self.z,
                                                                                         gcd=self.gcd)
        self.window_ruler_interval_list = initial_window_ruler_intervals
        for ruler_interval in initial_window_ruler_intervals:
            self.window_must_include_static[ruler_interval] = []

        for ruler_interval in initial_window_ruler_intervals:
            for literal in must_literals:
                if interval_intesection_intervallist(ruler_interval, must_literals[literal]):
                    self.window_must_include_static[ruler_interval].append(literal)
                if isinstance(literal, BinaryLiteral):
                    if literal.left_atom.get_predicate() in self.automata_predicates or literal.right_atom.get_predicate() in self.automata_predicates:
                        self.variable_literals.add(literal)
                else:
                    if literal.get_predicate() in self.automata_predicates:
                        self.variable_literals.add(literal)

            for predicate in self.involved_predicates:
                if type(self.D[predicate]) == list:
                    if interval_intesection_intervallist(ruler_interval, self.D[predicate]):
                        self.window_must_include_static[ruler_interval].append(Atom(predicate))
                    if predicate in self.automata_predicates:
                        self.variable_literals.add(Atom(predicate))
                else:
                    for entity in self.D[predicate]:
                        if interval_intesection_intervallist(ruler_interval, self.D[predicate][entity]):
                            self.window_must_include_static[ruler_interval].append(
                                Atom(predicate, entity))
                        if predicate in self.automata_predicates:
                            self.variable_literals.add(Atom(predicate, entity))

    def get_unbounded_literals_for_window(self, atom, ruler_interval, direction):
        """
        Return a list of possible unbounded literals for the given ruler_interval based
        on the pre-materialized results in [-2x-2z, 2x+2z]
        Args:
            atom (Atom instance):
            ruler_interval (Interval instance):
            direction (str): ``left'' or ``right''

        Returns:
            list of Literal instances

        """
        if ruler_interval not in self.window_must_include_static:
            return []
        unbounded_literals = []
        start_i = self.window_ruler_interval_list.index(ruler_interval)
        if direction == "left":
            for i in range(start_i, -1, -1):
                next_ruler_interval = self.window_ruler_interval_list[i]
                if atom not in self.window_must_include_static[next_ruler_interval]:
                    break
            else:
                open_operator = Operator("Boxminus", Interval(0, float("inf"), True, True))
                closed_operator = Operator("Boxminus", Interval(0, float("inf"), False, True))
                unbounded_literals.append(Literal(atom, [open_operator]))
                unbounded_literals.append(Literal(atom, [closed_operator]))
        else:
            for i in range(start_i, len(self.window_ruler_interval_list)):
                next_ruler_interval = self.window_ruler_interval_list[i]
                if atom not in self.window_must_include_static[next_ruler_interval]:
                    break
            else:
                open_operator = Operator("Boxplus", Interval(0, float("inf"), True, True))
                closed_operator = Operator("Boxplus", Interval(0, float("inf"), False, True))
                unbounded_literals.append(Literal(atom, [open_operator]))
                unbounded_literals.append(Literal(atom, [closed_operator]))

        return unbounded_literals

    def get_literals_for_ruler_interval(self, ruler_interval, direction, last_ruler_interval_literals=None):
        """
        Return a list of Atom or Literal instances for a given ruler interval
        Args:
            ruler_interval (an Interval instance):

        Returns:
            list of Atoms or Literal instances

        """
        static_must_literals = set(self.window_must_include_static[ruler_interval])
        unbounded_must_literals = set()
        if last_ruler_interval_literals is not None:
            if direction == "left":
                for literal in last_ruler_interval_literals:
                    if isinstance(literal, Literal) and len(literal.operators) == 0 and literal.operators[ 0].name == "Boxminus" and\
                            literal.operators[0].interval.right_value == float("inf"):
                        unbounded_must_literals.add(literal)
                        unbounded_must_literals.add(literal.atom)
            else:
                for literal in last_ruler_interval_literals:
                    if isinstance(literal, Literal) and len(literal.operators) == 0 and literal.operators[ 0].name == "Boxplus" and \
                            literal.operators[0].interval.right_value == float("inf"):

                        unbounded_must_literals.add(literal)
                        unbounded_must_literals.add(literal.atom)


        for com_literals in chain.from_iterable(combinations(self.variable_literals, r)
                                                   for r in range(len(self.variable_literals) + 1)):

            yield set(com_literals) | static_must_literals | unbounded_must_literals

    def get_literals_for_ruler_interval_with_visited(self, ruler_interval, direction, visited, last_ruler_interval_literals=None):
        """
        Return a list of Atom or Literal instances for a given ruler interval
        Args:
            ruler_interval (an Interval instance):

        Returns:
            list of Atoms or Literal instances

        """
        static_must_literals = self.window_must_include_static[ruler_interval]
        unbounded_must_literals = []
        for literal in static_must_literals:
            if isinstance(literal, Atom) and literal not in visited:
                if direction == "left":
                    res = self.get_unbounded_literals_for_window(literal, ruler_interval, "left")
                    if len(res) > 0:
                        visited[literal] = 1
                        unbounded_must_literals += res
                else:
                    res = self.get_unbounded_literals_for_window(literal, ruler_interval, "right")
                    if len(res) > 0:
                        visited[literal] = 1
                        unbounded_must_literals += res

        if last_ruler_interval_literals is not None:
            if direction == "left":
                for literal in last_ruler_interval_literals:
                    if isinstance(literal, Literal) and len(literal.operators) == 1 and literal.operators[0].name == "Boxminus" and \
                            literal.operators[0].interval.right_value == float("inf"):
                        unbounded_must_literals.append(literal)
                        unbounded_must_literals.append(literal.atom)
            else:
                for literal in last_ruler_interval_literals:
                    if isinstance(literal, Literal) and len(literal.operators) == 1 and literal.operators[0].name == "Boxplus" and \
                            literal.operators[0].interval.right_value == float("inf"):
                        unbounded_must_literals.append(literal)
                        unbounded_must_literals.append(literal.atom)

        for com_literals in chain.from_iterable(combinations(self.variable_literals, r)
                                                   for r in range(len(self.variable_literals) + 1)):

            yield list(com_literals) + static_must_literals + unbounded_must_literals

    def get_literals_for_window(self, window_ruler_interval_list,  visited, direction):
        def helper(index, result):
            if index == len(window_ruler_interval_list):
                window_ruler_intervals_literals = dict()
                for key, value in result.items():
                    window_ruler_intervals_literals[key] = value

                yield AutomataWindow(window_ruler_interval_list, window_ruler_intervals_literals,
                                     self.left_window_pattern_dict, self.right_window_pattern_dict)
                return

            else:
                last_interval_literals = None
                if index != 0:
                    last_interval_literals = result[window_ruler_interval_list[index-1]]

                for com_literals in self.get_literals_for_ruler_interval_with_visited(window_ruler_interval_list[index], direction, visited, last_interval_literals):
                    yield from helper(index+1, {**result, **{window_ruler_interval_list[index]: list(com_literals)}})

        yield from helper(0, {})

    def check_inconsistency(self):
        """
        This function check whether the given D and Program are consistency by running Buichi Automata.
        Returns:
           boolean
        """
        initial_window_len, initial_window_ruler_intervals =get_initial_ruler_intervals(
            [- self.x - self.z, -self.x + self.z])
        for l_min, r_min in self.search_window(initial_window_ruler_intervals):
            if self.search(l_min, "left", self.F_left):
                if self.search(r_min, "right", self.F_right):
                    return True
        return False

    def search_window(self, initial_window_ruler_intervals):
        """
        Instead of directly checking the window=[-x-z, -x+z, we start from
        the minimum window=[-x-z, -x+z], and then move in a rightward direction
        at a gcd step until the window reach to x+z. Then return two windows:
        lmin=[-x-z, -x+z], rmin=[x-z, x+z]
        Args:
            initial_window_ruler_intervals (list of Interval instances):

        Returns:
            (AutomataWindow instance, AutomataWindow instance)

        """
        visited = dict()
        def guess_help(w, w0):
            while w.ruler_intervals[-1] != Interval(self.x+self.z, self.x+self.z, False, False):
                last_interval_literals = w.ruler_intervals_literals[w.ruler_intervals[-1]]
                w.move_right()
                last_interval = w.ruler_intervals[-1]
                for com_literals in self.get_literals_for_ruler_interval_with_visited(last_interval, "right", visited, last_interval_literals):
                    w.ruler_intervals_literals[last_interval] = com_literals
                    if not self.check_satisfy(w):
                        return None
                    else:
                        break
            return (w0, w)

        # This is a recursive version
        def helper(stack):

            if len(stack) > 0 and stack[-1].ruler_intervals[-1] == Interval(self.x+self.z, self.x+self.z, False, False):
                yield stack[0], stack[-1]
                return
            last_w = stack[-1]
            new_w = copy.deepcopy(last_w)
            last_interval_literals = new_w.ruler_intervals_literals[new_w.ruler_intervals[-1]]
            new_w.move_right()
            last_interval = new_w.ruler_intervals[-1]

            for com_literals in self.get_literals_for_ruler_interval_with_visited(last_interval, "right", visited, last_interval_literals):
                new_w.ruler_intervals_literals[last_interval] += com_literals
                if self.check_satisfy(new_w):
                    yield from helper(stack+[new_w])
        flag = True
        for w in self.get_literals_for_window(initial_window_ruler_intervals, visited, "right"):
            if self.check_satisfy(w):
                if flag:
                    res = guess_help(copy.deepcopy(w), copy.deepcopy(w))
                    flag = False
                    if res is not None:
                        yield res[0], res[1]
                    else:
                        yield from helper([w])

                else:
                    yield from helper(w, copy.deepcopy(w))

    def consistency_check(self):
        """
        Returns:
           boolean
        """
        initial_window_len, initial_window_ruler_intervals = get_initial_ruler_intervals(self.points,
            left_border=- self.x - self.z, right_border= -self.x + self.z, gcd=self.gcd)

        for l_min, r_min in self.search_window(initial_window_ruler_intervals):
            left_flag = self.search(l_min, "left", self.left_conditions)
            if left_flag:
                right_flag = self.search(r_min, "right", self.right_conditions)
                if right_flag:
                    return True
        return False

    def search(self, W_0, d, F):
        T = list()
        R = set()
        label = defaultdict(set)
        T.append(W_0)

        while len(T) > 0:
            W = T[-1]
            increase_flag = True
            while increase_flag:
                for tmp_interval in W.ruler_intervals:
                    if len(W.ruler_intervals_literals[tmp_interval]) != 0:
                        break
                else:
                    return True
                if d == "left":
                    W_prime = copy.deepcopy(W)
                    last_interval_literals = W_prime.ruler_intervals_literals[W_prime.ruler_intervals[-1]]
                    W_prime.move_left()
                    first_interval = W_prime.ruler_intervals[0]
                    for com_literals in self.get_literals_for_ruler_interval(first_interval,d, last_interval_literals):
                        W_prime.ruler_intervals_literals[first_interval] = com_literals
                        if self.check_satisfy(W_prime) and W_prime not in T + list(R):
                            T.append(W_prime)
                            label[W_prime] = set()
                            W = W_prime
                            break
                    else:
                        increase_flag = False
                else:
                    W_prime = copy.deepcopy(W)
                    last_interval_literals = W_prime.ruler_intervals_literals[W_prime.ruler_intervals[-1]]
                    W_prime.move_right()
                    last_interval = W_prime.ruler_intervals[-1]
                    for com_literals in self.get_literals_for_ruler_interval(last_interval, d, last_interval_literals):
                        W_prime.ruler_intervals_literals[last_interval] = com_literals
                        if self.check_satisfy(W_prime) and W_prime not in T + list(R):
                            T.append(W_prime)
                            label[W_prime] = set()
                            W = W_prime
                            break
                        else:
                            increase_flag = False
                            break
                    else:
                        increase_flag = False
            subset_conditions = set()
            if (W in label and len(label[W]) != 0) or window_contain_accepting_conditions(F, W, subset_conditions, d):
                label[W] = label[W].union(subset_conditions)
                if label[W] == F:
                    return True
                self.propagate([W], label[W], T, R, label, d)
                if label[W] == F:
                    return True
            R.add(W)
            T.pop()

        return False

    def propagate(self, N, P, T, R, label, d):
        while len(N) != 0:
            W = N.pop()
            if d == "left":
                W_prime = copy.deepcopy(W)
                last_interval_literals = W_prime.ruler_intervals_literals[W_prime.ruler_intervals[-1]]
                W_prime.move_left()

                first_interval = W_prime.ruler_intervals[0]
                for subset_literal in self.get_literals_for_ruler_interval(first_interval, d, last_interval_literals):
                    W_prime.ruler_intervals_literals[first_interval] = subset_literal

                    if self.check_satisfy(W_prime) and W_prime in T + list(R):
                        if self.can_contribute(P, label[W_prime]):
                            N.append(W_prime)
                            label[W_prime] = label[W_prime].union(P)
            else:
                W_prime = copy.deepcopy(W)
                last_interval_literals = W_prime.ruler_intervals_literals[W_prime.ruler_intervals[-1]]
                W_prime.move_right()

                last_interval = W_prime.ruler_intervals[-1]
                for subset_literal in self.get_literals_for_ruler_interval(last_interval, d, last_interval_literals):
                    W_prime.ruler_intervals_literals[last_interval] = subset_literal
                    if self.check_satisfy(W_prime) and W_prime in T + list(R):
                        if self.can_contribute(P, label[W_prime]):
                            N.append(W_prime)
                            label[W_prime] = label[W_prime].union(P)

    def can_contribute(self, a, b):
        for item in a:
            if item not in b:
                return True
        return False

    def check_satisfy(self, w):
        if not check_satisfy_dataset(w, self.D):
            return False
        ruler_intervals_literals = w.ruler_intervals_literals
        ruler_intervals = w.ruler_intervals

        guess_D = defaultdict(lambda: defaultdict(list))
        binary_literals = []

        for ruler_interval in ruler_intervals:
            for literal in ruler_intervals_literals[ruler_interval]:
                if isinstance(literal, Atom):
                    if literal.get_entity() is None:
                        if literal.get_predicate() not in guess_D:
                            guess_D[literal.get_predicate()] = [ruler_interval]
                        else:
                            guess_D[literal.get_predicate()].append(ruler_interval)
                    else:
                        guess_D[literal.get_predicate()][literal.get_entity()].append(ruler_interval)
                elif isinstance(literal, BinaryLiteral):
                    binary_literals.append(literal)

                elif isinstance(literal, Literal):
                    if literal.operators[0].name == "Boxplus":
                        interval = Interval.add(ruler_interval, literal.operators[0].interval)
                        if literal.get_entity() is None:
                            if literal.get_predicate() not in guess_D:
                                guess_D[literal.get_predicate()] = [interval]
                            else:
                                guess_D[literal.get_predicate()].append(interval)
                        else:
                            if literal.get_predicate() not in guess_D:
                                guess_D[literal.get_predicate()][literal.get_entity()] = [interval]
                            else:
                                guess_D[literal.get_predicate()][literal.get_entity()].append(interval)

                    elif literal.operators[0].name == "Boxminus":
                        interval = Interval.sub(ruler_interval, literal.operators[0].interval)
                        if literal.get_entity() is None:
                            if literal.get_predicate() not in guess_D:
                                guess_D[literal.get_predicate()] = [interval]
                            else:
                                guess_D[literal.get_predicate()].append(interval)
                        else:
                            if literal.get_predicate() not in guess_D:
                                guess_D[literal.get_predicate()][literal.get_entity()] = [interval]
                            else:
                                guess_D[literal.get_predicate()][literal.get_entity()].append(interval)

                else:
                    raise Exception("Please convert Diamondminus or Diamondplus to Boxminus or Boxplus")


        if len(binary_literals) != 0:
            guess_points, left_right_literals = generate_guess_points(w, binary_literals, ruler_intervals, self.z, self.gcd)
            # guess existing intervals
            for literal in left_right_literals:
                if literal.get_predicate() in self.D and literal.get_entity() is None:
                    guess_D[literal.get_predicate()] = D[literal.get_predicate()]
                elif literal.get_predicate() in self.D and literal.get_entity() in self.D[literal.get_predicate()]:
                    guess_D[literal.get_predicate()][literal.get_entity()] = self.D[literal.get_predicate()][literal.get_entity()]
                else:
                    # guess an interval from guess_points
                    pass

        guess_D = coalescing_d(guess_D)
        for literal in self.p_literals:
            T = apply(literal, guess_D)
            if len(T) == 0:
                for ruler_interval in ruler_intervals:
                    if literal in ruler_intervals_literals[ruler_interval]:
                        return False
            else:
                for ruler_interval in ruler_intervals:
                    if interval_intesection_intervallist(ruler_interval, T) and literal not in \
                            ruler_intervals_literals[ruler_interval]:
                        return False

        prgram_flag = check_satisfy_program(w, program=self.program)
        return prgram_flag





























