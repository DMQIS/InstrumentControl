import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import periodogram as psd

n = int(input("How many files? "))  # How many files to graph?

for i in range(n):
    # Open file
    file = input("What is the name of file " + str(i+1) + "? ")
    data = np.load(file+".npy")
    chan = 1
    samplerate = 48000
    mn = np.min(data)*1.10
    mx = np.max(data)*1.10
    f, p = psd(data[:, chan], fs=samplerate)

    # Plot data
    plt.ion()  # to run GUI even1t loop
    figure, ax = plt.subplots()
    plt.title(file, fontsize=20)
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("g**2/Hz")
    plt.loglog(f, p)
    plt.grid(which="major", linestyle="-", color="black")
    plt.grid(which="minor", linestyle="--")

plt.show(block=True)
