from meteor_reasoner.graphutil.temporal_dependency_graph import CycleFinder
from meteor_reasoner.utils.conversion import *
from meteor_reasoner.automata.buichi_automata import *
from meteor_reasoner.automata.utils import *
from meteor_reasoner.utils.normalize import *
from meteor_reasoner.materialization.materialize import *


def consistency(D_1, program, F=None):
    contain_bottom = False
    for rule in program:
        if rule.head.get_predicate() == "Bottom":
            contain_bottom = True
            break
    if F is None and not contain_bottom:
        return True

    if F is None:
        must_literals = defaultdict(list)
        coalescing_d(D_1)
        relevant_rules = program
        CF = CycleFinder(program=program)
        non_recursive_predicates = CF.get_non_recursive_predicates()
        involved_predicates = [predicate for predicate in CF.predicate2id if predicate not in ["Bottom", "Top"]]
        automata_predicates = list(set(involved_predicates) - set(non_recursive_predicates))

        d_atoms, d_unbounded_literals = extract_dataset(D_1, involved_predicates, automata_predicates)
        points, x = get_dataset_points_x(D_1)
        z, gcd = get_gcd(relevant_rules)

        left_dict, right_dict = construct_left_right_pattern(points, gcd)
        limit = Interval(-2 * z - 2 * x, 2 * x + 2 * z, False, False)
        while True:
            flag, delta_new = materialize(D_1, relevant_rules, K=1)
            has_intersection = False
            for predicate in delta_new:
                for entity in delta_new[predicate]:
                    for interval in delta_new[predicate][entity]:
                        if Interval.inclusion(interval, limit):
                            has_intersection = True
                            break
                    if has_intersection:
                        break
                if has_intersection:
                    break
            else:
                break

        p_literals = []
        for literal in must_literals.keys():
            if not isinstance(literal, Atom):
                p_literals.append(literal)

        automata = BuchiAutomata(D=D_1, program=relevant_rules,
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

    else:
        must_literals = defaultdict(list)
        coalescing_d(D_1)

        # make the conversion
        new_rule, new_atom, _ = euqal_conversion(F)
        program.append(new_rule)
        D_1[new_atom.predicate][new_atom.entity] = [new_atom.interval]
        program = normalize(program)

        CF = CycleFinder(program=program)
        relevant_rules = CF.get_revevant_rules(F.get_predicate())
        CF = CycleFinder(program=relevant_rules)
        non_recursive_predicates = CF.get_non_recursive_predicates()
        involved_predicates = [predicate for predicate in CF.predicate2id if predicate not in ["Bottom", "Top"]]
        automata_predicates = list(set(involved_predicates) - set(non_recursive_predicates))


        D = defaultdict(lambda: defaultdict(dict))
        for predicate in involved_predicates:
            if predicate in D_1:
                for entity in D_1[predicate]:
                     D[predicate][entity] = D_1[predicate][entity]

        d_atoms, d_unbounded_literals = extract_dataset(D, involved_predicates, automata_predicates)
        points, x = get_dataset_points_x(D)
        z, gcd = get_gcd(relevant_rules)

        left_dict, right_dict = construct_left_right_pattern(points, gcd)
        limit = Interval(-2 * z - 2 * x, 2 * x + 2 * z, False, False)
        while True:
            flag, delta_new = materialize(D, relevant_rules, K=1)
            for predicate in delta_new:
                for entity in delta_new[predicate]:
                    for interval in delta_new[predicate][entity]:
                        if Interval.inclusion(interval, limit):
                            break
            else:
                break

        p_literals = []
        for literal in must_literals.keys():
            if not isinstance(literal, Atom):
                p_literals.append(literal)

        automata = BuchiAutomata(D=D, program=relevant_rules,
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