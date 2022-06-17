from meteor_reasoner.materialization.join_util import *
from meteor_reasoner.materialization.apply import *


def ground_generator(literal, context, D, D_index=None, delta_old=None, visited=False, flag=False):
    """
    This function is a generator, which generates entity and the context.
    Args:
        literal (a literal instance):
        context (a dictionary): store the mapping of  variables and constants
        D (a dictionary object): a global object storing all facts.

    Returns:
        entity and the context

    """
    predicate = literal.get_predicate()
    entity = copy.deepcopy(literal.get_entity())

    if visited:
        if predicate not in delta_old:
            return

        if len(entity) == 1 and entity[0].name == "nan":
            yield entity, dict()

        elif not contain_variable(entity):
            if predicate in delta_old and entity in delta_old[predicate]:
                yield entity, dict()

        elif not contain_variable_after_replace(entity, context):
            replaced_entity = []
            for term in entity:
                if term.type == "variable":
                    term.type = "constant"
                    term.name = context[term.name]
                    replaced_entity.append(term)
                else:
                    replaced_entity.append(term)

            if predicate in delta_old and tuple(replaced_entity) in delta_old[predicate]:
                yield tuple(replaced_entity), dict()
        else:
            for tmp_entity in delta_old[predicate]:
                tmp_context = dict()
                for term1, term2 in zip(entity, tmp_entity):
                    if term1.type == "constant" and term1.name != term2.name:
                        break
                    elif term1.type == "variable" and term1.name in context and context[term1.name] != term2.name:
                        break
                    elif term1.type == "variable" and term1.name in tmp_context and tmp_context[term1.name] != term2.name:
                        break
                    else:
                        if term1.type == "variable":
                           tmp_context[term1.name] = term2.name
                else:
                    yield tmp_entity, tmp_context

    elif not flag:
        if predicate not in D:
            return

        if len(entity) == 1 and entity[0].name == "nan":
            yield entity, dict()

        elif not contain_variable(entity):
            if predicate in D and entity in D[predicate]:
                yield entity, dict()

        elif not contain_variable_after_replace(entity, context):
            replaced_entity = []
            for term in entity:
                if term.type == "variable":
                    term.type = "constant"
                    term.name = context[term.name]
                    replaced_entity.append(term)
                else:
                    replaced_entity.append(term)
            replaced_entity = tuple(replaced_entity)
            if predicate in D and tuple(replaced_entity) in D[predicate]:
                yield tuple(replaced_entity), dict()
        else:
            if D_index is not None:
                index_str = []
                for i, term in enumerate(entity):
                    if term.type == "constant":
                        index_str.append(str(i) + "@" + term.name)
                    else:
                        if term.name in context:
                            index_str.append(str(i) + "@" + context[term.name])

                index_str = "||".join(index_str)
                if len(index_str) == 0:
                    for constant_entity in D[predicate]:
                        tmp_context = dict()
                        for term1, term2 in zip(entity, constant_entity):
                            if term1.type == "constant" and term1.name != term2.name:
                                break
                            elif term1.type == "variable" and term1.name in context and context[
                                term1.name] != term2.name:
                                break
                            elif term1.type == "variable" and term1.name in tmp_context and tmp_context[
                                term1.name] != term2.name:
                                break
                            else:
                                if term1.type == "variable":
                                    tmp_context[term1.name] = term2.name
                        else:
                            yield constant_entity, tmp_context
                else:
                    if index_str in D_index[predicate]:
                        for constant_entity in D_index[predicate][index_str]:
                            tmp_context = dict()
                            for term1, term2 in zip(entity, constant_entity):
                                if term1.type == "constant" and term1.name != term2.name:
                                    break
                                elif term1.type == "variable" and term1.name in context and context[
                                    term1.name] != term2.name:
                                    break
                                elif term1.type == "variable" and term1.name in tmp_context and tmp_context[
                                    term1.name] != term2.name:
                                    break
                                else:
                                    if term1.type == "variable":
                                        tmp_context[term1.name] = term2.name
                            else:
                                yield constant_entity, tmp_context

            else:
                for tmp_entity in D[predicate]:
                    tmp_context = dict()
                    for term1, term2 in zip(entity, tmp_entity):
                        if term1.type == "constant" and term1.name != term2.name:
                            break
                        elif term1.type == "variable" and term1.name in context and context[term1.name] != term2.name:
                            break
                        elif term1.type == "variable" and term1.name in tmp_context and tmp_context[
                            term1.name] != term2.name:
                            break
                        else:
                            if term1.type == "variable":
                                tmp_context[term1.name] = term2.name
                    else:
                        yield tmp_entity, tmp_context
    else:
        # index > visited
        if predicate not in D:
            return

        if len(entity) == 1 and entity[0].name == "nan":
            if predicate in delta_old and entity in delta_old[predicate]:
                if Interval.list_inclusion(D[predicate][entity], delta_old[predicate][entity]):
                    return
            yield entity, dict()

        elif not contain_variable(entity):
            if predicate in D and entity in D[predicate]:
                if predicate in delta_old and entity in delta_old[predicate]:
                    if Interval.list_inclusion(D[predicate][entity], delta_old[predicate][entity]):
                        return
                yield entity, dict()

        elif not contain_variable_after_replace(entity, context):
            replaced_entity = []
            for term in entity:
                if term.type == "variable":
                    term.type = "constant"
                    term.name = context[term.name]
                    replaced_entity.append(term)
                else:
                    replaced_entity.append(term)
            replaced_entity = tuple(replaced_entity)
            if predicate in D and tuple(replaced_entity) in D[predicate]:
                if predicate in delta_old and replaced_entity in delta_old[predicate]:
                    if Interval.list_inclusion(D[predicate][replaced_entity], delta_old[predicate][replaced_entity]):
                        return
                yield tuple(replaced_entity), dict()
        else:
            if D_index is not None:
                index_str = []
                for i, term in enumerate(entity):
                    if term.type == "constant":
                        index_str.append(str(i) + "@" + term.name)
                    else:
                        if term.name in context:
                            index_str.append(str(i) + "@" + context[term.name])

                index_str = "||".join(index_str)
                if len(index_str) == 0:
                    for constant_entity in D[predicate]:
                        tmp_context = dict()
                        for term1, term2 in zip(entity, constant_entity):
                            if term1.type == "constant" and term1.name != term2.name:
                                break
                            elif term1.type == "variable" and term1.name in context and context[
                                term1.name] != term2.name:
                                break
                            elif term1.type == "variable" and term1.name in tmp_context and tmp_context[
                                term1.name] != term2.name:
                                break
                            else:
                                if term1.type == "variable":
                                    tmp_context[term1.name] = term2.name
                        else:
                            if predicate in delta_old and constant_entity in delta_old[predicate]:
                                if Interval.list_inclusion(D[predicate][constant_entity],
                                                           delta_old[predicate][constant_entity]):
                                    continue
                            yield constant_entity, tmp_context
                else:
                    if index_str in D_index[predicate]:
                        for constant_entity in D_index[predicate][index_str]:
                            tmp_context = dict()
                            for term1, term2 in zip(entity, constant_entity):
                                if term1.type == "constant" and term1.name != term2.name:
                                    break
                                elif term1.type == "variable" and term1.name in context and context[
                                    term1.name] != term2.name:
                                    break
                                elif term1.type == "variable" and term1.name in tmp_context and tmp_context[
                                    term1.name] != term2.name:
                                    break
                                else:
                                    if term1.type == "variable":
                                        tmp_context[term1.name] = term2.name
                            else:
                                if predicate in delta_old and constant_entity in delta_old[predicate]:
                                    if Interval.list_inclusion(D[predicate][constant_entity],
                                                               delta_old[predicate][constant_entity]):
                                        continue
                                yield constant_entity, tmp_context

            else:
                for tmp_entity in D[predicate]:
                    tmp_context = dict()
                    for term1, term2 in zip(entity, tmp_entity):
                        if term1.type == "constant" and term1.name != term2.name:
                            break
                        elif term1.type == "variable" and term1.name in context and context[term1.name] != term2.name:
                            break
                        elif term1.type == "variable" and term1.name in tmp_context and tmp_context[
                            term1.name] != term2.name:
                            break
                        else:
                            if term1.type == "variable":
                                tmp_context[term1.name] = term2.name
                    else:
                        if predicate in delta_old and tmp_entity in delta_old[predicate]:
                            if Interval.list_inclusion(D[predicate][tmp_entity],
                                                       delta_old[predicate][tmp_entity]):
                                continue

                        yield tmp_entity, tmp_context


if __name__ == "__main__":
    from collections import defaultdict
    from meteor_reasoner.classes.term import Term
    from meteor_reasoner.materialization.index_build import build_index

    D = defaultdict(lambda: defaultdict(list))
    D["A"][tuple([Term("mike"), Term("nick")])] = [Interval(3, 4, False, False), Interval(6, 10, True, True)]
    D["B"][tuple([Term("nan")])] = [Interval(2, 8, False, False)]
    D_index = build_index(D)

    Delta = defaultdict(lambda: defaultdict(list))
    head = Atom("C", tuple([Term("nan")]))
    literal_a = Literal(Atom("A", tuple([Term("Y", "variable"), Term("X", "variable")])), [Operator("Boxminus", Interval(1, 2, False, False))])
    literal_b = Literal(Atom("B", tuple([Term("nan")])), [Operator("Diamondminus", Interval(0, 1, False, False))])

    body = [literal_a, literal_b]

    new_literal = BinaryLiteral(Atom("A", tuple([Term("X", "variable"), Term("Y", "variable")])), Atom("B", tuple([Term("nan")])), Operator("Since", Interval(1, 2, False, False)))
    body.append(new_literal)

    for atom_instance in ground_generator(literal_a, context={}, D=D, D_index=D_index):
        print(atom_instance)



