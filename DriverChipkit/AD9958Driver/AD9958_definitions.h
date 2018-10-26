
#ifndef AD9958_definitions_h
#define AD9958_definitions_h


#include <stdint.h>
struct registerStruct{
	uint32_t len; //length in bytes
	uint32_t value; //register value
};

struct PIN{
	int chipKitPin;
	volatile unsigned int *PORT;
	volatile unsigned int *PORTSET;
	volatile unsigned int *PORTCLR;
	int PIN;
	
};



extern PIN TRIGGER_IN;
extern PIN TRIGGER_OUT;

extern PIN P0;
extern PIN P1;	
extern PIN P2;
extern PIN P3;
extern PIN IO_UPDATE;
extern PIN CSB; //chip select
extern PIN RESET;
extern PIN SCLK;
extern PIN PWR_DWN;
extern PIN SDIO_3; //sync I/0
extern PIN SDIO_2; //AD9958: serial data out   ChipKit: MISO
extern PIN SDIO_1; // not used
extern PIN SDIO_0; //AD9958: serial data in    ChipKit: MOSI
extern registerStruct registerAD9958[25];




 
/****************************************************************************
AD9958 FUNCTIONS
****************************************************************************/	
void begin(void);
void setRegister(uint32_t registerAddress,uint32_t value, int doIO_update);
void readRegister(uint32_t registerAddress);
void setPWR_DWN_CTL(int flag);
void resetPulse(void);
void IO_update(void);
void fastDigitalWrite(PIN pin, int value);
void startTimerService(void);
void delayTimer(unsigned int clockCycles);
void resetTimer(void);
void waitForTimer(unsigned int clockCycles);
void setProfilePins(unsigned int flag, unsigned int mask);
void waitForTriggerIn(void);
int fastDigitalRead(PIN pin);
 
/**************************************************************************
Commands without hardware timing (no function stack)
**************************************************************************/
void unrecognized(const char *command);

/**************************************************************************
Commands for constructing function stack
**************************************************************************/
void setRegister_ConstructFS();
void resetAD9958_ConstructFS();
void IO_update_ConstructFS();
void setProfilePins_ConstructFS();
void setTriggerOut_ConstructFS();
void waitTriggerIn_ConstructFS();
void delayTimer_ConstructFS();
void resetTimer_ConstructFS();
void waitForTimer_ConstructFS();
void clearStack();
void runStack();
void checkStackFinished();
void checkLenStack();

/**************************************************************************
Functions inside function stack
**************************************************************************/
void begin_FS (uint32_t *dataIn);
void setRegister_FS(uint32_t *dataIn);
void IO_update_FS(uint32_t *dataIn);
void delayTimer_FS(uint32_t *dataIn);
void setProfilePins_FS(uint32_t *dataIn);
void setTriggerOut_FS(uint32_t *dataIn);
void waitTriggerIn_FS(uint32_t *dataIn);
void resetTimer_FS(uint32_t *dataIn);
void waitForTimer_FS(uint32_t *dataIn);


#endif
 