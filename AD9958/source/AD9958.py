"""
.. module:: AD9958


"""
###############################################################################
# AD9958 Real time RF source Python library
#
#-----------------------------------------------------------------------------
# MIT License
# Copyright (c) 2018 Pau Gomez Kabelka <paugomezkabelka@gmail.com>
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.
###############################################################################


from __future__ import division
import serial
import numpy as np
import time

class AD9958_class:
	"""
		Main AD9958 class

		:param ser: Serial port object 
		:type ser: serial.Serial 
		:param ref_clk: REF_CLK frequency in Hz.
		:type ref_clk: int
		:param PLL_multiplier: PLL multiplier for the AD9958 (SYS_CLK=ref_clk*PLL_multiplier)
		:type PLL_MULTIPLIER: int
		:param chipkit_clk: System clock of the chipkit Max 32
		:type chipkit_clk: int
	"""
	def __init__(self,ser,ref_clk,PLL_multiplier,chipkit_clk):	
	#Clock properties
		self.REF_CLK=ref_clk
		self.PLL_MULTIPLIER=PLL_multiplier
		self.SYS_CLK=self.REF_CLK*self.PLL_MULTIPLIER
		self.CHIPKIT_CLK=chipkit_clk
	#Enables channels
		self.ch0Enabled=1
		self.ch1Enabled=1

	# Starting communication
		self.ser=ser
		forceRestartFlag=False
		if not(self.ser.isOpen()):
			forceRestartFlag=True
			print "Serial port closed.  Requesting restart."
		else: 
			if not(self.checkStackFinished()):
				forceRestartFlag=True
				print "Function stack not finished. Requesting restart."
		
		if forceRestartFlag:
			self.ser.close()
			self.ser.open()
			print "Restarting serial port."
			time.sleep(5) #Waiting for microcontroller to start
		print "Serial port OK."
	
	# Modulation
		self.modulationLevel=0
		self.PPC=0
	
	#Sweep 
		self.sweepType=None 
	
	#Instructions counter
		self.instructionCounter=0	
	
	#Initializing register map
		self.registerMap0=np.zeros(25,dtype=np.uint32) #Register map of channel 0
		self.registerMap1=np.zeros(25,dtype=np.uint32) #Register map of channel 1
		self.registerMap=np.zeros(25,dtype=np.uint32) #Current register map
		self.commonRegisters=[0x00,0x01,0x02] #Registeres shared between channel 0 and channel 1
		
	
	


	def reset(self):
		"""
			Resets the AD9958 chip by pulsing the RESET pin.
		"""
		self.ser.write("reset\n")
		self.instructionCounter+=1

		return
		
		
	def setRegister(self,registerAddress,registerValue,doIO_update=True):
		"""
		Sets an internal register of the AD9958
		
		:param registerAddress: Register address.
		:type registerAddress: int
		:param registerValue: Value to be written into the register.
		:type registerValue: int
		:param doIO_update: Performs an IO update after writting to the register (Default is True).
		:type doIO_update: bool
		"""
		
		self.ser.write("setRegister "+str(registerAddress)+" "+str(registerValue)+" "+str(doIO_update&1)+" \n")	
		self.instructionCounter+=1
		
		#Individual registers
		if self.ch0Enabled or (registerAddress in self.commonRegisters):
			self.registerMap0[registerAddress]=registerValue
		if self.ch1Enabled or (registerAddress in self.commonRegisters):
			self.registerMap1[registerAddress]=registerValue
		#Working register
		if self.ch0Enabled:
			self.registerMap=np.copy(self.registerMap0)
		if self.ch1Enabled:
			self.registerMap=np.copy(self.registerMap1)
		if self.ch0Enabled and self.ch0Enabled:
			self.registerMap=self.registerMap0|self.registerMap1
		
		return
			
	# def readRegister(self,registerAddress):
		# self.ser.write("readRegister "+str(registerAddress)+" \n")
		# line = self.ser.readline()   # read a '\n' terminated line
		# registerValue=int(line[:-1]) #removes "\n" terminator and converts to int
		
		# if self.ch0Enabled or (registerAddress in self.commonRegisters):
			# self.registerMap0[registerAddress]=registerValue
		# if self.ch1Enabled or (registerAddress in self.commonRegisters):
			# self.registerMap1[registerAddress]=registerValue
		
		# return 
		
	# def readAllRegisters(self):
		# ch0EnabledAux=self.ch0Enabled
		# ch1EnabledAux=self.ch1Enabled
		# #Reading registers of channel 0
		# self.setEnabledChannels(1,0)
		# for i in range (0,25):
			# self.readRegister(i)
			
		# # Reading registers of channel 1
		# self.setEnabledChannels(0,1)
		# for i in range (0,25):
			# self.readRegister(i)
		# self.setEnabledChannels(ch0EnabledAux,ch1EnabledAux)
		# return

		
	def setEnabledChannels(self,setCh0Enabled,setCh1Enabled):
		"""
		Sets the enabled channels for the communication (read/write) of the AD9958 registers. The communication will only affect the channel with a logic high value.
			
		:param setCh0Enabled: Flag for channel 0 (True-> comm. enabled ; False-> comm. disabled).
		:type setCh0Enabled: bool
		:param setCh1Enabled: Flag for channel 1 (True-> comm. enabled ; False-> comm. disabled).
		:type setCh1Enabled: bool
		
		.. note::
			Channels 0x00, 0x01 and 0x02 are shared registers and get programmed regardless of the enabled channels settings.
		"""
		self.ch0Enabled=setCh0Enabled
		self.ch1Enabled=setCh1Enabled
		
		flag=((setCh1Enabled&1)<<7)+((setCh0Enabled&1)<<6)
		registerAddress=0x00
		registerValue=flag+(1<<1)
		self.setRegister(registerAddress,registerValue)
		
		
		
		return 

	def configureSysClock(self):
		"""
			Configures the SYS_CLK of the AD9958: sets the VCO gain and the PLL_MULTIPLIER. 		
		"""
		registerAddress=0x01
		if self.SYS_CLK>255e6:
			VCO_gain_control=1
		else:
			VCO_gain_control=0	
		Charge_pump_control=0
		
		registerValue=(VCO_gain_control<<23)+((self.PLL_MULTIPLIER)<<18)+(Charge_pump_control<<16)
		self.setRegister(registerAddress,registerValue)
		return
		
	def setSingleToneMode(self):
		"""
			Enables the Single Tone Mode of the AD9958.
		"""
		# AFP Select
		AFP_Select=0
		flag=AFP_Select<<22
		mask=~(3<<22) #mask for unchanged bits
		registerAddress=0x03
		registerValue=(mask&self.registerMap[registerAddress])|flag
		self.setRegister(registerAddress,registerValue)
		
		#set amplitude multiplier
		amplitudeMultiplierEnable=1
		registerAddress=0x06
		flag=amplitudeMultiplierEnable<<12
		mask=~(1<<12)
		registerValue=(mask&self.registerMap[registerAddress])|flag
		self.setRegister(registerAddress,registerValue)
		return
	
		
	def setFreqTuningWord(self,channelId,tuningWord):
		"""
			Sets the frequency tuning word. Perfroms the frequency register mapping from channelId to the AD9958 register addresses.
			
			:param channelId: channel ID (0-15)
			:type channelId: int
			:param tuningWord: frequency tuning word  (minVal=0 maxVal=2^32-1)
			:type tuningWord: int
			
		"""
		if channelId==0:
			registerAddress=0x04
		else:
			registerAddress=0x09+channelId
		
		registerValue=tuningWord
		self.setRegister(registerAddress,registerValue)
		return
	
	def setPhaseTuningWord(self,channelId,tuningWord):
		"""Sets the phase tuning word. Perfroms the phase register mapping from channelId to the AD9958 register addresses.
			
			:param channelId: channel ID (minVal=0 maxVal=15)
			:type channelId: int
			:param tuningWord: phase tuning word (minVal=0 maxVal=2^14-1)
			:type tuningWord: int
		"""
		if channelId==0:
			registerAddress=0x05
			registerValue=tuningWord		
		else:
			registerAddress=0x09+channelId
			registerValue=(tuningWord<<18)
		
		self.setRegister(registerAddress,registerValue)
		return
		
	
	def setAmplitudeTuningWord(self,channelId,tuningWord):
		"""Sets the amplitude tuning word. Perfroms the amplitude register mapping from channelId to the AD9958 register addresses.
			
			:param channelId: channel ID (minVal=0 maxVal=15)
			:type channelId: int
			:param tuningWord: amplitude tuning word (minVal=0 maxVal=2^10-1)
			:type tuningWord: int
		"""
		if channelId==0:
			registerAddress=0x06
			mask=~(2**10-1) #mask for unchanged bits
			registerValue=(mask&self.registerMap[registerAddress])|tuningWord  
		else:
			registerAddress=0x09+channelId
			registerValue=(tuningWord<<22)
		self.setRegister(registerAddress,registerValue)
		return	
	
	
	def setFreq(self,channelId,freq):
		"""Sets the frequency for a given channel ID.
		
		:param channelId: channel ID (minVal=0 maxVal=15)
		:type channelId: int
		
		:param freq: frequency in Hz (minVal=0 maxVal=SYS_CLK*(2^32-1)/2^32= 499999999.8835)
		:type freq: float
		"""
		tuningWord=int((freq/self.SYS_CLK)*(2**32))
		self.setFreqTuningWord(channelId,tuningWord)
		return
	
	def setPhase(self,channelId,phase):
		"""Sets the phase for a given channel ID .
		
		:param channelId: channel ID (minVal=0 maxVal=15) 
		:type channelId: int
		:param phase: phase in degrees (minVal=0 maxVal=360*(2^14-1)/2^14=359.9780)
		:type phase: float
		"""
		tuningWord=int(phase/360.*(2**14))
		self.setPhaseTuningWord(channelId,tuningWord)
		return
		
	def setAmplitude(self, channelId,amplitude):
		"""Sets the amplitude for a given channel ID.
		
		:param channelId: channel ID (minVal=0 maxVal=15)
		:type channelId: int
		
		:param amplitude: amplitude (minVal=0 maxVal=1)
		:type amplitude: float
		"""
		tuningWord=int(amplitude*(2**10-1))
		self.setAmplitudeTuningWord(channelId,tuningWord)
		return
		
			
	def IO_update(self):
		"""Performs an IO update.
		"""
		self.ser.write("IO_update \n")
		self.instructionCounter+=1
		return
		
	def setModulationMode(self,modulationTypeSelect,modulationLevelSelect,priorityChannel):
		"""
			Enables the modulation mode. For modulation levels 8 and 16, the PPC bits are set such that the profile PINs are only assigned to the priority channel.
			
			:param modulationTypeSelect: Type of modulation: "amplitude", "frequency" or "phase". 
			:type modulationTypeSelect: str
			:param modulationLevelSelect: Depth of modulation: 2,4,8,16.
			:type modulationLevelSelect: int
			:param priorityChannel: Channel (0 or 1) for which the modulation is set up in case of modulations levels 8 and 16.
			:type priorityChannel: int
		"""
		if modulationTypeSelect=="amplitude":
			AFP=1
			amplitudeMultiplierEnable=0
		elif modulationTypeSelect=="frequency":
			AFP=2
			amplitudeMultiplierEnable=1
		elif modulationTypeSelect=="phase":
			AFP=3
			amplitudeMultiplierEnable=1
		
		# Set AFP, linearSweepEnable, amplitudeMultiplierEnable
		linearSweepEnable=0
		registerAddress=0x03
		flag=(AFP<<22)+(linearSweepEnable<<14)
		mask=~((3<<22)+(1<<14))
		registerValue=(mask&self.registerMap[registerAddress])|flag
		self.setRegister(registerAddress,registerValue)
		
		
		#set amplitude multiplier
		if modulationLevelSelect==2:
			self.modulationLevel=0
			self.PPC=0
		elif modulationLevelSelect==4:
			self.modulationLevel=1
			self.PPC=(1<<2)+1
		elif modulationLevelSelect==8:
			self.modulationLevel=2
			if priorityChannel==0:
				self.PPC=1<<1
			elif priorityChannel==1:
				self.PPC=(1<<1)+1
		elif modulationLevelSelect==16:
			self.modulationLevel=3
			if priorityChannel==0:
				self.PPC=1<<1
			elif priorityChannel==1:
				self.PPC=(1<<1)+1
			
		rampUpRampDown=0
		registerAddress=0x01
		flag=(self.modulationLevel<<8)+(rampUpRampDown<<10)+(self.PPC<<12)
		mask=~((3<<8)+(3<<10)+(7<<12))
		registerValue=(mask&self.registerMap[registerAddress])|flag
		self.setRegister(registerAddress,registerValue)
		
		
		
		
		registerAddress=0x06
		flag=(amplitudeMultiplierEnable<<12)
		mask=~(1<<12)
		registerValue=(mask&self.registerMap[registerAddress])|flag
		self.setRegister(registerAddress,registerValue)
				
		
		return
		
	
	
	def setSweepMode(self,sweepTypeSelect):
		"""
			Enables the sweep mode.
			
			:param sweepTypeSelect: Type of sweep: "amplitude", "frequency" or "phase". 
			:type sweepTypeSelect: str
		"""
		#Sweep type
		self.sweepType=sweepTypeSelect			
		
		# Modulation level,  PPC
		self.modulationLevel=0
		self.PPC=0
		
		registerAddress=0x01
		flag=(self.modulationLevel<<8)+(self.PPC<<12)
		mask=~((3<<8)+(3<<10)+(7<<12))
		registerValue=(mask&self.registerMap[registerAddress])|flag
		self.setRegister(registerAddress,registerValue)
		
		
		#AFP, linearSweepEnable
		if self.sweepType=="amplitude":
			AFP=1
		elif self.sweepType=="frequency":
			AFP=2
		elif self.sweepType=="phase":
			AFP=3
		
		linearSweepEnable=1
		registerAddress=0x03
		flag=(AFP<<22)+(linearSweepEnable<<14)
		mask=~((3<<22)+(1<<14))
		registerValue=(mask&self.registerMap[registerAddress])|flag
		self.setRegister(registerAddress,registerValue)


		#set amplitude multiplier
		if self.sweepType=="amplitude":
			amplitudeMultiplierEnable=0
		elif self.sweepType=="frequency":
			amplitudeMultiplierEnable=1
		elif self.sweepType=="phase":
			amplitudeMultiplierEnable=1
			
		registerAddress=0x06
		flag=amplitudeMultiplierEnable<<12
		mask=~(1<<12)
		registerValue=(mask&self.registerMap[registerAddress])|flag
		self.setRegister(registerAddress,registerValue)
		
		
		
	def setSweepParameters(self,lowValue,highValue,rampUpTime,rampDownTime):
		"""
			 The optimal RSRR,RDW,FSRR,FDW values are found using :func:`AD9958_class.findOptimalRamp`.
			
			:param lowValue: Low value in the units of amplitude,frequency or phase.
			:type lowValue: float
			:param highValue: High value in the units of amplitude,frequency or phase.
			:type highValue: float
			:param rampUpTime: Ramp up time in s.
			:type rampUpTime: float
			:param rampDownTime: Ramp down time in s.
			:type rampDownTime: float
			
			.. warning::
				The optimal ramp found via :func:`AD9958_class.findOptimalRamp` is protected from a register overflow. However, if **highValue** is too close to its maximum, there might be no suitable ramp up for the chosen parameters. In this case, an error message is raized and RSRR,RDW,FSRR,FDW are set to 0. 
		"""
		
		
		
		
		#Calulate RSRR,RDW,FSRR,FDW
		RSRR,RDW,FSRR,FDW=self.findOptimalRamp(self.sweepType,lowValue,highValue,rampUpTime,rampDownTime)
		
		#Set RSRR and FSRR
		registerAddress=0x07
		registerValue=(FSRR<<8)+RSRR
		self.setRegister(registerAddress,registerValue)
		
		#Set RDW
		registerAddress=0x08
		registerValue=RDW
		self.setRegister(registerAddress,registerValue)
		
		#Set FDW
		registerAddress=0x09
		registerValue=FDW
		self.setRegister(registerAddress,registerValue)
		
		
		S0=lowValue
		E0=highValue
		
		#Set S0, E0
		if self.sweepType=="amplitude":
			self.setAmplitude(0,S0)
			self.setAmplitude(1,E0)
		elif self.sweepType=="frequency":
			self.setFreq(0,S0)
			self.setFreq(1,E0)
		elif self.sweepType=="phase":
			self.setPhase(0,S0)
			self.setPhase(1,E0)
			
		return

		
	def setDACFullScale(self):
		"""
			Sets the DAC output amplitude to full scale.
		"""
		registerAddress=0x03
		flag=(3<<8)
		mask=~(3<<8)
		registerValue=(mask&self.registerMap[registerAddress])|flag
		self.setRegister(registerAddress,registerValue)
		return

		
	def findOptimalRamp(self,rampTypeSelect,lowValue,highValue,rampUpTime,rampDownTime):
		"""
			Finds the optimal values for RSRR,RDW,FSRR,FDW for a given ramp. Each rising (R) or falling (F) ramps  is characterized by a  rising/falling delta word xDW and rising/faling delta time calculated from xSRR.
			For a given xSRR the time steps, the total number of initiated time steps and slopes are:
			
			.. math::
				\Delta t &=\mbox{SYNC\_CLK}\cdot xSRR \\\\
				N_{time\; steps} &=\mbox{ceil} \Big( \dfrac{rampXTime}{\Delta t} \Big) \\\\
				slope &= \dfrac{E0-S0}{rampXTime}
				
			where SYNC\_CLK=SYS_CLK/4=125MHz and S0 and E0 are the start and end points of the ramp written into the 32 bit registers of the AD9958. The xDW is calculated as follows:
			
			.. math::
				xDW=\mbox{ceil} \Big( \dfrac{E0-S0}{N_{time\; steps}} \Big)

			The figure of merit :math:`\\xi` evaluates the deviation form the obtained sweep to an ideal linear ramp:
			
			.. math::
				\\xi=\sum_{i=1}^{N_{DAC \; steps}} \int_{(i-1)\cdot \Delta t}^{i\cdot\Delta t}dt( i \cdot xDW -slope\cdot t )^2        +         \int_{N_{DAC \; steps} \cdot \Delta t}^{rampXTime}dt( N_{DAC \; steps} \cdot xDW -slope\cdot t )^2
				
			where :math:`N_{DAC \; steps}=\mbox{floor} \Big( \dfrac{E0-S0}{xDW} \Big)`
			
			
			
			For all xSRR ranging form 1 to 255, the figure of merit is evaluated analytically. The mimum of them is chosen as the optimum ramp parameter.
			
			
			:param rampTypeSelect: Type of ramp: "amplitude", "frequency" or "phase". 
			:type sweepTypeSelect: str
			:param lowValue: Low value in the units of amplitude,frequency or phase.
			:type lowValue: float
			:param highValue: High value in the units of amplitude,frequency or phase.
			:type highValue: float
			:param rampUpTime: Ramp up time in s.
			:type rampUpTime: float
			:param rampDownTime: Ramp down time in s.
			:type rampDownTime: float
			
			:return: [RSRR,RDW,FSRR,FDW]			
			
			
			.. warning::
				The AD9958 register overflows during a rising sweep when :math:`RDW\cdot \Tilde{N}_{DAC \; steps}+S0\geq 2^{32}` where :math:`\Tilde{N}_{DAC \; steps}=\mbox{ceil} \Big( \dfrac{E0-S0}{xDW} \Big)`. 
				The current implementation of :func:`AD9958_class.findOptimalRamp` excludes solutions leading to a register overflow. In case no alternative solution can be found, an error is raised and [0,0,0,0] is returned. 
			
		"""
		SYNC_CLK=self.SYS_CLK/4.
		
		#RAMP UP
		RSRRArray=np.array([])
		RDWArray=np.array([])
		figureOfMeritArray=np.array([])
		
		for RSRR in range(1,255):
			timeStep=RSRR/SYNC_CLK #
			NTimeSteps=np.ceil(rampUpTime/timeStep)#Amount of rising steps
			if rampTypeSelect=="frequency":
				S0=int(lowValue/self.SYS_CLK*2**32)
				E0=int(highValue/self.SYS_CLK*2**32)
				RDW=int(np.ceil((E0-S0)/NTimeSteps))
				
			elif rampTypeSelect=="phase":
				S0=int(lowValue/360*2**14)<<18
				E0=int(highValue/360*2**14)<<18
				RDW=int(np.ceil((E0-S0)/NTimeSteps))
				RDW=((RDW>>18)<<18)
			elif rampTypeSelect=="amplitude":
				S0=int(lowValue*2**10)<<22
				E0=int(highValue*2**10)<<22
				RDW=int(np.ceil((E0-S0)/NTimeSteps))
				RDW=((RDW>>22)<<22)
			
			if RDW>0:
				slope=(E0-S0)/(rampUpTime)
				NDACSteps=np.floor((E0-S0)/RDW)
				NDACStepsCeil=np.ceil((E0-S0)/RDW)
				
				figureOfMerit=0
				#ramp up figure of merit
				figureOfMerit+=1/6 *NDACSteps *timeStep *(RDW**2* (1 + NDACSteps)* (1 + 2 *NDACSteps) - RDW *slope *(1 + NDACSteps) *(-1 + 4* NDACSteps)* timeStep +  2 *slope**2 *NDACSteps**2 *timeStep**2)
				figureOfMerit+=1/3* slope**2 *(rampUpTime - NDACSteps*timeStep)**3
				
				# Saving RSRR,RDW and figureOfMerit
				if (RDW*NDACStepsCeil+S0)<2**32: #Avoids sweep overflow
					RDWArray=np.append(RDWArray,[RDW])
					RSRRArray=np.append(RSRRArray,[RSRR])
					figureOfMeritArray=np.append(figureOfMeritArray,[figureOfMerit])
		
		#Finding best figureOfMerit
		try:		
			minIndex=np.where(figureOfMeritArray==np.min(figureOfMeritArray))[0][0]
			RSRR=RSRRArray[minIndex]
			RDW=RDWArray[minIndex]
			print "Ramp up time: %.2e"%((E0-S0)/RDW*RSRR/SYNC_CLK)
		except:
			print "ERROR: the chosen final point amd ramp up time lead to register overflow for all available time steps (RSRR). Try a slightly smaller final point and/or a longer ramp."
			return [0,0,0,0]
		
				
		#RAMP DOWN
		FSRRArray=np.array([])
		FDWArray=np.array([])
		figureOfMeritArray=np.array([])
		
		for FSRR in range(1,255):
			timeStep=FSRR/SYNC_CLK #
			NTimeSteps=np.ceil(rampDownTime/timeStep)#Amount of rising steps

			if rampTypeSelect=="frequency":
				S0=int(lowValue/self.SYS_CLK*2**32)
				E0=int(highValue/self.SYS_CLK*2**32)
				FDW=int(np.ceil((E0-S0)/NTimeSteps))
			elif rampTypeSelect=="phase":
				S0=int(lowValue/360*2**14)<<18
				E0=int(highValue/360*2**14)<<18
				FDW=int(np.ceil((E0-S0)/NTimeSteps))
				FDW=((FDW>>18)<<18)
			elif rampTypeSelect=="amplitude":
				S0=int(lowValue*2**10)<<22
				E0=int(highValue*2**10)<<22
				FDW=int(np.ceil((E0-S0)/NTimeSteps))
				FDW=((FDW>>22)<<22)
			
			if FDW>0:
				slope=(E0-S0)/(rampDownTime)	
				NDACSteps=np.floor((E0-S0)/FDW)
				figureOfMerit=0
				#ramp up figure of merit
				figureOfMerit+=1/6 *NDACSteps *timeStep *(FDW**2* (1 + NDACSteps)* (1 + 2 *NDACSteps) - FDW *slope *(1 + NDACSteps) *(-1 + 4* NDACSteps)* timeStep +  2 *slope**2 *NDACSteps**2 *timeStep**2)
				figureOfMerit+=1/3* slope**2 *(rampDownTime - NDACSteps*timeStep)**3
				
				FDWArray=np.append(FDWArray,[FDW])
				FSRRArray=np.append(FSRRArray,[FSRR])
				figureOfMeritArray=np.append(figureOfMeritArray,[figureOfMerit])			
		
		#Finding best figureOfMerit
		minIndex=np.where(figureOfMeritArray==np.min(figureOfMeritArray))[0][0]
		FSRR=FSRRArray[minIndex]
		FDW=FDWArray[minIndex]	
		print "Ramp down time: %.2e"%((E0-S0)/FDW*FSRR/SYNC_CLK)		
		return np.array([RSRR,RDW,FSRR,FDW],dtype=int)

	def setTriggerOut(self,flag):
		"""
		Sets the state of the output trigger pin.
		
		:param flag: Trigger state.
		:type flag: bool
		"""
		self.ser.write("setTriggerOut "+str(flag&1)+ "\n")
		self.instructionCounter+=1
		return
	
	
	def setProfilePins (self,pin0Flag,pin1Flag,pin2Flag,pin3Flag):
		"""
		Sets the profile pins output sates. 
		
		:param pin0Flag: Profile pin 0 state.
		:type pin0Flag: bool
		:param pin1Flag: Profile pin 1 state.
		:type pin1Flag: bool
		:param pin2Flag: Profile pin 2 state.
		:type pin2Flag: bool
		:param pin3Flag: Profile pin 3 state.
		:type pin3Flag: bool
		"""
		self.ser.write("setProfilePins "+str(pin0Flag&1)+" "+str(pin1Flag&1)+" "+str(pin2Flag&1)+" "+str(pin3Flag&1)+" \n")
		self.instructionCounter+=1
		return
	
	def waitTriggerIn(self):
		"""
		Waits for a logic high on the trigger input port.
		"""
		self.ser.write("waitTriggerIn\n")
		self.instructionCounter+=1
		return
		
	def delayTimer(self,time):
		"""
		Holds the execution for the given amount of time. Uses Timer 2 and Timer 3 of the Chipkit Max32 in 32 bit mode.
		
		:param time: Hold time in seconds (max. 52s)
		:type time: float
		"""
		clkCycles=time*self.CHIPKIT_CLK
		self.ser.write("delayTimer "+str(clkCycles)+" \n")
		self.instructionCounter+=1
		return
	
	def resetTimer(self):
		"""
		Resets the internal timer (Timer 4 and Timer 5 of the Chipkit Max32) used for :func:`AD9958_class.waitForTimer`.
		"""
		self.ser.write("resetTimer \n")
		self.instructionCounter+=1
		return
		
	def waitForTimer(self,time):
		"""
		Waits until the the internal timer has reached the specified time. Uses Timer 4 and Timer 5 of the Chipkit Max32 in 32 bit mode.
		
		:param time: Value of the timer (in s) until execution is resumed. 
		:type time: float
		"""
		
		clkCycles=time*self.CHIPKIT_CLK
		self.ser.write("waitForTimer "+str(clkCycles)+" \n")
		self.instructionCounter+=1
		return	
		
	def clearPhaseAccumulator(self,doIO_update=True):
		"""
		Clears the phase accumulator of the AD9958. It enables and disables the autoclear phase accumulator.
		"""
		flag=1<<2
		mask=~(1<<2)
		registerAddress=0x03
		registerValue=(mask&self.registerMap[registerAddress])|flag
		self.setRegister(registerAddress,registerValue,doIO_update&1)
		
		flag=0<<2
		mask=~(1<<2)
		registerAddress=0x03
		registerValue=(mask&self.registerMap[registerAddress])|flag
		self.setRegister(registerAddress,registerValue,doIO_update&1)
		return
	
	
	def setModulationRegister(self,regChannel0,regChannel1):
		"""
		Sets the active amplitude/frequency/phase register for the ongoing modulation/sweep. Profile pins are set according to the modulation level and priority channel (encoded in PPC). 
		
		:param regChannel0: Active register for channel 0.
		:type regChannel0: int
		:param regChannel1: Active register for channel 1.
		:type regChannel1: int
		"""
	
		if self.modulationLevel==0:
			P0=0
			P1=0
			P2=regChannel0
			P3=regChannel1
		if self.modulationLevel==1:
			P0=(regChannel0>>1)&1
			P1=(regChannel0>>0)&1
			P2=(regChannel1>>1)&1
			P3=(regChannel1>>0)&1
		if self.modulationLevel==2:
			if self.PPC==(1<<1):
				P0=(regChannel0>>2)&1
				P1=(regChannel0>>1)&1
				P2=(regChannel0>>0)&1
				P3=0
			elif self.PPC==((1<<1)+1):	
				P0=(regChannel1>>2)&1
				P1=(regChannel1>>1)&1
				P2=(regChannel1>>0)&1
				P3=0
		if self.modulationLevel==3:
			if self.PPC==(1<<1):
				P0=(regChannel0>>3)&1
				P1=(regChannel0>>2)&1
				P2=(regChannel0>>1)&1
				P3=(regChannel0>>0)&1
			elif self.PPC==((1<<1)+1):	
				P0=(regChannel1>>3)&1
				P1=(regChannel1>>2)&1
				P2=(regChannel1>>1)&1
				P3=(regChannel1>>0)&1	
		
		self.setProfilePins(P0,P1,P2,P3)
		
		return
	
		
	def clearStack(self):
		"""
		Clears the function stack.
		"""
		self.ser.write("clearStack \n")
		self.instructionCounter=0
		return
		
	def runStack(self):
		"""
		Starts the function stack. 
		"""
		self.ser.write("runStack \n")
		
		return
			

	def checkLenRequest(self):
		"""
		Returns the number of requested instructions to the function stack. 
		
		:returns: Message of type *Requested instructions: X*.
		"""
	
		return "Requested instructions: %d"%self.instructionCounter

			
			
	def checkLenStack(self):
		"""
		Returns the current and maximum number of programmed instructions on the function stack. 
		
		:returns: Message of type *Programmed instructions: X (max len Y)*.
		"""
		
		self.ser.write("checkLenStack \n")
		txtStr=self.ser.readline()
		return txtStr[:-1] #returns all execpt the linebreak
	
		

			
	def checkStackFinished(self):
		"""
		Checks if the function stack execution is finished. Returns True if the funtion stack is empty or under consytruction. Return False if the function stack is still in execution (after calling runStack()).
		
		:returns: True/False.
	
		"""
		self.ser.write("checkStackFinished \n")
		if self.ser.readline()=="OK\n":
			return True
		else:
			return False
		
		
		
	def enableAutomaticRURD(self,stepSize,amplitudeRampRate):
		"""
		Enables the automatic ramp up/down feature controled by :func:`AD9958_class.setRampPins`.
		
		The total time elapsed after a full ramp up/down is:

		.. math::
			\dfrac{2^{10}-1}{SYNC\_CLK} \dfrac{amplitudeRampRate}{2^{stepSize}}

		For SYS_CLK=4xSYNC_CLK=500MHz this reduces to:
		
		.. math::
			8.2\dfrac{amplitudeRampRate}{2^{stepSize}}\;\; us
		
		:param stepSize: DAC step size selector. Accepted values: {0,1,2,3}. 
		:type stepSize: int
		:param amplitudeRampRate: Prescaler for the internal counter. Accepted values: 1-255.
		:type amplitudeRampRate: int
		"""
		flag=(amplitudeRampRate<<16)+(stepSize<<14)+(3<<11)
		mask=~((255<<16)+(3<<14)+(3<<11))
		registerAddress=0x06
		registerValue=(mask&self.registerMap[registerAddress])|flag
		self.setRegister(registerAddress,registerValue,doIO_update=1)
		
		
		return 
		
	def disableAutomaticRURD(self):
		"""
		Disables the automatic ramp up/down feature controled by :func:`AD9958_class.setRampPins`.
		"""
		flag=0<<11
		mask=~(1<<11)
		registerAddress=0x06
		registerValue=(mask&self.registerMap[registerAddress])|flag
		self.setRegister(registerAddress,registerValue,doIO_update=1)
		return 
		
	def setAutomaticRURDPins(self,ch0Flag,ch1Flag):
		"""
		Sets the amplitude to be ramped up or down on channel 0 and channel 1 . 
		
		:param ch0Flag: amplitude ramp flag (True->ramp up; False->ramp down)
		:type ch0Flag: bool
		:param ch1Flag: amplitude ramp flag (True->ramp up; False->ramp down)
		:type ch1Flag: bool
		"""
		self.setProfilePins(0,0,ch0Flag,ch1Flag)
		return
		
		
		
