from meteor_reasoner.classes.term import *
from meteor_reasoner.classes.rule import *
from collections import defaultdict
from meteor_reasoner.materialization.coalesce import coalescing
from meteor_reasoner.materialization.ground import *


def join(rule, D, delta_old, delta_new, common_fragment=None, D_index=None):
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
    literals = rule.body

    def ground_body(global_literal_index, visited, delta, context):
        if global_literal_index == len(literals):
            T = []
            for i in range(len(literals)):
                tmp_D = defaultdict(lambda: defaultdict(list))
                grounded_literal = copy.deepcopy(literals[i])
                if isinstance(grounded_literal, BinaryLiteral):
                    left_predicate = grounded_literal.left_atom.get_predicate()
                    right_predicate = grounded_literal.right_atom.get_predicate()
                    if left_predicate == "Top":
                        grounded_literal.right_atom.set_entity(delta[i][0])
                        tmp_D[grounded_literal.right_atom.get_predicate()][delta[i][0]] = delta[i][1]
                    elif right_predicate == "Top":
                        grounded_literal.left_atom.set_entity(delta[i][0])
                        tmp_D[grounded_literal.left_atom.get_predicate()][delta[i][0]] = delta[i][1]
                    else:
                        grounded_literal.left_atom.set_entity(delta[i][0])
                        tmp_D[grounded_literal.left_atom.get_predicate()][delta[i][0]] = delta[i][1]
                        grounded_literal.right_atom.set_entity(delta[i][2])
                        tmp_D[grounded_literal.right_atom.get_predicate()][delta[i][2]] = delta[i][3]

                else:
                    if grounded_literal.get_predicate() not in ["Bottom", "Top"]:
                        grounded_literal.set_entity(delta[i][0])
                        tmp_D[grounded_literal.get_predicate()][delta[i][0]] = delta[i][1]

                t = apply(grounded_literal, tmp_D)
                if len(t) == 0:
                    break
                else:
                    T.append(t)

            n_T = []
            if len(rule.negative_body_atoms) != 0:
                n_literals = rule.negative_body_atoms
                for i in range(len(n_literals)):
                    tmp_D = defaultdict(lambda: defaultdict(list))
                    grounded_literal = copy.deepcopy(n_literals[i])
                    if isinstance(grounded_literal, BinaryLiteral):
                        left_predicate = grounded_literal.left_atom.get_predicate()
                        right_predicate = grounded_literal.right_atom.get_predicate()
                        if left_predicate == "Top":
                            flag = False
                            right_atom = grounded_literal.right_atom
                            for _, term in enumerate(right_atom.get_entity()):
                                if term.type == "variable" and term.name not in context:
                                    flag = True
                                    break
                                elif term.type == "variable" and term.name in context:
                                    term.type = "constant"
                                    term.name = context[term.name]
                            if flag:
                                break
                            else:
                                tmp_predicate = right_atom.get_predicate()
                                tmp_entity = right_atom.get_entity()
                                if tmp_predicate in D and tmp_entity \
                                        in D[tmp_predicate]:
                                    tmp_D[tmp_predicate][tmp_entity] = D[tmp_predicate][tmp_entity]

                        elif right_predicate == "Top":
                            flag = False
                            left_atom = grounded_literal.left_atom
                            for _, term in enumerate(left_atom.get_entity()):
                                if term.type == "variable" and term.name not in context:
                                    flag = True
                                    break
                                elif term.type == "variable" and term.name in context:
                                    term.type = "constant"
                                    term.name = context[term.name]
                            if flag:
                                break
                            else:
                                tmp_predicate = left_atom.get_predicate()
                                tmp_entity = left_atom.get_entity()
                                if tmp_predicate in D and tmp_entity \
                                        in D[tmp_predicate]:
                                    tmp_D[tmp_predicate][tmp_entity] = D[tmp_predicate][tmp_entity]
                        else:
                            flag = False
                            right_atom = grounded_literal.right_atom
                            for _, term in enumerate(right_atom.get_entity()):
                                if term.type == "variable" and term.name not in context:
                                    flag = True
                                    break
                                elif term.type == "variable" and term.name in context:
                                    term.type = "constant"
                                    term.name = context[term.name]
                            if flag:
                                break
                            else:
                                tmp_predicate = right_atom.get_predicate()
                                tmp_entity = right_atom.get_entity()
                                if tmp_predicate in D and tmp_entity \
                                        in D[tmp_predicate]:
                                    tmp_D[tmp_predicate][tmp_entity] = D[tmp_predicate][tmp_entity]

                            left_atom = grounded_literal.left_atom
                            for _, term in enumerate(left_atom.get_entity()):
                                if term.type == "variable" and term.name not in context:
                                    flag = True
                                    break
                                elif term.type == "variable" and term.name in context:
                                    term.type = "constant"
                                    term.name = context[term.name]
                            if flag:
                                break
                            else:
                                tmp_predicate = left_atom.get_predicate()
                                tmp_entity = left_atom.get_entity()
                                if tmp_predicate in D and tmp_entity \
                                        in D[tmp_predicate]:
                                    tmp_D[tmp_predicate][tmp_entity] = D[tmp_predicate][tmp_entity]
                    else:
                        if grounded_literal.get_predicate() in ["Bottom", "Top"]:
                            raise ValueError("negative body atoms can not be Bottom or Top")

                        flag = False
                        for _, term in enumerate(grounded_literal.get_entity()):
                            if term.type == "variable" and term.name not in context:
                                flag = True
                                break
                            elif term.type == "variable" and term.name in context:
                                term.type = "constant"
                                term.name = context[term.name]
                        if flag:
                            break
                        else:
                            tmp_predicate = grounded_literal.get_predicate()
                            tmp_entity = grounded_literal.get_entity()
                            if tmp_predicate in D and tmp_entity \
                                    in D[tmp_predicate]:
                                tmp_D[tmp_predicate][tmp_entity] = D[tmp_predicate][tmp_entity]

                    t = apply(grounded_literal, tmp_D)
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

                    # store new facts to delta_new
                    diff_delta = []
                    if head_predicate not in D:
                        if head_predicate not in delta_new:
                            delta_new[head_predicate][replaced_head_entity] = T
                        else:
                            delta_new[head_predicate][replaced_head_entity] += T
                        if common_fragment is not None and common_fragment.cr_flag:
                            diff_delta = T

                    elif head_predicate in D and replaced_head_entity not in D[head_predicate]:
                        if head_predicate not in delta_new:
                            delta_new[head_predicate][replaced_head_entity] = T
                        else:
                            delta_new[head_predicate][replaced_head_entity] += T
                        if common_fragment is not None and common_fragment.cr_flag:
                            diff_delta = T
                    else:
                        coalesced_T_plus = coalescing(T + D[head_predicate][replaced_head_entity])
                        if not Interval.compare(coalesced_T_plus, D[head_predicate][replaced_head_entity]):
                            for interval1 in T:
                                if common_fragment is not None and common_fragment.cr_flag:
                                     diff_delta += Interval.diff(interval1, D[head_predicate][replaced_head_entity])
                                for interval2 in coalesced_T_plus:
                                    if Interval.intersection(interval1, interval2) is not None:
                                        flag = True
                                        for interval3 in D[head_predicate][replaced_head_entity]:
                                            if interval2 == interval3:
                                                flag = False
                                        if flag:
                                            delta_new[head_predicate][replaced_head_entity].append(interval2)

                    if common_fragment is not None and common_fragment.cr_flag and diff_delta is not None: # need to do judge whether it is overlap
                        for cr_interval in diff_delta:
                            if Interval.intersection(cr_interval, common_fragment.base_interval):
                                common_fragment.cr_flag = False
                                common_fragment.common = None
                                break
                            else:
                                if cr_interval.right_value <= common_fragment.base_interval.left_value:
                                    if cr_interval.right_value >= common_fragment.common.left_value:
                                        common_fragment.common.left_value = cr_interval.right_value
                                        common_fragment.common.left_open = not cr_interval.right_open
                                elif cr_interval.left_value >= common_fragment.base_interval.right_value:
                                    if cr_interval.left_value <= common_fragment.common.right_value:
                                        common_fragment.common.right_value = cr_interval.left_value
                                        common_fragment.common.right_open = not cr_interval.left_open
                                else:
                                    print(str(cr_interval))
                                    print(str(common_fragment.common))
                                    raise ValueError("Error Happen")

        elif global_literal_index == visited:
            ground_body(global_literal_index+1, visited, delta, context)

        else:
            current_literal = copy.deepcopy(literals[global_literal_index])
            if not isinstance(current_literal, BinaryLiteral):
                if current_literal.get_predicate() in ["Bottom", "Top"]:
                    ground_body(global_literal_index+1, delta, context)
                else:
                    for tmp_entity, tmp_interval, tmp_context in ground_unary_literal(current_literal, context, D, D_index):
                        tmp_entity_interval = tmp_interval if isinstance(tmp_interval, list) else list(tmp_interval)
                        tmp_delata = {global_literal_index: [tmp_entity, tmp_entity_interval]}
                        ground_body(global_literal_index+1,  visited, {**delta, **tmp_delata}, {**context, **tmp_context})

            else:
                left_predicate = current_literal.left_atom.get_predicate()
                right_predicate = current_literal.right_atom.get_predicate()

                if left_predicate in ["Bottom", "Top"]:
                    for tmp_entity, tmp_interval, tmp_context in ground_unary_literal(current_literal.right_atom,
                                                                                      context,  D, D_index):
                        tmp_entity_interval = tmp_interval if isinstance(tmp_interval, list) else list(tmp_interval)
                        tmp_delta = {global_literal_index: [tmp_entity, tmp_entity_interval]}
                        ground_body(global_literal_index + 1, visited, {**delta, **tmp_delta}, {**context, **tmp_context})

                elif right_predicate in ["Bottom", "Top"]:
                    for tmp_entity, tmp_interval, tmp_context in ground_unary_literal(current_literal.left_atom,
                                                                                      context, D, D_index):
                        tmp_entity_interval = tmp_interval if isinstance(tmp_interval, list) else list(tmp_interval)
                        tmp_delta = {global_literal_index: [tmp_entity, tmp_entity_interval]}
                        ground_body(global_literal_index + 1,visited, {**delta, **tmp_delta}, {**context, **tmp_context})

                else:
                    for left_entity, left_interval, tmp_context1 in ground_unary_literal(current_literal.left_atom, context, D):
                        for right_entity, right_interval, tmp_context2 in ground_unary_literal(current_literal.right_atom,
                                                                                               {**context,
                                                                                                **tmp_context1}, D):
                            tmp_left_interval = left_interval if isinstance(left_interval, list) else list(left_interval)
                            tmp_right_interval = right_interval if isinstance(right_interval, list) else list(right_interval)
                            tmp_delta = {global_literal_index: [left_entity, tmp_left_interval, right_entity, tmp_right_interval]}
                            ground_body(global_literal_index + 1, visited, {**delta, **tmp_delta}, {**context, **tmp_context1, **tmp_context2})

    for predicate in delta_old:
        for entity in delta_old[predicate]:
            for i in range(len(literals)):
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
                    ground_body(0, i,  {i: [entity, delta_old[predicate][entity]]}, context)




if __name__ == "__main__":
    D = defaultdict(lambda: defaultdict(list))
    D["A"][tuple([Term("mike")])] = [Interval(3, 4, False, False), Interval(6, 10, True, True)]
    D["B"] = [Interval(2,8, False, False)]

    Delta = defaultdict(lambda: defaultdict(list))
    head = Atom("C")
    body = [Literal(Atom("A", tuple([Term("X", "variable")])), [Operator("Boxminus", Interval(1, 2, False, False))]), Literal(Atom("B"), [Operator("Diamondminus", Interval(0, 1, False, False))])]

    new_literal = BinaryLiteral(Atom("A", tuple([Term("X", "variable")])), Atom("B"), Operator("Since", Interval(1, 2, False, False)))
    body.append(new_literal)

    rule = Rule(head, body)
    seminaive_join(rule, Delta, D)

    for predicate in Delta:
        print(predicate)
        for interval in Delta[predicate]:
            print(interval)

