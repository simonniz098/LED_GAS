
# General 
This repo contains a python script meant to be used on a raspberry pi to control multiple LED panels through GPIO, and show updates about an ongoing race with data pulled from Race Monitor. Its primary use is meant for racetracks to show information to spectators.

It also contains various files to control LED Gas panels from Hidly, with the company provided software (original_software folder)

LED Panel model:  [GAS12Z8888 by Hidly](https://www.hidlystore.com/index.php?route=product/product&path=68_106&product_id=702)

# Software
## Python script
The script must run on a Raspberry Pi model 3 and above, as it uses RPi.GPIO. Selenium is also used to query the Race-Monitor API, and Selenium cannot run on Micro-Python. It requires a full OS, which is not possible on smaller MCUs like Arduinos or ESP32.

### Race monitor data
Live races can be browsed at this link: https://www.race-monitor.com/Live 
From the link above, choose a race and grab the race id from the URL. For example:
https://www.race-monitor.com/Live/Race/155629 , grab 155629.
Go to the following link (and change the race id) to reach a page with live timing and minimal useless data:
https://api.race-monitor.com/Timing/?raceid=155629

### Initial Raspberry Pi setup

#### Wi-fi connection ####

Use Network Manager to connect to a wifi network. Make sure machine is fully up-to-date, otherwise wifi could be broken.
```shell
#Scan wifi networks
nmcli device wifi list
#Connect
nmcli device wifi connect $SSID password $PASSWORD
```

#### Chromedriver installation ####
```shell
apt-get install chromium-driver
```

### Selenium setup

Make sure you are running python 3. 

Create a python venv, as python packages are managed externally.

```python
pip3 install selenium
```

## Original software
The software provided by Hidly can only work with a properly equipped C7-270 board, which does not seem to be the case with most of them. They can be reached to buy a different board if you explain your needs by mail. It connects to a COM port and sends a series of bytes to the MCU on the C7-270 board. Since a naked C7-270 board lacks any RS232/422 pinout **AND** the required chips, there is no way to actually talk to the board with this software.


# Hardware 
## LED Panel information and pinout
The first panel in the chain receives input through an RJ-45 port, which is also connected to a flat-cable so every pin is exposed and easily accessible.

### CMOS transceiver
Data is sent through a SM74HC245D CMOS Chip [Datasheet here](https://www.mouser.com/datasheet/2/408/74HC245D_datasheet_en_20160804-959204.pdf). All required signals come in from the left side from the RJ45/Flat-cable and get sent to the right side with the following pinout:
| 1: Direction of input (low) | 20 (Vcc) |
| --- |---|
|2: Serial data in (SDI), White-Orange RJ45 wire  | 19: Enable Input (low) |
|3: Serial data Out (SDO) from the 4th led driver, sent to the next LED Panel in the chain  |18: Serial Data In (SDI), Pin 2 of LED Driver|
|4: Clock signal (CLK), White-Green RJ45 wire|17: SDO from last LED Driver, sent as SDI to next LED Panel in the chain|
|5: Latch Enable (LE), Blue RJ45 wire|16: Clock signal (CLK), Pin 3 of LED Driver|
|6: Output Enable (OE), White-Brown RJ45 wire|15: Latch Enable (LE), Pin 4 of LED Driver|
|7: Clock signal (CLK), from pin 16|14: Output Enable (OE), Pin 21 of LED Driver|
|8: Latch Enable (LE) from pin 15|13: Clock signal (CLK) to next panel|
|9: Output Enable (OE), from pin 14|12: Latch Enable (LE) to next panel|
|10: Ground (GND)|11: Output Enable (OE) to next panel|

Note: For the pinout above, RJ45 cable references are based of a T568-B cable. Most unused RJ45 wires act as ground.

### LED Driver 
There are 4 LED Drivers per "digit" or LED panel. The model is MBI5124GF, [Datasheet here](https://www.neumueller.com/datenblatt/macroblock/MBI5124%20Preliminary%20Datasheet%20%20V1.00-EN.pdf)
If the panel is working but is dim, connect a ground from your raspberry pi to the 12v ground of the LED panel or power supply.

## Original controller 
The controller model is a [C7-270 by Hidly](https://www.hidlystore.com/index.php?route=product/product&path=68_106&product_id=633) also. Controller is utter garbage, so the LED Panel was reverse engineered to be controlled by a raspberry pi.
 
Chip model: STC15W4K58S4 for web searches

Actual chip soldered on the board: IAP15W4K58S4 - 30I - LQFP64L2

[STC15W4K58S4 Datasheet](https://datasheet4u.com/pdf-down/S/T/C/STC15W4K32S4-STCMCU.pdf)

![image](https://github.com/user-attachments/assets/d476d903-ccb4-4b52-82f8-1387d125a998)


### Pinout

![image](https://github.com/user-attachments/assets/720675a7-5331-4edf-b443-3f7f6da0af8e)
