links_str = """
link(i1,i1b,we).
link(i1b,gneJ1,we).
link(i2,i2b,we).
link(i2b,gneJ1,we).
link(gneJ1,lnk1a,we).
link(lnk1a,lnk1b,we).
link(gneJ1,o1b,ew).
link(o1b,o1,ew).
link(lnk1b,lnk1a,ew).
link(lnk1a,gneJ1,ew).
link(lnk1b,lnk1c,we).
link(lnk1c,gneJ13,we).
link(gneJ13,o5b,we).
link(o5b,o5,we).
link(gneJ13,o4b,we).
link(o4b,o4,we).
link(gneJ13,lnk1c,ew).
link(lnk1c,lnk1b,ew).
link(i4,i4b,ew).
link(i4b,gneJ13,ew).
link(i3,i3b,ew).
link(i3b,gneJ13,ew).
link(i5,i5b,ew).
link(i5b,gneJ13,ew).
link(gneJ13,o5b,ew).
link(o5b,o5,ew).
"""
links = []
for item in links_str.split("\n"):
   if item.strip() == "":
       continue
   start = item.split("(")[1].split(",")[0]
   end = item.split(",", 1)[1].split(",")[0]
   links.append((start.strip(), end.strip()))


# shortbreak_writer = open("programs/efficient_shortbreak.txt", "w")
# template = "NotPos(V,{},{}):-Present(V),Lane({},{}),Pos(V,{},{})"
# for item1 in links:
#     for item2 in links:
#         if item1 != item2:
#             rule = template.format(item2[0], item2[1], item2[0], item2[1], item1[0], item1[1])
#             shortbreak_writer.write(rule+"\n")

third_writer = open("programs/simple_shortbreak_1.txt", "w")
template_1 = "ShortStop(V):-OnLane(V,{},{}),Boxminus[1,1]OnLane(V,{},{}),Boxminus[2,2]OnLane(V,{},{})"
template_2 = "ShortStop(V):-NonPresent(V),Boxminus[1,1]OnLane(V,{},{}),Boxminus[2,2]OnLane(V,{},{})"
template_3 = "ShortStop(V):-OnLane(V,{},{}),Boxminus[1,1]OnLane(V,{},{}),Boxminus[2,2]NonPresent(V)"
template_4 = "ShortStop(V):-NonPresent(V),Boxminus[1,1]OnLane(V,{},{}),Boxminus[2,2]NonPresent(V)"

for item1 in links:
    for item2 in links:
        for item3 in links:
            if item1 != item2 and item1 != item3:
                rule = template_1.format(item2[0], item2[1], item1[0], item1[1], item3[0], item3[1])
                third_writer.write(rule+"\n")

for item1 in links:
    for item2 in links:
        if item1 != item2:
            rule = template_2.format(item1[0], item1[1], item2[0], item2[1])
            third_writer.write(rule+"\n")

for item1 in links:
    for item2 in links:
        if item1 != item2:
            rule = template_3.format(item2[0], item2[1], item1[0], item1[1])
            third_writer.write(rule + "\n")

for item1 in links:
        rule = template_4.format(item1[0], item1[1])
        third_writer.write(rule + "\n")


template_1 = "ShortStop(V):-OnLane(V,{},{}),Boxminus[1,1]OnLane(V,{},{}),Boxminus[2,2]OnLane(V,{},{}),Boxminus[3,3]OnLane(V,{},{})"
template_2 = "ShortStop(V):-NonPresent(V),Boxminus[1,1]OnLane(V,{},{}),Boxminus[2,2]OnLane(V,{},{}),Boxminus[3,3]OnLane(V,{},{})"
template_3 = "ShortStop(V):-OnLane(V,{},{}),Boxminus[1,1]OnLane(V,{},{}),Boxminus[2,2]OnLane(V,{},{}),Boxminus[3,3]NonPresent(V)"
template_4 = "ShortStop(V):-NonPresent(V),Boxminus[1,1]OnLane(V,{},{}),Boxminus[2,2]OnLane(V,{},{}),Boxminus[3,3]NonPresent(V)"

for item1 in links:
    for item2 in links:
        for item3 in links:
            if item1 != item2 and item1 != item3:
                rule = template_1.format(item2[0], item2[1], item1[0], item1[1], item1[0], item1[1], item3[0], item3[1])
                third_writer.write(rule + "\n")

for item1 in links:
    for item2 in links:
        if item1 != item2:
            rule = template_2.format(item1[0], item1[1], item2[0], item1[1], item2[0], item2[1])
            third_writer.write(rule + "\n")

for item1 in links:
    for item2 in links:
        if item1 != item2:
            rule = template_3.format(item2[0], item2[1], item1[0], item1[1], item2[0], item1[1])
            third_writer.write(rule + "\n")

for item1 in links:
    rule = template_4.format(item1[0], item1[1], item1[1], item2[0])
    third_writer.write(rule + "\n")


template_1 = "ShortStop(V):-OnLane(V,{},{}),Boxminus[1,1]OnLane(V,{},{}),Boxminus[2,2]OnLane(V,{},{}),Boxminus[3,3]OnLane(V,{},{}),Boxminus[4,4]OnLane(V,{},{})"
template_2 = "ShortStop(V):-NonPresent(V),Boxminus[1,1]OnLane(V,{},{}),Boxminus[2,2]OnLane(V,{},{}),Boxminus[3,3]OnLane(V,{},{}),Boxminus[4,4]OnLane(V,{},{})"
template_3 = "ShortStop(V):-OnLane(V,{},{}),Boxminus[1,1]OnLane(V,{},{}),Boxminus[2,2]OnLane(V,{},{}),Boxminus[3,3]OnLane(V,{},{}),Boxminus[4,4]NonPresent(V)"
template_4 = "ShortStop(V):-NonPresent(V),Boxminus[1,1]OnLane(V,{},{}),Boxminus[2,2]OnLane(V,{},{}),Boxminus[3,3]OnLane(V,{},{}),Boxminus[4,4]NonPresent(V)"


for item1 in links:
    for item2 in links:
        for item3 in links:
            if item1 != item2 and item1 != item3:
                rule = template_1.format(item2[0], item2[1], item1[0], item1[1], item1[0], item1[1], item1[1], item1[0], item1[1],item3[0], item3[1])
                third_writer.write(rule + "\n")

for item1 in links:
    for item2 in links:
        if item1 != item2:
            rule = template_2.format(item1[0], item1[1], item2[0], item1[1], item1[1], item1[0], item1[1],item2[0], item2[1])
            third_writer.write(rule + "\n")

for item1 in links:
    for item2 in links:
        if item1 != item2:
            rule = template_3.format(item2[0], item2[1], item1[0], item1[1], item1[1], item1[0], item1[1],item2[0], item1[1])
            third_writer.write(rule + "\n")

for item1 in links:
    rule = template_4.format(item1[0], item1[1], item1[1], item2[0], item1[1], item1[0], item1[1])
    third_writer.write(rule + "\n")

template_1 = "ShortStop(V):-OnLane(V,{},{}),Boxminus[1,1]OnLane(V,{},{}),Boxminus[2,2]OnLane(V,{},{}),Boxminus[3,3]OnLane(V,{},{}),Boxminus[4,4]OnLane(V,{},{})Boxminus[5,5]OnLane(V,{},{})"
template_2 = "ShortStop(V):-NonPresent(V),Boxminus[1,1]OnLane(V,{},{}),Boxminus[2,2]OnLane(V,{},{}),Boxminus[3,3]OnLane(V,{},{}),Boxminus[4,4]OnLane(V,{},{})Boxminus[5,5]OnLane(V,{},{})"
template_3 = "ShortStop(V):-OnLane(V,{},{}),Boxminus[1,1]OnLane(V,{},{}),Boxminus[2,2]OnLane(V,{},{}),Boxminus[3,3]OnLane(V,{},{}),Boxminus[4,4]OnLane(V,{},{})Boxminus[5,5]NonPresent(V)"
template_4 = "ShortStop(V):-NonPresent(V),Boxminus[1,1]OnLane(V,{},{}),Boxminus[2,2]OnLane(V,{},{}),Boxminus[3,3]OnLane(V,{},{}),Boxminus[4,4]OnLane(V,{},{})Boxminus[5,5]NonPresent(V)"

for item1 in links:
    for item2 in links:
        for item3 in links:
            if item1 != item2 and item1 != item3:
                rule = template_1.format(item2[0], item2[1], item1[0], item1[1], item1[0], item1[1], item1[1], item1[0], item1[1], item1[0], item1[1], item3[0], item3[1])
                third_writer.write(rule + "\n")

for item1 in links:
    for item2 in links:
        if item1 != item2:
            rule = template_2.format(item1[0], item1[1], item2[0], item1[1], item1[1], item1[0], item1[1], item1[0], item1[1],item2[0], item2[1])
            third_writer.write(rule + "\n")

for item1 in links:
    for item2 in links:
        if item1 != item2:
            rule = template_3.format(item2[0], item2[1], item1[0], item1[1], item1[1], item1[0], item1[1], item1[0], item1[1], item2[0], item1[1])
            third_writer.write(rule + "\n")

for item1 in links:
    rule = template_4.format(item1[0], item1[1], item1[1], item2[0], item1[1], item1[0], item1[1], item1[0], item1[1])
    third_writer.write(rule + "\n")


