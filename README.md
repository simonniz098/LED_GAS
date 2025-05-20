# General Info

Manufacturer info for C7-270: http://www.hidlyled.com/LED-Gas-Station-Sign-Remote-Controller-C7-270-p299.html

Chip model: STC15W4K58S4 for web searches

Actual chip soldered on the board: IAP15W4K58S4 - 30I - LQFP64L2 

![Datasheet](https://datasheet4u.com/pdf-down/S/T/C/STC15W4K32S4-STCMCU.pdf)

![image](https://github.com/user-attachments/assets/d476d903-ccb4-4b52-82f8-1387d125a998)
IAP: The program Flash in user program area can be used as EEPROM

15: MCU model STC 1T 8051

W: Operating Voltage 5.5V ~ 2.5V

4K : 4096 bytes of SRAM

58 : 58 Kilobytes of program space

S4 : 4 UARTs (can be used simultaneously), SPI (serial port interface), Internal EEPROM, A/D Converter(PWM can also be used as DAC), CCP/PWM/PCA

30: Up to 30Mhz

I: Industrial temperature range, -40c to 85c

LQFP: Package type (?)

64: Number of pins

# Pinout

    Recommend UART1 on [P3.6/RxD_2, P3.7/TxD_2] or [P1.6/RxD_3/XTAL2, P1.7/TxD_3/XTAL1]
Both suggestions point to wrong places.

For [P3.6/RxD_2, P3.7/TxD_2], traces go to a missing RF component

For [P1.6/RxD_3/XTAL2, P1.7/TxD_3/XTAL1], traces go to a missing unidentified micro-controller.

UART1 is likely on [P1.6/RxD_3/XTAL2,P1.7/TxD_3/XTAL1], as these traces go to a 74HC245D chip (![Datasheet here](https://www.mouser.com/datasheet/2/408/74HC245D_datasheet_en_20160804-959204.pdf)

UART3 is on [P0.0/RxD3,P0.1/TxD3]. Not used but pins are available on the board.

UART4 is on [P0.2/RxD4,P0.3/TxD4]. Not used but pins are available on the board.

SPI is on [P1.2/SS,P1.3/MOSI,P1.4/MISO,P1.5/SCLK]. Goes to U6, missing micro-controller.
![image](https://github.com/user-attachments/assets/720675a7-5331-4edf-b443-3f7f6da0af8e)

J1 pin 1 is GND
