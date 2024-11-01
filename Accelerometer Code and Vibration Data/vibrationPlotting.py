# Script to plot PSDs on the same graph

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import periodogram as psd
from scipy import signal

# window_size is an important parameter affecting the resolution of the analysis.
window_size = 1 #split data into 1 second windows and average over the entirety of the sample

# file1 = "stillRemoteFrame_z_1.npy"
# file2 = "stillFridgeFrame_z_1.npy"
# file3 = "divingBoard_z_1.npy"

# file1 = "pt1.npy"
# file2= "stillRemoteFrame_z_1.npy"

file1 = "pt2.npy"
file2 = "stillFridgeFrame_z_1.npy"

# file2 = "pt2.npy"
# file3 = "divingBoardBeam1_z_1.npy"

# file1 = "PT_line_1.npy"
# file2 = "PT_line_2.npy"
# file3 = "PT_line_3.npy"


# Set up graph
plt.ion()
figure, ax = plt.subplots()
# plt.title(("Comparing frequency spectrum at various points on fridge"), fontsize=20)
plt.title(("Frequency spectrum on Olaf PT lines"), fontsize=20)

plt.xlabel("Frequency [Hz]")
plt.ylabel("Acceleration Spectral Density [g**2/HZ]")
plt.grid(which="major", linestyle="-", color="black")
plt.grid(which="minor", linestyle="--")

mx = []
mn = []
chan = 1
samplerate = 48000 # always verify this matches the actual data sample rate

 # Average and plot data (@sas maybe come back & replace with a scipy periodogram function that performs automatic windowing)
def plot_psd(file_name):
    # Open file:
    data = np.load(file_name)
    # Determine how many times to split the data:
    splits = int(np.size(data[:, chan]) / samplerate / window_size)
    #error handling:
    if splits < 1:
        print("File " + file_name + " is too short or window length is too long. Please try again.")
        exit()
    # define variable so we can average all N=splits PSDs:
    psds = np.zeros(int(samplerate / 2 * window_size + 1))
    for j in range(splits):
        f, p = psd(data[int(samplerate * window_size * j):int(samplerate * window_size * (j + 1)), chan],
                   fs=samplerate)
        psds = np.add(psds, p)
    # use this value for transmissibility:
    avg_PSD = psds / splits
    # Plot:
    plt.loglog(f, avg_PSD, label=file_name)

    return avg_PSD, f

avg_PSD1, freqs = plot_psd(file1)
avg_PSD2, freqs = plot_psd(file2)
# avg_PSD3 = plot_psd(file3)

plt.ylim((10**-11, 10**-5)) # for PSD plotting


# auto-scaling based on limits:
# plt.axis((.9 / window_size, samplerate / 2 * 1.1, 10 ** (np.log10(min(mn)) - .5), 10 ** (np.log10(max(mx)) + .5)))
plt.legend()
plt.show(block=True)
