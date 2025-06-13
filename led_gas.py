#!/usr/bin/env python3

import RPi.GPIO as gpio
from time import sleep
from datetime import datetime
from sys import exit

#Portion pour importer les donnees de race monitor
from selenium import webdriver
#from selenium.webdriver import FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
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
    ',': pDP,
    ' ': 0,
}

#Fonction pour preparer le panneau a recevoir des donnees
#Eteint le panneau
def init_send():
  #Latch low pour envoi de donnees
  gpio.output(LATCH, gpio.LOW)
  gpio.output(OUTPUT_ENABLE, gpio.HIGH)

#Fonction d'envoi au panneau
def send(bits):
    
  #Loop sur chacun des OUT du LED Driver 
  num_bits = 63
  for bit in format(bits,"064b"):
    #Preparer le bit a envoyer
    gpio.output(SDI, int(bit))

    #print("D{}: {} ".format(num_bits,bit),end="")
    #Forcer le clock low
    gpio.output(CLOCK, gpio.LOW)
    sleep(HALF_PERIOD)

    #On doit utiliser le "rising edge" du clock pour la transmission de donnees
    #Mettre le clock a high pour que le LED driver lise SDI
    gpio.output(CLOCK, gpio.HIGH)
    sleep(HALF_PERIOD)

    #Remettre le clock low
    gpio.output(CLOCK, gpio.LOW)
    #Seulement requis pour affichag de debug
    num_bits = num_bits - 1
  
#Fonction pour commencer a afficher le panneau apres l'envoi de donnees
def finish_send():
  #Fin de l'envoi
  gpio.output(SDI, gpio.LOW)
  #Latch HIGH pour dire qu'on a fini l'envoi
  gpio.output(LATCH, gpio.HIGH)
  #Allumer le panneau
  gpio.output(OUTPUT_ENABLE, gpio.LOW)
  sleep(HALF_PERIOD)
  gpio.output(LATCH, gpio.LOW)
     

#Pour vider un board. nb_digit est une variable globale
def reset_panneau():
  print("Reset du panneau")
  init_send()
  for i in range(nb_digit):
    bits = int(0)
    send(bits)
  finish_send()

#Lire le raceId pour aller poker l'API apres
def read_raceId():
  while True:
    try:
      raceId = int(input("Entrer le ID de la course (123456): "))
      if len(str(raceId)) != 6:
        raise ValueError
      print("ID fourni: {}".format(raceId))
      return raceId
    except ValueError:
      print("ERREUR: Mauvais format de ID. Entrer 6 chiffres")
  
#Requiert headless sinon crash parce que pas d'env graphique
def init_selenium():
  serv = Service(executable_path="/usr/bin/chromedriver")
  opts = webdriver.ChromeOptions()
  opts.add_argument("--headless")
  browser = webdriver.Chrome(options=opts,service=serv)
  return browser

def read_api(browser):
  displayContainers = browser.find_elements(by=By.CLASS_NAME, value="displayContainer")
  for dis in displayContainers:
      if dis.is_displayed():
          displayContainer = dis
          break
  timingHeader = displayContainer.find_element(by=By.CLASS_NAME, value="timingHeader")
  timingHeaderElems = timingHeader.find_elements(by=By.TAG_NAME, value='div')
  racers= displayContainer.find_elements(by=By.CLASS_NAME, value="racerName")
  #Trouver le nombre de laps
  race_info = []
  race_info.append(find_lap(timingHeaderElems))
  race_info.extend(find_positions(racers))
  print("Race info: {}".format(race_info))
  return race_info

def find_lap(timingHeaderElems):
  lap_idx = 0
  for index,elem in enumerate(timingHeaderElems):
    if elem.text == "Laps to go:":
      lap_idx = index + 1
      break
  #ljust pour afficher les tours a gauche du panneau"
  return timingHeaderElems[lap_idx].text.ljust(4)
  
def find_positions(racers):
  positions=[]
  for position,racer in enumerate(racers):
    #On veut pas plus que 5 positions dans liste
    if len(positions) == 5:
        break
    #Pour eviter les lignes "Waiting for info"
    if racer.text.startswith("#"):
      #Mettre la position, index + 1
      #Garder le numero du pilote
      #  Retirer le #
      #  Remplir d'espaces a gauche pour pas decaler l'affichage des autres panneaux
      #  On inscrit seulement 3 caracteres pour pouvoir afficher la position sur le panneau. ex: 1. 88
      pos_chars = str(position + 1) + "." + racer.text.split(" ")[0].strip("#").rjust(3," ").upper()[0:3]
      #Enlever les caracteres invalides
      for idx,char in enumerate(pos_chars):
        if char not in CHAR_MAP.keys():
          pos_chars.replace(char," ")
      positions.append(pos_chars)
  #S'assurer qu'on a 5 entrees de positions, et quand y'a rien on affiche un panneau vide
  while len(positions) < 5:
    positions.append("    ")
  return positions

######### MAIN #########
browser = init_selenium()
raceId = read_raceId()
url="https://api.race-monitor.com/Timing/?raceid={}".format(raceId)

#4 digit par panneau de gaz * 6 panneaux = 24
nb_digit = 24

print("Configuration du GPIO")
#Enleve des erreurs si on control+c le script
gpio.setwarnings(False)
gpio.setmode(gpio.BCM)

#Pour pin Output Enable, low pour affichage, high pour eteindre
OUTPUT_ENABLE = 15
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
SDI = 25
gpio.setup(SDI, gpio.OUT)

    
#Le panneau le plus proche du controlleur recoit la derniere info envoyee.
#Donc avec 6 panneaux, le lap est sur le board le plus loin et P5 est sur 
#le panneau branche direct sur le pi
print("Connecting to {}".format(url))
browser.get(url)
old_race_info = []
while True:
  try: 
    race_info = read_api(browser)
    if old_race_info != race_info:
      init_send()
      for pane in race_info:
        index = 0
        for char in pane:
          #Pour afficher le point sans gaspiller un digit on check si on peut le mettre avec le caractere d'avant
          if char not in [".",","]:
            bits = CHAR_MAP[char]
            if index < len(pane) - 2 and pane[index + 1] in [".",","]:
              bits = bits | CHAR_MAP[pane[index + 1]]
            send(bits)
          index = index + 1
      finish_send()
      sleep(1)
    else:
      print("{}: Pas de nouvelle info a afficher".format(datetime.now()))
    old_race_info = race_info
  except KeyboardInterrupt:
    reset_panneau()
    break

