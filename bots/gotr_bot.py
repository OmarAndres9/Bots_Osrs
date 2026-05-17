from base_bot import BaseBot
from vision import buscar_template, click_humano, capturar_pantalla
from pathlib import Path
import time
import random


TEMPLATES = Path("templates/gotr")

MINING_TEMPLATES = ["guardian_rock_elemental.png", "guardian_rock_catalytic.png"]
CRAFT_TEMPLATE = "great_guardian.png"
DEPOSIT_TEMPLATES = ["guardian_deposit.png", "guardian_deposit_rune.png"]
ENTER_TEMPLATE = "portal_enter.png"
EXIT_TEMPLATE = "portal_exit.png"
REWARD_TEMPLATE = "reward_chest.png"
POWER_TEMPLATE = "guardian_power.png"
WAITING_TEMPLATE = "waiting_game.png"

MAX_ESSENCE_MINED = 24
MIN_ESSENCE_TO_CRAFT = 10
ESPERA_REINTENTO = 1.0
MAX_REINTENTOS = 8


class GuardiansOfTheRiftBot(BaseBot):

    def __init__(self):
        super().__init__("Guardians of the Rift")

    def _template(self, name: str) -> Path:
        return TEMPLATES / name

    def _buscar_objeto(self, template: str | list, confianza: float = 0.80):
        if isinstance(template, list):
            for t in template:
                result = self._buscar_objeto(t, confianza)
                if result:
                    return result
            return None
        return buscar_template(self._template(template), confianza)

    # ──────────────────────────────────────────
    # Fases del juego
    # ──────────────────────────────────────────

    def _entrar_minijuego(self) -> bool:
        self.log("Entrando a Guardians of the Rift...")
        for _ in range(MAX_REINTENTOS):
            if not self._running:
                return False
            portal = self._buscar_objeto(ENTER_TEMPLATE)
            if portal:
                click_humano(*portal)
                self.esperar(5.0, variacion=1.0)
                return True
            self.esperar(2.0)
        self.log("No se encontró el portal de entrada.")
        return False

    def _esperar_inicio(self):
        self.log("Esperando inicio de partida...")
        espera_total = 0
        while espera_total < 45:
            if not self._running:
                return False
            coords = self._buscar_objeto(WAITING_TEMPLATE, confianza=0.60)
            if coords is None:
                self.log("Partida iniciada.")
                self.esperar(3.0, variacion=1.0)
                return True
            self.esperar(2.0)
            espera_total += 2
        self.log("Tiempo de espera agotado, asumiendo inicio.")
        return True

    def _minar_esencia(self) -> int:
        self.log("Buscando roca de guardián para minar...")
        minado = 0
        fallos_seguidos = 0

        while minado < MAX_ESSENCE_MINED:
            if not self._running:
                return minado

            coords = self._buscar_objeto(MINING_TEMPLATES)
            if coords:
                click_humano(*coords)
                self.esperar(2.5, variacion=1.0)
                minado += 1
                fallos_seguidos = 0
                if minado % 5 == 0:
                    self.log(f"  Esencia minada: {minado}")
            else:
                fallos_seguidos += 1
                if fallos_seguidos >= MAX_REINTENTOS:
                    self.log("  No se encuentran más rocas.")
                    break
                self.esperar(ESPERA_REINTENTO)

            self.pausa_humana()

        return minado

    def _crear_runas(self) -> bool:
        self.log("Buscando el Great Guardian para crear runas...")
        for _ in range(MAX_REINTENTOS):
            if not self._running:
                return False
            coords = self._buscar_objeto(CRAFT_TEMPLATE)
            if coords:
                click_humano(*coords)
                self.esperar(1.5, variacion=0.5)
                click_humano(*coords)
                self.esperar(4.0, variacion=1.0)
                self.log("  Runas creadas en el Great Guardian.")
                return True
            self.esperar(1.5)
        self.log("  No se encontró el Great Guardian.")
        return False

    def _depositar_runas(self) -> bool:
        self.log("Depositando runas en el Guardian...")
        for _ in range(MAX_REINTENTOS):
            if not self._running:
                return False
            coords = self._buscar_objeto(DEPOSIT_TEMPLATES)
            if coords:
                click_humano(*coords)
                self.esperar(1.5, variacion=0.5)
                click_humano(*coords)
                self.esperar(3.0, variacion=1.0)
                self.log("  Runas depositadas.")
                return True
            self.esperar(1.5)
        self.log("  No se encontró el punto de depósito.")
        return False

    def _manejar_evento_poder(self) -> bool:
        self.log("Posible evento especial detectado...")
        for _ in range(3):
            if not self._running:
                return False
            coords = self._buscar_objeto(POWER_TEMPLATE)
            if coords:
                click_humano(*coords)
                self.esperar(5.0, variacion=1.0)
                self.log("  Evento especial completado.")
                return True
            self.esperar(1.0)
        return False

    def _recolectar_recompensas(self) -> bool:
        self.log("Buscando cofre de recompensas...")
        for _ in range(MAX_REINTENTOS * 2):
            if not self._running:
                return False
            coords = self._buscar_objeto(REWARD_TEMPLATE)
            if coords:
                click_humano(*coords)
                self.esperar(2.0, variacion=0.5)
                self.log("  Recompensas recolectadas.")
                return True
            self.esperar(2.0)
        self.log("  No se encontró el cofre.")
        return False

    def _salir_minijuego(self) -> bool:
        self.log("Saliendo del minijuego...")
        for _ in range(MAX_REINTENTOS):
            if not self._running:
                return False
            coords = self._buscar_objeto(EXIT_TEMPLATE)
            if coords:
                click_humano(*coords)
                self.esperar(3.0, variacion=1.0)
                return True
            self.esperar(1.5)
        return False

    # ──────────────────────────────────────────
    # Loop principal
    # ──────────────────────────────────────────

    def loop(self):
        self.log("--- Nueva partida ---")

        if not self._entrar_minijuego():
            self.log("No se pudo entrar. ¿Estás cerca del portal?")
            self.stats["errores"] += 1
            return

        self._esperar_inicio()

        partida_activa = True
        while partida_activa and self._running:
            self._manejar_evento_poder()

            esencia = self._minar_esencia()
            if esencia < MIN_ESSENCE_TO_CRAFT:
                self.log("  Poca esencia obtenida, reintentando minar...")
                esencia += self._minar_esencia()

            if not self._running:
                break

            self._crear_runas()
            self._depositar_runas()

            self.stats["vueltas"] += 1
            self.log(f"Ciclo {self.stats['vueltas']} completado ({esencia} esencia).")

            hay_roca = self._buscar_objeto(MINING_TEMPLATES, confianza=0.70)
            if hay_roca is None:
                self.log("  Parece que la partida terminó.")
                partida_activa = False

        self._recolectar_recompensas()
        self._salir_minijuego()
        self.log("Partida finalizada.")
