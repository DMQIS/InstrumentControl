import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import periodogram as psd
from scipy.fft import fft, fftfreq


chan = 1
samplerate = 48000
s = .1

plt.ion()  # to run GUI event loop
figure, ax = plt.subplots()
plt.title(" ", fontsize=20)
plt.xlabel("Frequency (Hz)")
plt.ylabel("Transmissibility")

lst = []

for i in range(2):
    # Open files
    file = input("What is the name of file " + str(i + 1) + "? ")
    data = np.load(file + ".npy")
    splits = int(np.size(data[:, chan]) / samplerate / s)

    if splits < 1:
        print("File is too short or time is too long. Please try again.")
        exit()

    # Average and plot data
    new = np.zeros(int(samplerate * s))
    for j in range(splits):
        q = fft(data[int(samplerate * s * j):int(samplerate * s * (j + 1)), chan])
        new = np.add(new, q)
    x = fftfreq(int(np.size(data[0:int(samplerate*s), chan])/1), 1/samplerate)
    lst.append(new)

# f, p = psd(data[0][0:, chan], fs=samplerate)
# p1 = fft(data[0][0:, chan])
# x = fftfreq(int(len(data[0])/1), 1/samplerate)
# print(f, p, x, p1)
# f, q = psd(data[1][0:, chan], fs=samplerate)
# q1 = fft(data[1][0:, chan])
# x = fftfreq(int(len(data[1])/1), 1/samplerate)
# print(f, q, x, q1)
r = np.divide(lst[1], lst[0])
# r1 = np.divide(q1, p1)
# print(r, r1)
# plt.loglog(f, r, color="pink", label="Periodogram")
plt.loglog(x, np.abs(r), color="navy", label="Fourier Transform")


plt.grid(which="major", linestyle="-", color="black")
plt.grid(which="minor", linestyle="--")

plt.legend()
plt.show(block=True)
