import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import periodogram as psd

n = int(input("How many splits? "))

files = []
data = []

file = input("What is the name of the file? ")
files.append(file)
data.append(np.load(file+".npy"))


chan = 1
samplerate = 48000
size = len(data[0])/n

plt.ion()  # to run GUI even1t loop
figure, ax = plt.subplots()
plt.title(files[0], fontsize=20)
plt.xlabel("Frequency (Hz)")
plt.ylabel("psd units")


for i in range(n):
    f, p = psd(data[0][int(size*i):int(size*(i+1)), chan], fs=samplerate)
    plt.loglog(f, p)

plt.show(block=True)