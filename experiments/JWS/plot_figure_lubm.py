import pickle
import os
import matplotlib.pyplot as plt
from stream_distribution import generate_stream_distribution

datafiles = ["../datasets/jsw/lubm5.txt", "../datasets/jsw/lubm10.txt","../datasets/jsw/lubm15.txt","../datasets/jsw/lubm20.txt"]
rulepath = "./programs/meteor_recursive.txt"
output_path = "./results/lubm_streams.pkl"

if not os.path.exists(output_path):
   generate_stream_distribution(datafiles, rulepath, output_path)


fig, ax1 = plt.subplots(1)
lubm_streams = pickle.load(open(output_path, "rb"))
x1 = [i*0.5 for i in range(len(lubm_streams[0]))]
for i in lubm_streams:
    ax1.plot(x1, lubm_streams[i])

ax1.set_xlabel("Time point")
ax1.set_ylabel("# of Facts")
ax1.legend(["D1","D2","D3","D4"])
plt.tight_layout()
plt.savefig("./figures/lubm_streams.png")
plt.show()

exit()

stream5 = pickle.load(open("./results/sr_lubm5_meteor_recursive.pkl", "rb"))
stream10 = pickle.load(open("./results/sr_lubm10_meteor_recursive.pkl", "rb"))
stream15 = pickle.load(open("./results/sr_lubm15_meteor_recursive.pkl", "rb"))
stream20 = pickle.load(open("./results/sr_lubm20_meteor_recursive.pkl", "rb"))

stream5_non = pickle.load(open("./results/sr_lubm5_meteor_nonrecursive.pkl", "rb"))
stream10_non = pickle.load(open("./results/sr_lubm10_meteor_nonrecursive.pkl", "rb"))
stream15_non = pickle.load(open("./results/sr_lubm15_meteor_nonrecursive.pkl", "rb"))
stream20_non = pickle.load(open("./results/sr_lubm20_meteor_nonrecursive.pkl", "rb"))


fig, ax1 = plt.subplots(1)

x1 = [i for i in range(0, len(stream5["window_size_raw"])+1)]
ax1.plot(x1, [0]+stream5["window_size_raw"], label='D1',linewidth=1)  # etc.
ax1.plot(x1, [0]+stream10["window_size_raw"], label='D2',linewidth=1)  # etc.
ax1.plot(x1, [0]+stream15["window_size_raw"], label='D3',linewidth=1)  # etc.
ax1.plot(x1, [0]+stream20["window_size_raw"], label='D4',linewidth=1)  # etc.
ax1.set_xlabel("Time point")
ax1.set_ylabel("# of Facts")
ax1.legend()
plt.tight_layout()
plt.savefig("./figures/lubm_recursive.png")
plt.show()

fig, ax1 = plt.subplots(1)
x1 = [i for i in range(0, len(stream5_non["window_size_raw"])+1)]
ax1.plot(x1, [0]+stream5_non["window_size_raw"], label='D1',linewidth=1)  # etc.
ax1.plot(x1, [0]+stream10_non["window_size_raw"], label='D2',linewidth=1)  # etc.
ax1.plot(x1, [0]+stream15_non["window_size_raw"], label='D3',linewidth=1)  # etc.
ax1.plot(x1, [0]+stream20_non["window_size_raw"], label='D4',linewidth=1)  # etc.
ax1.set_xlabel("Time point")
ax1.set_ylabel("Run Time(s)")

ax1.legend()
plt.tight_layout()
plt.savefig("./figures/lubm_nonrecursive.png")
plt.show()
