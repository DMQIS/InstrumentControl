#!/usr/bin/env python
'''
heater.py

Run MC heater up and down and log temperatures + resistances in working dir

usage: ./heater.py
authors: Noah, Jamie
5/30/2023: wrote script
'''

import serial
import codecs
from datetime import timedelta, datetime, tzinfo
from time import sleep

# options
maxheatpct = 100.0  # max MC heater percent
heaterpctinc = 1.0 # heater percent increment
ntemp = 9 # minutes between adjusting heater percent
nlog = 1  # minutes between saving temperatures + resistances to log
#samp_chlist = [1,2,3,4,9,10,11,12,13,14,15,16] # sample channels
samp_chlist = [1,2,3,4,9,10,11,12,13,14,15]
therm_chlist = [6,8] # thermometer channels

# python2 codec problem
codecs.register(lambda name: codecs.lookup('utf-8') if name == 'cp65001' else None)

# connect to Lakeshore 372
port = serial.Serial('COM8',57600,parity=serial.PARITY_ODD,bytesize=serial.SEVENBITS,timeout=1.0)

# setup timezone
class SLACTZ(tzinfo):
	def utcoffset(self, dt):
		return timedelta(hours=-8) + self.dst(dt)
	def dst(self, dt):
		# DST starts last Sunday in March
		d = datetime(dt.year, 4, 1)   # ends last Sunday in October
		self.dston = d - timedelta(days=d.weekday() + 1)
		d = datetime(dt.year, 11, 1)
		self.dstoff = d - timedelta(days=d.weekday() + 1)
		if self.dston <=  dt.replace(tzinfo=None) < self.dstoff:
			return timedelta(hours=1)
		else:
			return timedelta(0)
	def tzname(self,dt):
		return "SLAC"
slac = SLACTZ()

# come up with a file name
t0 = datetime.now(tz=slac)
fn = 'tcsweep_{0:d}{1:02d}{2:02d}_{3:02d}{4:02d}{5:02d}.txt'.format(t0.year,t0.month,t0.day,t0.hour,t0.minute,t0.second)

# Noah functions
def sendCMD(cmd):
	port.write((cmd+'\r\n').encode())
	sleep(1)

def getResponse():
	resp = port.readline()
	sleep(0.5)
	return resp.decode().strip() # remove whitespace/newlines

def printID():
	sendCMD('*IDN?')
	print(getResponse())

def getReadings(chlist=samp_chlist):
	# returns dict, {ch:R}, Rs in Ohms
	retvals = dict()
	for ch in chlist:
		sendCMD('SRDG? {0:d}'.format(ch))
		retvals[ch] = getResponse()
	return retvals

def getTemps(chlist=therm_chlist):
	temps = []
	for ch in chlist:
		sendCMD('RDGK? {0:d}'.format(ch))
		temps.append(getResponse())
	return temps

def setHeater():
	# set up heater
	sendCMD('HTRSET 0,120,0,0,1')
	sendCMD('HTRSET? 0')
	print('HEATER:',getResponse())
	sleep(1)
	sendCMD('RANGE 0,4') # sample heater, 1.0 mA
	sleep(1)
	sendCMD('RANGE? 0')
	sleep(1)
	print('RANGE:',getResponse())
	sleep(1)

def setHeaterPCT(pct):
	sendCMD('MOUT 0,{0:.2f}'.format(pct))

def getHeaterPCT():
	sendCMD('MOUT? 0')
	return getResponse()

# heater loop
printID()
heating = True
heatpct = 0.0 # MC heater percent
loopctr = 0 # loop counter
t1 = datetime.now(tz=slac)
try:
	setHeater()
	while True:
		# reading + writing
		if loopctr % nlog == 0:
			rs = getReadings()
			ts = getTemps()
			for i in range(len(therm_chlist)):
				print('T{0:d}: {1:.3f} mK'.format(therm_chlist[i],float(ts[i])*1e3))
			print(rs)
			# assemble data string, then write
			t1 = datetime.now(tz=slac)
			t1h = t1.hour + t1.minute/60.0 + t1.second/3600.0
			datastr = '{0:.5f},'.format(t1h)
			for temp in ts:
				datastr += temp + ','
			for ch in samp_chlist:
				datastr += rs[ch] + ','
			datastr += '\n'
			with open(fn,'a+') as fp: # file pointer. append!
				fp.write(datastr)
		# adjust heater
		if loopctr % ntemp == 0:
			if heating:
				heatpct += heaterpctinc
			else:
				heatpct -= heaterpctinc
				if heatpct <= 0:
					heatpct = 0
			setHeaterPCT(heatpct)
		print(loopctr, getHeaterPCT())
		# increment, sleep
		loopctr += 1
		sleep(60)
		# check heating endpoints
		if heatpct >= maxheatpct:
			heating = False
		if not heating and heatpct <= 0:
			break
	# keep going for an hour
	for secondloop in range(60):
		if loopctr % nlog == 0:
			rs = getReadings()
			ts = getTemps()
			for i in range(len(therm_chlist)):
				print('T{0:d}: {1:.3f} mK'.format(therm_chlist[i],float(ts[i])*1e3))
			print(rs)
			# assemble data string, then write
			t1 = datetime.now(tz=slac)
			t1h = t1.hour + t1.minute/60.0 + t1.second/3600.0
			datastr = '{0:.5f},'.format(t1h)
			for temp in ts:
				datastr += temp + ','
			for ch in samp_chlist:
				datastr += rs[ch] + ','
			datastr += '\n'
			with open(fn,'a+') as fp: # file pointer. append!
				fp.write(datastr)
		print(loopctr, getHeaterPCT())
		# increment, sleep
		loopctr += 1
		sleep(30)

except: # if something goes wrong, turn off heater
	setHeaterPCT(0.0)
	print('Error! Exiting...')
# done! now close
print('Completed in {0:.1f} sec'.format((t1-t0).total_seconds()))
port.close()

