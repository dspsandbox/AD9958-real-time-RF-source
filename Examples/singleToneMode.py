##############################################################################
# SINGLE TONE MODE EXAMPLE with adjustable amplitudes, frequencies  
# phases on ch0 and ch1 
#
#-----------------------------------------------------------------------------
# Hardware parameters:
# 	* ref_clk= 25 MHz
#	* PLL_multiplier=20 (leads to an effective sampling rate of 400MHz)  
# 	* chipkit_clk=80 MHz (onboard clock of the Chipkit Max 32) 
#-----------------------------------------------------------------------------
# MIT License
# Copyright (c) 2018 Pau Gomez Kabelka <paugomezkabelka@gmail.com>
##############################################################################

from __future__ import division
import serial
import time
import sys
sys.path.append('..') #Makes AD9958 libray (sitting inside the parent folder) available
import AD9958	

	
RF_COM_PORT="COM7"


serRF=serial.Serial(RF_COM_PORT, 9600, timeout=0.2)
print "Starting RF serial port."
time.sleep(5) #Waiting for microcontroller to start

print "Programming sequence."
RF=AD9958.AD9958_class(ser=serRF,ref_clk=25e6,PLL_multiplier=20,chipkit_clk=80e6)
RF.clearStack()


###################################
# Start sequence (function stack)
###################################
RF.reset()
RF.resetTimer()
RF.configureSysClock()

#Channel 0 and 1
RF.setEnabledChannels(1,1) #Enable communication to ch0 and ch1
RF.setDACFullScale()
RF.setSingleToneMode()


#Channel 0
RF.setEnabledChannels(1,0)  #Enable communication only to ch0
RF.setFreq(0,1e6) #1 MHz
RF.setAmplitude(0,0.5) #half amplitude
RF.setPhase(0,0) #0 deg


#Channel 1
RF.setEnabledChannels(0,1) #Enable communication only to ch1
RF.setFreq(0,1e6) #1 MHz
RF.setAmplitude(0,1) #full amplitude
RF.setPhase(0,90) #90 deg

# Clearing phase accumulator on both channels at the same time (optional)
RF.setEnabledChannels(1,1)
RF.clearPhaseAccumulator()


###################################
# End sequence (function stack)
###################################

RF.runStack()

serRF.close()




