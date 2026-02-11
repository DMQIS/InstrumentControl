import serial
import time


class CryoSwitch:

    def __init__(self, portName, verbose=True, debug=False):
        self.port = serial.Serial(portName, 9600, timeout=0.0)
        self.verbose = verbose
        self.debug = debug

        self.switchNum = 3

        time.sleep(5)

        initMsg = self.getResponse()

        self.verbose = False
        self.getPulseDurations()
        self.verbose = verbose

    def getResponse(self):
        msg = list()
        rcv = self.port.readline()
        while(len(rcv) > 0):
            rStr = rcv.decode()
            if(rStr[0] != '#'):
                msg.append(rStr)
                if(self.verbose):
                    print(rStr, end='')
            rcv = self.port.readline()
        return msg

    def send(self, cmd, sleepTime=0.1):
        if(self.debug):
            print("Sending: ", cmd)
        self.port.write((cmd+"\r\n").encode())
        time.sleep(sleepTime)
        return self.getResponse()

    def openPorts(self, switch):
        return self.send("all "+str(int(switch)))

    def openAllPorts(self):
        for i in range(1, switchNum+1):
            self.openPorts(i)

    def enablePort(self, switch, port):
        self.send("tog "+str(int(switch))+" "+str(int(port))+" cls")

    def disablePort(self, switch, port):
        self.send("tog "+str(int(switch))+" "+str(int(port))+" opn")

    def setOpenDuration(self, duration):
        self.send("opd "+str(duration))
        self.getPulseDurations()

    def setCloseDuration(self, duration):
        self.send("cld "+str(int(duration)))
        self.getPulseDurations()

    def getPulseDurations(self):
        msg = self.send("dur")
        clm = msg[0]
        opm = msg[1]

        self.closeDuration = int(clm.split(' ')[4])
        self.openDuration = int(opm.split(' ')[4])

        return [self.closeDuration, self.openDuration]

    def getOpenDuration(self):
        return self.openDuration

    def getCloseDuration(self):
        return self.closeDuration

    def togglePulseStreaming(self):
        self.send("stm")

    def enableSlot(self, port):
        for i in (1, 2):
            self.enablePort(i, port)

    def disableSlot(self, port):
        for i in (1, 2):
            self.disablePort(i, port)
