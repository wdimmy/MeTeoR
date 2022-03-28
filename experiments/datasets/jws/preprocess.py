from collections import defaultdict
import re
vehicles = defaultdict(set)

start_timepoint = 0
end_timepoint = 201 #exclusive
data_path = "hackathon/traffic1.txt"
with open(data_path) as file:
    for line in file:
        if line.startswith("OnLane("):
            vehicle = line.split("(")[1].split(",")[0].strip()
            value = line.split("[")[1].split(",")[0].strip()
            vehicles[vehicle].add(int(value))

present_template = "{}({})@[{},{}]"
link_template =  "{}({},{})@[{},{}]"
new_traffic = []
for key in vehicles:
   for i in range(start_timepoint, end_timepoint):
       if i in vehicles[key]:
           new_traffic.append(present_template.format("Present", key, i, i)+"\n")
       else:
           new_traffic.append(present_template.format("NonPresent", key, i, i)+"\n")


links = []
m = re.compile(r"\((.+),(.+),.*")
with open("hackathon/kb.txt") as file:
    for line in file:
        if line.startswith("link"):
            ans = m.search(line)
            if ans is not None:
                links.append((ans.group(1), ans.group(2)))

for i in range(start_timepoint, end_timepoint):
    for link in links:
       new_traffic.append(link_template.format("Link", link[0], link[1], i, i))

with open(data_path, "a") as file:
    for fact in new_traffic:
        file.write(fact)




