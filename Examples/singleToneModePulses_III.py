##############################################################################
# SINGLE TONE MODE RF PULSES EXAMPLE (III). Set of 2 pulses on ch0 with 
# different amplitude freq and phase. Each pulse is initiated after an extrenal 
# trigger event. 
# 
#-----------------------------------------------------------------------------
# Hardware parameters:
# 	* ref_clk= 25 MHz
#	* PLL_multiplier=20 (SYS_CLK=500MHz) 
# 	* chipkit_clk=80MHz (onboard clock of the Chipkit Max 32) 
#	* A rising edge on TRIGG_IN will initiate each pulse.
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


#PULSE 1
RF.waitTriggerIn() #Waits for 1st rising edge
#RF.clearPhaseAccumulator() # Add this line if the phase should be reset at this point of the code
RF.setTriggerOut(1) # output trigger for monitoring purposes
t=0
RF.resetTimer() #Resets the timer on the Chipkit Max 32 board. Requiered to use the waitForTimer() function.

RF.setFreq(0,1e6)
RF.setPhase(0,0)

t+=20e-6              
RF.waitForTimer(t)       #waits until t=20us
RF.setAmplitude(0,1)

t+=100e-6
RF.waitForTimer(t)       #waits until t=120us
RF.setAmplitude(0,0)
RF.setTriggerOut(0)


#PULSE 2
RF.waitTriggerIn() #Waits for 2st rising edge
#RF.clearPhaseAccumulator() # Add this line if the phase should be reset at this point of the code
RF.setTriggerOut(1) # output trigger for monitoring purposes
t=0
RF.resetTimer() #Resets the timer on the Chipkit Max 32 board. Important to include after each exetrnal trigger event when using the waitForTimer() function.

RF.setFreq(0,2e6)
RF.setPhase(0,0)

t+=20e-6              
RF.waitForTimer(t)       #waits until t=20us
RF.setAmplitude(0,0.5)

t+=100e-6
RF.waitForTimer(t)       #waits until t=120us
RF.setAmplitude(0,0)
RF.setTriggerOut(0)


###################################
# End sequence (function stack)
###################################
print RF.checkLenRequest()
print RF.checkLenStack()
RF.runStack()





