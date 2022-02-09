from meteor_reasoner.materialization.utils import *
from meteor_reasoner.utils.conversion import *
from meteor_reasoner.automata.buichi_automata import *
from meteor_reasoner.automata.utils import *
from meteor_reasoner.utils.normalize import *
from meteor_reasoner.materialization.index_build import *


def consistency(D, program):
    contain_bottom = False
    for rule in program:
        if rule.head.get_predicate() == "Bottom":
            contain_bottom = True
            break

    if not contain_bottom:
        return True

    must_literals = defaultdict(list)
    coalescing_d(D)
    CF = CycleFinder(program=program)
    non_recursive_predicates = CF.get_non_recursive_predicates()
    involved_predicates = [predicate for predicate in CF.predicate2id if predicate not in ["Bottom", "Top"]]
    automata_predicates = list(set(involved_predicates) - set(non_recursive_predicates))

    D_index = build_index(D)
    materialize_pre(D, rules=relevant_rules, non_recursive_predicates=non_recursive_predicates, D_index=D_index,
                    must_literals=must_literals)
    d_atoms, d_unbounded_literals = extract_dataset(D, involved_predicates, automata_predicates)
    points, x = get_dataset_points_x(D)
    z, gcd = get_gcd(program)

    left_dict, right_dict = construct_left_right_pattern(points, gcd)
    materialize_limit(D, relevant_rules, D_index, limit=Interval(-2 * z - 2 * x, 2 * x + 2 * z, False, False),
                      must_literals=must_literals)

    for key, value in must_literals.items():
        value = coalescing(value)
        must_literals[key] = value

    p_literals = []
    for literal in must_literals.keys():
        if not isinstance(literal, Atom):
            p_literals.append(literal)

    automata = BuchiAutomata(D=D, program=program,
                             p_literals=p_literals,
                             unbounded_literals=d_unbounded_literals,
                             involved_predicates=involved_predicates,
                             automata_predicates=automata_predicates,
                             left_dict=left_dict,
                             right_dict=right_dict,
                             x=x, z=z, gcd=gcd, points=points)

    automata.build_prior(must_literals=must_literals)
    flag = automata.consistency_check()
    return flag