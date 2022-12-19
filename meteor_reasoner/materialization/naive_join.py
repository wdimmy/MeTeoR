from meteor_reasoner.classes.rule import *
from meteor_reasoner.materialization.ground import *
from meteor_reasoner.classes.term import Term
from collections import defaultdict
from meteor_reasoner.materialization.index_build import build_index
from meteor_reasoner.utils.operate_dataset import print_dataset
from meteor_reasoner.materialization.coalesce import coalescing_d


def naive_join(rule, D, delta_new, D_index=None, must_literals=None):
    """
    This function implement the join operator when variables exist in the body of the rule.
    Args:
        rule (a Rule instance):
        delta_new (a dictionary object): store new materialized results.
        D (a dictionary object): a global variable storing all facts.
        common_fragment: Canonical Representation related

    Returns:
        None
    """
    head_entity = rule.head.get_entity()
    head_predicate = rule.head.get_predicate()
    literals = rule.body + rule.negative_body

    def ground_body(global_literal_index, delta, context):
        if global_literal_index == len(literals):
            T = []
            for i in range(len(rule.body)):
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
                    T.append(t)
                    if must_literals is not None:
                        must_literals[grounded_literal] += t
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
                    if must_literals is not None:
                        must_literals[grounded_literal] += t

            if len(n_T) > 0 and len(n_T) == len(rule.negative_body_atoms):
                n_T = interval_merge(T)
            else:
                n_T = []

            try:
                if len(head_entity) > 1 or head_entity[0].name != "nan":
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
            except:
                print("hello")

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

                        if must_literals is not None:
                            must_literals[tmp_head] += T
                        T = reverse_apply(tmp_head, tmp_D)
                    delta_new[head_predicate][replaced_head_entity] += T
                    if must_literals is not None:
                        must_literals[Atom(head_predicate, replaced_head_entity)] += T

        else:
            current_literal = copy.deepcopy(literals[global_literal_index])
            if not isinstance(current_literal, BinaryLiteral):
                if current_literal.get_predicate() in ["Bottom", "Top"]:
                    ground_body(global_literal_index+1, delta, context)
                else:
                    for tmp_entity, tmp_context in ground_generator(current_literal, context, D, D_index):
                        tmp_delata = {global_literal_index: [tmp_entity]}
                        ground_body(global_literal_index+1, {**delta, **tmp_delata}, {**context, **tmp_context})
            else:
                left_predicate = current_literal.left_literal.get_predicate()
                right_predicate = current_literal.right_literal.get_predicate()

                if left_predicate in ["Bottom", "Top"]:
                    for tmp_entity, tmp_context in ground_generator(current_literal.right_literal, context,  D, D_index):
                        tmp_delta = {global_literal_index: [tmp_entity]}
                        ground_body(global_literal_index + 1, {**delta, **tmp_delta}, {**context, **tmp_context})

                elif right_predicate in ["Bottom", "Top"]:
                    for tmp_entity, tmp_context in ground_generator(current_literal.left_literal, context, D, D_index):
                        tmp_delta = {global_literal_index: [tmp_entity]}
                        ground_body(global_literal_index + 1, {**delta, **tmp_delta}, {**context, **tmp_context})

                else:
                    for left_entity, tmp_context1 in ground_generator(current_literal.left_literal, context, D):
                        for right_entity, tmp_context2 in ground_generator(current_literal.right_literal.atom,{**context, **tmp_context1}, D):
                            tmp_delta = {global_literal_index: [left_entity, right_entity]}
                            ground_body(global_literal_index + 1, {**delta, **tmp_delta}, {**context, **tmp_context1, **tmp_context2})

    ground_body(0, {}, dict())


if __name__ == "__main__":
    D = defaultdict(lambda: defaultdict(list))
    D["A"][tuple([Term("mike"), Term("nick")])] = [Interval(3, 4, False, False), Interval(6, 10, True, True)]
    D["B"][tuple([Term("nan")])] = [Interval(2, 8, False, False)]
    D["P"][tuple([Term("a")])] = [Interval(1, 1, False, False)]
    D_index = build_index(D)

    Delta = defaultdict(lambda: defaultdict(list))
    head = Atom("C", tuple([Term("nan")]))
    literal_a = Literal(Atom("A", tuple([Term("Y", "variable"), Term("X", "variable")])),
                        [Operator("Boxminus", Interval(1, 2, False, False))])
    literal_b = Literal(Atom("B", tuple([Term("nan")])), [Operator("Diamondminus", Interval(0, 1, False, False))])

    body = [literal_a, literal_b]

    new_literal = BinaryLiteral(Atom("A", tuple([Term("X", "variable"), Term("Y", "variable")])),
                                Atom("B", tuple([Term("nan")])), Operator("Since", Interval(1, 2, False, False)))
    body.append(new_literal)
    literal_p = Literal(Atom("P", tuple([Term("X", "variable")])),
                        [Operator("Diamondminus", Interval(1, 1, False, False))])
    head_p = Atom("P", tuple([Term("X", "variable")]))

    rule = Rule(head_p, [literal_p])
    i = 0
    delta_old = D
    while i < 5:
        i += 1
        delta_new = defaultdict(lambda: defaultdict(list))
        naive_join(rule, D=D, delta_new=delta_new, D_index=D_index)
        print("new:")
        print_dataset(delta_new)
        for predicate in delta_new:
            if predicate not in D:
                D[predicate] = delta_new[predicate]
            else:
                for entity in delta_new[predicate]:
                    D[predicate][entity] = D[predicate][entity] + delta_new[predicate][entity]
        coalescing_d(D)
        delta_old = delta_new











