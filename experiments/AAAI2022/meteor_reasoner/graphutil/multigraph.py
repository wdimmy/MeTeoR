import networkx as nx


class TemporalDependencyGraph():
    def __init__(self):
        self.G = nx.MultiDiGraph()

    def add_edge(self, node1, node2, value):
        self.G.add_edge(node1, node2, weight=value)

    def add_edge_list(self, edges):
        for node1, node2, value in edges:
            self.G.add_edge(node1, node2, weight=2)

    @staticmethod
    def allzerocycle(results):
        def helper(i, path):
            if i == len(results):
                if sum(path) != 0:
                    return -1
                else:
                    return 0

            for item in results[i]:
                res = helper(i+1, path+[item])
                if res == -1:
                    return -1

        res = helper(0, [])
        if res is not None:
            return True
        else:
            return False

    def is_cyclic(self):
        visited = set()
        for node in self.G:
            # judge whether there exist a self-loop
            node_edge_data = self.G.get_edge_data(node, node)
            if node_edge_data is not None:
                for value in node_edge_data.values():
                    if value != 0:
                        return True

            descendants = nx.algorithms.descendants(self.G, node)
            for child in descendants:
                if node in self.G.neighbors(child):  #exist a loop
                    all_simple_paths = set([tuple(path[1:] + [node]) for path in nx.all_simple_paths(self.G, node, child)])
                    all_simple_paths = [path for path in all_simple_paths if tuple(sorted(path)) not in visited]
                    for path in all_simple_paths:
                        visited.add(tuple(sorted(path)))
                        last_node = node
                        path_weights_list = []
                        for path_node in path:
                            weight_tuple = []
                            for value in self.G.get_edge_data(last_node, path_node).values():
                                if value["weight"][0] != value["weight"][1]:
                                    return True
                                weight_tuple.append(value["weight"][0])
                            path_weights_list.append(weight_tuple)
                            last_node = path_node

                        result = self.allzerocycle(path_weights_list)
                        if result:
                            return True
        return False