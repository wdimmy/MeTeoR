from meteor_reasoner.graphutil.graph_strengthening import *
from meteor_reasoner.graphutil.multigraph import *
from meteor_reasoner.utils.loader import load_program
rulepath = input("Input the program path:")

with open(rulepath) as file:
    program = file.readlines()
program = load_program(program)
rules = transformation(program)
paris = construct_pair(rules)
G = TemporalDependencyGraph()
for pair in paris:
    G.add_edge(pair[0], pair[1], [pair[2], pair[3]])

print("Is the program finitely materialisable:", G.is_cyclic())
print(G.is_cyclic())