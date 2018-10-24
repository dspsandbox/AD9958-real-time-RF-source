
/* 
Library created for simple, fast and controllable SPI communication. Specially avoiding the arduino style overhead.


MIT License

Copyright (c) 2015 Pau Gomez Kabelka <paugomezkabelka@gmail.com>

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
#if !defined(_SPI_SIMPLE_H_INCLUDED)
#define _SPI_SIMPLE_H_INCLUDED

#define __LANGUAGE_C__

#include <stdio.h>
#include <WProgram.h>

#include <p32_defs.h>

class SPI_simple_Class {
public:
	
	uint32_t transfer(uint32_t dataOut);
	void begin(int BRG, int MODE, int SMP, int CKE, int CKP);	
	void end();
  
};

extern SPI_simple_Class SPI_simple;


#endif
