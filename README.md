<p align='center'>
  <img width='40%' src='https://github.com/wdimmy/MeTeoR/blob/main/MeTeoR.png' />
</p>

--------------------------------------------------------------------------------

[![PyPI](https://img.shields.io/pypi/v/meteor-reasoner)](https://pypi.org/project/meteor-reasoner/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/wdimmy/MeTeoR/blob/master/LICENSE)

## Overview

The Metric Temporal Reasoner (MeTeoR) is a scalable reasoner for full DatalogMTL, an extension of Datalog with operators from Metric 
Temporal Logic (MTL). In MeTeoR, we provide lots of 
pluggable functional modules that can be directly reused by other researchers for their research work in the DatalogMTL domain. Besides, we 
will keep continuous maintenance and updates to MeTeoR and provide more implementations from the latest research in DatalogMTL. Currently, 
MeTeoR mainly consists of the following six modules:
<p align='center'>
  <img width='80%' src='https://github.com/wdimmy/MeTeoR/blob/main/modules.png' />
</p>

Besides, MeTeoR provides the implementation for the following papers:


**[MeTeoR: Practical Reasoning in Datalog with Metric Temporal Operators](https://arxiv.org/abs/2201.04596)** Published in AAAI 2022.

**[Finitely Materialisable Datalog Programs with Metric Temporal Operators](https://proceedings.kr.org/2021/59/)** Published in KR 2021.

**Materialisation-based Reasoning in DatalogMTL with Bounded Intervals** Under review for KR 2022.

MeTeoR is an on-going effort, and we are planning to increase our coverage in the future.

## Installation
You can install MeTeoR using Python's package manager `pip`.

#### Requirements
 - Python>=3.7
 - Numpy>=1.16.0
 - pandas>=0.24.0
 - urllib3>=1.24.0
 - scikit-learn>=0.20.0
 - networkx
 - outdated>=0.2.0

#### Pip install
The recommended way to install MeTeoR is using Python's package manager pip:
```bash
pip install meteor_reasoner
```

```bash
python -c "import meteor_reasoner; print(meteor_reasoner.__version__)"
# This should print "1.0.1". Otherwise, please update the version by
pip install -U meteor_reasoner
```


#### From source
You can also install MeTeoR from source. This is recommended if you want to contribute to MeTeoR.
```bash
git clone https://github.com/wdimmy/MeTeoR
cd MeTeoR
pip install -e .
```

## Package Usage
We showcase one features of MeTeoR, namely, easy-to-use data parser.
#### (1) Data parser
The format of the datasets and the program could be found in the example foler.
```python
from meteor_reasoner.utils.loader import *
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--datapath", type=str)
parser.add_argument("--rulepath", type=str)
args = parser.parse_args()

# load the dataset and the program
with open(args.datapath) as file:
        data = file.readlines()
with open(args.rulepath) as file:
        program = file.readlines()
D = load_dataset(data)
D_index = defaultdict(lambda: defaultdict(list))
program = load_program(program)

```

## Citing MeTeoR
If you use MeTeoR in your work, please cite our papers (Bibtex below).
```
@article{wang2022meteor,
  title={MeTeoR: Practical Reasoning in Datalog with Metric Temporal Operators},
  author={Wang, Dingmin and Hu, Pan and Wa{\l}{\k{e}}ga, Przemys{\l}aw Andrzej and Grau, Bernardo Cuenca},
  journal={arXiv preprint arXiv:2201.04596},
  year={2022}
}
```
