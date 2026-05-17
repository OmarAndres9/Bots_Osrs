from base_bot import BaseBot
from vision import buscar_template, click_humano, drop_items
from pathlib import Path
import time
import random


BASE_TEMPLATES = Path("templates/mining")

MAX_REINTENTOS = 8
ESPERA_REINTENTO = 2.0


def _loc(name, template_dir, rock_templates, ore_templates, wait_time, drop_shift=True):
    return {
        "name": name,
        "template_dir": template_dir,
        "rock_templates": rock_templates if isinstance(rock_templates, list) else [rock_templates],
        "ore_templates": ore_templates if isinstance(ore_templates, list) else [ore_templates],
        "wait_time": wait_time,
        "drop_shift": drop_shift,
    }


MINING_SPOTS = [
    _loc("Varrock — Iron",        "varrock",       "iron_rock.png",     "iron_ore.png",        4.0),
    _loc("Varrock — Silver",      "varrock",       "silver_rock.png",   "silver_ore.png",      5.0),
    _loc("Al Kharid — Copper/Tin","alkharid",      ["copper_rock.png", "tin_rock.png"], ["copper_ore.png", "tin_ore.png"], 3.0),
    _loc("Al Kharid — Iron",      "alkharid",      "iron_rock.png",     "iron_ore.png",        4.0),
    _loc("Mining Guild — Coal",   "mining_guild",  "coal_rock.png",     "coal_ore.png",        5.0),
    _loc("Mining Guild — Mithril","mining_guild",  "mithril_rock.png",  "mithril_ore.png",     6.0),
    _loc("Rimmington — Gold",     "rimmington",    "gold_rock.png",     "gold_ore.png",        6.0),
    _loc("Rimmington — Iron",     "rimmington",    "iron_rock.png",     "iron_ore.png",        4.0),
    _loc("Motherlode Mine",       "motherlode",    "paydirt_rock.png",  "paydirt.png",         4.0),
    _loc("Fossil Island — Volcanic", "fossil_island", "volcanic_rock.png", ["numulite.png", "volcanic_ash.png"], 5.0),
]


class MiningBot(BaseBot):

    def __init__(self, spot: dict):
        self.spot = spot
        super().__init__(f"Minería — {spot['name']}")
        self.template_dir = BASE_TEMPLATES / spot["template_dir"]

    def _tp(self, name: str) -> Path:
        return self.template_dir / name

    def _buscar_roca(self):
        for t in self.spot["rock_templates"]:
            coords = buscar_template(self._tp(t))
            if coords:
                return coords
        return None

    def _inventario_lleno(self) -> bool:
        for t in self.spot["ore_templates"]:
            encontrados = 0
            for _ in range(28):
                if buscar_template(self._tp(t), confianza=0.75):
                    encontrados += 1
                else:
                    break
            if encontrados >= 24:
                return True
        return False

    def _dropear_mineral(self):
        self.log("  Soltando mineral...")
        total = 0
        for t in self.spot["ore_templates"]:
            path = self._tp(t)
            if path.exists():
                if self.spot.get("drop_shift", True):
                    total += drop_items(path)
                else:
                    from vision import drop_items_derecho
                    total += drop_items_derecho(path)
        self.log(f"  Items soltados: {total}")

    def _minar(self) -> bool:
        self.log(f"Buscando roca...")
        for intento in range(1, MAX_REINTENTOS + 1):
            if not self._running:
                return False

            coords = self._buscar_roca()
            if coords is None:
                self.log(f"  Roca no encontrada (intento {intento}/{MAX_REINTENTOS})")
                time.sleep(ESPERA_REINTENTO)
                continue

            x, y = coords
            self.log(f"  Minando...")
            click_humano(x, y)
            self.esperar(self.spot["wait_time"], variacion=1.5)
            return True

        self.log(f"  No se encontró roca tras {MAX_REINTENTOS} intentos.")
        return False

    def loop(self):
        self.log(f"--- Iniciando minería: {self.spot['name']} ---")

        for _ in range(50):
            if not self._running:
                return

            if self._inventario_lleno():
                self._dropear_mineral()
                self.esperar(0.5)

            self._minar()
            self.stats["vueltas"] += 1
            self.pausa_humana()

        self.log("Ciclo completado.")
