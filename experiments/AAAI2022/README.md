MeTeoR is a reasoner for DatalogMTL, a knowledge representation language that extends Datalog with operators from metric temporal logic (MTL). The reasoner is developed in python and provides many easy-to-use and independent interfaces, which are quite useful in coping with DatalogMTL-related reasoning tasks. As an example, the reasoner provides the following two functionalities. 


** Fact Entailment **
pipeline.py implements practical fact entailment (Algorithm 2) described in the paper. By running one of the following commands, you can check whether the fact is entailed by the given program and the dataset. You can change the values for "--datapath",  "--rulepath" and "--fact" accordingly. 

```shell 
T1:  python pipeline.py --datapath ./data/lubm.json --rulepath ./programs/p.txt --fact "a1:UndergraduateStudent(http://www.department0.university0.edu/undergraduatestudent100)@[11,12]"
T2:  python pipeline.py --datapath ./data/lubm.json --rulepath ./programs/p.txt --fact "a1:ResearchAssistantCandidate(http://www.department0.university0.edu/graduatestudent2)@[22.5,24)"
T3:  python pipeline.py --datapath ./data/lubm.json --rulepath ./programs/p.txt --fact "a1:SmartStudent(http://www.department0.university0.edu/graduatestudent84)@[24,24.5]"
T4:  python pipeline.py --datapath ./data/lubm.json --rulepath ./programs/p.txt --fact "a1:FullProfessor(http://www.department0.university0.edu/fullprofessor1)@[100,300]"
T5:  python pipeline.py --datapath ./data/lubm.json --rulepath ./programs/p.txt --fact "a1:FullProfessor(http://www.department0.university0.edu/fullprofessor1)@[-3,-2]"

```
--------------------------------------------------------------------------------

** Materialisation **
materialise.py implements materialisation for non-recursive DatalogMTL programs. Assuming that the given program is non-recursive, you may run the following command to obtain, for a given predicate (in this case, a1:ResearchAssistant), the set of all facts with maximal intervals that are entailed by the program and the dataset. 

```shell 
python materialise.py --datapath ./data/lubm.json --rulepath ./programs/p1.txt --predicate a1:ResearchAssistant --resultpath ./result.txt

```
--------------------------------------------------------------------------------
