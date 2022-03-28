import pickle
# lubm_streams = pickle.load(open("results/traffic_streams.pkl","rb"))
# stream5 = pickle.load(open("./results/sr_lubm5_meteor_recursive.pkl", "rb"))
# stream10 = pickle.load(open("./results/sr_lubm10_meteor_recursive.pkl", "rb"))
# stream15 = pickle.load(open("./results/sr_lubm15_meteor_recursive.pkl", "rb"))
# stream20 = pickle.load(open("./results/sr_lubm20_meteor_recursive.pkl", "rb"))


# traffic distribution
# file_template = "tizk_data/traffic_{}.dat"
# stream = pickle.load(open("./results/traffic_streams.pkl", "rb"))
# for key in stream:
#     writer = open(file_template.format("small"), "w") if key == 0 else open(file_template.format("large"), "w")
#     writer.write("t n" + "\n")
#     for i, value in enumerate(stream[key]):
#         writer.write(str(i)+" "+str(value)+"\n")


# memory size
file_template = "tizk_data/traffic_size_{}.dat"
for name in ["small", "large"]:
    stream = pickle.load(open("./results/sr_traffic_shortbreak_{}.pkl".format(name), "rb"))
    writer = open(file_template.format(name), "w")
    writer.write("t n"+"\n")
    writer.write("0 0" + "\n")
    for i, value in enumerate(stream["window_size_raw"]):
        j = i+1
        writer.write(str(j)+" "+str(value)+"\n")


#
# file_template = "tizk_data/traffic_time_{}.dat"
# for name in ["small", "large"]:
#     stream = pickle.load(open("./results/sr_traffic_shortbreak_{}.pkl".format(name), "rb"))
#     prev = stream["run_times"][0]
#     gap = 0
#     gaps = []
#     for i in stream["run_times"][1:]:
#         gap = max(i - prev, gap)
#         gaps.append(i - prev)
#         prev = i
#     gaps.append(gaps[-1] - 0.1)
#     writer = open(file_template.format(name), "w")
#     writer.write("t n"+"\n")
#     for i, value in enumerate(gaps):
#         writer.write(str(i)+" "+str(value)+"\n")


