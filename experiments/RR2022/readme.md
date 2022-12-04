# Seminaive Materialisation in DatalogMTL

This repository contains code and other related resources of our paper "Seminaive Materialisation in DatalogMTL".

<span id='overview'/>

### Overview:
* <a href='#introduction'>1. Introduction</a>
* <a href='#data'>2. Automatic Temporal Data Generation </a>
    * <a href='#lubm'>2.1. Temporal LUBM Benchmark</a>
      * <a href="#downloadlubm">2.1.1 Download LUBM generator</a>
      * <a href="#datalog">2.1.2 Obtain datalog facts</a>
      * <a href="#datalogmtl">2.1.3 Add punctual intervals</a>
* <a href='#experiment'>3. Materialisation (Naive, Seminaive and Optimised Seminaive)  </a>

****

<span id='introduction'/>

#### 1. Introduction: <a href='#overview'>[Back to Top]</a>
DatalogMTL is an extension of Datalog with metric temporal operators that has found applications in
temporal ontology-based data access and query answering, as well as in stream reasoning. Practical algorithms for DatalogMTL
are reliant on materialisation-based reasoning, where temporal facts are derived in a forward chaining manner in successive
rounds of rule applications. Current materialisation-based procedures are, however, based on a naive evaluation strategy, 
where the main source of inefficiency stems from redundant computations.

In this paper, we propose a materialisation-based procedure which, analogously to the classical seminaive algorithm in Datalog,
aims at minimising redundant computation by ensuring that each temporal rule instance is considered at most once during the execution
of the algorithm. Our experiments show that our optimised seminaive strategy for DatalogMTL is able to significantly reduce materialisation times.
****


<span id="data"/>

#### 2. Automatic Temporal Data Generation </a>

<span id="lubm"/>

##### 2.1 Lehigh University Benchmark (LUBM)

<span id="downloadlubm"/>

######  2.1.1 Download the LUBM data generator

You can download the data generator (UBA) from **SWAT Projects - Lehigh University Benchmark (LUBM)** [website](http://swat.cse.lehigh.edu/projects/lubm/). In particular,
we used [UBA1.7](http://swat.cse.lehigh.edu/projects/lubm/uba1.7.zip).

After downloading the  UBA1.7 package, you need to add package's path to CLASSPATH. For examole,

```shell
export CLASSPATH="$CLASSPATH:your package path"
```

<span id="datalog"/>

###### 2.1.2 Generate the owl files
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

generate_datalog.extract_triplet(owl_path, out_dir)
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

###### 2.1.3 Add punctual intervals

Up to now, we only construct the atemporal data, so the final step will be adding temporal information
(intervals) to these atemporal data. In the stream reasoning scenario, we consider punctual intervals, namely,
the leftendpint equals to the right endpoint (e.g., A@[1,1]). To be more specific, assuming that we have a datalog-like 
dataset in **datalog/datalog_data.txt**,
if we want to create a dataset containing 10000 facts and each facts has at most 2 intervals, each of 
time points are randomly chosen from a range [0, 300], we can run he following command (remember to add **--min_val=0, --max_val=300, --punctual**). 
```shell

python add_intervals.py --datalog_file_path datalog/datalog_data.txt --factnum 10000 --intervalnum 2 --min_val 0 --max_val 300 --punctual 

```

In the **datalog/10000.txt**, there should be 10000 facts, each of which in the form P(a,b)@\varrho, and 
a sample of facts are shown as follows,
```
undergraduateDegreeFrom(ID1,ID2)@[7,7]
takesCourse(ID34,ID4)@[46,46]
undergraduateDegreeFrom(ID5,ID6)@[21,21]
name(ID18,ID9)@[22,22]
......
```

<span id="experiment"/>

#### 3. Materialisation (Naive, Seminaive and Optimised Seminaive) 

After generating the temporal data using the aforementioned method,  we run the three different kinds of 
materialisation. 

##### Naive Materialisation

```shell
python naive.py --datapath your_dataset_path --rulepath your_program_path --K number of rule application
```

##### Seminaive Materialisation

```shell
python seminaive.py --datapath your_dataset_path --rulepath your_program_path --K number of rule application
```

##### Optimised Seminaive Materialisation

```shell
python optimisation.py --datapath your_dataset_path --rulepath your_program_path --K number of rule application
```




--------------------------------------------------------------------------------
