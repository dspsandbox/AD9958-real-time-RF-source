


#define __LANGUAGE_C__

#define	OPT_BOARD_INTERNAL

#include "SPI_simple.h"
#include <p32_defs.h>
/* 
Starts a SPI communication (on SPI2) in master mode and using the fastest peripherical clock rate (80/2 MHz) 
	int BRG: 
		SPI clock divider (0-255)
		SPI_clock = peripherical_clock / 2*(BRG+1)
		
	int MODE:
		1x = 32-bit data width
		01 = 16-bit data width
		00 = 8-bit data width	
	
	int SMP: 
		Data Input Sample Phase bit
		1 = Input data sampled at end of data output time
		0 = Input data sampled at middle of data output time
		
	int CKE: SPI Clock Edge Select bit
		1 = Serial output data changes on transition from active clock state to Idle clock state (see CKP bit)
		0 = Serial output data changes on transition from Idle clock state to active clock state (see CKP bit)
	
	int CKP: 
		Clock Polarity Select bit
		1 = Idle state for clock is a high level; active state is a low level
		0 = Idle state for clock is a low level; active state is a high level
		

*/ 
void SPI_simple_Class::begin(int BRG, int MODE, int SMP, int CKE, int CKP) 
{
	
	
	SYSKEY = 0xAA996655; // Write Key1 to SYSKEY
	SYSKEY = 0x556699AA; // Write Key2 to SYSKEY
	OSCCONCLR = (0x3 << 19); // set PB divisor to minimum (1:1)
	SYSKEY = 0x0; // write invalid key to force lock
	IEC1CLR=(0x7 <<4); // Disables all SPI2 interrupts
	SPI2CON = 0x0; // Stops and resets the SPI2.
	SPI2BRG=BRG; // clock frequency
	SPI2CON=(1<<15)+(MODE<<10)+(SMP<<9)+(CKE<<8)+(CKP<<6)+(1<<5); // SPI ON, MODE, SMP, CKE, CKP, Master mode

}

uint32_t SPI_simple_Class::transfer(uint32_t dataOut)
{
	while((SPI2STAT&(1<<3))==0);   //Waits for SPITBE (SPI Transmit Buffer Empty Status bit) to be 1
	IFS1CLR=(1<<6); //sets flag
	SPI2BUF=dataOut; 	
	uint32_t  dataIn;
	while((SPI2STAT&1)==0);   //Waits for SPIRBF (SPI Receive Buffer Full Status bit) to be 1
	dataIn=SPI2BUF;
	return dataIn;
}

void SPI_simple_Class::end()
{
	SPI2CON=0x0;
}

SPI_simple_Class SPI_simple;