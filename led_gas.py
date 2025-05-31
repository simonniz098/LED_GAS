#!/usr/bin/python3

import RPi.GPIO as gpio
from time import sleep
from random import randint
from sys import exit

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
pA = 0xFF << 40
pB = 0xFF << 8
pC = 0xFF
pD = 0xFF << 16
pE = 0xFF << 32
pF = 0xFF << 56
pG = 0xFF << 48
pDP = 0xFF << 24
#bits = bits | A | B | C | D | E | F | G | DP
#print(format(bits,"064b"))

CHAR_MAP = {
    # Numbers:
    '0': pA | pB | pC | pD | pE | pF,
    '1': pB | pC,
    '2': pA | pB | pD | pE | pG,
    '3': pA | pB | pC | pD | pG,
    '4': pB | pC | pF | pG,
    '5': pA | pC | pD | pF | pG,
    '6': pA | pC | pD | pE | pF | pG,
    '7': pA | pB | pC,
    '8': pA | pB | pC | pD | pE | pF | pG,
    '9': pA | pB | pC | pD | pF | pG,
    # Letters:
    'A': pA | pB | pC | pE | pF | pG,
    'B': pC | pD | pE | pF | pG,
    'C': pA | pD | pE | pF,
    'D': pB | pC | pD | pE | pG,
    'E': pA | pD | pE | pF | pG,
    'F': pA | pE | pF | pG,
    'G': pA | pC | pD | pE | pF,
    'H': pB | pC | pE | pF | pG,
    'I': pB | pC,
    'J': pB | pC | pD,
    'L': pD | pE | pF,
    'O': pA | pB | pC | pD | pE | pF,
    'P': pA | pB | pE | pF | pG,
    'R': pE | pG,
    'S': pA | pC | pD | pF | pG,
    'U': pB | pC | pD | pE | pF,
    'Y': pB | pC | pD | pF | pG,
    'Z': pA | pB | pD | pE | pG,
    '.': pDP,
    ',': pDP
}


#Fonction d'envoi au panneau
def send(bits):
  #On doit utiliser le "rising edge" du clock pour la transmission de donnees
  #Latch low pour envoi de donnees
  gpio.output(LATCH, gpio.LOW)
  gpio.output(OUTPUT_ENABLE, gpio.HIGH)
    
  #Loop sur chacun des OUT du LED Driver 
  num_bits = 63
  for bit in format(bits,"064b"):
    #Preparer le bit a envoyer
    gpio.output(SDI, int(bit))

    #print("D{}: {} ".format(num_bits,bit),end="")
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
  gpio.output(OUTPUT_ENABLE, gpio.LOW)
  sleep(HALF_PERIOD)
  gpio.output(LATCH, gpio.LOW)
     

#Pour vider un board. nb_digit est une variable globale
def reset_panneau():
  print("Reset du panneau")
  for i in range(nb_digit):
    bits = int(0)
    send(bits)

#Valide l'input pour que ce soit affiche normalement
def read_input():
  try:
    bad_char = True
    while bad_char:
      chars = input("Entrer caracteres: ")
      chars = chars.upper().rstrip()
      bad_char = False
      for char in chars:
        if char not in CHAR_MAP.keys():
          print("Caractere invalide, recommencer avec lettre et chiffres et . seulement (pas de M, K, V, X)")
          bad_char = True
    #Le panneau affiche l'input a l'envers
    return chars
  except KeyboardInterrupt:
    reset_panneau()
    gpio.cleanup()
    exit(0)
  

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

while True:
  try:
    #4 digit par panneau
    nb_digit = int(input("Combien de panneaux sont connectes au controlleur? ")) * 4
    break
  except ValueError:
    print("ERREUR: Entrer seulement un chiffre de 1 a 8")
    
while True:
  try: 
    chars = read_input()
    index = 0
    for char in chars:
      #Pour afficher le point sans gaspiller un digit on check si on peut le mettre avec le caractere d'avant
      if char not in [".",","]:
        bits = CHAR_MAP[char]
        if index < len(chars) - 2 and chars[index + 1] in [".",","]:
          bits = bits | CHAR_MAP[chars[index + 1]]
        send(bits)
      index = index + 1
  except KeyboardInterrupt:
    reset_panneau()
    break

gpio.cleanup()
