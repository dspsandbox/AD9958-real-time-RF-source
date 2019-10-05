##############################################################################
# SINGLE TONE MODE RF PULSES EXAMPLE (I). Set of 3 pulses on ch0 with 
# different amplitude freq and phase. This example uses the delayTimer() function
# for setting the duration of each RF pulse and the spacing between them. 
# 
#-----------------------------------------------------------------------------
# Hardware parameters:
# 	* ref_clk= 25 MHz
#	* PLL_multiplier=20 (SYS_CLK=500MHz)
# 	* chipkit_clk=80MHz (onboard clock of the Chipkit Max 32) 
#	* A rising edge on TRIGG_IN will initiate the sequence.
# 	* TRIGG_OUT is used for monitoring the pulses 
#-----------------------------------------------------------------------------
# MIT License
# Copyright (c) 2019 DSPsandbox (pau.gomez@dspsandbox.org)
##############################################################################

from __future__ import division
import serial
import time
import sys
sys.path.append('..') #Makes AD9958 libray (sitting inside the parent folder) available
import AD9958	

	
	
###################################
# Setting up serial communication
###################################

RF_COM_PORT="COM7"

try:
	serRF   #Check if serial port is defined (if not this line raises a NameError)
except NameError:  
	serRF=serial.Serial(RF_COM_PORT, 9600, timeout=0.2)
	print "Starting RF serial port."
	time.sleep(5) #Waiting for microcontroller to start


##################################################
#Initialization of AD9958 object & function stack
##################################################
print "Initialize AD9958 object."
RF=AD9958.AD9958_class(ser=serRF,ref_clk=25e6,PLL_multiplier=20,chipkit_clk=80e6)
RF.clearStack()



###################################
# Start sequence (function stack)
###################################
print "Programming sequence."
RF.reset()
RF.resetTimer()
RF.configureSysClock()

#Channel 0 and 1
RF.setEnabledChannels(1,1)
RF.setDACFullScale()
RF.setSingleToneMode()
RF.setAmplitude(0,0) 



RF.setEnabledChannels(1,0) #Enable communication only to ch0

RF.waitTriggerIn() #Waits for a rising edge
#RF.clearPhaseAccumulator()  # Add this line if the phase should be reset at this point of the code
RF.setTriggerOut(1) # output trigger for monitoring purposes


#PULSE 1
RF.setFreq(0,1e6)
RF.setPhase(0,0)
RF.setAmplitude(0,1)
RF.delayTimer(100e-6) #100 us delay
RF.setAmplitude(0,0)

RF.delayTimer(100e-6)

#PULSE 2
RF.setFreq(0,2e6)
RF.setPhase(0,0)
RF.setAmplitude(0,0.5)
RF.delayTimer(100e-6)
RF.setAmplitude(0,0.0)

RF.delayTimer(100e-6)

#PULSE 3
RF.setFreq(0,1e6)
RF.setPhase(0,0)
RF.setAmplitude(0,0.25)
RF.delayTimer(100e-6)
RF.setAmplitude(0,0.0)
RF.setTriggerOut(0) 


###################################
# End sequence (function stack)
###################################
print RF.checkLenRequest()
print RF.checkLenStack()
RF.runStack()





