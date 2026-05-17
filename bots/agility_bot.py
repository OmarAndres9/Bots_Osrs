from base_bot import BaseBot
from vision import buscar_template, click_humano, xp_visible
from bots.courses import AgilityCourse, ALL_COURSES
from pathlib import Path
import time
import random


BASE_TEMPLATES = Path("templates/agility")

MAX_REINTENTOS = 5
ESPERA_REINTENTO = 1.5


class AgilityBot(BaseBot):

    def __init__(self, course: AgilityCourse | str):
        if isinstance(course, str):
            course = ALL_COURSES[course]
        self.course = course
        super().__init__(f"Agility — {course.name}")
        self.template_dir = BASE_TEMPLATES / course.template_dir

    def loop(self):
        vuelta = self.stats["vueltas"] + 1
        self.log(f"Vuelta {vuelta} — {self.course.name}")

        for obs in self.course.obstacles:
            if not self._running:
                return

            exito = self._completar_obstaculo(obs)
            if not exito:
                self.log(f"Fallo crítico en '{obs.name}'. Abortando vuelta.")
                self._running = False
                return

            self.pausa_humana()

        self.stats["vueltas"] += 1
        self.log(f"Vuelta {self.stats['vueltas']} completada.")
        self.esperar(random.uniform(0.5, 1.5))

    def _completar_obstaculo(self, obs) -> bool:
        nombre = obs.name
        template = self.template_dir / obs.template
        espera = obs.wait_time

        for intento in range(1, MAX_REINTENTOS + 1):
            if not self._running:
                return False

            coords = buscar_template(template)

            if coords is None:
                self.log(f"  {nombre}: no encontrado (intento {intento}/{MAX_REINTENTOS})")
                time.sleep(ESPERA_REINTENTO)
                continue

            x, y = coords
            self.log(f"  {nombre}: clickeando...")
            click_humano(x, y)
            self.esperar(espera)

            xp_path = BASE_TEMPLATES / "xp_bar.png"
            if xp_visible(xp_path):
                self.log(f"  {nombre}: OK")
                return True
            else:
                self.log(f"  {nombre}: sin XP, reintentando...")

        self.stats["errores"] += 1
        self.log(f"  {nombre}: FALLO tras {MAX_REINTENTOS} intentos.")
        return False
