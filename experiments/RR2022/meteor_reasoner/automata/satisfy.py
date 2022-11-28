from meteor_reasoner.automata.utils import *
from meteor_reasoner.materialization.apply import *
from meteor_reasoner.materialization.coalesce import *
from collections import defaultdict


def check_satisfy_dataset(w, D, involved_predicates=[]):
    """
    This function is to check whether all facts in ``D'' have been installed in each of ruler intervals
    of the given Window ``w'' if facts in ruler intervals holds in ``D''.
    Args:
        w (a Window instance):
        D (dictionary of dictionary object): contain all facts
        involved_predicates (a list of str): contain all predicates that are needed to be checked.

    Returns:
        boolean

    """
    for ruler_interval in w.ruler_intervals:
        for predicate in involved_predicates:
            for entity, interval_list in D[predicate].items():
                if interval_intesection_intervallist(ruler_interval, interval_list) and Atom(predicate) not \
                        in w.get_ruler_intervals_literals()[ruler_interval]:
                    return False
    return True


def check_satisfy_program(w, program):
    """
    For each rule in the program, this function checks whether the head exists if all literals(or atoms) in the body exists
    in  each ruler interval of the given Window ``w'' .
    Args:
        w (a Window instance):
        program (a list of rules):

    Returns:
        boolean.

    """

    ruler_intervals_literals = w.ruler_intervals_literals
    for ruler_interval in w.ruler_intervals:
        for rule in program:
            if not ground_rule(rule, ruler_intervals_literals[ruler_interval]):
                return False
    return True


def get_matched_literals(literal, installed_literals):
    """
    Given a literal, this function is to return all literals in ``installed_literals'' that have same predicate and operator(s).
    Args:
        literal (an Atom, Literal or BiLiteral instance):
        installed_literals (a list of Atom, Literal or BiLiteral instances in a ruler interval):

    Returns:
        A list of matched Atom or Literal or BiLiteral instances.

    """
    predicate_matched_literals = []
    for item in installed_literals:
        if isinstance(item, BinaryLiteral) and isinstance(literal, BinaryLiteral):
            if literal.left_literal.get_predicate() == item.left_literal.get_predicate() and literal.right_literal.get_predicate() == item.right_literal.get_predicate():
                if literal.operator == item.operator:
                    predicate_matched_literals.append(item)
        elif isinstance(item, Literal) and isinstance(literal, Literal):
            if literal.get_predicate() == item.get_predicate() and literal.operators == item.operators:
                predicate_matched_literals.append(item)
        elif isinstance(item, Atom) and isinstance(literal, Atom):
            if literal.get_predicate() == item.get_predicate():
                predicate_matched_literals.append(item)

    return predicate_matched_literals


def ground_literal(literal, context, installed_literals):
    """
    Check whether the literal Ground the
    Args:
        literal:
        context:
        installed_literals:

    Returns:

    """
    if isinstance(literal, BinaryLiteral):
        for item in get_matched_literals(literal, installed_literals):
            tmp_context = dict()
            literal_left_entity = literal.left_literal.get_entity()
            item_left_entity = item.left_literal.get_entity()
            left_valid_flag = True

            if literal.left_literal.get_predicate() not in ["Top"]:
                if literal_left_entity is not None:
                    for i in range(len(literal_left_entity)):
                        if literal_left_entity[i].type == "constant":
                            if literal_left_entity[i] != item_left_entity[i]:
                                left_valid_flag = False
                                break
                        else:
                            if literal_left_entity[i].name not in context:
                                tmp_context[literal_left_entity[i].name] = item_left_entity[i]
                            else:
                                if literal_left_entity[i].name != context[literal_left_entity[i].name]:
                                    left_valid_flag = False
                                    break

            if left_valid_flag:
                literal_right_entity = literal.right_literal.get_entity()
                item_right_entity = item.right_literal.get_entity()
                right_valid_flag = True

                if literal.right_literal.get_predicate() not in ["Top"]:
                    if literal_right_entity is not None:
                        for i in range(len(literal_right_entity)):
                            if literal_right_entity[i].type == "constant":
                                if literal_right_entity[i] != item_right_entity[i]:
                                    right_valid_flag = False
                                    break
                            else:
                                if literal_right_entity[i].name not in context:
                                    tmp_context[literal_right_entity[i].name] = item_right_entity[i]
                                else:
                                    if literal_right_entity[i].name != context[literal_right_entity[i].name]:
                                        right_valid_flag = False
                                        break

                if right_valid_flag:
                    yield item, tmp_context
    else:
        entity = literal.get_entity()
        tmp_context = dict()
        valid_flag = True
        for item in get_matched_literals(literal, installed_literals):
            if entity is not None:
                for i in range(len(entity)):
                    if entity[i].type == "constant":
                        if entity[i] != item.get_entity()[i]:
                            valid_flag = False
                            break
                    else:
                        if entity[i].name not in context:
                            tmp_context[entity[i].name] = item.get_entity()[i]
                        else:
                            if item.get_entity()[i] != context[entity[i].name]:
                                valid_flag = False
                                break
            if valid_flag:
                yield item, tmp_context


def ground_rule(rule, installed_literals):
    """
    Grounding the rule and then check whether the grounded head exists when all grounded literals in the body exists.
    Args:
        rule (a Rule instance):
        installed_literals (a list of Literal or Atom instances):
    Returns:
        boolean
    """
    head_predicate = rule.head.get_predicate()
    head_entity = rule.head.get_entity()
    body_literals = rule.body

    def ground_body(global_literal_index, context, flag):
        if global_literal_index == len(body_literals):
            if head_predicate == "Bottom":
                flag[0] = False
                return
            if head_entity is None:
                if rule.head not in installed_literals:
                    flag[0] = False
                return

            ground_head_entity = []
            for i, term in enumerate(head_entity):
                if term.type == "constant":
                    ground_head_entity.append(term)
                else:
                    ground_head_entity.append(context[term.name])

            ground_head_entity = tuple(ground_head_entity)
            ground_head = copy.deepcopy(rule.head)
            ground_head.set_entity(ground_head_entity)
            if ground_head not in installed_literals:
                flag[0] = False
                return
        else:
            for _, tmp_context in ground_literal(body_literals[global_literal_index], context, installed_literals):
                if flag[0]:
                    ground_body(global_literal_index+1, {**context, **tmp_context}, flag)

    flag = [True]
    ground_body(0, {}, flag)
    return flag[0]


def return_must_heads(rule, installed_literals):
    """
    Grounding the rule and then check whether the grounded head exists when all grounded literals in the body exists.
    Args:
        rule (a Rule instance):
        installed_literals (a list of Literal or Atom instances):
    Returns:
        boolean
    """
    head_predicate = rule.head.get_predicate()
    head_entity = rule.head.get_entity()
    body_literals = rule.body

    def ground_body(global_literal_index, context, heads):
        if global_literal_index == len(body_literals):
            if head_predicate == "Bottom":
                heads.add(Atom("Bottom"))

            ground_head_entity = []
            for i, term in enumerate(head_entity):
                if term.type == "constant":
                    ground_head_entity.append(term)
                else:
                    ground_head_entity.append(context[term.name])

            ground_head_entity = tuple(ground_head_entity)
            ground_head = copy.deepcopy(rule.head)
            ground_head.set_entity(ground_head_entity)
            heads.add(ground_head)
        else:
            for _, tmp_context in ground_literal(body_literals[global_literal_index], context, installed_literals):
                ground_body(global_literal_index+1, {**context, **tmp_context}, heads)

    heads = set()
    ground_body(0, {}, heads)
    return heads


def add_p_literals(p_literals, w):
    tmp_D = defaultdict(lambda: defaultdict(list))
    for tmp_ruler_interval in w.ruler_intervals:
        for tmp_atom in w.ruler_intervals_literals[tmp_ruler_interval]:
            if isinstance(tmp_atom, Atom):
                tmp_D[tmp_atom.get_predicate()][tmp_atom.get_entity()].append(tmp_ruler_interval)
    coalescing_d(tmp_D)
    tmp_must_installed_literals = defaultdict(list)
    for literal in p_literals:
        tmp_T = apply(literal, tmp_D)
        if len(tmp_T) != 0:
            tmp_must_installed_literals[literal] = tmp_T

    for ruler_interval in w.ruler_intervals:
        for tmp_literal, tmp_intervals in tmp_must_installed_literals.items():
            for tmp_interval in tmp_intervals:
                if Interval.inclusion(ruler_interval, tmp_interval):
                    w.ruler_intervals_literals[ruler_interval] |= set([tmp_literal])






