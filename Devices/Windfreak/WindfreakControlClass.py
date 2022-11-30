from windfreak import SynthHD

class WindfreakControl:

    def __init__(self, devpath):
        self.channels = [0,1]
        self.device = None
        self.devpath = devpath

    def connectDevice(self):
        self.device = SynthHD(self.devpath)
        self.device.init()
        print("Device is now connected in a safe state")

    def disconnectDevice(self):
        self.device.close()
        del self.device
        self.device = None
        print("Device is now disconnected")

    def getFreq(self, channel):
        if self.device == None:
            print("You have not connected a device yet! Please run the connectDevice command")
        elif channel not in self.channels:
            print("Invalid channel number! Channel number must be 0 or 1")
        else:
            print("Channel " + str(channel) + " frequency is: " + str(self.device[channel].frequency/ 10**6) + " MHz")

    def getPower(self, channel):
        if self.device == None:
            print("You have not connected a device yet! Please run the connectDevice command")
        elif channel not in self.channels:
            print("Invalid channel number! Channel number must be 0 or 1")
        else:
            print("Channel " + str(channel) + " power is: " + str(self.device[channel].power) + " dBm")

    def getPhase(self, channel):
        if self.device == None:
            print("You have not connected a device yet! Please run the connectDevice command")
        elif channel not in self.channels:
            print("Invalid channel number! Channel number must be 0 or 1")
        else:
            print("Channel " + str(channel) + " phase is: " + str(self.device[channel].phase) + " degrees")

    def getref_freq(self):
        if self.device == None:
            print("You have not connected a device yet! Please run the connectDevice command")
        else:
            print("Device reference frequency is: " + str(self.device[channel].ref_frequency/(10**6)) + " MHz")

    def getState(self, channel):
        if self.device == None:
            print("You have not connected a device yet! Please run the connectDevice command")
        elif channel not in self.channels:
            print("Invalid channel number! Channel number must be 0 or 1")
        else:
            self.getFreq(channel)
            self.getPower(channel)
            self.getPhase(channel)

    def setFreq(self, channel, freq):
        if self.device == None:
            print("You have not connected a device yet! Please run the connectDevice command")
        else:
            if channel not in self.channels:
                print("Invalid channel number! Channel number must be 0 or 1")
            if freq < 10 or freq > 15000:
                print("Input frequency is outside the frequency range! Input frequency must be between 10 MHz and 15 GHz")
            else:
                self.device[channel].frequency = freq * 10 ** 6
                print("Channel " + str(channel) + "  frequency is now set to: " + str(self.device[channel].frequency / 10**6) + " MHz")

    def setPower(self, channel, Power):
        if self.device == None:
            print("You have not connected a device yet! Please run the connectDevice command")
        else:
            if channel not in self.channels:
                print("Invalid channel number! Channel number must be 0 or 1")
            if Power < -50 or Power > 20:
                print("Input power is outside the power range! Input power must be between -50 dBm and 20 dBm")
            else:
                self.device[channel].power = Power
                print("Channel " + str(channel) + "  power is now set to: " + str(self.device[channel].power) + " dBm")

    def setPhase(self, channel, Phase):
        if self.device == None:
            print("You have not connected a device yet! Please run the connectDevice command")
        else:
            if channel not in self.channels:
                print("Invalid channel number! Channel number must be 0 or 1")
            else:
                phaseCorrection = Phase % 360
                self.device[channel].phase = phaseCorrection
                print("Channel " + str(channel) + "  phase is now set to: " + str(self.device[channel].phase) + " degrees")

    def setref_freq(self, reference):
        if self.device == None:
             print("You have not connected a device yet! Please run the connectDevice command")
         
        else:
            if reference != 10 or reference != 27:
                print("Reference fequency outside of range! Reference frequency must be 10 or 27 MHz")
            else:
                self.device.ref_frequency = reference * 10**6
                print("Device reference frequency is now set to: " + str(self.device.ref_frequency/10**6) + " MHz")
        

    def rf_turnOn(self, channel):
        if self.device == None:
            print("You have not connected a device yet! Please run the connectDevice command")
        elif channel not in self.channels:
            print("Invalid channel number! Channel number must be 0 or 1")
        else:
            self.device[channel].rf_enable = True
            print("Channel " + str(channel) + " rf is now turned on")

    def rf_turnOff(self, channel):
        if self.device == None:
            print("You have not connected a device yet! Please run the connectDevice command")
        elif channel not in self.channels:
            print("Invalid channel number! Channel number must be 0 or 1")
        else:
            self.device[channel].rf_enable = False
            print("Channel " + str(channel) + " rf is now turned off")

    def rf_toggle(self, channel):
        if self.device == None:
            print("You have not connnected a device yet! Please run the connectDevice command")
        elif channel not in self.channels:
            print("Invalid channel number! Channel number must be 0 or 1")
        else:
            if self.device[channel].rf_enable == True:
                self.rf_turnOff(channel)
            else:
                self.rf_turnOn(channel)
        
    def pa_turnOn(self, channel):
        if self.device == None:
            print("You have not connected a device yet! Please run the connectDevice command")
        elif channel not in self.channels:
            print("Invalid channel number! Channel number must be 0 or 1")
        else:
            self.device[channel].pa_enable = True
            print("Channel " + str(channel) + " PA is now turned on")

    def pa_turnOff(self, channel):
        if self.device == None:
            print("You have not connected a device yet! Please run the connectDevice command")
        elif channel not in self.channels:
            print("Invalid channel number! Channel number must be 0 or 1")
        else:
            self.device[channel].pa_enable = False
            print("Channel " + str(channel) + " PA is now turned off")

    def pll_turnOn(self, channel):
        if self.device == None:
            print("You have not connected a device yet! Please run the connectDevice command")
        elif channel not in self.channels:
            print("Invalid channel number! Channel number must be 0 or 1")
        else:
            self.device[channel].pll_enable = True
            print("Channel " + str(channel) + " PLL is now turned on")

    def pll_turnOff(self, channel):
        if self.device == None:
            print("You have not connected a device yet! Please run the connectDevice command")
        elif channel not in self.channels:
            print("Invalid channel number! Channel number must be 0 or 1")
        else:
            self.device[channel].pll_enable = False
            print("Channel " + str(channel) + " PLL is now turned off")
