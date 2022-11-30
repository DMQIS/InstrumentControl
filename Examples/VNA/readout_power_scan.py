import sys
sys.path.append('C:\\Users\\nexus\\Desktop\\Share\\Share\\CodeSync\\Device_control')
#sys.path.append('Z:\\CodeSync\\Device_control')
#sys.path.append('C:\\Users\\tajdy\\Documents\\SLAC\\TWPA_code\\Device_control')

import VNA, TWPA
import Labber
import numpy as np
import matplotlib.pyplot as plt

client = Labber.connectToServer('localhost', timeout=30)

twpa = TWPA.TWPA(client)
vna = VNA.VNA()

pump_f = 9.2e9
pump_p = 0
pump_atten = 7 # that is -7 dB

fi = 4e9
ff = 8e9
fn = 101

avg_cnt = 10
IFBW = 1e4

pi = -25
pf = -50
pn = 10
ps = np.linspace(pi,pf,pn)

twpa.connectAll()
twpa.setPump(pump_f,pump_p,pump_atten)
print(f"TWPA pump params: {twpa.getPump()}")

vna.setRFOn()
vna.setIFBW(IFBW)
vna.setStartFreq(fi)
vna.setStopFreq(ff)
vna.setNPoints(fn)
vna.setFormat('mlin')

twpa_on = np.zeros((pn,avg_cnt,fn))

twpa.turnOn()

for i,p in enumerate(ps):

	vna.setPower(p)
	print(f"Readout power at VNA set: {p}")
	for j in range(avg_cnt):
		if j%(avg_cnt//10) == 0:
			print(f"count: {j}")
		f,r,im = vna.getData() 
		twpa_on[i,j] = r

twpa.turnOff()

twpa_off = np.zeros((pn,avg_cnt,fn))

for i,p in enumerate(ps):

	vna.setPower(p)
	print(f"Readout power at VNA set: {p}")
	for j in range(avg_cnt):
		if j%(avg_cnt//10) == 0:
			print(f"count: {j}")
		f,r,im = vna.getData()
		twpa_off[i,j] = r

SNR = np.var(twpa_off, axis=1) / np.var(twpa_on, axis=1)
print(SNR.shape)

twpa.disconnectAll()
vna.setRFOff()

extent = [fi,ff,pf,pi]
plt.imshow(SNR, extent=extent, interpolation='none', aspect='auto')
plt.show()