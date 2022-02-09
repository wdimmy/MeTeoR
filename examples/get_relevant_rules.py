from meteor_reasoner.graphutil.temporal_dependency_graph import *
from meteor_reasoner.utils.loader import load_program
# rulepath = input("Input the program path:")
# predicate = input("Input the predicate:")

rulepath = "./demo/aaai22_fullprogram.txt"
predicate = "a1:Scientist"
with open(rulepath) as file:
    program = file.readlines()
program = load_program(program)
CF = CycleFinder(program=program)
relevant_rules = CF.get_revevant_rules(predicate)
for rule in relevant_rules:
    print(rule)

