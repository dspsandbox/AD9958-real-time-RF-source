## Introduction
This **AD9958 real time RF source** is a package of Python and C++ libraries for real-time control of a  AD9958 direct digital synthesizer  (DDS). These sythesizer has been implemented in the group of Prof. Morgan Mitchell at [ICFO](www.ICFO.eu) for RF and uW state preparation and control of a Rb 87 BEC.

In the following I will give closer details on the hardware needed, programming of the Chikit Max 32 microcontroller, internal connection and about on Python API.

## Hardware
* **AD9958 eval board** Dual channel DDS with a DAC sampling rate of upt to 500 MHz. For further details please check the documentation on the [AD9958](https://www.analog.com/en/products/ad9958.html) and the [evaluation bard](https://www.analog.com/en/design-center/evaluation-hardware-and-software/evaluation-boards-kits/eval-ad9958.html).

* **chipKIT Max32** PIC32 board with a 80MHz on board clock. This microcontroller recieves the requested RF setting over its serial port and sets the corresponding register on the AD9958 via an SPI bus. For detailed information please refer to the [chipKIT Max 32 reference manual](https://reference.digilentinc.com/chipkit_max32/refmanual),  the [PIC32MX5XX/6XX/7XX data sheet](http://ww1.microchip.com/downloads/en/DeviceDoc/60001156J.pdf) and the more complete [PIC32MX Familiy Reference Manual](http://hades.mech.northwestern.edu/images/2/21/61132B_PIC32ReferenceManual.pdf).

* **Reference RF clock** for operating the DDS. In order to achieve the maximum sampling rate of the AD9958, a minimum clock frequency of 25 MHz is required. Please refer to the  AD9958 eval board documentation for the max/min ratings in terms of power and frequency.

* **Linear volatge regulators** for supplying the 3.3V and 1.8V required by the Ad9958 eval board. A good example of a LM317T variable voltage regulator diagram can be found [here](https://www.electronics-tutorials.ws/blog/variable-voltage-power-supply.html).

* **Computer** with a Python 2.7 distribution installed (my personal preference is to directly install the appropiate [Anaconda](https://www.anaconda.com/download/) distribution). Please note that the current project was developed under Python 2.7, the extension to Python 3 has not been tested yet. In order to programm the chipKIT Max32, the Arduino IDE and an additional board manager have to be installed. The whole procedure is well explained [https://chipkit.net/wiki/index.php?title=ChipKIT_core]().


#### Connections





Documentation available under https://gkpau.github.io/AD9958-real-time-RF-source/


