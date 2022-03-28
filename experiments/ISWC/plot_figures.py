import matplotlib.pyplot as plt
x = [5, 10, 20, 30]

y1 = [287.51, 687.97, 1421.23,2046.63]
y2 = [354.57, 494.53, 842.64, 1157.70]
y3 = [381.12, 423.65, 612.11, 801.22]

plt.figure(figsize=(5, 2.7))
plt.plot(x, y1, label='Naive')  # Plot some data on the (implicit) axes.
plt.plot(x, y2, label='Seminaive')  # etc.
plt.plot(x, y3, label='Optimised')


plt.xlabel('Number of iterations')
plt.ylabel('Run times (s)')
plt.title("Dataset (5 million facts)")
plt.legend()
plt.show()