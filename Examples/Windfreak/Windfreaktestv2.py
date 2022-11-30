import time
from WindfreakControlClass import *

windfreakTest = WindfreakControl("COM5")


windfreakTest.connectDevice()

windfreakTest.setFreq(0, 7500)

windfreakTest.setPower(0, -5.0)

windfreakTest.setref_freq(27)
windfreakTest.pa_turnOn(0)
windfreakTest.pll_turnOn(0)
windfreakTest.rf_turnOn(0)

time.sleep(60)

windfreakTest.rf_turnOff(0)
windfreakTest.pa_turnOff(0)
windfreakTest.pll_turnOff(0)

windfreakTest.disconnectDevice()

del windfreakTest