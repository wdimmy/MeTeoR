from meteor_reasoner.graphutil.graph import *
from meteor_reasoner.materialization.ground import ground_generator
from meteor_reasoner.materialization.apply import apply


def no_new_facts(delta_new, D, limit):
    for predicate in delta_new:
        for entity in delta_new[predicate]:
            if predicate in D and entity in D[predicate]:
                diff_interval_list = Interval.diff_list(delta_new[predicate][entity], D[predicate][entity])
                if len(diff_interval_list) > 0:
                    for interval in diff_interval_list:
                        new_interval = Interval.intersection(limit, interval)
                        if new_interval is not None:
                            return False
            else:
                for interval in delta_new[predicate][entity]:
                    new_interval = Interval.intersection(limit, interval)
                    if new_interval is not None:
                       return False
    return True


def literal_contain_no_variable(literal):
    if isinstance(literal, Atom):
        if literal.get_predicate() not in ["Bottom", "Top"] and len(literal.entity) == 1 and literal.entity[0].name == "nan":
            return True
    elif isinstance(literal, Literal):
        if isinstance(literal, Literal) and len(literal.atom.entity) == 1 and literal.atom.entity[0].name == "nan":
            return True
    elif isinstance(literal, BinaryLiteral):
        if literal.left_atom.get_predicate() in ["Bottom", "Top"] or (
                len(literal.left_atom.entity) == 1 and literal.left_atom.entity[0].name == "nan"):
            if literal.right_atom.get_predicate() in ["Bottom", "Top"] or (
                    len(literal.right_atom.entity) == 1 and literal.right_atom.entity[0].name == "nan"):
                return True


def split_rules_predicates(program):
    """
    This function split all rules in the given program into non-recursive rules and recursive rules.
    Besides, this function also split all predicates in the given program into involved predicates and automata predicated.

    None-recursive rules: rules needed to be completely materialized before running the automata
    Recursive rules: rules that can not be completely materialized
    Involved predicates refer to invariable predicates but are needed to be considered in the Automata construction
    Automata predicates refer to variable predicates in the Automata construction whose states are uncertain
    Args:
        program (list of Rule instances):

    Returns:
        set, set, set, set

    """
    graph = Graph(program)

    non_recursive_rules, automata_rules = graph.split_rules("a1:FullProfessor")
    involved_predicates = set()
    automata_predicates = set()

    for rule in non_recursive_rules:
        involved_predicates.add(rule.head.get_predicate())
        for literal in rule.body:
            if isinstance(literal, BinaryLiteral):
                if literal.left_atom.get_predicate() not in ["Bottom", "Top"]:
                    involved_predicates.add(literal.left_atom.get_predicate())
                if literal.right_atom.get_predicate() not in ["Bottom", "Top"]:
                    involved_predicates.add(literal.right_atom.get_predicate())
            else:
                if literal.get_predicate() not in ["Bottom", "Top"]:
                    involved_predicates.add(literal.get_predicate())

    for rule in automata_rules:
        automata_predicates.add(rule.head.get_predicate())
        involved_predicates.add(rule.head.get_predicate())
        for literal in rule.body:
            if isinstance(literal, BinaryLiteral):
                if literal.left_atom.get_predicate() not in ["Bottom", "Top"]:
                    involved_predicates.add(literal.left_atom.get_predicate())
                    automata_predicates.add(rule.head.get_predicate())
                if literal.right_atom.get_predicate() not in ["Bottom", "Top"]:
                    involved_predicates.add(literal.right_atom.get_predicate())
                    automata_predicates.add(rule.head.get_predicate())
            else:
                if literal.get_predicate() not in ["Bottom", "Top"]:
                    involved_predicates.add(literal.get_predicate())
                    automata_predicates.add(rule.head.get_predicate())

    return (non_recursive_rules, automata_rules, involved_predicates, automata_predicates)


def entail_same_nonrecursive_predicates(D, delta_new, non_predicates):
    for predicate in delta_new:
        if predicate in non_predicates:
            if predicate not in D:
                 return False
            for entity in delta_new[predicate]:
                   if entity in D[predicate]:
                       if not Interval.list_inclusion(delta_new[predicate][entity], D[predicate][entity]):
                            return False
                   else:
                       return False
    return True


def pre_calculate_threshold(rules, propagation, D, D_index, non_predicates):
    observed_rules = defaultdict(list)
    if propagation == 1:
        for rule in rules:
            min_right = float("inf")
            for tmp_literal in rule.body:
                literal = copy.deepcopy(tmp_literal)
                intervals = []
                if isinstance(literal, BinaryLiteral):
                    left_predicate = literal.left_literal.get_predicate()
                    right_predicate = literal.right_literal.get_predicate()

                    if left_predicate in ["Bottom", "Top"]:
                        if right_predicate not in non_predicates:
                            continue # it is not recursive
                        for tmp_entity, tmp_context in ground_generator(literal.right_literal, dict(), D, D_index):
                            literal.set_entity([tmp_entity])
                            tmp_interval_list = apply(literal, D)
                            intervals = intervals + tmp_interval_list

                    elif right_predicate in ["Bottom", "Top"]:
                        if left_predicate not in non_predicates:
                            continue
                        for tmp_entity, tmp_context in ground_generator(literal.left_literal, dict(), D, D_index):
                            literal.set_entity([tmp_entity])
                            tmp_interval_list = apply(literal, D)
                            intervals = intervals + tmp_interval_list
                    else:
                        if left_predicate not in non_predicates or right_predicate not in non_predicates:
                            continue
                        for left_entity, tmp_context1 in ground_generator(literal.left_literal, dict(), D):
                            for right_entity, tmp_context2 in ground_generator(literal.right_literal, tmp_context1, D):
                                literal.set_entity([left_entity, right_entity])
                                tmp_interval_list = apply(literal, D)
                                intervals = intervals + tmp_interval_list
                else:
                    if literal.get_predicate() not in non_predicates:
                        continue
                    for tmp_entity, tmp_context in ground_generator(literal, dict(), D, D_index):
                        literal.set_entity(tmp_entity)
                        tmp_interval_list = apply(literal, D)
                        intervals = intervals + tmp_interval_list

                if len(intervals) != 0:
                    tmp_max_right = max([item.right_value for item in intervals])
                    min_right = min(tmp_max_right, min_right)
                else:
                    rules.remove(rule)
                    break

            if min_right != float("inf"):
                observed_rules[min_right].append(rule)

    # backward propagation
    elif propagation == 2:
        for rule in rules:
            max_left = float("-inf")
            for literal in rule.body:
                intervals = []
                if isinstance(literal, BinaryLiteral):
                    left_predicate = literal.left_literal.get_predicate()
                    right_predicate = literal.right_literal.get_predicate()

                    if left_predicate in ["Bottom", "Top"]:
                        if right_predicate not in non_predicates:
                            continue  # it is not recursive
                        for tmp_entity, tmp_context in ground_generator(literal.right_literal, dict(), D, D_index):
                            literal.set_entity([tmp_entity])
                            tmp_interval_list = apply(literal, D)
                            intervals = intervals + tmp_interval_list

                    elif right_predicate in ["Bottom", "Top"]:
                        if left_predicate not in non_predicates:
                            continue
                        for tmp_entity, tmp_context in ground_generator(literal.left_literal, dict(), D, D_index):
                            literal.set_entity([tmp_entity])
                            tmp_interval_list = apply(literal, D)
                            intervals = intervals + tmp_interval_list
                    else:
                        if left_predicate not in non_predicates or right_predicate not in non_predicates:
                            continue
                        for left_entity, tmp_context1 in ground_generator(literal.left_literal, dict(), D):
                            for right_entity, tmp_context2 in ground_generator(literal.right_literal, tmp_context1, D):
                                literal.set_entity([left_entity, right_entity])
                                tmp_interval_list = apply(literal, D)
                                intervals = intervals + tmp_interval_list
                else:
                    for tmp_entity, tmp_context in ground_generator(literal, dict(), D, D_index):
                        literal.set_entity([tmp_entity])
                        tmp_interval_list = apply(literal, D)
                        intervals = intervals + tmp_interval_list

                if len(intervals) != 0:
                    tmp_min_left = min([item.left_value for item in intervals])
                    min_right = max(tmp_min_left, max_left)
                else:
                    rules.remove(rule)
                    break

            if max_left != float("-inf"):
                observed_rules[max_left].append(rule)

    observed_rules = sorted(observed_rules.items(), key=lambda item: item[0])
    return observed_rules

