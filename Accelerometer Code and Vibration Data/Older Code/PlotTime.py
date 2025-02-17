import numpy as np
import matplotlib.pyplot as plt

n = int(input("How many files? "))  # How many files to graph?

for i in range(n):
    # Open data
    file = input("What is the name of file " + str(i+1) + "? ")
    data = np.load(file+".npy")
    chan = 1
    samplerate = 48000
    mn = np.min(data)*1.10
    mx = np.max(data)*1.10

    # Graph data
    plt.ion()  # to run GUI event loop
    figure, ax = plt.subplots()
    plt.title(file, fontsize=20)
    plt.xlabel("Time (s)")
    plt.ylabel("g")
    plt.axis([0, len(data)/samplerate, mn, mx])

    x = np.linspace(0, len(data)/samplerate, len(data))
    line, = plt.plot(x, data[:, chan])

plt.show(block=True)
