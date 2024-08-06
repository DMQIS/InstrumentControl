import numpy as np
import matplotlib.pyplot as plt

print("NOTE: Only works if files are same length!!!")

n = int(input("How many files? "))

data = []
lengths = []

for i in range(n):
    file = input("What is the name of file " + str(i+1) + "? ")
    data.append(np.load(file+".npy"))
    lengths.append(len(data[i]))


chan = 1
samplerate = 48000
mn = -1  # np.min(data)*1.10
mx = 1  # np.max(data)*1.10


plt.ion()  # to run GUI event loop
figure, ax = plt.subplots()
plt.title(" ", fontsize=20)
plt.xlabel("Time (s)")
plt.ylabel("g")
plt.axis([0, max(lengths)/samplerate, mn, mx])


for i in range(n):
    x = np.linspace(0, max(lengths)/samplerate, lengths[i])
    line, = plt.plot(x, data[i][:, chan])

plt.show(block=True)
