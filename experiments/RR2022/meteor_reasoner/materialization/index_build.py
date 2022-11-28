from collections import defaultdict


def build_index(D, D_index=None):
    """
    Implement an index construction, assuming that the entity only contains at most two terms
    Args:
        D (dictionary of dictionary):
    Returns:
        Dictionary of Dictionary
    """
    if D_index is None:
        D_index = defaultdict(lambda: defaultdict(list))
        for predicate in D.keys():
            for entity, intervals in D[predicate].items():
                if len(entity) == 1:
                    break
                else:
                    for i, item in enumerate(entity):
                        D_index[predicate][str(i) + "@" + item.name].append(entity)

                    if len(entity) > 2:
                        for i, item1 in enumerate(entity):
                            for j, item2 in enumerate(entity):
                                if j <= i:
                                    continue
                                D_index[predicate][str(i) + "@" + item1.name+"||"+str(j) + "@" + item2.name].append(entity)
        return D_index
    else:
        for predicate in D.keys():
            for entity, intervals in D[predicate].items():
                if len(entity) == 1:
                    break
                else:
                    for i, item in enumerate(entity):
                        D_index[predicate][str(i) + "@" + item.name].append(entity)
                    if len(entity) > 2:
                        for i, item1 in enumerate(entity):
                            for j, item2 in enumerate(entity):
                                if j <= i:
                                    continue
                                D_index[predicate][str(i) + "@" + item1.name+"||"+str(j) + "@" + item2.name].append(entity)




