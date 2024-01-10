## https://github.com/nkurinsky/NEXUS_RF/blob/main/AcquisitionScripts/VNAMeas.py

import numpy as np
import h5py
import os

class VNAMeas:

	## Class attributes
	series  = "00000000_000000"		## [STRING] YYYYMMDD_HHMMSS
	device  = "whatsinthefridge"	## [STRING] Chip identifier
	s_parameter = "S21"				## [STRING] S-parameter to measure

	vna_power    = 0.0			    ## [FLOAT] (dBM) RF stimulus power
	device_power = 0.0				## [FLOAT] (dBM) Power at device given fridge attenuation
	
	n_avgs  = 1						## [INT] How many sweeps to take at a given power
	n_samps = 5e4					## [FLOAT] How many samples to take evenly spaced in freq range

	f_min   = 5e9			     	## [FLOAT] (Hz) minimum frequency of sweep range
	f_max   = 7e9				    ## [FLOAT] (Hz) maximum frequency of sweep range

	freqs  = np.array([])
	amps   = np.array([])
	phases = np.array([])

	def __init__(self, series):
		self.series = series
		return None

	def show(self):
		print("VNA Measurement:", self.series)
		print("====---------------------------====")
		print("|           Series:  ", self.series)
		print("|   Chip Power [dBm]:", self.device_power)
		print("|   VNA Power:       ", self.vna_power)
		print("|   N averages:      ", self.n_avgs)
		print("|   N sweep samples: ", self.n_samps)
		print("|   Sweep f min [Hz]:", self.f_min)
		print("|   Sweep f max [Hz]:", self.f_max)
		print("|   # freq saved:    ", len(self.Qvals))
		print("|   # mag saved:     ", len(self.Ivals))
		print("|   # phases saved:  ", len(self.Qvals))
		print("====---------------------------====")
		return self.series


	def save_hdf5(self, filepath, filename=None):
		## Configure filename
		if filename is None:
			desc = (self.series + "__pwr"	+ str(self.device_power) + 
			  "__avgs" + str(self.n_avgs) + "__npts" + str(self.n_samps) + 
		   	  "__f" + str(self.f_min) + "-" + str(self.f_max))
			filename = desc
		else:
			filename = self.series + "_" + filename

		## Configure filepath
		if not os.path.isdir(filepath):
			os.makedirs(filepath)
		os.chdir(filepath)
		print("Saving data to", filepath, "as", filename+".h5")
			
		with h5py.File(filename+".h5", "w") as f:
			d_series      = f.create_dataset("series" , data=np.array([self.series], dtype='S'))
			d_device      = f.create_dataset("device" , data=np.array([self.device], dtype='S'))
			d_s_parameter = f.create_dataset("s_parameter", data=np.array([self.s_parameter], dtype='S'))
			d_vna_power   = f.create_dataset("vna_power"  , data=np.array([self.vna_power]))
			d_dev_power   = f.create_dataset("device_power"  , data=np.array([self.device_power]))
			d_n_avgs      = f.create_dataset("n_avgs" , data=np.array([self.n_avgs]))
			d_n_samps     = f.create_dataset("n_samps", data=np.array([self.n_samps]))

			d_f_min       = f.create_dataset("f_min"  , data=np.array([self.f_min]))
			d_f_max       = f.create_dataset("f_max"  , data=np.array([self.f_max]))

			d_freqs  = f.create_dataset("freqs",  data=self.freqs.astype(float))
			d_amps   = f.create_dataset("amps",   data=self.amps.astype(float))
			d_phases = f.create_dataset("phases", data=self.phases.astype(float))

			f.close()

		return filepath, filename+".h5"
	
	def store_data(self, f, I, Q):
		S21 = I + 1j*Q
		linmag = np.abs(S21)
		logmag = 20*np.log10(linmag)
		phases = np.angle(S21)
		self.freqs = f
		self.amps = logmag
		self.phases = phases
		return logmag, phases


def read_hdf5(filepath, filename):
	filename = os.path.join(filepath, filename)
	if filename[-3:] != ".h5":
		filename += ".h5"

	with h5py.File(filename, "r") as f:
		_sers = f["series"][0].decode('UTF-8')
		sweep = VNAMeas(_sers)
		sweep.device  = f["device"][0].decode('UTF-8')
		sweep.s_parameter = f["s_parameter"][0].decode('UTF-8')

		sweep.n_avgs  = f["n_avgs"][0]
		sweep.n_samps = f["n_samps"][0]
		sweep.f_min   = f["f_min"][0]
		sweep.f_max   = f["f_max"][0]
		
		sweep.vna_power    = f["vna_power"][0]
		sweep.device_power = f["device_power"][0]
		
		sweep.freqs  = np.array(f["freqs"])
		sweep.amps   = np.array(f["amps"])
		sweep.phases = np.array(f["phases"])

		return sweep

	