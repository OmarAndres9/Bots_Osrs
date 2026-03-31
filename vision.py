"""
vision.py — Módulo de visión computacional
==========================================
Funciones reutilizables por todos los bots:
  - Captura de pantalla
  - Template matching (buscar imagen en pantalla)
  - Movimiento de mouse con curva Bézier (más humano)
"""

import cv2
import numpy as np
import pyautogui
import time
import random
from PIL import ImageGrab
from pathlib import Path


CONFIANZA_MINIMA = 0.80


# ──────────────────────────────────────────
# Captura de pantalla
# ──────────────────────────────────────────

def capturar_pantalla() -> np.ndarray:
    """Toma screenshot y lo convierte a formato BGR de OpenCV."""
    frame = np.array(ImageGrab.grab())
    return cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)


# ──────────────────────────────────────────
# Template matching
# ──────────────────────────────────────────

def buscar_template(ruta: str | Path, confianza: float = CONFIANZA_MINIMA) -> tuple[int, int] | None:
    """
    Busca una imagen en la pantalla actual.

    Retorna:
        (x, y) del centro si se encontró con suficiente confianza.
        None si no se encontró.
    """
    ruta = Path(ruta)
    if not ruta.exists():
        return None

    template = cv2.imread(str(ruta))
    if template is None:
        return None

    h, w = template.shape[:2]
    pantalla = capturar_pantalla()

    resultado = cv2.matchTemplate(pantalla, template, cv2.TM_CCOEFF_NORMED)
    _, conf_max, _, pos = cv2.minMaxLoc(resultado)

    if conf_max >= confianza:
        cx = pos[0] + w // 2
        cy = pos[1] + h // 2
        return (cx, cy)
    return None


def xp_visible(ruta_xp: str | Path, confianza: float = CONFIANZA_MINIMA) -> bool:
    """Verifica si la barra de XP está visible en pantalla."""
    return buscar_template(ruta_xp, confianza) is not None


# ──────────────────────────────────────────
# Movimiento de mouse — Curva Bézier
# ──────────────────────────────────────────

def mover_bezier(x_dest: int, y_dest: int):
    """
    Mueve el mouse usando una curva Bézier cuadrática.
    Mucho más humano que la línea recta de pyautogui.moveTo().

    La curva tiene un punto de control aleatorio que desvía
    el camino, simulando la trayectoria natural de la mano.
    """
    x0, y0 = pyautogui.position()

    # Punto de control aleatorio (crea la curvatura)
    margen = 60
    ctrl_x = random.randint(
        min(x0, x_dest) - margen,
        max(x0, x_dest) + margen
    )
    ctrl_y = random.randint(
        min(y0, y_dest) - margen,
        max(y0, y_dest) + margen
    )

    pasos = random.randint(25, 45)

    for i in range(pasos + 1):
        t = i / pasos

        # Fórmula Bézier cuadrática
        x = int((1-t)**2 * x0 + 2*(1-t)*t * ctrl_x + t**2 * x_dest)
        y = int((1-t)**2 * y0 + 2*(1-t)*t * ctrl_y + t**2 * y_dest)

        pyautogui.moveTo(x, y)

        # Velocidad variable: más rápido en el medio, más lento al inicio/fin
        velocidad = 0.008 + 0.006 * abs(0.5 - t)
        time.sleep(velocidad + random.uniform(0, 0.004))


def click_humano(x: int, y: int):
    """
    Mueve el mouse con curva Bézier y hace click con desvío aleatorio.
    """
    # Desvío fino en el destino (±4px)
    dx = random.randint(-4, 4)
    dy = random.randint(-4, 4)

    mover_bezier(x + dx, y + dy)
    time.sleep(random.uniform(0.04, 0.12))  # pausa natural antes de clickear
    pyautogui.click()
