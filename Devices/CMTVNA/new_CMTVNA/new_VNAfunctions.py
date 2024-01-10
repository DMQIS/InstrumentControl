import socket
import time
import numpy as np

class VNA:

    def __init__(self, server_ip='127.0.0.1', server_port=5025):
        self.server_address = (server_ip, server_port)

    def _sendCmd(self,cmd):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(self.server_address)
        s.sendall(cmd.encode())
        s.close()
        return

    def _getData(self,cmd):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(self.server_address)
        #Clear register
        s.sendall("*CLS\n".encode())
        s.sendall(cmd.encode())
        s.settimeout(120)
        try:
            chunks = []
            data = b''.join(chunks)
            while not "\n" in data.decode():
                chunk = s.recv(4096)
                if chunk == b'':
                    raise RuntimeError("socket connection broken")
                chunks.append(chunk)
                data = b''.join(chunks)

        except socket.timeout:
            s.close()
            raise RuntimeError("No data received from VNA")

        datavals = data.decode()
        datavals = datavals.rstrip("\n")
        return datavals

    def setPower(self, power):
        self._sendCmd("SOURce:POWer "+str(power)+"\n")
        print("SOURce:POWer "+str(power))
        #power should be in dBm

    def getPower(self):
        power=0
        power=self._sendCmd("SOURce:POWer?"+"\n")
        print("Power is "+str(power)+" dBm")
        return power

    def singleTrigAndWait(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(self.server_address)
        print("Starting frequency sweep and waiting for complete. . .")
        s.sendall("TRIG:SING\n".encode())
        s.sendall("DISP:WIND:TRAC:Y:AUTO\n".encode())
        s.sendall("*OPC?\n".encode())
        opComplete = s.recv(8)
        print("Done. . . ", "("+str(opComplete)+")")
        s.close()
        return

    def takeSweep(self, f_min, f_max, n_step, n_avs, ifb=10e3, s_parameter="S21"):
        #Set sweep params
        self._sendCmd("SENS:FREQ:STAR "+str(f_min)+"\n")
        self._sendCmd("SENS:FREQ:STOP "+str(f_max)+"\n")
        self._sendCmd("SENS:SWE:POIN "+str(n_step)+"\n")
        self._sendCmd("CALC:PAR:DEF "+ s_parameter+"\n")
        self._sendCmd("CALC:SEL:FORM POLar\n")
        self._sendCmd("TRIG:SOUR BUS\n")
        self._sendCmd("SENS:BWID "+str(ifb)+"\n")

        #Set averaging settings
        self._sendCmd("TRIG:AVER ON\n")
        self._sendCmd("SENS:AVER ON\n")
        self._sendCmd("SENS:AVER:COUN "+str(n_avs)+"\n")

        #Autoscale GUI Display
        self._sendCmd("DISP:WIND:TRAC:Y:AUTO\n")
        self.singleTrigAndWait()

        data = self._getData("CALC:TRAC:DATA:FDAT?\n")
        fs = self._getData("SENS:FREQ:DATA?\n")

        freqs=str(fs)
        S21=str(data)
        #S21_phase=str(phase_data

        f = freqs.split(",")
        S21 = S21.split(',')
        I = S21[::2]
        Q = S21[1::2]

        #print(freqs)
        freqs = [float(i) for i in f]
        Ivals = [float(i) for i in I]
        Qvals = [float(i) for i in Q]
        #print(S21)
        return np.array(freqs), np.array(Ivals), np.array(Qvals)

    def timeDomain(self, lapse, f0, npts, ifb=10e3):
        ## Show the time details
        print("Taking time domain trace with:")
        print("-     CW F [Hz]:", f0)
        print("- Number points:", npts)
        print("- Sampling rate:", ifb)
        print("-  Duration [s]:", lapse)

        ## Set the frequency parameters
        self._sendCmd("SENS:FREQ:STAR "+str(f0)+"\n")
        self._sendCmd("SENS:FREQ:STOP "+str(f0)+"\n")
        self._sendCmd("SENS:SWE:POIN "+str(int(npts))+"\n")
        self._sendCmd("SENS:BWID "+str(ifb)+"\n")

        #Set averaging settings
        self._sendCmd("TRIG:AVER OFF\n")
        self._sendCmd("SENS:AVER OFF\n")

        # self._sendCmd("CALC:PAR:DEF S21\n")
        self._sendCmd("TRIG:SOUR BUS\n")

        #Set up GUI display window
        self._sendCmd("DISP:SPL 6\n") ## top panel, 2 bottom quadrants

        self._sendCmd("CALC1:PAR:DEF S21\n")
        self._sendCmd("CALC1:SEL:FORM MLOG\n")
        self._sendCmd("DISP:WIND1:TRAC:Y:AUTO\n")

        self._sendCmd("CALC2:PAR:DEF S21\n")
        self._sendCmd("CALC2:SEL:FORM POLar\n")

        self._sendCmd("CALC3:PAR:DEF S21\n")
        self._sendCmd("CALC3:SEL:FORM PHASE\n")

        self._sendCmd("DISPlay:UPDate:IMMediate\n")

        data = ""
        tpts = ""
        elapsed = 0

        ## Take a single time domain trace
        while (elapsed < lapse):
            bgn = time.time()
            self.singleTrigAndWait()
            elapsed += (time.time() - bgn)
            print("Live-time elapsed:",elapsed,"seconds")

            ## Pull the data 
            data += self._getData("CALC:TRAC:DATA:FDAT?\n")
            tpts += self._getData("SENS:FREQ:DATA?\n")
        print("Total live-time elapsed:",elapsed,"seconds")

        S21  = str(data).split(',')
        tpts = str(tpts).split(",")
        
        S21_real = S21[::2]
        S21_imag = S21[1::2]

        return tpts, S21_real, S21_imag