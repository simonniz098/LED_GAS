#!/usr/bin/python3

import RPi.GPIO as gpio
from time import sleep
from random import randint

#Doc sur learn.sparkfun.com/tutorials/raspberry-gpio/python-rpigpio-api
#Pour info sur les pinouts, la commande "pinout" existe.
  
## repartition des LED sur le panneau
##    A
##  F   B
##    G
##  E   C
##    D
##        DP

# donc un 1 = B | C
# 0xFF = 11111111, on bitshift de 40 pour que ce soit de la position 40 a 47
#Python 3 utilise des ints 64 bits
bits = int(0)
A = 0xFF << 40
B = 0xFF << 8
C = 0xFF
D = 0xFF << 16
E = 0xFF << 32
F = 0xFF << 56
G = 0xFF << 48
DP = 0xFF << 24
#bits = bits | A | B | C | D | E | F | G | DP
#print(format(bits,"064b"))


#Fonction d'envoi au panneau
def send(bits):
  #On doit utiliser le "rising edge" du clock pour la transmission de donnees
  try:
    #Latch low pour envoi de donnees
    gpio.output(LATCH, gpio.LOW)
    gpio.output(OUTPUT_ENABLE, gpio.HIGH)
      
    #Loop sur chacun des OUT du LED Driver 
    num_bits = 63
    for bit in format(bits,"064b"):
      #Preparer le bit a envoyer
      gpio.output(SDI, int(bit))
  
      print("D{}: {} ".format(num_bits,bit),end="")
      #Forcer le clock low
      gpio.output(CLOCK, gpio.LOW)
      sleep(HALF_PERIOD)
  
      #Mettre le clock a high pour que le LED driver lise SDI
      gpio.output(CLOCK, gpio.HIGH)
      sleep(HALF_PERIOD)
  
      #Remettre le clock low
      gpio.output(CLOCK, gpio.LOW)
      #Seulement requis pour affichag de debug
      num_bits = num_bits - 1
    
    #Fin de l'envoi
    gpio.output(SDI, gpio.LOW)
    #Latch HIGH pour dire qu'on a fini l'envoi
    gpio.output(LATCH, gpio.HIGH)
    print("LATCH high fin")
    gpio.output(OUTPUT_ENABLE, gpio.LOW)
    sleep(HALF_PERIOD)
    gpio.output(LATCH, gpio.LOW)
     
  except KeyboardInterrupt:
    print("Stop")
    gpio.cleanup()

######### MAIN #########
gpio.setmode(gpio.BOARD) #Utiliser les pins numbers comme sur commande pinout

#Pour pin Output Enable, low pour affichage, high pour eteindre
OUTPUT_ENABLE = 26
gpio.setup(OUTPUT_ENABLE, gpio.OUT)

CLOCK = 24
#Frequence pour clock, 5khz
FREQUENCY_HZ = 5000 
PERIOD = 1.0 / FREQUENCY_HZ # Periode en secondes
HALF_PERIOD = PERIOD / 2 # Demi-periode pour high et low
gpio.setup(CLOCK, gpio.OUT)

#Pour pousser les donnees recues, high. Pour lire donnees, low
LATCH = 23
gpio.setup(LATCH, gpio.OUT)

#Serial Data In, ce qui envoie les bits au driver LED
SDI = 22
gpio.setup(SDI, gpio.OUT)

##Liste pour output Pins selon longueur du panneau. 64 pins par digit
NB_PANNEAU=4
#premiere passe pour wiper les panneaux
print("reset du panneau")
for i in range(NB_PANNEAU):
  bits = int(0)
  send(bits)

##Afficher un 1
bits = int(0)
bits = bits | B | C 
print("print du panneau")
send(bits)

#Afficher un 2
bits = int(0)
bits = bits | A | B | G | E | D
send(bits)
gpio.cleanup()
