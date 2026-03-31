"""
base_bot.py — Clase base para todos los bots
=============================================
Cualquier bot nuevo solo necesita:
    1. Heredar de BaseBot
    2. Implementar el método loop()

Todo lo demás (threading, start/stop, logging) viene incluido.
"""

import threading
import time
import random
from abc import ABC, abstractmethod


class BaseBot(ABC):
    """
    Clase base abstracta para todos los bots.

    Uso:
        class MiBot(BaseBot):
            def loop(self):
                # lógica del bot aquí
                pass
    """

    def __init__(self, nombre: str):
        self.nombre    = nombre
        self._running  = False
        self._thread   = None
        self._log_cb   = None   # callback para enviar logs a la UI
        self.stats     = {"vueltas": 0, "errores": 0}

    # ----------------------------------------------------------
    # Método abstracto — cada bot lo implementa a su manera
    # ----------------------------------------------------------

    @abstractmethod
    def loop(self):
        """Lógica principal del bot. Se ejecuta en bucle hasta que stop() sea llamado."""
        pass

    # ----------------------------------------------------------
    # Control de ejecución
    # ----------------------------------------------------------

    def start(self):
        """Inicia el bot en un thread separado para no bloquear la UI."""
        if self._running:
            self.log("Ya está corriendo.")
            return
        self._running = True
        self._thread  = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        self.log(f"Bot iniciado.")

    def stop(self):
        """Detiene el bot de forma segura."""
        if not self._running:
            return
        self._running = False
        self.log(f"Bot detenido.")

    def is_running(self) -> bool:
        return self._running

    # ----------------------------------------------------------
    # Loop interno con manejo de errores
    # ----------------------------------------------------------

    def _run(self):
        """
        Wrapper del loop principal.
        Captura errores para que un crash del bot no tire la UI.
        """
        self.log("Iniciando secuencia...")
        time.sleep(3)  # Pausa para cambiar al juego

        while self._running:
            try:
                self.loop()
            except Exception as e:
                self.stats["errores"] += 1
                self.log(f"ERROR: {e}")
                if self.stats["errores"] >= 5:
                    self.log("Demasiados errores consecutivos. Deteniendo bot.")
                    self._running = False
                    break
                time.sleep(2)

        self.log("Bot finalizado.")

    # ----------------------------------------------------------
    # Logging — envía mensajes a la UI
    # ----------------------------------------------------------

    def set_log_callback(self, callback):
        """Registra una función que recibe los mensajes de log."""
        self._log_cb = callback

    def log(self, mensaje: str):
        """Envía un mensaje al log de la UI (thread-safe)."""
        texto = f"[{self.nombre}] {mensaje}"
        print(texto)  # siempre imprime en consola
        if self._log_cb:
            self._log_cb(texto)

    # ----------------------------------------------------------
    # Utilidades compartidas por todos los bots
    # ----------------------------------------------------------

    def esperar(self, base: float, variacion: float = 0.4):
        """Espera un tiempo aleatorio alrededor de 'base' segundos."""
        t = max(0.3, base + random.uniform(-variacion, variacion))
        time.sleep(t)

    def pausa_humana(self):
        """
        Simula una pausa humana ocasional (mirar la pantalla, distraerse).
        Se activa ~15% del tiempo.
        """
        if random.random() < 0.15:
            pausa = random.uniform(2.0, 8.0)
            self.log(f"Pausa humana: {pausa:.1f}s")
            time.sleep(pausa)
