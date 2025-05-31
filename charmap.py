#!/usr/bin/python3

## repartition des LED sur un panneau
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
    'S': pA | pC | pD | pF | pG,           
    'U': pB | pC | pD | pE | pF,           
    'Y': pB | pC | pD | pF | pG,           
    'Z': pA | pB | pD | pE | pG,
    '.': pDP
}
