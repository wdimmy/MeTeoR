import argparse
import os
parser = argparse.ArgumentParser()
parser.add_argument("--fixatom_datalogmtl_file_path", type=str)
parser.add_argument("--repeated_num", type=int, default=10)
parser.add_argument("--scale", default=50, type=float)
args = parser.parse_args()


lines = []
with open(args.fixatom_datalogmtl_file_path) as file:
   for line in file:
        a, b = line.split("@")
        b = b.strip()
        left_bracket = b[0]
        right_bracket = b[-1]
        left_point, right_point = b[1:-1].split(",")
        fact = "{}@{}{},{}{}"
        for i in range(args.repeated_num):
            new_fact = fact.format(a, left_bracket, float(left_point) + i*args.scale, float(right_point) + i*args.scale, right_bracket)
            lines.append(new_fact+"\n")

fix_num = int(len(lines) / args.repeated_num)
increased_num = int(len(lines))
with open(os.path.join(os.path.dirname(args.fixatom_datalogmtl_file_path), "fixatom_{}_{}".format(fix_num, increased_num)), "w") as file:
    for line in lines:
        file.write(line)



