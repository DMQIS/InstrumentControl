import numpy as np
from scipy import signal

# window_size is an important parameter affecting the resolution of the analysis.

def psd_fn(file_name, window_size, samplerate, chan = 1):
    # Open file:
    data = np.load(file_name)
    # Determine how many times to split the data:
    splits = int(np.size(data[:, chan]) / samplerate / window_size)
    print('# of splits:' + str(splits))
    #error handling:
    if splits < 1:
        print("File " + file_name + " is too short or window length is too long. Please try again.")
        exit()

    # define variable so we can average all N=splits PSDs:
    psds = np.zeros(int(samplerate / 2 * window_size + 1))

    for j in range(splits):
        f, p = signal.periodogram(data[int(samplerate * window_size * j):int(samplerate * window_size * (j + 1)), chan],
                   fs=samplerate)
        psds = np.add(psds, p)
    avg_PSD = psds / splits

    return avg_PSD, f