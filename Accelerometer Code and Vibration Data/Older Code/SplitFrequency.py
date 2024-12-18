import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import periodogram as psd

n = int(input("How many splits? "))  # How many parts should the data be split into? For 1s from 60s files, use 60.

files = []
data = []

# Collect data
file = input("What is the name of the file? ")
files.append(file)
data.append(np.load(file+".npy"))


chan = 1
samplerate = 48000
size = len(data[0])/n

# Set up graph
plt.ion()  # to run GUI event loop
figure, ax = plt.subplots()
plt.title(files[0], fontsize=20)
plt.xlabel("Frequency (Hz)")
plt.ylabel("g**2/Hz")
plt.grid(which="major", linestyle="-", color="black")
plt.grid(which="minor", linestyle="--")


# Graph data
for i in range(n):
    f, p = psd(data[0][int(size*i):int(size*(i+1)), chan], fs=samplerate)
    plt.loglog(f, p)

plt.show(block=True)
