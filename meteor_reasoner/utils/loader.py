from meteor_reasoner.utils.parser import *
from collections import defaultdict

def load_dataset(lines):
    """
    Read string-like facts into a dictionary object.

    Args:
        lines (list of strings): a list of facts in the form of  A(x,y,z)@[1,2] or A@[1,2)

    Returns:
        A defaultdict object, in which the key is the predicate and the value is a dictionary (key is
        the entity and the value is a list of Interval instances) or a list of Interval instance when
        there is no entity.

    """
    D = defaultdict(lambda: defaultdict(dict))
    for line in lines:
        line = line.strip().replace(" ","")
        if line == "":
            continue
        try:
          predicate, entity, interval = parse_str_fact(line)
        except:
            continue
        if predicate not in D:
            if entity:
               D[predicate] = {entity: [interval]}
            else:
               D[predicate] = [interval]
        else:
            if isinstance(D[predicate], list) and entity is not None:
                raise ValueError("One predicate can not have both entity and Null cases!")

            if not isinstance(D[predicate], list) and entity is None:
                raise ValueError("One predicate can not have both entity and Null cases!")

            if entity:
                if entity in D[predicate]:
                    D[predicate][entity].append(interval)
                else:
                    D[predicate][entity] = [interval]
            else:
                D[predicate].append(interval)


    return D


def load_program(rules):
    """
    Format each string-like rule into a rule instance.

    Args:
        rules (list of strings): each string represents a rule, e.g. A(X):- Boxminus[1,2]B(X)

    Returns:
        list of rule instances
    """
    program = []
    for line in rules:
        rule = parse_rule(line)
        program.append(rule)

    return program
