from meteor_reasoner.demo.dataset import CASES

names = ["case_1", "case_2", "case_3", "case_4", "case_5", "case_6", "case_7", "case_8"]
for name in names:
    dataset, program, _= CASES[name]

    with open(name+"_dataset.txt", "w") as file:
        for item in dataset:
            file.write(item+"\n")

    with open(name + "_program.txt", "w") as file:
        for item in program:
            file.write(item+"\n")

