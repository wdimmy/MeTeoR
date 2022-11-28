# CanonicalRepresentation
This is for the algorithm calculating the Canonical Representation
of a program and a dataset. 


We provide some example datasets and programs in the "demos" folder, 
where case_i_dataset.txt, case_j_program.txt, 0<=i,j<=8, is a pair which represents a dataset name and 
a program name, respectively,


**Only calculates the canonical representation**

```shell 
python run.py --datapath ./demos/case_0_dataset.txt --rulepath ./demos/case_0_program.txt
```
The output should be like this:
```
The w is: 2
The maximum number: 1.5
The minimum number: 0
left period: [-3.5,-2.5)
Q ['[-3.5,-3.5]']
right period: (4.0,4.5]
P ['(4.0,4.5]']
```
--------------------------------------------------------------------------------



**Only calculates the canonical representation**

```shell 
python run.py --datapath ./demos/case_0_dataset.txt --rulepath ./demos/case_0_program.txt --fact "P@0"
```
The output should be like this (entailed before the canonical representation is obtained):
```
The w is: 2
The maximum number: 1.5
The minimum number: 0
The fact: P@[0,0] is entailed

```
```
python run.py --datapath ./demos/case_0_dataset.txt --rulepath ./demos/case_0_program.txt --fact "P@100.5"
```

The output should be like this (entailment checking based on the the canonical representation that has previously been obtained):
```
The w is: 2
The maximum number: 1.5
The minimum number: 0
left period: [-3.5,-2.5)
Q ['[-3.5,-3.5]']
right period: (4.0,4.5]
P ['(4.0,4.5]']
Entailment: True
```

```
python run.py --datapath ./demos/case_0_dataset.txt --rulepath ./demos/case_0_program.txt --fact "Q@100.6"
```

The output should be like this (entailment checking based on the the canonical representation that has previously been obtained):
```
The w is: 2
The maximum number: 1.5
The minimum number: 0
left period: [-3.5,-2.5)
Q ['[-3.5,-3.5]']
right period: (4.0,4.5]
P ['(4.0,4.5]']
Entailment: False
```

--------------------------------------------------------------------------------

