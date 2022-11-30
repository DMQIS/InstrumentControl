import sys
sys.path.append('C:\\Users\\nexus\\Desktop\\Share\\Share\\CodeSync\\Device_control')
#sys.path.append('Z:\\CodeSync\\Device_control')
#sys.path.append('C:\\Users\\tajdy\\Documents\\SLAC\\TWPA_code\\Device_control')

import Labber
import TWPA
import Attenuator
import VNA

import os
import time
import json

import numpy as np
import matplotlib.pyplot as plt

# before running any of these things, ensure HEMT and TWPA are on
# as of writing, best TWPA params are 9.2G and 0 dBm power pump, 7 dB on the attenuator

# all of this was done with VNA atten 10 dB

def VNAPowerS21(vna, fs, powers, average_count):
	"""
	Scan S21 (or in our case actually S43) for several readout powers
	and plot the resulting 2D heatmap.
	"""

	vna.setFormat('mlog')
	vna.setNPoints(average_count)
	vna.setRFOn()

	data = np.zeros((powers.size,fs.size))

	print('working')
	for i,p in enumerate(powers):
		print(p)
		vna.setPower(p)
		for j,f in enumerate(fs):
			vna.setStartFreq(f)
			vna.setStopFreq(f)
			_,r,_ = vna.getData()
			data[i,j] = np.mean(r)

	plt.figure()
	extent = [fs[0], fs[-1], powers[-1]-10, powers[0]-10] # 10 dB on atten
	plt.imshow(data, extent=extent, aspect='auto', interpolation='none')

	vna.setRFOff()
	vna.setIntTrigger()

	return data

def AveragedS43(vna, fs, average_count):

	vna.setFormat('mlog')
	vna.setNPoints(average_count)
	vna.setRFOn()

	data = np.zeros((fs.size))

	for i,f in enumerate(fs):
		print(f"freq {i+1}/{fs.size}")
		vna.setStartFreq(f)
		vna.setStopFreq(f)
		_,r,_ = vna.getData()
		data[i] = np.mean(r)

	vna.setRFOff()

	return data


def ScanAuxAtOneReadoutFreq(readout_f, avg_cnt, readout_power, aux_power, aux_fi, aux_ff, aux_npts, aux_port=2):
	"""

	"""

	aux_fs = np.linspace(aux_fi, aux_ff, aux_npts)

	# set up VNA 

	vna = VNA.VNA()
	vna.setStartFreq(readout_f)
	vna.setStopFreq(readout_f)
	vna.setNPoints(avg_cnt)

	vna.setPower(readout_power)

	vna.setFormat('mlog')

	vna.setRFOn()

	# set up aux source on VNA

	vnaAux = VNA.VNAAux()
	vnaAux.setPort(aux_port)
	vnaAux.setPower(aux_power)

	vnaAux.enable()

	data = np.zeros(aux_fs.size)

	for i,aux_f in enumerate(aux_fs):
		print(aux_f)
		vnaAux.setCWFreq(aux_f)
		f,r,_ = vna.getData()
		data[i] = np.mean(r)

	vna.setRFOff()
	vnaAux.disable()

	vna.setIntTrigger()

	plt.plot(aux_fs,data[:,0].T)
	plt.show()

def twoTone(readout_fs, readout_powers, aux_fs, aux_powers, avg_cnt, baseline_avg_cnt, IFBW, twpa_freq, twpa_power, twpa_atten, data_dir, tag, aux_port=2, aux_atten=10, readout_atten=20, plot=True):
	"""
	The measurement of S43 as a func of readout frequency, readout power, qubit freq, and qubit power.
	output: saves .npy files to data_dir, as well as a json of the parameters for the run (the args to this function)
	The indices of the main result are [fr, pr, fq, pq]
	The indices of the baseline scan are [fr, pr]
	(the baseline is a higher avg count scan with qubit pump off)

	THE freq AND power ARRAYS MUST BE NPARRAYS OF FLOATS
	"""

	if not os.path.exists(data_dir):
		print("making savedir")
		os.makedirs(data_dir)

	paramset = {
		"frs":list(readout_fs),
		"prs":list(readout_powers),
		"fqs":list(aux_fs),
		"pqs":list(aux_powers),
		"avg_cnt":avg_cnt,
		"bl_avg_cnt":baseline_avg_cnt,
		"IFBW":IFBW,
		"twpa_f":twpa_freq,
		"twpa_netp":twpa_power-twpa_atten,
		"aux_atten":aux_atten,
		"readout_atten":readout_atten
	}

	with open(f"{data_dir}\\{tag}_metadata.json", "w") as paramfile:
		json.dump(paramset, paramfile)

	vna_format = 'polar'

	# set up TWPA
	client = Labber.connectToServer('localhost', timeout=30)

	twpa = TWPA.TWPA(client)

	twpa.connectAll()
	twpa.setPump(twpa_freq,twpa_power,twpa_atten)
	twpa.turnOn()
	print("TWPA set to:")
	print(twpa.getPump())

	# set up attens

	four_port = Attenuator.Attenuator('COM4', verbose=False)
	four_port.set(1,aux_atten)
	four_port.set(2,readout_atten)

	# set up VNA 

	vna = VNA.VNA()

	vna.setIFBW(IFBW)

	vna.setFormat(vna_format)

	vna.setRFOn()

	# set up aux source on VNA

	vnaAux = VNA.VNAAux()
	vnaAux.setPort(aux_port)

	# see (approximately) how long it's going to take to do this

	begin = time.time()
	vna.setNPoints(avg_cnt)
	vna.setPower(readout_powers[0])
	vnaAux.setPower(aux_powers[0])
	vnaAux.setCWFreq(aux_fs[0])
	vna.setStartFreq(readout_fs[0])
	vna.setStopFreq(readout_fs[0])
	for i in range(10):
		f,r,im = vna.getData()
	dt = time.time() - begin # seconds
	time_per_read = dt / 10 / 60 # minutes
	total_iterations = readout_powers.size*aux_powers.size*aux_fs.size*readout_fs.size
	total_time = np.round(time_per_read*total_iterations,2) # min

	# start taking data!

	dataRe = np.zeros((readout_fs.size, readout_powers.size, aux_fs.size, aux_powers.size))
	dataIm = np.zeros((readout_fs.size, readout_powers.size, aux_fs.size, aux_powers.size))

	baselineRe = np.zeros((readout_fs.size,readout_powers.size))
	baselineIm = np.zeros((readout_fs.size,readout_powers.size))

	for j,p in enumerate(readout_powers):
		vna.setPower(p)

		vnaAux.enable()
		vna.setNPoints(avg_cnt)

		for i,pq in enumerate(aux_powers):
			vnaAux.setPower(pq)

			for k,aux_f in enumerate(aux_fs):
				vnaAux.setCWFreq(aux_f)

				for l,read_f in enumerate(readout_fs):
					iteration = l+k*readout_fs.size+i*aux_fs.size*readout_fs.size+j*aux_powers.size*aux_fs.size*readout_fs.size
					#print(f"Remaining time (mins): {np.round(iteration*time_per_read,2)}/{total_time} | readout freq {l+1}/{readout_fs.size} readout power {j+1}/{readout_powers.size}, aux freq {k+1}/{aux_fs.size}, aux power {i+1}/{aux_powers.size}  | pq: {pq}, fq: {aux_f}, pr: {p}, fr: {read_f}")
					print(f"Remaining time (mins): {np.round(iteration*time_per_read,2)}/{total_time} | pq: {pq}, fq: {aux_f}, pr: {p}, fr: {read_f}")
					vna.setStartFreq(read_f)
					vna.setStopFreq(read_f)

					f,r,im = vna.getData()
					dataRe[l,j,k,i] += np.mean(r)
					dataIm[l,j,k,i] += np.mean(im)

		vnaAux.disable()
		vna.setNPoints(baseline_avg_cnt)

		for l,read_f in enumerate(readout_fs):
			print(f"Baseline for readout power {j+1}/{readout_powers.size} readout freq {l+1}/{readout_fs.size} | Readout power: {p}, Readout freq: {read_f}")
			vna.setStartFreq(read_f)
			vna.setStopFreq(read_f)
			
			f,r,im = vna.getData()
			baselineRe[l,j] += np.mean(r)
			baselineIm[l,j] += np.mean(im)

	# TODO make saving nice and save params too like the TWPA stuff
	np.save(f"{data_dir}\\{tag}_Re", dataRe)
	np.save(f"{data_dir}\\{tag}_Im", dataIm)
	np.save(f"{data_dir}\\{tag}_baseline_Re", baselineRe)
	np.save(f"{data_dir}\\{tag}_baseline_Im", baselineIm)
	print(f"Data saved to {data_dir}.")

	twpa.turnOff()
	twpa.disconnectAll()
	four_port.set(1,95)
	four_port.set(2,95)
	vna.setRFOff()

	vna.setIntTrigger()

	print("Run finished successfully.")

	if plot:
		extent = [aux_fs[0], aux_fs[-1],readout_fs[-1], readout_fs[0]]
		plt.figure()
		plt.title(f"{tag}, readout power {readout_powers[0]-readout_atten}, qubit power {aux_powers[0]-aux_atten}")
		plt.imshow(dataRe[:,0,:,0]-baselineRe[:,0], extent=extent, interpolation='none', aspect='auto')

def TwoToneBaselineOnly(VNA_fi, VNA_ff, npts, IFBW, readout_power, baseline_avg_cnt, twpa_freq, twpa_power, twpa_atten, aux_atten=10, readout_atten=10):
	"""
	For if you need to retake only the baseline measurement for some reason.
	This only exists because I needed it once and decided not to delete it.
	Below are some sample values.
	
	twpa_freq=9.2e9
	twpa_power = 0
	twpa_atten = 7

	vna_format = 'polar'

	VNA_fi = 5.82645e9
	VNA_ff = 5.82945e9
	npts = 501

	IFBW = 1e3

	readout_power = -50 # dBm
	baseline_avg_cnt = 1000
	"""

	# set up TWPA
	client = Labber.connectToServer('localhost', timeout=30)

	twpa = TWPA.TWPA(client)

	twpa.connectAll()
	twpa.setPump(twpa_freq,twpa_power,twpa_atten)
	print("TWPA set to:")
	print(twpa.getPump())

	# set up attens

	four_port = Attenuator.Attenuator('COM4', verbose=False)
	four_port.set(1,aux_atten)
	four_port.set(2,readout_atten)

	# set up VNA 

	vna = VNA.VNA()
	vna.setStartFreq(VNA_fi)
	vna.setStopFreq(VNA_ff)
	vna.setNPoints(npts)

	vna.setPower(readout_power)
	vna.setIFBW(IFBW)

	vna.setFormat(vna_format)

	vna.setRFOn()

	# set up aux source on VNA

	vnaAux = VNA.VNAAux()
	vnaAux.setPort(2)
	vnaAux.disable()

	baselineRe = np.zeros(npts)
	baselineIm = np.zeros(npts)


	for j in range(baseline_avg_cnt):
		if j%(baseline_avg_cnt//10) == 0:
			print(j)
		f,r,im = vna.getData()
		baselineRe += r
		baselineIm += im

	baselineRe /= baseline_avg_cnt
	baselineIm /= baseline_avg_cnt

	np.save("TTCW_scan_real_baseline_Mag", baselineRe)
	np.save("TTCW_scan_real_baseline_Phase", baselineIm)


if __name__ == "__main__":

	data_dir="C:\\Users\\nexus\\Desktop\\Share\\Share\\Data\\2022-05-26"

	pqi = -45
	pqf = -25
	pqn = 3
	pqs = np.linspace(pqi,pqf,pqn)

	pri = -40
	prf = -40
	prn = 1
	prs = np.linspace(pri,prf,prn)

	# args for reference:
	#TwoTone(readout_fs, readout_powers, aux_fs, aux_powers, avg_cnt, baseline_avg_cnt, IFBW, twpa_freq, twpa_power, twpa_atten, data_dir, tag, aux_port=2, aux_atten=10, readout_atten=10, plot=True)

	resonator_fs = [5.8275e9, 5.9588e9, 6.0745e9, 6.1875e9]
	ground_states = [5.828473e9, 5.95938e9, 6.075066e9, 6.188073e9]
	readout_span = 500e3
	readout_nf = 51
	qubit_transition_freqs = [4.65e9, 4.65e9, 4.83e9, 4.8e9]
	qubit_span = 20e6
	qubit_nf = 151

	# two tone scans

	for i in range(len(resonator_fs)):

		if i != 2:
			continue
		print(f"qubit {i+1}"+" -"*30)

		tag = f"qubit_{i+1}_pqs_scan"
		
		frs = np.linspace(ground_states[i]-readout_span, ground_states[i]+readout_span, readout_nf)
		fqs = np.linspace(qubit_transition_freqs[i]-qubit_span, qubit_transition_freqs[i]+qubit_span, qubit_nf)
		twoTone(frs, prs, fqs, pqs, 100, 1000, 1e3, 9.4e9, 0, 8, data_dir, tag, aux_atten=10, readout_atten=20, plot=False)

		tag = f"qubit_{i+1}_stark"
		
		prn_stark = 30

		frs_stark = np.array([ground_states[i]])
		prs_stark = np.linspace(-55, -15, prn_stark)
		fqs_stark = fqs
		pqs_stark = np.array([-25.])
		twoTone(frs_stark, prs_stark, fqs_stark, pqs_stark, 100, 1000, 1e3, 9.4e9, 0, 8, data_dir, tag, aux_atten=10, readout_atten=20, plot=False)