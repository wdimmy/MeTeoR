from meteor_reasoner.classes.rule import *
from meteor_reasoner.materialization.ground import *
from meteor_reasoner.classes.term import Term
from collections import defaultdict
from meteor_reasoner.materialization.index_build import build_index
from meteor_reasoner.utils.operate_dataset import print_dataset
from meteor_reasoner.materialization.coalesce import coalescing_d
from decimal import Decimal


def inclusion_check(D, rule, i, context, records, single=False):
    head_literal = copy.deepcopy(rule.head)

    if isinstance(head_literal, BinaryLiteral):
        left_head_literal = head_literal.left_literal
        right_head_literal = head_literal.right_literal

        left_predicate = left_head_literal.get_predicate()
        right_predicate = right_head_literal.get_predicate()

        if left_predicate not in D or right_predicate not in D:
            return False

        left_head_entity = left_head_literal.get_entity()
        right_head_entity = right_head_literal.get_entity()
        left_head_replaced_entity = []
        for term in left_head_entity:
            if term.type == "variable":
                term.type = "constant"
                term.name = context[term.name]
                left_head_replaced_entity.append(term)
            else:
                left_head_replaced_entity.append(term)
        right_head_replaced_entity = []
        for term in right_head_entity:
            if term.type == "variable":
                term.type = "constant"
                term.name = context[term.name]
                right_head_replaced_entity.append(term)
            else:
                right_head_replaced_entity.append(term)
        left_head_replaced_entity = tuple(left_head_replaced_entity)
        right_head_replaced_entity = tuple(right_head_replaced_entity)
        head_literal.left_literal.set_entity(left_head_replaced_entity)
        head_literal.right_literal.set_entity(right_head_replaced_entity)
        if left_head_replaced_entity not in D[left_predicate] or right_head_replaced_entity not in D[right_predicate]:
            return False

    else:
        head_predicate = head_literal.get_predicate()
        if head_predicate not in D:
            return False
        head_entity = head_literal.get_entity()
        head_replaced_entity = []
        for term in head_entity:
            if term.type == "variable":
                term.type = "constant"
                term.name = context[term.name]
                head_replaced_entity.append(term)
            else:
                head_replaced_entity.append(term)
        head_replaced_entity = tuple(head_replaced_entity)
        head_literal.set_entity(tuple(head_replaced_entity))
        if head_replaced_entity not in D[head_predicate]:
            return False

    prefix_literals = [head_literal]
    if single:
        start = i
    else:
        start = 0

    for literal in rule.body[start:i+1]:
        ground_literal = copy.deepcopy(literal)
        if isinstance(ground_literal, BinaryLiteral):
            left_head_literal = ground_literal.left_literal
            right_head_literal = ground_literal.right_literal
            left_head_entity = left_head_literal.get_entity()
            right_head_entity = right_head_literal.get_entity()
            left_head_replaced_entity = []
            for term in left_head_entity:
                if term.type == "variable":
                    term.type = "constant"
                    term.name = context[term.name]
                    left_head_replaced_entity.append(term)
                else:
                    left_replaced_entity.append(term)
            right_replaced_entity = []
            for term in right_head_entity:
                if term.type == "variable":
                    term.type = "constant"
                    term.name = context[term.name]
                    right_replaced_entity.append(term)
                else:
                    right_head_replaced_entity.append(term)

            left_replaced_entity = tuple(left_replaced_entity)
            right_replaced_entity = tuple(right_replaced_entity)
            ground_literal.left_literal.set_entity(left_replaced_entity)
            ground_literal.right_literal.set_entity(right_replaced_entity)

        else:
            body_entity = ground_literal.get_entity()
            body_replaced_entity = []
            for term in body_entity:
                if term.type == "variable":
                    term.type = "constant"
                    term.name = context[term.name]
                    body_replaced_entity.append(term)
                else:
                    body_replaced_entity.append(term)
            body_replaced_entity = tuple(body_replaced_entity)
            ground_literal.set_entity(body_replaced_entity)

        if tuple(prefix_literals+[ground_literal]) in records:
            return True
        prefix_literals.append(ground_literal)

    head_intervals = reverse_apply(head_literal, D)
    flag = False
    body_intervals = [Interval(Decimal("-inf"), Decimal("inf"), True, True)]
    for i, literal in enumerate(prefix_literals):
        if i == 0:
            continue # at least two literals
        t = apply(literal, D)
        body_intervals = Interval.list_union(body_intervals, t)
        if len(body_intervals) == 0 or Interval.list_inclusion(body_intervals, head_intervals):
            flag = True
            records[tuple(prefix_literals[:i+1])] = True # can add some permutation, TOD
            break
    return flag


def optimized_seminaive_join(rule, D,  delta_old, delta_new,  D_index=None, records= {}, non_predicates=dict()):
    """
    This function implement the join operator when variables exist in the body of the rule.
    Args:
        rule (a Rule instance):
        Delta (a dictionary object): store new materialized results.
        D (a dictionary object): a global variable storing all facts.

    Returns:
        None
    """
    head_entity = rule.head.get_entity()
    head_predicate = rule.head.get_predicate()
    literals = rule.body + rule.negative_body

    def ground_body(global_literal_index, visited, delta, context):
        if global_literal_index == len(literals):
            T = []
            for i in range(len(rule.body)):
                grounded_literal = copy.deepcopy(literals[i])
                if isinstance(grounded_literal, BinaryLiteral):
                    grounded_literal.set_entity(delta[i])
                else:
                    if grounded_literal.get_predicate() not in ["Bottom", "Top"]:
                        grounded_literal.set_entity(delta[i][0])
                if i == visited:
                   t = apply(grounded_literal, delta_old)
                else:
                   t = apply(grounded_literal, D)
                if len(t) == 0:
                    break
                else:
                    T.append(t)
            n_T = []
            for i in range(len(rule.body), len(literals)):
                grounded_literal = copy.deepcopy(literals[i])
                if isinstance(grounded_literal, BinaryLiteral):
                    grounded_literal.set_entity(delta[i])
                else:
                    if grounded_literal.get_predicate() not in ["Bottom", "Top"]:
                        grounded_literal.set_entity(delta[i][0])
                t = apply(grounded_literal, D)
                if len(t) == 0:
                    break
                else:
                    n_T.append(t)

            if len(n_T) > 0 and len(n_T) == len(rule.negative_body_atoms):
                n_T = interval_merge(T)
            else:
                n_T = []

            if head_entity is not None:
                replaced_head_entity = []
                for term in head_entity:
                    if term.type == "constant":
                        replaced_head_entity.append(term)
                    else:
                        if term.name not in context:
                            raise ValueError("Head variables in Rule({}) do not appear in the body".format(str(rule)))
                        else:
                            new_term = Term.new_term(context[term.name])
                            replaced_head_entity.append(new_term)
                replaced_head_entity = tuple(replaced_head_entity)
            else:
                replaced_head_entity = head_entity

            if len(T) == len(literals):
                T = interval_merge(T)
                exclude_t = []
                if len(T) != 0 and len(n_T) != 0:
                    exclude_t = interval_merge([T, n_T])
                if len(exclude_t) != 0:
                    T = Interval.diff(T, exclude_t)

                if len(T) != 0:
                    if not isinstance(rule.head, Atom):
                        tmp_D = defaultdict(lambda: defaultdict(list))
                        tmp_D[head_predicate][replaced_head_entity] = T
                        tmp_head = copy.deepcopy(rule.head)
                        tmp_head.set_entity(replaced_head_entity)
                        T = reverse_apply(tmp_head, tmp_D)

                    delta_new[head_predicate][replaced_head_entity] = delta_new[head_predicate][
                                                                          replaced_head_entity] + T

        elif global_literal_index == visited:
            ground_body(global_literal_index+1, visited, delta, context)

        else:
            current_literal = copy.deepcopy(literals[global_literal_index])
            if not isinstance(current_literal, BinaryLiteral):
                if current_literal.get_predicate() in ["Bottom", "Top"]:
                    ground_body(global_literal_index+1, delta, context)
                else:
                    for tmp_entity, tmp_context in ground_generator(current_literal, context, D, D_index):
                        tmp_delata = {global_literal_index: [tmp_entity]}
                        # check whether it is needed to continue to do the evaluation
                        if current_literal.get_predicate() in non_predicates:
                            if not contain_variable_after_replace(head_entity, {**context, **tmp_context}):  # head can be grounded
                                if inclusion_check(D, rule, global_literal_index, records=records, context={**context, **tmp_context}):
                                    continue

                        ground_body(global_literal_index+1,  visited, {**delta, **tmp_delata}, {**context, **tmp_context})

            else:
                left_predicate = current_literal.left_literal.get_predicate()
                right_predicate = current_literal.right_literal.get_predicate()

                if left_predicate in ["Bottom", "Top"]:
                    for tmp_entity, tmp_context in ground_generator(current_literal.right_literal, context,  D, D_index):
                        tmp_delta = {global_literal_index: [tmp_entity]}

                        if right_predicate.get_predicate() in non_predicates:
                            if not contain_variable_after_replace(head_entity,
                                                                  {**context, **tmp_context}):  # head can be grounded
                                if inclusion_check(D, rule, global_literal_index, records=records,
                                                   context={**context, **tmp_context}):
                                    continue

                        ground_body(global_literal_index + 1, visited, {**delta, **tmp_delta}, {**context, **tmp_context})

                elif right_predicate in ["Bottom", "Top"]:
                    for tmp_entity, tmp_interval, tmp_context in ground_generator(current_literal.left_literal, context, D, D_index):
                        tmp_delta = {global_literal_index: [tmp_entity]}
                        if left_predicate.get_predicate() in non_predicates:
                            if not contain_variable_after_replace(head_entity,
                                                                  {**context, **tmp_context}):  # head can be grounded
                                if inclusion_check(D, rule, global_literal_index, records=records,
                                                   context={**context, **tmp_context}):
                                    continue

                        ground_body(global_literal_index + 1,visited, {**delta, **tmp_delta}, {**context, **tmp_context})

                else:
                    for left_entity, left_interval, tmp_context1 in ground_generator(current_literal.left_literal, context, D):
                        for right_entity, right_interval, tmp_context2 in ground_generator(current_literal.right_literal,{**context, **tmp_context1}, D):
                            tmp_delta = {global_literal_index: [left_entity, right_entity]}
                            if right_predicate.get_predicate() in non_predicates and left_predicate in non_predicates:
                                if not contain_variable_after_replace(head_entity, {**context, **tmp_context1, **tmp_context2}):  # head can be grounded
                                    if inclusion_check(D, rule, global_literal_index, records=records,
                                                       context={**context, **tmp_context1, **tmp_context2}):
                                        continue

                            ground_body(global_literal_index + 1, visited, {**delta, **tmp_delta}, {**context, **tmp_context1, **tmp_context2})

    for predicate in delta_old:
        for i in range(len(rule.body)):
            if not isinstance(literals[i], BinaryLiteral):
                if literals[i].get_predicate() == predicate:
                    break
            else:
                left_predicate = literals[i].left_atom.get_predicate()
                right_predicate = literals[i].right_atom.get_predicate()
                if left_predicate == predicate:
                    break
                elif right_predicate == predicate:
                    break
        else:
            continue
        for entity in delta_old[predicate]:
            for i in range(len(rule.body)):
                if isinstance(literals[i], BinaryLiteral):
                    left_predicate = literals[i].left_atom.get_predicate()
                    right_predicate = literals[i].right_atom.get_predicate()

                    if left_predicate == predicate:
                        context = dict()
                        for term1, term2 in zip(literals[i].left_atom.get_entity(), entity):
                            if term1.type == "constant" and term1.name != term2.name:
                                break
                            elif term1.type == "variable" and term1.name in context and context[
                                term1.name] != term2.name:
                                break
                            else:
                                if term1.type == "variable":
                                    context[term1.name] = term2.name

                        if right_predicate in ["Bottom", "Top"]:
                            ground_body(0, i, {i: [entity]}, context)

                        else:
                            for tmp_entity, tmp_interval, tmp_context in ground_generator(literals[i].right_atom,
                                    context, D, D_index):
                                ground_body(0, i, {i: [entity, tmp_entity]}, {**context, **tmp_context})

                    elif right_predicate == predicate:
                        context = dict()
                        for term1, term2 in zip(literals[i].right_atom.get_entity(), entity):
                            if term1.type == "constant" and term1.name != term2.name:
                                break
                            elif term1.type == "variable" and term1.name in context and context[
                                term1.name] != term2.name:
                                break
                            else:
                                if term1.type == "variable":
                                    context[term1.name] = term2.name
                        if left_predicate in ["Bottom", "Top"]:
                            ground_body(0, i, {i: [entity]}, context)
                        else:
                            for tmp_entity, tmp_interval, tmp_context in ground_generator(literals[i].left_atom, context, D, D_index):
                                ground_body(0, i, {i: [tmp_entity, entity]}, {**context, **tmp_context})

                else:
                    if literals[i].get_predicate() == predicate:
                        context = dict()
                        for term1, term2 in zip(literals[i].get_entity(), entity):
                            if term1.type == "constant" and term1.name != term2.name:
                                break
                            elif term1.type == "variable" and term1.name in context and context[term1.name] != term2.name:
                                break
                            else:
                                if term1.type == "variable":
                                    context[term1.name] = term2.name

                        # check whether it is needed to continue to do the evaluation
                        if literals[i].get_predicate() in non_predicates:
                            if not contain_variable_after_replace(head_entity, context): # head can be grounded
                                if inclusion_check(D, rule, i, records=records, context=context, single=True):
                                    continue

                        ground_body(0, i,  {i: [entity]}, context)


if __name__ == "__main__":
    from meteor_reasoner.utils.operate_dataset import print_dataset
    from meteor_reasoner.utils.loader import *
    from meteor_reasoner.materialization.materialize import seminaive_combine

    raw_program = [
        "P(X,Y):-Diamondminus[0,1]P(X,Y)",
        "R(Y):-Q(Y),H(Z),P(X,Y)",
        "Q(X):-K(X,Y)"
    ]
    raw_data = [
        "P(a,b)@0",
        "K(b,c)@[1,2]",
        "H(c)@[2,5]"
    ]
    D = load_dataset(raw_data)
    coalescing_d(D)
    D_index = build_index(D)
    program = load_program(raw_program)
    records = dict()
    non_predicates = ["H", "Q"]
    delta_old = D
    i = 0
    while i < 5:
        i += 1
        delta_new = defaultdict(lambda: defaultdict(list))
        for rule in program:
            optimized_seminaive_join(rule, D=D, delta_old=delta_old, delta_new=delta_new, D_index=D_index, non_predicates=non_predicates, records=records)
        print("{} iteration new:".format(i))
        print_dataset(delta_new)

        delta_old = defaultdict(lambda: defaultdict(list))
        fixpoint = seminaive_combine(D, delta_new, delta_old, D_index)

    exit()













