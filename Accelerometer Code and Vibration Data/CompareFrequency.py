import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import periodogram as psd

n = int(input("How many files? "))

files = []
data = []
lengths = []

for i in range(n):
    file = input("What is the name of file " + str(i+1) + "? ")
    files.append(file)
    data.append(np.load(file+".npy"))
    lengths.append(len(data[i]))


chan = 1
samplerate = 48000

plt.ion()  # to run GUI event loop
figure, ax = plt.subplots()
plt.title(" ", fontsize=20)
plt.xlabel("Frequency (Hz)")
plt.ylabel("psd units")


for i in range(n):
    f, p = psd(data[i][:, chan], fs=samplerate)
    plt.loglog(f, p, label=files[i])

plt.legend()
plt.show(block=True)
