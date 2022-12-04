import subprocess
import os
import shutil
# import argparse
#
# parser = argparse.ArgumentParser()
# parser.add_argument("--univ_num", type=int, help= "Input the number of universities you want to generate.")
# parser.add_argument("--dir_name", type=str, help= "Input the directory path used for the generated owl files.")
# args = parser.parse_args()


def generate(univ_num=1, dir_name="./owl_data"):
    onto="http://swat.cse.lehigh.edu/onto/univ-bench.owl"
    cmd = "java edu.lehigh.swat.bench.uba.Generator -univ {} -onto {}"

    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    os.chdir(dir_name)
    subprocess.call(cmd.format(univ_num, onto), shell=True)
    os.chdir("../")
    subprocess.call("rm *log.txt*", shell=True)

    for filename in os.listdir("./"):
        if "University" in filename and ".owl" in filename:
            start_index = filename.index("University")
            new_name = filename[start_index:]
            foldername = filename[0:start_index-1]
            if not os.path.exists('./' + foldername):
                os.makedirs('./' + foldername)
            shutil.move("./" + filename, os.path.join(foldername, new_name))


if __name__ == "__main__":
    generate()