"""
bots/agility_bot.py — Bot de Agilidad
======================================
Corre el curso Gnome Stronghold automáticamente.
Hereda de BaseBot e implementa loop().
"""

from base_bot import BaseBot
from vision import buscar_template, click_humano, xp_visible
from pathlib import Path
import time
import random


TEMPLATES = Path("templates/agility")

OBSTACULOS = [
    {"nombre": "Log Balance",       "template": "log_balance.png",     "espera": 3.5},
    {"nombre": "Obstacle Net 1",    "template": "obstacle_net_1.png",  "espera": 2.0},
    {"nombre": "Tree Branch 1",     "template": "tree_branch_1.png",   "espera": 2.5},
    {"nombre": "Balancing Rope",    "template": "balancing_rope.png",  "espera": 3.0},
    {"nombre": "Tree Branch 2",     "template": "tree_branch_2.png",   "espera": 2.5},
    {"nombre": "Obstacle Net 2",    "template": "obstacle_net_2.png",  "espera": 2.0},
    {"nombre": "Obstacle Pipe",     "template": "obstacle_pipe.png",   "espera": 3.0},
]

MAX_REINTENTOS = 5


class AgilityBot(BaseBot):

    def __init__(self):
        super().__init__("Agility")

    def loop(self):
        """Una vuelta completa al curso."""
        self.log(f"Vuelta {self.stats['vueltas'] + 1} iniciando...")

        for obs in OBSTACULOS:
            if not self._running:
                return

            exito = self._completar_obstaculo(obs)
            if not exito:
                self.log(f"Fallo crítico en {obs['nombre']}. Abortando vuelta.")
                self._running = False
                return

            self.pausa_humana()  # pausa aleatoria ocasional entre obstáculos

        self.stats["vueltas"] += 1
        self.log(f"Vuelta {self.stats['vueltas']} completada.")
        self.esperar(random.uniform(0.5, 1.5))

    def _completar_obstaculo(self, obs: dict) -> bool:
        nombre   = obs["nombre"]
        template = TEMPLATES / obs["template"]
        espera   = obs["espera"]

        for intento in range(1, MAX_REINTENTOS + 1):
            if not self._running:
                return False

            coords = buscar_template(template)

            if coords is None:
                self.log(f"  {nombre}: no encontrado (intento {intento})")
                time.sleep(1.5)
                continue

            x, y = coords
            self.log(f"  {nombre}: encontrado en ({x},{y}), clickeando...")
            click_humano(x, y)
            self.esperar(espera)

            xp_path = TEMPLATES / "xp_bar.png"
            if xp_visible(xp_path):
                self.log(f"  {nombre}: XP confirmada.")
                return True
            else:
                self.log(f"  {nombre}: sin XP, reintentando...")

        self.log(f"  {nombre}: FALLO tras {MAX_REINTENTOS} intentos.")
        return False
