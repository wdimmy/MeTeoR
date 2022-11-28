from meteor_reasoner.utils.loader import *


class CycleFinder:
    def __init__(self, program):
        self.predicate2id = {}
        self.id2predicate = {}
        self.loop = list()
        self.graph = defaultdict(list)
        self.SCC_components = []
        self.Time = 0
        self.program = program
        self.build(program)
        self.cycle_generate()

    def add(self, predicate):
        if predicate not in self.predicate2id:
            id = len(self.predicate2id)
            self.predicate2id[predicate] = id
            self.id2predicate[id] = predicate

    def addedge(self, predicate1, predicate2):
        self.add(predicate1)
        self.add(predicate2)
        id1 = self.predicate2id[predicate1]
        id2 = self.predicate2id[predicate2]
        self.graph[id1].append(id2)

    def is_reachable(self, s, d):
        visited = [False] * self.V
        queue = []

        queue.append(s)
        visited[s] = True
        while queue:
            n = queue.pop(0)
            if n == d:
                return True
            for i in self.graph[n]:
                if visited[i] == False:
                    queue.append(i)
                    visited[i] = True

        return False

    def SCCUtil(self, u, low, disc, stackMember, st):
        disc[u] = self.Time
        low[u] = self.Time
        self.Time += 1
        stackMember[u] = True
        st.append(u)
        for v in self.graph[u]:
            if disc[v] == -1:
                self.SCCUtil(v, low, disc, stackMember, st)
                low[u] = min(low[u], low[v])

            elif stackMember[v] == True:
                low[u] = min(low[u], disc[v])

        w = -1
        if low[u] == disc[u]:
            tmp = []
            while w != u:
                w = st.pop()
                tmp.append(w)
                stackMember[w] = False

            self.SCC_components.append(tmp)

    def SCC(self):
        disc = [-1] * (self.V)
        low = [-1] * (self.V)
        stackMember = [False] * (self.V)
        st = []
        for i in range(self.V):
            if disc[i] == -1:
                self.SCCUtil(i, low, disc, stackMember, st)

    def build(self, program):
        for rule in program:
            head_predicate = rule.head.get_predicate()
            self.add(head_predicate)
            for literal in rule.body:
                if isinstance(literal, BinaryLiteral):
                    self.add(literal.left_literal.get_predicate())
                    self.add(literal.right_literal.get_predicate())
                else:
                   self.add(literal.get_predicate())

        for rule in program:
            head_predicate = rule.head.get_predicate()
            for literal in rule.body:
                if isinstance(literal, Literal) or isinstance(literal, Atom):
                    if literal.get_predicate() == head_predicate:
                        self.loop.append([self.predicate2id[head_predicate]])
                    self.addedge(literal.get_predicate(), head_predicate)
                else:
                    if head_predicate == literal.left_literal.get_predicate():
                        self.loop.append([self.predicate2id[head_predicate]])
                    if head_predicate == literal.right_literal.get_predicate():
                        self.loop.append([self.predicate2id[head_predicate]])

                    self.addedge(literal.left_literal.get_predicate(), head_predicate)
                    self.addedge(literal.right_literal.get_predicate(), head_predicate)

        self.V = len(self.predicate2id)


    def get_revevant_rules(self, predicate):
        relevant_rules = set()
        r_prime_body_prime = []
        old_len = len(relevant_rules)
        while True:
            for rule in self.program:
                if rule.head.get_predicate() in [predicate, "Bottom"] or rule in relevant_rules:
                    relevant_rules.add(rule)
                    for literal in rule.body:
                        if not isinstance(literal, BinaryLiteral):
                            r_prime_body_prime.append(literal.get_predicate())
                        else:
                            r_prime_body_prime.append(literal.left_literal.get_predicate())
                            r_prime_body_prime.append(literal.right_literal.get_predicate())

            for rule in self.program:
                head_predicate = rule.head.get_predicate()
                if head_predicate in r_prime_body_prime:
                    relevant_rules.add(rule)

            if len(set(relevant_rules)) > old_len:
                old_len = len(set(relevant_rules))
                continue

            else:
                break

        return list(relevant_rules)

    def cycle_generate(self):
        self.SCC()
        for scc in self.SCC_components:
            if len(scc) > 1:
                self.loop.append([id for id in scc])


    def get_non_recursive_predicates(self):
        non_recursive_predicates = set()
        for predicate in self.predicate2id:
            if not self.is_recursive_predicate(predicate):
                non_recursive_predicates.add(predicate)
        return [item for item in list(non_recursive_predicates) if item not in ["Top", "Bottom"]]


    def is_recursive_predicate(self, predicate):
        for cycle in self.loop:
            if predicate in self.predicate2id and self.predicate2id[predicate] in cycle:
                return True
            for middle_predicate in cycle:
                if self.is_reachable(middle_predicate, self.predicate2id[predicate]):
                    return True
        return False
