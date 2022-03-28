import matplotlib.pyplot as plt
from stream_distribution import generate_stream_distribution
import pickle
import os
datafiles = ["../datasets/jsw/hackathon/traffic1.txt", "../datasets/jsw/hackathon/traffic3.txt"]
rulepath = "./programs/efficient_shortbreak.txt"
output_path = "./results/traffic_streams.pkl"

if not os.path.exists(output_path):
   generate_stream_distribution(datafiles, rulepath, output_path)

fig, ax1 = plt.subplots(1)
traffic_streams = pickle.load(open(output_path, "rb"))
x1 = [i for i in range(0, len(traffic_streams[0]))]
for key in traffic_streams:
    ax1.plot(x1, traffic_streams[key], label='Small',linewidth=1)
    ax1.plot(x1, traffic_streams[key], label='large',linewidth=1)
ax1.set_xlabel("Time point")
ax1.set_ylabel("# of Facts")
plt.tight_layout()
plt.legend()
plt.savefig("./figures/traffic_streams.png")
plt.show()

fig, ax1 = plt.subplots(1)
streams_large = pickle.load(open("results/sr_traffic_shortbreak_large.pkl", "rb"))
streams_small = pickle.load(open("results/sr_traffic_shortbreak_small.pkl", "rb"))


prev = streams_small["run_times"][0]
gap_max_small = 0
gaps_small = []
for i in streams_small["run_times"][1:]:
    gap_max_small = max(i-prev, gap_max_small)
    gaps_small.append(i-prev)
    prev = i
gaps_small.append(gaps_small[-1]-0.02)
print("maximum run time:(small)", gap_max_small)
print("average run time:(small)", sum(gaps_small)/len(gaps_small))

prev = streams_large["run_times"][0]
gap_max_large = 0
gaps_large = []
for i in streams_large["run_times"][1:]:
    gap_max_large = max(i-prev, gap_max_large)
    gaps_large.append(i-prev)
    prev = i
gaps_large.append(gaps_large[-1]-0.1)
print("maximum run time:(large)", gap_max_large)
print("average run time:(large)", sum(gaps_large)/len(gaps_large))


print(max(streams_small["window_size_raw"]))
print(max(streams_large["window_size_raw"]))

print("maximum size:(small)", max(streams_small["window_size_raw"]))
print("average size:(small)", sum(streams_small["window_size_raw"])/ len(streams_small["window_size_raw"]))
print("maximum size:(large)", max(streams_large["window_size_raw"]))
print("average size:(large)", sum(streams_large["window_size_raw"])/ len(streams_large["window_size_raw"]))

fig, ax1 = plt.subplots(1)

x1 = [i for i in range(0, len(streams_small["window_size_raw"])+1)]
ax1.plot(x1, [0]+streams_small["window_size_raw"], label='Small',linewidth=1)  # etc.
ax1.plot(x1, [0]+streams_large["window_size_raw"], label='Large',linewidth=1)  # etc.
ax1.set_xlabel("Time point")
ax1.set_ylabel("# of Facts")
ax1.legend()
plt.tight_layout()
plt.savefig("./figures/traffic_time.png")
plt.show()

fig, ax1 = plt.subplots(1)
x1 = [i for i in range(0, len(gaps_small))]
ax1.plot(x1, gaps_small, label='Small',linewidth=1)  # etc.
ax1.plot(x1, gaps_large, label='Large',linewidth=1)  # etc.
ax1.set_xlabel("Time point")
ax1.set_ylabel("Run Time(s)")

ax1.legend()
plt.tight_layout()
plt.savefig("./figures/traffic_time.png")
plt.show()
