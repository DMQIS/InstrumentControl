import numpy as np
import matplotlib.pyplot as plt

print("NOTE: Only works if files are same length!!!")

n = int(input("How many files? "))  # How many files to compare?

files = []
data = []
lengths = []

# Collect data
for i in range(n):
    file = input("What is the name of file " + str(i+1) + "? ")
    files.append(file)
    data.append(np.load(file+".npy"))
    lengths.append(len(data[i]))


chan = 1
samplerate = 48000
mn = -1  # Graph minimum
mx = 1  # Graph maximum

# Set up graph
plt.ion()  # to run GUI event loop
figure, ax = plt.subplots()
plt.title(" ", fontsize=20)
plt.xlabel("Time (s)")
plt.ylabel("g")
plt.axis([0, max(lengths)/samplerate, mn, mx])

# Plot data
for i in range(n):
    x = np.linspace(0, max(lengths)/samplerate, lengths[i])
    line, = plt.plot(x, data[i][:, chan], label=files[i])

plt.legend()
plt.show(block=True)
