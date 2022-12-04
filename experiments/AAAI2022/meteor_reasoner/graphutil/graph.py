from meteor_reasoner.graphutil.temporal_dependency_graph import *
from meteor_reasoner.graphutil.topological_sort import *


class Graph:
    def __init__(self, program):
        self.program = program
        self.head2rule = defaultdict(list)
        self.initialize()

    def initialize(self):
        self.build_head_map_rule()
        self.split_program()

    def split(self, rules, target_predicate):
        CF = CycleFinder(program=rules)
        CF.SCC()
        scc2id = defaultdict(int)
        id2scc = defaultdict(set)
        predicateid2sccid = dict()
        cnt = 0
        for scc in CF.SCC_components:
            scc2id[tuple(scc)] = cnt
            id2scc[cnt] = tuple(scc)
            for predicate in scc:
                predicateid2sccid[predicate] = cnt
            cnt += 1

        new_graph = defaultdict(list)
        graph = CF.graph

        for key, value in graph.items():
            key_id = predicateid2sccid[key]
            neighbors = []
            for neighbor in value:
                neighbor_id = predicateid2sccid[neighbor]
                if neighbor_id == key_id:
                    continue
                else:
                    neighbors.append(neighbor_id)
            if len(neighbors) > 0:
                new_graph[key_id] = new_graph[key_id] + neighbors

        TS = TopologicalSorting(new_graph, len(scc2id))
        sorted_scc = TS.topologicalSort()

        target_id = CF.predicate2id[target_predicate]
        non_rescursive_scc = set()
        automata_scc = set()

        target_predicate_scc_id_index = -1
        for i, scc_id in enumerate(sorted_scc):
            if target_id in id2scc[scc_id]:
                target_predicate_scc_id_index = i
                break
        if target_predicate_scc_id_index == -1:
            raise ValueError("No such predicate")

        first_cyclic_scc_id_index = -1
        for i, scc_id in enumerate(sorted_scc[:target_predicate_scc_id_index]):
              if len(id2scc[scc_id]) > 1:
                  first_cyclic_scc_id_index = i

        if first_cyclic_scc_id_index == -1:
            # no cycle before target_predicate_scc_id_index
            for scc_id in sorted_scc[:target_predicate_scc_id_index]:
                non_rescursive_scc = non_rescursive_scc.union(id2scc[scc_id])

            automata_scc = id2scc[sorted_scc[target_predicate_scc_id_index]]
        else:
            for scc_id in sorted_scc[:first_cyclic_scc_id_index]:
                non_rescursive_scc = non_rescursive_scc.union(id2scc[scc_id])
            for scc_id in sorted_scc[first_cyclic_scc_id_index:target_predicate_scc_id_index]:
                automata_scc = automata_scc.union(id2scc[scc_id])

        non_recursive_rules = set()
        automata_rules = set()

        for predicate_id in non_rescursive_scc:
            for rule in self.head2rule[CF.id2predicate[predicate_id]]:
                non_recursive_rules.add(rule)

        for predicate_id in automata_scc:
            for rule in self.head2rule[CF.id2predicate[predicate_id]]:
               flag = True
               for literal in rule.body:
                   if isinstance(literal, BinaryLiteral):
                       if literal.left_atom.get_predicate() not in ["Top", "Bottom"] and CF.predicate2id[literal.left_atom.get_predicate()] not in automata_scc:
                           flag = False
                       if literal.right_atom.get_predicate() not in ["Top", "Bottom"] and CF.predicate2id[literal.right_atom.get_predicate()] not in automata_scc:
                           flag = False
                   else:
                       if literal.get_predicate() not in automata_scc:
                           flag = False
               if flag:
                    automata_rules.add(rule)
               else:
                    non_recursive_rules.add(rule)

        return non_recursive_rules, automata_rules

    def build_head_map_rule(self):
        for rule in self.program:
            head = rule.head
            self.head2rule[head.get_predicate()].append(rule)

    def split_program(self):
        for rule in self.program:
            head_predicate = rule.head.get_predicate()
            self.cluster.add(head_predicate)
        for rule in self.program:
            head_predicate = rule.head.get_predicate()
            for literal in rule.body:
                 if (isinstance(literal, Literal) or isinstance(literal, Atom)) and literal.get_predicate() in self.cluster.predicate2id:
                    self.cluster.addedge(head_predicate, literal.get_predicate())
                 elif isinstance(literal, BinaryLiteral):
                     if literal.left_atom.get_predicate() in self.cluster.predicate2id:
                         if literal.left_atom.get_predicate() == head_predicate:
                             self.cluster.addedge(head_predicate, literal.left_atom.get_predicate() + "_")
                             self.cluster.addedge(literal.left_atom.get_predicate() + "_", head_predicate)
                         else:
                             self.cluster.addedge(literal.left_atom.get_predicate(), head_predicate)

                     if literal.right_atom.get_predicate() in self.cluster.predicate2id:
                         if literal.right_atom.get_predicate() == head_predicate:
                             self.cluster.addedge(head_predicate, literal.right_atom.get_predicate() + "_")
                             self.cluster.addedge(literal.right_atom.get_predicate() + "_", head_predicate)
                         else:
                             self.cluster.addedge(literal.right_atom.get_predicate(), head_predicate)

    def split_rules(self, target_predicate):
        predicates = self.cluster.get_connected_predicates(target_predicate)
        rules = set()
        for predicate in predicates:
            rules = rules.union(set(self.head2rule[predicate]))

        return self.split(rules, target_predicate)


