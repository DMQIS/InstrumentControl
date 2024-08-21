import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq


chan = 1
samplerate = 48000
s = 1  # Sets time to split and average over

plt.ion()  # to run GUI event loop
figure, ax = plt.subplots()
plt.title(" ", fontsize=20)
plt.xlabel("Frequency [Hz]")
plt.ylabel("Transmissibility")

lst = []

for i in range(2):
    # Open files
    if i == 0:
        file = input("What is the name of the input file? ")
    else:
        file = input("What is the name of the output file? ")

    data = np.load(file + ".npy")
    splits = int(np.size(data[:, chan]) / samplerate / s)

    if splits < 1:
        print("File is too short or time is too long. Please try again.")
        exit()

    # Average data
    new = np.zeros(int(samplerate * s))
    for j in range(splits):
        q = fft(data[int(samplerate * s * j):int(samplerate * s * (j + 1)), chan])
        new = np.add(new, q)
    x = fftfreq(int(np.size(data[0:int(samplerate*s), chan])/1), 1/samplerate)
    lst.append(new)

# Divide and plot data
r = np.divide(lst[1], lst[0])
plt.loglog(x, np.abs(r), color="navy")


plt.grid(which="major", linestyle="-", color="black")
plt.grid(which="minor", linestyle="--")
plt.show(block=True)
