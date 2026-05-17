import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "bots"))

from bots.agility_bot import AgilityBot
from bots.courses import ALL_COURSES
from bots.gotr_bot import GuardiansOfTheRiftBot
from bots.fishing_bot import FishingBot, FISHING_SPOTS
from bots.mining_bot import MiningBot, MINING_SPOTS


class BotManager:

    def __init__(self):
        self.bots = {}

        for key, course in ALL_COURSES.items():
            self.bots[f"Agilidad — {course.name}"] = AgilityBot(course)

        for spot in FISHING_SPOTS:
            self.bots[f"Pesca — {spot['name']}"] = FishingBot(spot)

        for spot in MINING_SPOTS:
            self.bots[f"Minería — {spot['name']}"] = MiningBot(spot)

        self.bots["Guardians of the Rift"] = GuardiansOfTheRiftBot()

    def nombres(self) -> list[str]:
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
