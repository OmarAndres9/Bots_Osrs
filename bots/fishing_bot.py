from base_bot import BaseBot
from vision import buscar_template, click_humano, drop_items
from pathlib import Path
import time
import random


BASE_TEMPLATES = Path("templates/fishing")

MAX_REINTENTOS = 8
ESPERA_REINTENTO = 1.5


def _loc(name, template_dir, spot_templates, fish_templates, wait_time, drop_shift=True):
    return {
        "name": name,
        "template_dir": template_dir,
        "spot_templates": spot_templates if isinstance(spot_templates, list) else [spot_templates],
        "fish_templates": fish_templates if isinstance(fish_templates, list) else [fish_templates],
        "wait_time": wait_time,
        "drop_shift": drop_shift,
    }


FISHING_SPOTS = [
    _loc("Barbarian Village",     "barbarian_village", "fishing_spot.png",     ["raw_trout.png", "raw_salmon.png"],     15.0),
    _loc("Draynor Village",       "draynor",           "fishing_spot.png",     "raw_lobster.png",                       20.0),
    _loc("Karamja",               "karamja",           "fishing_spot.png",     ["raw_tuna.png", "raw_swordfish.png"],    20.0),
    _loc("Catherby — Net",        "catherby",          "fishing_spot_net.png", ["raw_shrimp.png", "raw_anchovies.png"],  8.0),
    _loc("Catherby — Lobster",    "catherby",          "fishing_spot_cage.png", "raw_lobster.png",                      20.0),
    _loc("Catherby — Harpoon",    "catherby",          "fishing_spot_harpoon.png", ["raw_tuna.png", "raw_swordfish.png"], 20.0),
    _loc("Shilo Village",         "shilo_village",     "fishing_spot.png",     ["raw_tuna.png", "raw_swordfish.png"],    20.0),
]


class FishingBot(BaseBot):

    def __init__(self, spot: dict):
        self.spot = spot
        super().__init__(f"Pesca — {spot['name']}")
        self.template_dir = BASE_TEMPLATES / spot["template_dir"]

    def _tp(self, name: str) -> Path:
        return self.template_dir / name

    def _buscar_spot(self):
        for t in self.spot["spot_templates"]:
            coords = buscar_template(self._tp(t))
            if coords:
                return coords
        return None

    def _inventario_lleno(self) -> bool:
        for t in self.spot["fish_templates"]:
            encontrados = 0
            for _ in range(28):
                if buscar_template(self._tp(t), confianza=0.75):
                    encontrados += 1
                else:
                    break
            if encontrados >= 24:
                return True
        return False

    def _dropear_pescado(self):
        self.log("  Soltando pescado...")
        total = 0
        for t in self.spot["fish_templates"]:
            path = self._tp(t)
            if path.exists():
                if self.spot.get("drop_shift", True):
                    total += drop_items(path)
                else:
                    from vision import drop_items_derecho
                    total += drop_items_derecho(path)
        self.log(f"  Items soltados: {total}")

    def _pescar(self):
        self.log(f"Buscando spot de pesca...")
        for intento in range(1, MAX_REINTENTOS + 1):
            if not self._running:
                return False

            coords = self._buscar_spot()
            if coords is None:
                self.log(f"  Spot no encontrado (intento {intento}/{MAX_REINTENTOS})")
                time.sleep(ESPERA_REINTENTO)
                continue

            x, y = coords
            self.log(f"  Spot encontrado, pescando...")
            click_humano(x, y)
            self.esperar(self.spot["wait_time"], variacion=3.0)
            return True

        self.log(f"  No se encontró spot tras {MAX_REINTENTOS} intentos.")
        return False

    def loop(self):
        self.log(f"--- Iniciando pesca: {self.spot['name']} ---")

        for _ in range(50):
            if not self._running:
                return

            if self._inventario_lleno():
                self._dropear_pescado()
                self.esperar(0.5)

            self._pescar()
            self.stats["vueltas"] += 1
            self.pausa_humana()

        self.log("Ciclo completado.")
