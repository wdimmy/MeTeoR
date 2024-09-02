<p align='center'>
  <img width='40%' src='https://raw.githubusercontent.com/wdimmy/MeTeoR/main/MeTeoR.png' />
</p>

--------------------------------------------------------------------------------

[![PyPI](https://img.shields.io/pypi/v/meteor-reasoner)](https://pypi.org/project/meteor-reasoner/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/wdimmy/MeTeoR/blob/master/LICENSE)

## Overview

* <a href='#introduction'>1. Introduction</a>
* <a href='#core'>2. Core Modules</a>
     * <a href='#lubm'>2.1. Materialisation </a>
     * <a href='#lubm'>2.2  DatalogMTL Periodicity </a> 
     
* <a href='#dataandprogram'>3. Dataset and Program </a>
    * <a href='#data'>3.1 Dataset</a>
        * <a href='#dformat'>3.1.1 Norms of DatalogMTL datasets </a>
        * <a href='#lubm'>3.1.2 Automatic Temporal Data Generator</a>
        * <a href='#dothers'>3.1.3 Other available datasets applicable to DatalogMTL</a>
        
    * <a href='#program'>3.2 Programs</a>
        * <a href='#pformat'>3.2.1 Norms of DatalogMTL programs </a>
        * <a href='#pothers'>3.2.2 Available DatalogMTL programs</a>
  
* <a href='#example'>4. Installation and Examples </a>

* <a href='#web'>5. Demo Website </a>

****


<span id='introduction'/>

#### 1. Introduction

The Metric Temporal Reasoner (MeTeoR) is a scalable reasoner for full DatalogMTL, an extension of Datalog with operators from Metric 
Temporal Logic (MTL). In MeTeoR, we provide lots of 
pluggable functional modules that can be directly reused by other researchers for their research work in the DatalogMTL domain. Besides, we 
will keep continuous maintenance and updates to MeTeoR and provide more implementations from the latest research in DatalogMTL. 

<span id='core'/>

#### 2. Core Modules

We implemented some core modules in MeTeoR mainly based on previously published paper:

##### 2.1 Materiliasation 

The most common technique of choice in scalable Datalog reasoners is materialisation (a.k.a., forward chaining). Facts entailed by a program and
dataset are derived in successive rounds of rule applications until a fixpoint is reached; both this process and its output are often referred to as materialisation.

Based on our published two papers [MeTeoR: Practical Reasoning in Datalog with Metric Temporal Operator](https://ojs.aaai.org/index.php/AAAI/article/download/20535/version/18832/20294) and
[Seminaïve Materialisation in DatalogMTL](https://arxiv.org/pdf/2208.07100.pdf), we implemented three ways of doing materialisation:
* Naive Materialisation
* Semi-naive Materialisation
* Optimisation Materialisation 

##### 2.2 DatalogMTL Periodicity
A direct implementation of materialisation-based reasoning in DatalogMTL is, however, problematic since forward
chaining may require infinitely many rounds of rule applications. In the paper [Materialisation-based Reasoning in DatalogMTL with Bounded Intervals](), we made a 
detailed analysis of the periodic structure of canonical models. We formulate saturation conditions that a partial materialisation needs to satisfy so that
the canonical model can be recovered via unfolding. Finally, we propose a practical reasoning algorithm where
saturation can be efficiently detected as materialisation progresses, and where the relevant periods used to evaluate entailment
queries via unfold- ing are efficiently computed.

MeTeoR is an on-going effort, and we are planning to increase our coverage in the future.

<span id='dataandprogram'/>

#### 3. Dataset and Program 

<span id='data' />

##### 3.1 Dataset 

<span id='dformat'/>

###### 3.1.1 Norms of DatalogMTL datasets
Our data parser support the following four kinds of forms:
* A@1 # no terms
* A(a)@1 or A(a)@[1,1]# punctual interval 
* A(a,b)@<1,2> # n-ary tuple of terms, where < is ( or [ and > is ) or ]

<span id='lubm'/>

###### 3.1.2 Automatic Temporal Data Generator
###### Download the LUBM data generator

You can download the data generator (UBA) from **SWAT Projects - Lehigh University Benchmark (LUBM)** [website](http://swat.cse.lehigh.edu/projects/lubm/). In particular,
we used [UBA1.7](http://swat.cse.lehigh.edu/projects/lubm/uba1.7.zip).

After downloading the  UBA1.7 package, you need to add package's path to CLASSPATH. For examole,

```shell
export CLASSPATH="$CLASSPATH:your package path"
```

<span id="datalog"/>

###### Generate the owl files
```
==================
USAGES
==================

command:
   edu.lehigh.swat.bench.uba.Generator
      	[-univ <univ_num>]
	[-index <starting_index>]
	[-seed <seed>]
	[-daml]
	-onto <ontology_url>

options:
   -univ number of universities to generate; 1 by default
   -index starting index of the universities; 0 by default
   -seed seed used for random data generation; 0 by default
   -daml generate DAML+OIL data; OWL data by default
   -onto url of the univ-bench ontology
```

We found some naming and storage issues when using the above command provided 
by the official documentation. To provide a more user-friendly way, we 
wrote a script which can be directly used to generate required owl files
by passing some simple arguments. An example is shown as follows,

```python
from meteor_reasoner.datagenerator import generate_owl

univ_nume = 1 # input the number of universities you want to generate
dir_name = "./data" # input the directory path used for the generated owl files.

generate_owl.generate(univ_nume, dir_name)

```
In  **./data**, you should obtain a serial of owl files like below,
```
University0_0.owl 
University0_12.owl  
University0_1.owl
University0_4.owl
.....
```

Then, we need to convert the owl files to datalog-like facts. We also prepare
a script that can be directly used to do the conversion. 
```python
from meteor_reasoner.datagenerator import generate_datalog

owl_path = "owl_data" # input the dir_path where owl files locate
out_dir = "./output" # input the path for the converted datalog triplets

generate_datalog.extract_triplets(owl_path, out_dir)
```
In **./output**, you should see a **./output/owl_data**  containing data
in the form of
```
UndergraduateStudent(ID0)
undergraduateDegreeFrom(ID1,ID2)
takesCourse(ID3,ID4)
undergraduateDegreeFrom(ID5,ID6)
UndergraduateStudent(ID7)
name(ID8,ID9)
......
```
and **./output/statistics.txt**  containing the statistics information
about the converted datalog-like data in the form of
```
worksFor:540
ResearchGroup:224
....
AssistantProfessor:146
subOrganizationOf:239
headOf:15
FullProfessor:125
The number of unique entities:18092
The number of triplets:8604
```
<span id="datalogmtl"/>

###### Add intervals

Up to now, we only construct the atemporal data, so the final step will be adding temporal information
(intervals) to these atemporal data.  We create a script to automatically add intervals to the atemporal
data. The required arguments are shown as follows
```
  --datalog_file_path DATALOG_FILE_PATH
  --factnum FACTNUM
  --intervalnum INTERVALNUM
  --unit UNIT
  --punctual            specify whether we only add punctual intervals
  --openbracket         specify whether we need to add open brackets
  --min_val MIN_VAL
  --max_val MAX_VAL
```

To be more specific, assuming that we have a datalog-like dataset in **datalog/datalog_data.txt**,
if we want to create a dataset containing 10000 facts and each facts has at most 2 intervals,
we can run he following command
```shell

python add_intervals.py --datalog_file_path datalog/datalog_data.txt --factnum 10000 --intervalnum 2

```

In the **datalog/10000.txt**, there should be 10000 facts, each of which in the form P(a,b)@\varrho, and 
a sample of facts are shown as follows,
```
UndergraduateStudent(ID0)@[1,18]
undergraduateDegreeFrom(ID1,ID2)@[7,18]
takesCourse(ID3,ID4)@[12,46]
undergraduateDegreeFrom(ID5,ID6)@[21,24]
UndergraduateStudent(ID7)@[3,10]
name(ID8,ID9)@[5,22]
```

<span id="dothers"/>

Generated LUBM Dataset: [Download](https://rulerag.s3.eu-north-1.amazonaws.com/lubm_data.zip) 

##### 3.1.3 Other available datasets applicable to DatalogMTL

##### itemporal 
For the dataset generation based on the iItemporal platform, we refer readers to the 
[official github repository](https://github.com/kglab-tuwien/iTemporal), where a nice web-based  interface 
and an easy-to-configure file have been provided for the data generation. A more technical
details about iTemporal can also be found in their [ICDE 2022](https://ieeexplore.ieee.org/document/9835220). 

Generated iTemporal Dataset: [Download](https://rulerag.s3.eu-north-1.amazonaws.com/iTemporal_data.zip) 

##### Meteorological Benchmark
It is a freely available dataset with meteorological observations over the years 1949–2010. The original
dataset could be downalod [here](https://www.engr.scu.edu/~emaurer/gridded_obs/index_gridded_obs.html), which 
consists of daily and monthly weather data from 16 states of the USA. You can construct temporal datasets from 
this large-scale original weather according to your norms. 

<span id="program"/>

##### 3.2 Programs

<span id="pformat"/>

##### 3.2.1 Norms of input DatalogMTL programs
We define the following notations to represent the six MTL operators:
* Diamondminus[1,2] or SOMETIME[-2,-1]
* Boxminus[1,2] or ALWAYS[-2,-1]
* Diamondplus[1,2] or SOMETIME[1,2]
* Boxplus[1,2] or ALWAYS[1,2]
* Since[1,2]
* Until[1,2]

We use ":-" to separate the head and the body atoms and "," as the separator between different 
metric atoms in the body. Besides, constants are represented with the combination of different alphabets in which the
first letter should be **lowercase**; on the contrary, variables are represented with the combination of different alphabets in which the
first letter should be **uppercase**.


As an example, a rule could be written as follows,
```
A(X):- B(a), SOMETIME[-1,0]C(X), Diamondminus[1,2]D(X)
```



<span id="pothers"/>

##### 3.2.2 Available DatalogMTL programs

Currently, there are DatalogMTL program from real-world applications, so most of DatalogMTL rule sets are 
manually created. Here, we mention two rule sets widely used in our experiments. One is LUBM program, which 
is extended the 56 plain Datalog rules obtained from the OWL 2 RL fragment of LUBM with 29 temporal rules
involving recursion and mentioning all metric operators available in DatalogMTL. Our constructed DatalogMTL program could be 
found [here](https://github.com/wdimmy/MeTeoR/blob/main/experiments/AAAI2022/programs/p.txt). 

Besides, Brandt et al. 2018 have constructed two DatalogMTL program sets, but the datasets they used are not publicly available. 
Here, we adapted their weather DatalogMTL program to obtain a a non-recursive program ΠW consisting of 4 rules, which are applicable to
the Meteorological Benchmark. The four rules could be found [here](https://github.com/wdimmy/MeTeoR/blob/main/experiments/AAAI2022/programs/w.txt). 

Finally, we also suggest you to use the aforementioned **iTemporal**, which can automatically generate both
the dataset and the program. 
        
<span id='example'/>

#### Installation
You can install MeTeoR using Python's package manager `pip`.

##### Requirements
 - Python>=3.7
 - Numpy>=1.16.0
 - pandas>=0.24.0
 - urllib3>=1.24.0
 - scikit-learn>=0.20.0
 - networkx
 - rdflib==4.2.2
 - outdated>=0.2.0

You can install the required packages using the following command:
```bash
pip install "numpy==1.16.0" "pandas==0.24.0" "urllib3==1.24.0" "scikit-learn==0.20.0" "networkx==2.6.3" "rdflib==4.2.2" "outdated==0.2.0"
```

##### Pip install
The recommended way to install MeTeoR is using Python's package manager pip:
```bash
pip install - U meteor_reasoner
```

##### From source
You can also install MeTeoR from source. This is recommended if you want to contribute to MeTeoR.
```bash
git clone https://github.com/wdimmy/MeTeoR
cd MeTeoR
pip install -e .
```

##### Examples 
###### Data parser
The format of the datasets and the program could be found in the example foler.
```python
from meteor_reasoner.utils.loader import load_dataset, load_program

data = ["A(a)@1", "B(a)@[1,2]", "C@(1,2]"]
program = ["A(X):-Diamondminus[1,2]A(X)", "D(X):- Boxminus[1,2]A(X), B(X)Since[1,2]C"]
D = load_dataset(data)
Program = load_program(program)

```

###### Materialisation
```python
from meteor_reasoner.materialization.materialize import materialize
flag = materialize(D, Program, mode="naive", K=10) # naiave approach 
flag = materialize(D, Program, mode="seminaive", K=10) # seminaive approach
flag = materialize(D, Program, mode="opt", K=10) #  optimised seminaive approach
````

The above code snippets shows at most 10 rounds of rule applicatioins and the flag represents whether 
it reaches to the fixed point. The derived facts will be kept in D. 


###### Obtain the Periodic Structure

```python 
from meteor_reasoner.canonical.utils import find_periods
from meteor_reasoner.canonical.canonical_representation import CanonicalRepresentation
from meteor_reasoner.utils.operate_dataset import print_dataset

CR = CanonicalRepresentation(D, Program)
CR.initilization()
D1, common, varrho_left, left_period, left_len, varrho_right, right_period, right_len = find_periods(CR)

if varrho_left is None and varrho_right is None:
    print("This program is finitely materialisable for this dataset.")
    print_dataset(D1)
else:
    if varrho_left is not None:
        print("left period:", str(varrho_left))
        for key, values in left_period.items():
            print(str(key), [str(val) for val in values])
    else:
        print("left period:", "[" + str(CR.base_interval.left_value - CR.w) + "," + str(CR.base_interval.left_value), ")")
        print("[]")

    if varrho_right is not None:
        print("right period:", str(varrho_right))
        for key, values in right_period.items():
            print(str(key), [str(val) for val in values])
    else:
        print("right period:", "(" + str(CR.base_interval.right_value), "," +  str(CR.base_interval.right_value + CR.w) + "]")
        print("[]")
```

In particular, you can do the fact entailment based on the achieved periodic structure and an example 
is shown as follows,

```python 
from meteor_reasoner.utils.parser import parse_str_fact
from meteor_reasoner.classes.atom import Atom
from meteor_reasoner.canonical.utils import fact_entailment
fact = "A(a)@-20"
predicate, entity, interval = parse_str_fact(fact)
F = Atom(predicate, entity, interval)
print("Entailment:", fact_entailment(D1, F, common, left_period, left_len, right_period, right_len))
```
The fact is not entailed by the given dataset and the program, so "Entailment: False" will be printed out.

<span id="web" />


#### 5. Demo Website 
We also built a demo website, which provides a easy-to-use interface for interested users to play with our MeTeoR reasoner. 
You can visit this [link](https://datalogmtl.github.io/). 

## Citing MeTeoR
If you use MeTeoR in your work, please cite our papers (Bibtex below).
```
@inproceedings{wang2022meteor,
  title={Meteor: Practical reasoning in datalog with metric temporal operators},
  author={Wang, Dingmin and Hu, Pan and Wa{\l}{\k{e}}ga, Przemys{\l}aw Andrzej and Grau, Bernardo Cuenca},
  booktitle={Proceedings of the AAAI Conference on Artificial Intelligence},
  volume={36},
  number={5},
  pages={5906--5913},
  year={2022}
}

@article{wang2022seminaive,
  title={Seminaive Materialisation in DatalogMTL},
  author={Wang, Dingmin and Wa{\l}{\k{e}}ga, Przemys{\l}aw Andrzej and Grau, Bernardo Cuenca},
  journal={arXiv preprint arXiv:2208.07100},
  year={2022}
}
```
