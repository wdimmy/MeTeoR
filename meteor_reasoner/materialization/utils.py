from meteor_reasoner.graphutil.graph import *


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
