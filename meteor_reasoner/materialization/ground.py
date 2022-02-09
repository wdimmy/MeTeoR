from meteor_reasoner.materialization.join_util import *
from meteor_reasoner.materialization.apply import *


def ground_unary_literal(literal, context, D, D_index=None):
    """
    This function is a generator, which generates entity, interval and the context.
    Args:
        literal (a literal instance):
        context (a dictionary): store the mapping of  variables and constants
        D (a dictionary object): a global object storing all facts.

    Returns:
        entity, interval, and the context

    """
    predicate = literal.get_predicate()
    entity = copy.deepcopy(literal.get_entity())

    if predicate in D:
        if len(entity) == 1 and entity[0].name == "nan":
            if predicate in D:
                yield entity, D[predicate][entity], dict()


        elif not contain_variable(entity):
            if predicate in D and entity in D[predicate]:
                yield entity, D[predicate][entity], dict()

        elif not contain_variable_after_replace(entity, context):
            replaced_entity = []
            for term in entity:
                if term.type == "variable":
                    term.type = "constant"
                    term.name = context[term.name]
                    replaced_entity.append(term)
                else:
                    replaced_entity.append(term)

            if predicate in D and tuple(replaced_entity) in D[predicate]:
                yield tuple(replaced_entity), D[predicate][tuple(replaced_entity)], dict()

        else:
            if D_index is not None:
                index_str = []
                for i, term in enumerate(entity):
                    if term.type == "constant":
                        index_str.append(str(i) + "@" + term.name)
                    else:
                        if term.name in context:
                            index_str.append(str(i)+"@"+context[term.name])

                index_str = "||".join(index_str)
                if len(index_str) == 0:
                    for constant_entity, intervals in copy.deepcopy(D[predicate]).items():
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
                            yield constant_entity, D[predicate][constant_entity], tmp_context
                else:
                    if index_str in D_index[predicate]:
                        for constant_entity in D_index[predicate][index_str]:
                            tmp_context = dict()
                            for term1, term2 in zip(entity, constant_entity):
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
                                yield constant_entity, D[predicate][constant_entity], tmp_context

            else:
                for tmp_entity in D[predicate]:
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
                        yield tmp_entity, D[predicate][tmp_entity], tmp_context
