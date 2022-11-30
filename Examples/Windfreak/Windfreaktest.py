import WindfreakControlClass

windfreakTest = WindfreakControl("COM5")

windfreakTest.getFreq(1) #should throw because the device is not connected yet

windfreakTest.connectDevice()

windfreakTest.getFreq(1) #this should not throw hopefully and should return something

windfreakTest.getFreq(2) #this should throw as an invalid channel

windfreakTest.disconnectDevice()

windfreakTest.getPower(1) #should throw as I disconnected the device

windfreakTest.connectDevice()

windfreakTest.getref_freq()

windfreakTest.setref_freq(50)

windfreakTest.setref_freq(101)

for i in range(0,2):
    windfreakTest.getFreq(i) #noThrow

    windfreakTest.getPower(i) #noThrow

    windfreakTest.getPhase(i) #noThrow

    windfreakTest.getState(i) #noThrow

    windfreakTest.setFreq(i, 16000) #Throw

    windfreakTest.setFreq(i, 5) #Throw

    windfreakTest.setFreq(i, 50) #noThrow

    windfreakTest.setPower(i, -60) #Throw

    windfreakTest.setPower(i, 30) #Throw

    windfreakTest.setPower(i, -5) #noThrow

    windfreakTest.setPhase(i, 25) #noThrow

    windfreakTest.setPhase(i, 395) #noThrow should be a phase of 35
    
    '''
    Note I did not account for negative numbers yet.
    '''

    windfreakTest.getState(i)

windfreakTest.rf_turnOn(1)

windfreakTest.rf_turnOff(1)

windfreakTest.rf_toggle(1) #should be turned on here

windfreakTest.rf_turnOff(1)

windfreakTest.disconnectDevice()

print("Test concluded")

del windfreakTest
    
