This is all of the code for running the Digiducer USB Digital Accelerometer (333D01) and plotting the data that it returns. All of the data that has been collected is also stored here. 


NAMING CONVENTIONS FOR CODE (.PY FILES):

"USE_THIS" will plot a periodogram that takes a large sample of data, splits it into smaller sections of time (as specified by the response to "Time?"), and plots the average.

"Accelerometer" will collect data from the accelerometer

"Sum" will compare data like USE_THIS, but adds up all three axis at each location

"Transmissibility" displays the transmissibility between two data sets
 
Codes with "Plot" will plot data from multiple files side by side
 
Codes with "Compare" will plot data from multiple files on the same plot

Codes with "Split" will seperate one file into multiple time sections and plot them on the same plot
 
Codes with "Time" will plot acceleration graphs with respect to time
 
Codes with "Frequency" will plot periodograms with respect to frequency


NAMING CONVENTIONS FOR DATA (.NPY FILES):

Names of files correspond to the location and set up of data collection (images on Confluence)

Numbers in files refer to the orientation/axis of data collection

Files with "Off" contain data from when the pulse tube is off

Flies with "SH" are data taken from Shawn Henderson's DR
