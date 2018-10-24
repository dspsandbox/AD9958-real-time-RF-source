/*

MIT License

Copyright (c) 2018 Pau Gomez Kabelka <paugomezkabelka@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


*/

#include <stdint.h>
#include "SPI_simple.h"
#include "AD9958_definitions.h"
#include "SerialCommand.h"

/****************************************************************************
GENERAL VARIABLES
****************************************************************************/
uint32_t dataOut=0;
uint32_t readNotWrite=0;
unsigned int regValue;
SerialCommand sCmd; 

typedef void (*generalFunction)(uint32_t* ); //General function type that accepts an uint32_t array as input param
generalFunction functionStack [1000];
uint32_t parameterArray[1000][5];
int functionIndex=0;

int triggerValue=0;
int triggerValueOld=0;


/****************************************************************************
PINS

Defined in a public class so they can be easily changed be the user.
****************************************************************************/
PIN TRIGGER_IN;
PIN TRIGGER_OUT;

PIN P0;
PIN P1;	
PIN P2;
PIN P3;
PIN IO_UPDATE;
PIN CSB; //chip select
PIN RESET;
PIN SCLK;
PIN PWR_DWN;
PIN SDIO_3; //sync I/0
PIN SDIO_2; //AD9958: serial data out   ChipKit: MISO
PIN SDIO_1; // not used
PIN SDIO_0; //AD9958: serial data in    ChipKit: MOSI


/****************************************************************************
REGISTERS
****************************************************************************/
registerStruct registerAD9958[25];	// There are 25 registers from 0x00 to 0x18



	

/****************************************************************************
SETUP
****************************************************************************/
void setup() {
begin();
Serial.begin(9600);

//Commands outside function stack
sCmd.setDefaultHandler(unrecognized);
//Commands for function stack (exact timing).
sCmd.addCommand("setRegister",setRegister_ConstructFS);
sCmd.addCommand("reset",resetAD9958_ConstructFS);
sCmd.addCommand("IO_update",IO_update_ConstructFS);
sCmd.addCommand("setProfilePins",setProfilePins_ConstructFS);
sCmd.addCommand("setTriggerOut",setTriggerOut_ConstructFS);
sCmd.addCommand("waitTriggerIn",waitTriggerIn_ConstructFS);
sCmd.addCommand("delayTimer",delayTimer_ConstructFS);
sCmd.addCommand("resetTimer",resetTimer_ConstructFS);
sCmd.addCommand("waitForTimer",waitForTimer_ConstructFS);
sCmd.addCommand("clearStack",clearStack);
sCmd.addCommand("runStack",runStack);
sCmd.addCommand("checkStackFinished",checkStackFinished);
}




/****************************************************************************
LOOP
****************************************************************************/
void loop() {
	sCmd.readSerial();
	}


	
	
/****************************************************************************
AD9958 FUNCTIONS
****************************************************************************/

void begin(void) 
{
	

//DEFAULT PIN CONFIGURATIONS
	
	TRIGGER_IN.chipKitPin=18;
	TRIGGER_IN.PORT=&PORTD;
	TRIGGER_IN.PORTSET=&PORTDSET;
	TRIGGER_IN.PORTCLR=&PORTDCLR;
	TRIGGER_IN.PIN=15;
		
	TRIGGER_OUT.chipKitPin=19;
	TRIGGER_OUT.PORT=&PORTD;
	TRIGGER_OUT.PORTSET=&PORTDSET;
	TRIGGER_OUT.PORTCLR=&PORTDCLR;
	TRIGGER_OUT.PIN=14;
	
	P0.chipKitPin=30;
	P0.PORT=&PORTE;
	P0.PORTSET=&PORTESET;
	P0.PORTCLR=&PORTECLR;
	P0.PIN=7;
		
	P1.chipKitPin=31;	
	P1.PORT=&PORTE;
	P1.PORTSET=&PORTESET;
	P1.PORTCLR=&PORTECLR;
	P1.PIN=6;
	
	P2.chipKitPin=32;
	P2.PORT=&PORTE;
	P2.PORTSET=&PORTESET;
	P2.PORTCLR=&PORTECLR;
	P2.PIN=5;
	
	P3.chipKitPin=33;
	P3.PORT=&PORTE;
	P3.PORTSET=&PORTESET;
	P3.PORTCLR=&PORTECLR;
	P3.PIN=4;
	
	IO_UPDATE.chipKitPin=34;
	IO_UPDATE.PORT=&PORTE;
	IO_UPDATE.PORTSET=&PORTESET;
	IO_UPDATE.PORTCLR=&PORTECLR;
	IO_UPDATE.PIN=3;
	
	CSB.chipKitPin=35; //chip select
	CSB.PORT=&PORTE;
	CSB.PORTSET=&PORTESET;
	CSB.PORTCLR=&PORTECLR;
	CSB.PIN=2;
	
	SCLK.chipKitPin=52;
	SCLK.PORT=&PORTG;
	SCLK.PORTSET=&PORTGSET;
	SCLK.PORTCLR=&PORTGCLR;
	SCLK.PIN=6;
	
	RESET.chipKitPin=36;
	RESET.PORT=&PORTE;
	RESET.PORTSET=&PORTESET;
	RESET.PORTCLR=&PORTECLR;
	RESET.PIN=1;
		
	PWR_DWN.chipKitPin=37;
	PWR_DWN.PORT=&PORTE;
	PWR_DWN.PORTSET=&PORTESET;
	PWR_DWN.PORTCLR=&PORTECLR;
	PWR_DWN.PIN=0;
	
	SDIO_3.chipKitPin=38; //sync I/0
	SDIO_3.PORT=&PORTD;
	SDIO_3.PORTSET=&PORTDSET;
	SDIO_3.PORTCLR=&PORTDCLR;
	SDIO_3.PIN=10;
	
	SDIO_2.chipKitPin=50; //AD9958: serial data out   ChipKit: MISO
	SDIO_2.PORT=&PORTG;
	SDIO_2.PORTSET=&PORTGSET;
	SDIO_2.PORTCLR=&PORTGCLR;
	SDIO_2.PIN=7;
	
	SDIO_1.chipKitPin=39; // not used
	SDIO_1.PORT=&PORTD;
	SDIO_1.PORTSET=&PORTDSET;
	SDIO_1.PORTCLR=&PORTDCLR;
	SDIO_1.PIN=5;
	
	SDIO_0.chipKitPin=51; //AD9958: serial data in    ChipKit: MOSI
	SDIO_0.PORT=&PORTG;
	SDIO_0.PORTSET=&PORTGSET;
	SDIO_0.PORTCLR=&PORTGCLR;
	SDIO_0.PIN=8;
	

//PIN DIRECTION and INITIALIZATION
	
	pinMode(TRIGGER_IN.chipKitPin,INPUT);
	pinMode(TRIGGER_OUT.chipKitPin,OUTPUT);
	pinMode(P0.chipKitPin,OUTPUT);
	pinMode(P1.chipKitPin,OUTPUT);
	pinMode(P2.chipKitPin,OUTPUT);
	pinMode(P3.chipKitPin,OUTPUT);
	pinMode(IO_UPDATE.chipKitPin,OUTPUT);
	pinMode(CSB.chipKitPin,OUTPUT);
	pinMode(RESET.chipKitPin,OUTPUT);
	pinMode(SCLK.chipKitPin,OUTPUT);
	pinMode(PWR_DWN.chipKitPin,OUTPUT);
	pinMode(SDIO_3.chipKitPin,OUTPUT);
	pinMode(SDIO_2.chipKitPin,INPUT);
	pinMode(SDIO_1.chipKitPin,OUTPUT);
	pinMode(SDIO_0.chipKitPin,OUTPUT);
	
	digitalWrite(TRIGGER_OUT.chipKitPin,0);
	digitalWrite(P0.chipKitPin,0);
	digitalWrite(P1.chipKitPin,0);
	digitalWrite(P2.chipKitPin,0);
	digitalWrite(P3.chipKitPin,0);
	digitalWrite(IO_UPDATE.chipKitPin,0);
	digitalWrite(CSB.chipKitPin,1);
	digitalWrite(RESET.chipKitPin,0);
	digitalWrite(SCLK.chipKitPin,0);
	digitalWrite(PWR_DWN.chipKitPin,0);
	digitalWrite(SDIO_3.chipKitPin,0);
	digitalWrite(SDIO_1.chipKitPin,0);
	digitalWrite(SDIO_0.chipKitPin,0);

//INITILAIZE REGISTERS TO DEFAULT
	
	registerAD9958[0].len=1;
	registerAD9958[0].value=0xF0;
	
	registerAD9958[1].len=3;
	registerAD9958[1].value=0;
	
	registerAD9958[2].len=2;
	registerAD9958[2].value=0;
	
	registerAD9958[3].len=3;
	registerAD9958[3].value=(0x03<<8+0x02);
	
	registerAD9958[4].len=4;
	registerAD9958[4].value=0;
	
	registerAD9958[5].len=2;
	registerAD9958[5].value=0;
	
	registerAD9958[6].len=3;
	registerAD9958[6].value=0;
	
	registerAD9958[7].len=2;
	registerAD9958[7].value=0;
	
	registerAD9958[8].len=4;
	registerAD9958[8].value=0;
	
	registerAD9958[9].len=4;
	registerAD9958[9].value=0;
	
	registerAD9958[10].len=4;
	registerAD9958[10].value=0;
	
	registerAD9958[11].len=4;
	registerAD9958[11].value=0;
	
	registerAD9958[12].len=4;
	registerAD9958[12].value=0;
	
	registerAD9958[13].len=4;
	registerAD9958[13].value=0;
	
	registerAD9958[14].len=4;
	registerAD9958[14].value=0;
	
	registerAD9958[15].len=4;
	registerAD9958[15].value=0;
	
	registerAD9958[16].len=4;
	registerAD9958[16].value=0;
	
	registerAD9958[17].len=4;
	registerAD9958[17].value=0;
	
	registerAD9958[18].len=4;
	registerAD9958[18].value=0;
	
	registerAD9958[19].len=4;
	registerAD9958[19].value=0;
	
	registerAD9958[20].len=4;
	registerAD9958[20].value=0;
	
	registerAD9958[21].len=4;
	registerAD9958[21].value=0;
	
	registerAD9958[22].len=4;
	registerAD9958[22].value=0;
	
	registerAD9958[23].len=4;
	registerAD9958[23].value=0;
	
	registerAD9958[24].len=4;
	registerAD9958[24].value=0;
	
//START TIMER SERVICE
	startTimerService();

//SET PWR_DWN 
	setPWR_DWN_CTL(0);
	
//Reset device 
	resetPulse();
	
//SPI communication 
	//After master reset SPI communication is in single-bit 2-wire mode
	//Instruction cycle:
	int BRG=0; //40 MHz clock rate
	int MODE=0; //8 bit SPI
	int CKP=0; 
	int CKE=1; 
	int SMP=0;
	SPI_simple.begin(BRG, MODE, SMP, CKE, CKP);
	setRegister(0,(1<<1),1); //set to single bit 3-wire mode
	
	return;
}






void setRegister(uint32_t registerAddress,uint32_t value,int doIO_update){
	uint32_t len=registerAD9958[registerAddress].len;
	uint32_t readNotWrite=0;
	
	fastDigitalWrite(CSB,0);
	SPI_simple.transfer(((readNotWrite<<7)+registerAddress)); //send instruction byte
	
	for(uint32_t i=len;i>0;i--){
		SPI_simple.transfer((value>>((i-1)*8))); //data transfer
	}
	fastDigitalWrite(CSB,1);
	if (doIO_update){
		IO_update();
	}
	registerAD9958[registerAddress].value=value; //update register value	
	return;
}





// void readRegister(uint32_t registerAddress){
	// uint32_t len=registerAD9958[registerAddress].len;
	// uint32_t readNotWrite=1;
	// uint32_t dataIn;
	
	// fastDigitalWrite(CSB,0);
	// SPI_simple.transfer(((readNotWrite<<7)+registerAddress)); //send instruction byte
	// registerAD9958[registerAddress].value=0;
	// for(uint32_t i=len;i>0;i--){
		// dataIn=SPI_simple.transfer(0); //data transfer
		// registerAD9958[registerAddress].value+=dataIn<<((i-1)*8);
	// }
	// fastDigitalWrite(CSB,1);
	// return;
// }




void setPWR_DWN_CTL(int flag){
	digitalWrite(PWR_DWN.chipKitPin,flag);
	return;
}


void resetPulse(void){
	digitalWrite(RESET.chipKitPin,1);
	digitalWrite(RESET.chipKitPin,0);
	return;
}

void IO_update(void){
	fastDigitalWrite(IO_UPDATE,1);
	delayTimer(0); //10 clock cycles
	fastDigitalWrite(IO_UPDATE,0);
	return;
}
	



void fastDigitalWrite(PIN pin, int value){
	if (value>0){
		*(pin.PORTSET)=(1<<(pin.PIN));
	}
	else{
		*(pin.PORTCLR)=(1<<(pin.PIN));
	}
	return;
}


void startTimerService(void){
	T4CON = 0x0; // Stop any 16/32-bit Timer4 operation
	T5CON = 0x0; // Stop any 16-bit Timer5 operation
	T4CONSET = (1<<3); // Enable 32-bit mode
	TMR4= 0x0; // Clear contents of the TMR4 and TMR5
	PR4 = 0xFFFFFFFF; // Load PR4 and PR5 registers with 32-bit value
	T4CONSET = (1<<15)+(1<<3); // Start Timer45
	
	T2CON = 0x0; // Stop any 16/32-bit Timer2 operation
	T3CON = 0x0; // Stop any 16-bit Timer3 operation
	T2CONSET = (1<<3); // Enable 32-bit mode
	TMR2= 0x0; // Clear contents of the TMR4 and TMR5
	PR2 = 0xFFFFFFFF; // Load PR2 and PR3 registers with 32-bit value
	T2CONSET = (1<<15)+(1<<3); // Start Timer23
	
	
	return;	
}


void delayTimer(unsigned int clockCycles){
	TMR2=0;
	while(TMR2<clockCycles){};
	return;
	
}

void resetTimer(void){
	TMR4=0;
}

void waitForTimer(unsigned int clockCycles){
	while(TMR4<clockCycles){};
	return;
}


void setProfilePins(unsigned int flag,unsigned int mask){
	//This is a fast hack since P0,P1,P2,P3 are on the same port and this way they can be rewritten in a single instruction
	PORTE=(PORTE&mask)|flag;
	return;
}


void waitForTriggerIn(){
	triggerValue=fastDigitalRead(TRIGGER_IN);
	while(true){   //Waiting for a rising edge
		triggerValueOld=triggerValue;
		triggerValue=fastDigitalRead(TRIGGER_IN);
		if(triggerValue and (!triggerValueOld)){  //rising edge has been detected
			break;
		}
	};
	return;
}

int fastDigitalRead(PIN pin){
	return (((*(pin.PORT))>>pin.PIN)&1);
} 
	
	
	
	
	
	
/**************************************************************************
Commands without hardware timing (no function stack)
**************************************************************************/

void unrecognized(const char *command) {
	Serial.println("ERROR! Received command: ");
	Serial.println(command);
	return;
}



/**************************************************************************
Commands for constructing function stack
**************************************************************************/

void setRegister_ConstructFS(){
	uint32_t regAddress;
	uint32_t regValue;
	int doIO_update;
	char *arg;

	arg = sCmd.next();
	regAddress = strtoul(arg,NULL,0);	
	arg = sCmd.next();
	regValue = strtoul(arg,NULL,0);
	arg = sCmd.next();
	doIO_update = strtoul(arg,NULL,0);
	
	functionStack[functionIndex]=setRegister_FS;
	parameterArray[functionIndex][0]=regAddress;
	parameterArray[functionIndex][1]=regValue;
	parameterArray[functionIndex][2]=doIO_update;
	
	functionIndex++;
	return;
}
	

void resetAD9958_ConstructFS(){
	functionStack[functionIndex]= begin_FS;
	
	functionIndex++;
	return;	
}


void IO_update_ConstructFS(){
	functionStack[functionIndex]=IO_update_FS;
	
	functionIndex++;
	return;	
}


	
void setProfilePins_ConstructFS(){
	int P0Flag,P1Flag,P2Flag,P3Flag;
	char *arg;
	unsigned int mask;
	unsigned int flag;
	arg = sCmd.next();
	P0Flag=strtoul(arg,NULL,0);
	arg = sCmd.next();
	P1Flag=strtoul(arg,NULL,0);
	arg = sCmd.next();
	P2Flag=strtoul(arg,NULL,0);
	arg = sCmd.next();
	P3Flag=strtoul(arg,NULL,0);

	
	mask=~((1<<P0.PIN)|(1<<P1.PIN)|(1<<P2.PIN)|(1<<P3.PIN));
	flag=(P0Flag<<P0.PIN)|(P1Flag<<P1.PIN)|(P2Flag<<P2.PIN)|(P3Flag<<P3.PIN);
	

	functionStack[functionIndex]= setProfilePins_FS;
	parameterArray[functionIndex][0]=flag;
	parameterArray[functionIndex][1]=mask;

	functionIndex++;
	return;
}



void setTriggerOut_ConstructFS(){
	char *arg;
	unsigned int flag;
	arg = sCmd.next();
	flag=strtoul(arg,NULL,0);
	functionStack[functionIndex]= setTriggerOut_FS;
	parameterArray[functionIndex][0]=flag;
	
	functionIndex++;
	return;
}



void waitTriggerIn_ConstructFS(){
	functionStack[functionIndex]= waitTriggerIn_FS;
	
	functionIndex++;
	return;
}


void delayTimer_ConstructFS(){
	char *arg;
	unsigned int clockCycles;
	arg = sCmd.next();
	clockCycles=strtoul(arg,NULL,0);
	
	functionStack[functionIndex]= delayTimer_FS;
	parameterArray[functionIndex][0]=clockCycles;
	
	functionIndex++;
	return;	
}


void resetTimer_ConstructFS(){
	functionStack[functionIndex]=  resetTimer_FS;
	
	functionIndex++;
	return;	
}


void waitForTimer_ConstructFS(){
	char *arg;
	unsigned int clockCycles;
	arg = sCmd.next();
	clockCycles=strtoul(arg,NULL,0);
	
	functionStack[functionIndex]= waitForTimer_FS;
	parameterArray[functionIndex][0]=clockCycles;
	
	functionIndex++;
	return;	
}

void clearStack(){
	functionIndex=0;
}

void runStack(){
	noInterrupts();
	TMR4=0;
	for(int j=0; j<functionIndex;j++){
		functionStack[j](parameterArray[j]);
		
	}
	
	interrupts();
	Serial.println("OK");
	return;
}



void checkStackFinished(){
  Serial.println("OK");
}


/**************************************************************************
Functions inside function stack
**************************************************************************/

void begin_FS (uint32_t *dataIn){ 
	begin();
	};
void setRegister_FS(uint32_t *dataIn){
	uint32_t aux=TMR4;
	setRegister(dataIn[0],dataIn[1],dataIn[2]);
	};

void IO_update_FS(uint32_t *dataIn){
	IO_update();
	};
void delayTimer_FS(uint32_t *dataIn){
	delayTimer(dataIn[0]);
	};
void setProfilePins_FS(uint32_t *dataIn){
	setProfilePins(dataIn[0],dataIn[1]);
	};
void setTriggerOut_FS(uint32_t *dataIn){
	fastDigitalWrite(TRIGGER_OUT,dataIn[0]);
	};
void waitTriggerIn_FS(uint32_t *dataIn){
	waitForTriggerIn();
	};
void resetTimer_FS(uint32_t *dataIn){
	resetTimer();
};
void waitForTimer_FS(uint32_t *dataIn){
	waitForTimer(dataIn[0]);
};


