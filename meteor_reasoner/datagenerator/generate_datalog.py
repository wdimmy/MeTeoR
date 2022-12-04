import rdflib
from collections import defaultdict
import os
# import argparse
# parser = argparse.ArgumentParser()
# parser.add_argument("--owl_path",  type=str, help="input the dir_path where owl files locate.")
# parser.add_argument("--out_dir", type=str, help="input the path for the converted datalog triplets.")
# args = parser.parse_args()


def extract_triplets(owl_path, out_dir):
    entities = dict() # the key is the entity ids
    ID_ = "ID"
    ID_cnt = 0

    predicates = defaultdict(int)
    a1 = "http://swat.cse.lehigh.edu/onto/univ-bench.owl#"
    ignores = ["http://www.w3.org/2002/07/owl#imports", a1 + "emailAddress", a1 + "telephone"]

    if owl_path.endswith("/"):
        owl_path = owl_path[:-1]

    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    fileout = open(os.path.join(out_dir, os.path.split(owl_path)[1]), "w")
    for filename in os.listdir(owl_path):
        g = rdflib.Graph()
        g.load(os.path.join(owl_path, filename))
        degree_intervals_dict = defaultdict(dict)
        for s, p, o in g:
            s, p, o = str(s), str(p), str(o)
            if p in ignores:
              continue

            if p == "http://www.w3.org/1999/02/22-rdf-syntax-ns#type":
                _prefix, _value = o.split("#")
                if "Ontology" in _value:
                    continue
                str_s = str(s).lower().strip()
                if str_s not in entities:
                    entities[str_s] = ID_ + str(ID_cnt)
                    str_s = ID_ + str(ID_cnt)
                    ID_cnt += 1
                else:
                    str_s = entities[str_s]

                fact = _value + "(" + str_s + ")"
                fileout.write(fact + "\n")
                predicates[_value] += 1

            else:
                _prefix, _value = p.split("#")
                str_s = str(s).lower()
                str_o = str(o).lower()
                if str_s not in entities:
                    entities[str_s] = ID_ + str(ID_cnt)
                    str_s = ID_ + str(ID_cnt)
                    ID_cnt += 1
                else:
                    str_s = entities[str_s]

                if str_o not in entities:
                    entities[str_o] = ID_ + str(ID_cnt)
                    str_o = ID_ + str(ID_cnt)
                    ID_cnt += 1
                else:
                    str_o = entities[str_o]

                fact = _value + "(" + str_s + "," + str_o + ")"
                fileout.write(fact + "\n")
                predicates[_value] += 1

    with open(os.path.join(out_dir, "statistics.txt"), "w") as file:
        number_triplets = 0
        for predicate, num in predicates.items():
            number_triplets += num
            file.write(predicate + ":" + str(num) + "\n")

        file.write("The number of unique entities:" + str(len(entities)) + "\n")
        file.write("The number of triplets:" + str(number_triplets))





