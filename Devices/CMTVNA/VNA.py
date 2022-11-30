# Allows communication via COM interface
try:
	import win32com.client
except:
	print("You will first need to import the pywin32 extension")
	print("to get COM interface support.")
	print("Try http://sourceforge.net/projects/pywin32/files/ )?")
	input("\nPress Enter to Exit Program\n")
	exit()

# Allows time.sleep() command
import time

import socket
import select
from time import sleep
import math

class VNAAux:
        def __init__(self, server_ip='127.0.0.1', server_port=5025, timeout=1):
                self.server_address = (server_ip, server_port)
                self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.s.connect(self.server_address)
                self.s.settimeout(timeout)

        def send(self,cmd):
                cmdn = cmd+"\n"
                self.s.sendall(cmdn.encode())
                return

        def query(self,cmd,bufsize=1024):
                self.send(cmd)
                ret = self.s.recv(bufsize)
                ret = ret.decode()
                return ret[:-1]

        def isEnabled(self):
                stat = int(self.query("SOUR:AUX?"))
                return (stat == 1)

        def enable(self):
                self.send("SOUR:AUX 1")

        def disable(self):
                self.send("SOUR:AUX 0")
 
        def getPower(self):
                return float(self.query("SOUR:AUX:POW?"))

        def setPower(self,power_level_dbm):
                self.send("SOUR:AUX:POW "+str(power_level_dbm))

        def getStartFreq(self):
                return float(self.query("SOUR:AUX:FREQ:STAR?"))

        def setStartFreq(self,f_low):
                self.send("SOUR:AUX:FREQ:STAR "+str(f_low))

        def getStopFreq(self):
                return float(self.query("SOUR:AUX:FREQ:STOP?"))

        def setStopFreq(self,f_high):
                self.send("SOUR:AUX:FREQ:STOP "+str(f_high))

        def setCWFreq(self,f_cw):
                self.setStartFreq(f_cw)
                self.setStopFreq(f_cw)

        def getPort(self):
                return int(self.query("SOUR:AUX:PORT?"))

        def setPort(self,portNum):
                self.send("SOUR:AUX:PORT "+str(portNum))



class VNA:
        
        def __init__(self,instrument='S4VNA',hide=False):
                
                #Instantiate COM client
                try:
                        self.app = win32com.client.Dispatch(instrument + ".application")
                        count=0
                        print("Waiting for app to load")
                        while(self.app.Ready == 0):
                                time.sleep(1)
                                count+=1
                                if(count > 60):
                                        raise(Error("Timeout waiting for program"))
                        self.name = self.app.name
                        if(hide):
                                self.hide()
                except:
                        print("Error establishing COM server connection to " + instrument + ".")
                        print("Check that the VNA application COM server was registered")
                        print("at the time of software installation.")
                        print("This is described in the VNA programming manual.")
                        input("\nPress Enter to Exit Program\n")
                        exit()

        def getPower(self):
                return self.app.scpi.GetSOURce(1).power.level.immediate.amplitude

        def setPower(self,power_level_dbm):
                self.app.scpi.GetSOURce(1).power.level.immediate.amplitude = power_level_dbm
                
        def setParameter(self,parameter):
                self.app.scpi.GetCALCulate(1).GetPARameter(1).define = parameter
                # "S21", "S11", "S12", etc. R54/140 must use
                # "S11"; TR devices must use "S11" or "S21";
                #  Ports 3 and 4 available for S8081 only

        def setFormat(self,fmt):
                # e.g. mlog, phase, smith
                self.app.scpi.GetCALCulate(1).GetPARameter(1).select()
                self.app.scpi.GetCALCulate(1).selected.format = fmt

        def getTrigger(self):
                return self.app.scpi.trigger.sequence.source

        def setBusTrigger(self):
                self.app.scpi.trigger.sequence.source = "bus"

        def setIntTrigger(self):
                self.app.scpi.trigger.sequence.source = "int"
                
        def setStartFreq(self,f1_hz):
                self.app.scpi.GetSENSe(1).frequency.start = f1_hz

        def getStartFreq(self):
                return self.app.scpi.GetSENSe(1).frequency.start

        def setStopFreq(self,f2_hz):
	        self.app.scpi.GetSENSe(1).frequency.stop = f2_hz

        def getStopFreq(self):
                return self.app.scpi.GetSENSe(1).frequency.stop

        def setNPoints(self,num_points):
                self.app.scpi.GetSENSe(1).sweep.points = num_points

        def getNPoints(self):
                return self.app.scpi.GetSENSe(1).sweep.points

        def getIFBW(self):
                return self.app.scpi.GetSENSe(1).BANDwidth.RESolution

        def setIFBW(self,ifbw):
                self.app.scpi.GetSENSe(1).BANDwidth.RESolution = ifbw

        def RFEnabled(self):
                return self.app.scpi.output.state

        def setRFOn(self):
                self.app.scpi.output.state = True

        def setRFOff(self):
                self.app.scpi.output.state = False

        def AverageEnabled(self):
                return self.app.scpi.GetSENSe(1).average.state

        def setAverageOn(self):
                self.app.scpi.GetSENSe(1).average.state = True

        def setAverageOff(self):
                self.app.scpi.GetSENSe(1).average.state = False

        def getAverages(self):
                return self.app.scpi.GetSENSe(1).average.count

        def setAverages(self,count):
                self.app.scpi.GetSENSe(1).average.count = count

        def show(self):
                self.app.scpi.display.show()

        def hide(self):
                self.app.scpi.display.hide()
                
        def getData(self,f_low=None,f_high=None,n_pts=None,parameter=None):
                #Execute the measurement
                if(self.getTrigger() == 'INT'):
                        print("Setting Bus Trigger")
                        self.setBusTrigger()

                self.app.scpi.trigger.sequence.single()
                
                self.app.scpi.GetCALCulate(1).GetPARameter(1).select()
                res = self.app.scpi.GetCALCulate(1).selected.data.Fdata
                f = self.app.scpi.GetCALCulate(1).selected.data.xaxis
                
                #Discard complex-valued points
                Re = res[0::2]
                Im = res[1::2]

                return [f,Re,Im]

