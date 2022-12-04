from meteor_reasoner.utils.loader import *
from meteor_reasoner.canonical.find_common_fragment import CanonicalRepresentation, find_left_right_periods, fact_entailment
from meteor_reasoner.canonical.calculate_w import get_w


def is_entail(dataset, program, fact):
    """
    Args:
        dataset: a list of string of the form A(a,b)@[1,2]
        program: a list of string of the form A:- B, C
        fact: a string of the form A(a,b)@[1,2]
    Returns:
        Boolean value
    """
    D = load_dataset(dataset)
    program = load_program(program)
    predicate, entity, interval = parse_str_fact(fact)
    fact = Atom(predicate, entity, interval)

    # calculate w
    # will change the program, so we need to make a copy
    t_program = copy.deepcopy(program)
    w = 2 * get_w(t_program)
    # calculate the minimum value and maximum value in the dataset
    maximum_number = -10
    minimum_number = 100
    for predicate in D:
        for entity in D[predicate]:
            for interval in D[predicate][entity]:
                maximum_number = max(interval.right_value, maximum_number)
                minimum_number = min(interval.left_value, minimum_number)

    # calculate the canonical representation
    CR = CanonicalRepresentation(D, program)
    D1, common, varrho_left, left_period, left_len, varrho_right, right_period, right_len = find_left_right_periods(CR, w, fact)

    flag = fact_entailment(D1, fact, common, left_period, left_len, right_period, right_len)
    return flag


if __name__ == "__main__":
    dataset = [
        "HighTemperature(sensor1) @ [0, 27.5]",
        "HighTemperature(sensor2) @ 3.5",
        "HighTemperature(sensor2) @ 5.1",
        "HighTemperature(sensor2) @ 10",
        "HighTemperature(sensor2) @ 14.7",
        "HighTemperature(sensor2) @ 20"
    ]
    # dataset = ["A(a)@[1,2]", "B(a)@[1,2]"]
    program = [
        "Overheat(X):- ALWAYS[-10,0]HighTemperature(X)",
        "Overheat(X): - ALWAYS[-20,0]SOMETIME[-5.5,0]HighTemperature(X)",
        "Alert: - Overheat(X), Overheat(Y)"
    ]
    # program = ["C(X):-A(X),B(X)"]
    fact = "Alert@25"
    print(is_entail(dataset, program, fact))
