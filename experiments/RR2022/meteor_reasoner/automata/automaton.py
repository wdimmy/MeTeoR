from meteor_reasoner.utils.conversion import *
from multiprocessing.pool import ThreadPool
from meteor_reasoner.automata.buichi_automata import *
from meteor_reasoner.automata.utils import *
from meteor_reasoner.utils.normalize import *
from meteor_reasoner.materialization.index_build import *
from meteor_reasoner.materialization.t_operator import naive_immediate_consequence_operator
from meteor_reasoner.utils.operate_dataset import print_dataset


def contain_new_in_limit(D, delta_new, delta_old, D_index, limit):
    for head_predicate in delta_new:
        for entity, T in delta_new[head_predicate].items():
            if head_predicate not in D or entity not in D[head_predicate]:
                D[head_predicate][entity] = D[head_predicate][entity] + T
                delta_old[head_predicate][entity] = delta_old[head_predicate][entity] + T
                # update index
                for i, item in enumerate(entity):
                    D_index[head_predicate][str(i) + "@" + item.name].append(entity)
                if len(entity) > 2:
                    for i, item1 in enumerate(entity):
                        for j, item2 in enumerate(entity):
                            if j <= i:
                                continue
                            D_index[head_predicate][str(i) + "@" + item1.name + "||" + str(j) + "@" + item2.name].append(entity)
            else:
                coalesced_T = coalescing(T + D[head_predicate][entity])
                if not Interval.compare(coalesced_T, D[head_predicate][entity]):
                    for interval1 in coalesced_T:
                        flag = True
                        for interval2 in D[head_predicate][entity]:
                            if interval1.left_value == interval2.left_value and interval1 == interval2:
                                flag = False
                                break
                            elif interval2.left_value > interval1.left_value:
                                break
                        if flag:
                            delta_old[head_predicate][entity].append(interval1)
                    D[head_predicate][entity] = coalesced_T
    fixpoint = True
    if len(delta_old) != 0:
        fixpoint = False
        coalescing_d(D)
        coalescing_d(delta_old)
        for predicate in delta_old:
            for entity in delta_old[predicate]:
                for interval in delta_old[predicate][entity]:
                    if not Interval.inclusion(interval, limit):
                        return fixpoint, False
    return fixpoint, True


def automata(D, program, timeout=120):
    pool1 = ThreadPool(processes=1)
    async_result1 = pool1.apply_async(consistency, args=(D, program))

    try:
        result = async_result1.get(timeout=timeout)  # setting 120 as the timeout time
        return result
    except:
        return "timeout"


def consistency(D, program, F=None):
    contain_bottom = False
    for rule in program:
        # if the program contains no Bottom in the head, it is definitely consistent
        if rule.head.get_predicate() == "Bottom":
            contain_bottom = True
            break
    if F is None and not contain_bottom:
        return True

    if F is not None:
        # construct a new fact and a new rule, which will be added to the daset and the program, respectively.
        # in this way, we change the fact entailment problem to the consistency checking problem
        new_rule, new_atom, _ = euqal_conversion(F)
        program.append(new_rule)
        D[new_atom.predicate][new_atom.entity] = [new_atom.interval]
        #program = normalize(program)
    
    # must_literals store those immediate results calculated during the materialisation process
    # in this way, we can know the time range for which some metric atoms hold.
    must_literals = defaultdict(list)
    coalescing_d(D)
    D_index = build_index(D)
    relevant_rules = program
    CF = CycleFinder(program=program)
    non_recursive_predicates = CF.get_non_recursive_predicates()
    involved_predicates = [predicate for predicate in CF.predicate2id if predicate not in ["Bottom", "Top"]]
    automata_predicates = list(set(involved_predicates) - set(non_recursive_predicates))
    d_atoms, d_unbounded_literals = extract_dataset(D, involved_predicates, automata_predicates)
    
    # print("bounded atoms:")
    # for atom in d_atoms:
    #     print(atom)
    # print("unbounded atoms:")
    # for atom in d_unbounded_literals:
    #     print(atom)
    # exit()

    points, x = get_dataset_points_x(D)
    constants = get_constants(D, program)
    
    # print("points:", points)
    # print("x:", x)
    # for constant in constants:
    #     print(constant)
    # exit()

    z, gcd = get_gcd(relevant_rules)
    left_dict, right_dict = construct_left_right_pattern(points, gcd)

    while True:
        delta_new = naive_immediate_consequence_operator(program, D, D_index, must_literals=must_literals)
        delta_old = defaultdict(lambda: defaultdict(list))
        fixpoint, flag = contain_new_in_limit(D, delta_new, delta_old, D_index, limit=Interval(-4 * x - 4 * z,  4 * x + 4 * z, False, False))
        if not flag:
            break

    if "Bottom" in D:
        return False

    if fixpoint:
        return True

    remove_redundant_atoms = []
    for atom, intervals in must_literals.items():
        if isinstance(atom, Literal) and len(atom.operators) == 0:
            if atom.atom in must_literals:
                must_literals[atom.atom] += must_literals[atom]
                remove_redundant_atoms.append(atom)
    for atom in remove_redundant_atoms:
        del must_literals[atom]

    for key, value in must_literals.items():
        value = coalescing(value)
        must_literals[key] = value
    

    p_literals = []
    for rule in relevant_rules:
        for literal in rule.body:
            if isinstance(literal, BinaryLiteral) or (isinstance(literal, Literal) and len(literal.operators) != 0):
                p_literals.append(literal)
    
    automata = BuchiAutomata(D=D, program=relevant_rules,
                             p_literals=p_literals,
                             unbounded_literals=d_unbounded_literals,
                             involved_predicates=involved_predicates,
                             automata_predicates=automata_predicates,
                             left_dict=left_dict,
                             right_dict=right_dict,
                             constants=constants,
                             x=x, z=z, gcd=gcd, points=points)

    automata.build_prior(must_literals=must_literals)
    flag = automata.consistency_check()
    return flag


if __name__ == "__main__":
    #raw_data = "B(a,b)@[2,30]\nB(c,b)@[4,20]\nA(a)@[10,20]\nD(b)@[13,24]\nD(a)@[3,5]".split("\n")
    # raw_data = ["Backup@0"]
    # D = load_dataset(raw_data)
    # D_index = defaultdict(lambda: defaultdict(list))
    # build_index(D, D_index)
    # #raw_program ="A(X):-SOMETIME[1,2]B(X,Y)\n C(X):-ALWAYS[-4,0]A(X)\nC(X):-SOMETIME[-2,-1]D(X)\nD(X):-SOMETIME[-2,-1]C(X)".split("\n")
    # raw_program = ["Backup :- SOMETIME[-1]Backup"]
    # Program = load_program(raw_program)
    # #fact = "D(a)@[-10,3]"
    # fact = "Backup@-1"
    # fact = parse_str_fact(fact)
    # F = Atom(fact[0], fact[1], fact[2])
    #
    # flag = consistency(D, Program, F)
    # print("flag:", flag)


    #raw_data = ["P@0", "R@0"]
    raw_data = ["P@0","Q@0"]
    raw_data = ["Alive(adam)@0"]
    #raw_data = ["Alive(adam)@0"]
    D = load_dataset(raw_data)
    D_index = defaultdict(lambda: defaultdict(list))
    build_index(D, D_index)
    # raw_program ="A(X):-SOMETIME[1,2]B(X,Y)\n C(X):-ALWAYS[-4,0]A(X)\nC(X):-SOMETIME[-2,-1]D(X)\nD(X):-SOMETIME[-2,-1]C(X)".split("\n")
    #raw_program = ["P :- SOMETIME[-1,0] P", "R :- SOMETIME[-1,0] R", "Q :- ALWAYS[0,+inf) P", "Q :- ALWAYS[0,+inf) R"]
    raw_program = ["ALWAYS[0,1]P:- P", "R:- ALWAYS[0,+inf)P, Q","ALWAYS[0,1]R:- R", "S:-ALWAYS[0,+inf)R"]
    raw_program = ["ALWAYS[0,1]Alive(X):-Alive(X)", "Immortal(X):-ALWAYS[0,+inf)Alive(X)"]
    #raw_program = ["ALWAYS[0,1] Alive(X) :-  Alive(X)", "Immortal(X) :- ALWAYS[0,+inf) Alive(X)"]
    Program = load_program(raw_program)
    # fact = "D(a)@[-10,3]"
    #fact = "Immortal(adam)@-1"
    fact = "S@3"
    fact = "Immortal(adam)@0"
    fact = parse_str_fact(fact)
    F = Atom(fact[0], fact[1], fact[2])

    flag = consistency(D, Program, F)
    print("flag:", flag)



