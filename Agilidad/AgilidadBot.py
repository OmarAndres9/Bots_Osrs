import pyautogui
import time
import random


pyautogui.FAILSAFE = True
pyautogui.PAUSE= 0.1


OBSTACULO = [
    {"nombre": "Log Balance",        "x": 500, "y": 350},
    {"nombre": "Obstacle Net (1)",   "x": 510, "y": 320},
    {"nombre": "Tree Branch (1)",    "x": 490, "y": 295},
]


Tiempos_Espera = [
    "Log Balance": 3.5,
    "Obstacle Net": 2.0,
    "Tree Branch": 2.5.
]

def espera_aleatirio(base, variacion=0.4):
    tiempo= base + random.uniform(-variacion,variacion)
    tiempo= max(0.5,tiempo)

    print (f"esperando{tiempo:.f}s...")
    time.sleep(tiempo)


def mover_y_clickear(x,y, nombre):
    desvio_x = random.randint(-5, 5)
    desvio_y = random.randint(-5, 5)

    destino_x = x + desvio_x

    destino_y = y +desvio_y

    durancion_movimiento = random.uniform(0.15, 0.35)

    print(f"Moviéndose a {nombre} → ({destino_x}, {destino_y})")

    
    pyautogui.moveTo(destino_x, destino_y, duration=durancion_movimiento)
    
    time.sleep(random.uniform(0.05,0.15))
    
    pyautogui.click()
    
    print(f"click en {nombre}") 