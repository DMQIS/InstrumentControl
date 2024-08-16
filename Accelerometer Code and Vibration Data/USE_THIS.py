import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import periodogram as psd

n = int(input("How many files? "))  # How many files to compare?
s = float(input("Time (in seconds)? "))  # Set time which is used to split data

# Set up graph
plt.ion()
figure, ax = plt.subplots()
plt.title("", fontsize=20)
plt.xlabel("Frequency (Hz)")
plt.ylabel("g**2/Hz")
plt.grid(which="major", linestyle="-", color="black")
plt.grid(which="minor", linestyle="--")

mx = []
mn = []
chan = 1
samplerate = 48000

for i in range(n):
    # Open files
    file = input("What is the name of file " + str(i+1) + "? ")
    data = np.load(file+".npy")
    splits = int(np.size(data[:, chan])/samplerate/s)

    if splits < 1:
        print("File is too short or time is too long. Please try again.")
        exit()

    # Average and plot data
    new = np.zeros(int(samplerate/2*s+1))
    for j in range(splits):
        _, p = psd(data[int(samplerate*s*j):int(samplerate*s*(j+1)), chan], fs=samplerate)
        new = np.add(new, p)
    f, _ = psd(data[0:int(samplerate*s), chan], fs=samplerate)
    plt.loglog(f, new/splits, label=file)

    mx.append(np.max(new)/splits)
    mn.append(float(np.sort(new)[1])/splits)

plt.axis((.9/s, samplerate/2*1.1, 10**(np.log10(min(mn))-.5), 10**(np.log10(max(mx))+.5)))
plt.legend()
plt.show(block=True)
