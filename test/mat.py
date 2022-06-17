from meteor_reasoner.materialization.materialize import *
from meteor_reasoner.utils.loader import load_dataset, load_program
#
# dataset = """
# a1:name(http://www.department4.university4.edu/undergraduatestudent406,undergraduatestudent406)@(154.5,157.5]
# a1:doctoralDegreeFrom(http://www.department4.university4.edu/associateprofessor0,http://www.university181.edu)@[97.5,100.5)
# a1:publicationAuthor(http://www.department5.university4.edu/fullprofessor6/publication10,http://www.department5.university4.edu/fullprofessor6)@(169.0,171.5]
# a1:takesCourse(http://www.department0.university0.edu/undergraduatestudent433,http://www.department0.university0.edu/course2)@(34.0,35.0)
# a1:takesCourse(http://www.department0.university0.edu/undergraduatestudent5,http://www.department0.university0.edu/course21)@(124.5,126.0)
# a1:publicationAuthor(http://www.department4.university0.edu/fullprofessor1/publication4,http://www.department4.university0.edu/fullprofessor1)@[25.0,34.0]
# a1:undergraduateDegreeFrom(http://www.department9.university0.edu/lecturer1,http://www.university169.edu)@[176.5,183.5)
# a1:takesCourse(http://www.department10.university0.edu/undergraduatestudent15,http://www.department10.university0.edu/course25)@(153.5,163.5)
# a1:takesCourse(http://www.department3.university1.edu/undergraduatestudent464,http://www.department3.university1.edu/course28)@[32.0,37.0)
# a1:takesCourse(http://www.department5.university1.edu/graduatestudent75,http://www.department5.university1.edu/graduatecourse17)@[159.0,161.0]
# a1:takesCourse(http://www.department7.university1.edu/undergraduatestudent185,http://www.department7.university1.edu/course21)@[19.0,23.0)
# a1:UndergraduateStudent(http://www.department8.university1.edu/undergraduatestudent119)@[137.0,138.0)
# a1:UndergraduateStudent(http://www.department9.university1.edu/undergraduatestudent185)@(79.0,84.0]
# a1:takesCourse(http://www.department10.university1.edu/undergraduatestudent164,http://www.department10.university1.edu/course23)@[143.5,147.5)
# a1:publicationAuthor(http://www.department14.university1.edu/fullprofessor4/publication0,http://www.department14.university1.edu/fullprofessor4)@[162.5,163.5]
# a1:takesCourse(http://www.department18.university1.edu/undergraduatestudent255,http://www.department18.university1.edu/course53)@(100.5,109.5)
# a1:publicationAuthor(http://www.department18.university1.edu/fullprofessor3/publication1,http://www.department18.university1.edu/fullprofessor3)@[33.0,37.0]
# a1:memberOf(http://www.department4.university2.edu/undergraduatestudent259,http://www.department4.university2.edu)@[73.5,81.5)
# a1:FullProfessor(http://www.department5.university2.edu/fullprofessor7)@(117.5,126.5]
# a1:name(http://www.department6.university2.edu/associateprofessor8/publication1,publication1)@(74.5,77.5]
# """

# D= ["R1(c1,c2)@[0,1]", "R2(c1,c2)@[1,2]", "R3(c2,c3)@[2,3]", "R5(c2)@[0,1]"]
# Program = [
#     "R1(X,Y):- Diamondminus[1,1]R1(X,Y)",
#     "Boxplus[1,1]R5(Y):- R2(X,Y),Boxplus[1,2]R3(Y,Z)",
#     "R4(X):- Diamondminus[0,1]R5(X)",
#     "R6(Y):-R5(Y), Boxminus[0,2]R4(Y),R1(X,Y)"
# ]

with open("/experiments/AAAI2023/programs/case_10_dataset.txt") as file:
    data = file.readlines()
with open("/experiments/AAAI2023/programs/case_10_program.txt") as file:
    program = file.readlines()

D = load_dataset(data)
D_index = build_index(D)
rules = load_program(program)
for i in range(1,10):
    print("Iteration:", i)
    print("=====================")
    print("Before D:")
    print_dataset(D)
    print("Derived facts:")
    delta_new = naive_immediate_consequence_operator(rules, D, D_index)
    print_dataset(delta_new)
    print("After D:")
    materialize(D, rules, D_index=D_index, delta_old=D, K=1)
    print_dataset(D)


D= ["R1(c1,c2)@[0,1]", "R2(c1,c2)@[1,2]", "R3(c2,c3)@[2,3]", "R5(c2)@[0,1]"]
Program = [
    "R1(X,Y):- Diamondminus[1,1]R1(X,Y)",
    "Boxplus[1,1]R5(Y):- R2(X,Y),Boxplus[1,2]R3(Y,Z)",
    "R4(X):- Diamondminus[0,1]R5(X)",
    "R6(Y):-R5(Y), Boxminus[0,2]R4(Y),R1(X,Y)"
]

D = load_dataset(D)
D_index = build_index(D)
rules = load_program(Program)
for i in range(1,4):
    print("Iteration:", i)
    print("=====================")
    print("Before D:")
    print_dataset(D)
    print("Derived facts:")
    delta_new = seminaive_immediate_consequence_operator(rules, D, D_index)
    print_dataset(delta_new)
    print("After D:")
    materialize(D, rules, D_index=D_index, delta_old=D, seminaive=True, K=1)
    print_dataset(D)



