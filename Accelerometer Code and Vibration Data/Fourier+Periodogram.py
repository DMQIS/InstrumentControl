import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq
from scipy.signal import periodogram as psd

file = input("What is the name of the file? ")
data = np.load(file + ".npy")

# Plot data v time
chan = 1
samplerate = 48000
mn = np.min(data)*1.10
mx = np.max(data)*1.10

plt.ion()  # to run GUI even1t loop
figure, ax = plt.subplots()
plt.title(file, fontsize=20)
plt.xlabel("Time (s)")
plt.ylabel("g")
plt.axis([0, len(data)/samplerate, mn, mx])

x = np.linspace(0, len(data)/samplerate, int(len(data)))
line, = plt.plot(x, data[:, chan])

# Plot fourier transform and periodogram
chan = 1
samplerate = 48000
mn = np.min(data)*1.10
mx = np.max(data)*1.10
f, q = psd(data[:, chan], fs=samplerate)
p = fft(data[:, chan])
x = fftfreq(int(len(data)), 1/samplerate)

plt.ion()  # to run GUI event loop
figure, ax = plt.subplots()
plt.loglog(x, np.abs(p), color="blue")  # fourier transform
plt.loglog(f, q, color="pink")  # periodogram
plt.grid(which="major", linestyle="-", color="black")
plt.grid(which="minor", linestyle="--")

plt.show(block=True)
