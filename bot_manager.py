"""
bot_manager.py — Gestor central de bots
=========================================
Registra todos los bots disponibles y expone
métodos simples para la UI: start, stop, estado.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "bots"))

from bots.agility_bot import AgilityBot
# Para agregar un bot nuevo:
#   from bots.fishing_bot import FishingBot
#   from bots.mining_bot  import MiningBot


class BotManager:
    """
    Registro central de todos los bots disponibles.

    Para agregar un bot nuevo:
        1. Crea el archivo en bots/mi_bot.py heredando BaseBot
        2. Importa la clase arriba
        3. Agrégala a self.bots en __init__
    """

    def __init__(self):
        self.bots = {
            "Agility — Gnome Stronghold": AgilityBot(),
            # "Fishing — Barbarian Village": FishingBot(),
            # "Mining — Motherlode Mine":    MiningBot(),
        }

    def nombres(self) -> list[str]:
        """Lista de nombres para el selector de la UI."""
        return list(self.bots.keys())

    def iniciar(self, nombre: str, log_callback=None):
        bot = self.bots.get(nombre)
        if bot:
            if log_callback:
                bot.set_log_callback(log_callback)
            bot.start()

    def detener(self, nombre: str):
        bot = self.bots.get(nombre)
        if bot:
            bot.stop()

    def detener_todos(self):
        for bot in self.bots.values():
            bot.stop()

    def estado(self, nombre: str) -> bool:
        bot = self.bots.get(nombre)
        return bot.is_running() if bot else False

    def stats(self, nombre: str) -> dict:
        bot = self.bots.get(nombre)
        return bot.stats if bot else {}
