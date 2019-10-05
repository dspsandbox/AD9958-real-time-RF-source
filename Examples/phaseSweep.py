##############################################################################
# PHASE SWEEP EXAMPLE. Phase sweep on ch0 and ch1 with different 
# ramp parameters on each channel.
#
#-----------------------------------------------------------------------------
# Hardware parameters:
# 	* ref_clk= 25 MHz
#	* PLL_multiplier=20 (SYS_CLK=500MHz)
# 	* chipkit_clk=80MHz (onboard clock of the Chipkit Max 32) 
#	* A rising edge on TRIGG_IN will initiate the sweep
# 	* TRIGG_OUT is used for monitoring the modulation 
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
RF.setSweepMode("phase")




#Channel 0
RF.setEnabledChannels(1,0)
RF.setSweepParameters(0,90,10e-6,30e-6)
RF.setAmplitude(0,1) 
RF.setFreq(0,0.5e6)
RF.setPhase(0,0)



#Channel 1 
RF.setEnabledChannels(0,1)
RF.setSweepParameters(0,270,10e-6,10e-6)
RF.setAmplitude(0,1) 
RF.setFreq(0,0.5e6)
RF.setPhase(0,0)



RF.setModulationRegister(0,0)
RF.setTriggerOut(0)

RF.waitTriggerIn() #Waits for  rising edge
###############################################################################
#CLEAR PHASE ACCUMULATOR 
# Uncomment these line if the phase should be reset at this point of the code

#RF.setEnabledChannels(1,1)  # Enables ch0 and ch1 for clearing the phase accumulator
#RF.clearPhaseAccumulator()  
###############################################################################
RF.setTriggerOut(1) # output trigger for monitoring purposes

#start of up sweep ch0
RF.setModulationRegister(1,0)
RF.delayTimer(10e-6)

#start of up sweep ch1
RF.setModulationRegister(1,1)

RF.delayTimer(10e-6)

#start of down sweep on ch0 and ch1
RF.setModulationRegister(0,0)
RF.setTriggerOut(0)


###################################
# End sequence (function stack)
###################################
print RF.checkLenRequest()
print RF.checkLenStack()
RF.runStack()





