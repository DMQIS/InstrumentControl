# Original Code taken from GitHub of Digiducer then edited


# !/usr/bin/env python3
# Example of accessing USB Audio devices produced by The Modal Shop (TMS)
#
# Devices include Digital Accelerometers and Digital Signal Conditioners
# Developed using Python 3.10.5 on Windows
#
# Device interface details are available in The Modal Shop manual
# MAN-0343 (USB Audio Interface Guide)
#
# Version 1.0 6/21/2022 TEC
#
import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
import datetime
from sys import platform
import time
import queue
from scipy.signal import periodogram as psd

# define sensitivity for attached sensors if using digital signal conditioner
# Units are mV / engineering units ie 100mV / g
# set to 0 to not apply sensitivity to get volts
#
# Digital Accelerometers like the 333D01 return g's.  That can be scale to m/s^2
eu_sen = np.array([100.0, 100.0])
eu_units = ["g", "g"]
s = int(input("How long is this run in seconds? ")) # set length of measurement
blocksize = 48000*s  # Number of samples to acquire per block
samplerate = 48000  # 48000, 44100, 32000, 22100, 16000, 11050, 8000
reps = 1  # repetitions of data collection
mn = -1  # Graph minimum
mx = 1  # Graph maximum
chan = 1  # channel (0 or 1) (Channel 1 should be more sensitive)
name = input("What is the name of this run? ")  # Name for save files

# TMSFindDevices
#
# returns an array of TMS compatible devices with associated information
#
# Returns dictionary items per device
#   "device"        - Device number to be used by SoundDevice stream
#   "model"         - Model number
#   "serial_number" - Serial number
#   "date"          - Calibration date
#   "format"        - format of data from device, 0 - acceleration, 1 - voltage
#   "sensitivity_int - Raw sensitivity as integer counts/EU ie Volta or m/s^2
#   "scale"         - sensitivity scaled to float for use with a
#                     -1.0 to 1.0 scaled data.  Format returned with
#                     'float32' format to SoundDevice stream.


def TMSFindDevices():
    # The Modal Shop model number substrings
    models = ["485B", "333D", "633A", "SDC0"]

    # Windows has a variety of API's to access audio
    # many of them manipulate the data and do not support setting actual
    # requested sample rates.  Windows Kernal Streaming allows direct control
    # so find devices using that API
    if platform == "win32":         # Windows...
        hapis = sd.query_hostapis()
        api_num = 0
        for api in hapis:
            if api['name'] == "Windows WDM-KS":
                break
            api_num += 1
    else:
        # Not Windows - other platforms don't have the issue with the API
        api_num = 0
    # Return all available audio inputs
    devices = sd.query_devices()
    dev_info = []   # Array to store info about each compa
    dev_num = 0
    # Iterate through available devices and find ones named with a TMS model.
    # Note this returns multiple instances of the same device, because there
    # are different audio API's available.
    for device in devices:
        if device['hostapi'] == api_num:
            name = device['name']
            match = next((x for x in models if x in name), False)
            if match is not False:
                loc = name.find(match)
                model = name[loc:loc+6]  # Extract the model
                fmt = name[loc+7:loc+8]  # Extract the format of data
                serialnum = name[loc+8:loc+14]  # Extract the serial number
                # parse devices that are voltage
                if fmt == "2" or fmt == '3':
                    form = 1    # Voltage
                    # Extract the sensitivity
                    sens = [int(name[loc+14:loc+21]), int(name[loc+21:loc+28])]
                    if fmt == "3":  # 50mV reference for format 3
                        sens[0] *= 20  # Convert to 1V reference
                        sens[1] *= 20
                    scale = np.array([8388608.0/sens[0],
                                      8388608.0/sens[1]],
                                     dtype='float32')  # scale to volts
                    date = datetime.datetime.strptime(name[loc+28:loc+34], '%y%m%d')
                    # Isolate the calibration date from the fullname string
                elif fmt == "1":
                    # These devices are acceleration
                    form = 0
                    # Extract the sensitivity
                    sens = [int(name[loc+14:loc+19]), int(name[loc+19:loc+24])]
                    scale = np.array([855400.0/sens[0],
                                      855400.0/sens[1]],
                                     dtype='float32')  # scale to g's
                    date = datetime.datetime.strptime(name[loc+24:loc+30], '%y%m%d')
                    # Isolate the calibration date from the fullname string
                else:
                    print("Expecting a different format")
                    # raise FormatError("Expecting 1, 2, or 3 format")
                # Add new device to array
                dev_info.append({"device": dev_num,
                                 "model": model,
                                 "serial_number": serialnum,
                                 "date": date,
                                 "format": form,
                                 "sensitivity_int": sens,
                                 "scale": scale,
                                 })
        dev_num += 1
    if len(dev_info) == 0:
        print("ERROR: No compatible devices found")
        exit()
        # raise NoDevicesFound("No compatible devices found")
    print(dev_info)
    return dev_info

# sounddevice utilizes a call back from PortAudio to lower latency of
# processing
# This is called from a different thread
# Use queue to send data to main processing thread


def callback(indata, frames, time, status):
    if status:
        print(status)
    q.put(indata[:, :])  # Place data in queue


# Find compatible devices and extra parameters from the device name


info = TMSFindDevices()
# This example just uses the first device for simplicity.
if len(info) > 1:
    print("Using first device found.")

# Default to first found - a selection could be added if needed from devices in info
dev = 0

# Determine data scaling
units = ["Volts", "Volts"]
scale = info[dev]['scale']
if info[dev]['format'] == 1:  # voltage data so there may be a sensor sensitivity
    for ch in range(len(scale)):
        if eu_sen[ch] != 0.0:
            scale[ch] *= 1.0 / (eu_sen[ch]/1000.0)
            units[ch] = eu_units[ch]
elif info[dev]['format'] == 0:  # acceleration units (this one is used for the accelerometer)
    units = ["g", "g"]

# Use q to get data from callback - call back is in different thread
q = queue.Queue()

stream = sd.InputStream(
        device=info[dev]['device'], channels=2,
        samplerate=samplerate, dtype='float32', blocksize=blocksize,
        callback=callback)

# start recording data
stream.start()
for i in range(reps):
    data = q.get()
    # Note: data *= scale and using 'data' directly in the plot doesn't
    # always scale correctly.  Sometimes accesses unscaled data.
    sdata = data * scale  # Scale the data by an array multiplication

    # sdata is scaled to engineering units (EU) and ready for processing
    # appropriate for your specific application

    # save the data in a .npy file
    if reps == 1:
        np.save(name, sdata)
    else:
        np.save(name + "_" + str(i+1), sdata)

# Stop collecting data
stream.stop()


# plot the data in a periodogram for a quick visual
plt.ion()  # to run GUI even1t loop
figure, ax = plt.subplots()
plt.title(name, fontsize=20)
plt.xlabel("Frequency (Hz)")
plt.ylabel("g**2/Hz")

f, p = psd(sdata[:, chan], fs=samplerate)
plt.loglog(f, p)

plt.show(block=True)
