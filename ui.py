"""
ui.py — Interfaz principal con CustomTkinter
=============================================
Instalación:
    pip install customtkinter

Ejecutar:
    python ui.py
"""

import customtkinter as ctk
import threading
import time
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from bot_manager import BotManager


# ──────────────────────────────────────────
# Tema
# ──────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


class OSRSBotApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.manager = BotManager()
        self.bot_activo = None

        self._construir_ventana()
        self._construir_header()
        self._construir_selector()
        self._construir_controles()
        self._construir_stats()
        self._construir_log()

        # Actualizar stats cada segundo
        self._actualizar_stats_loop()

    # ──────────────────────────────────────
    # Construcción de la UI
    # ──────────────────────────────────────

    def _construir_ventana(self):
        self.title("OSRS Bot Manager")
        self.geometry("520x680")
        self.resizable(False, False)
        self.configure(fg_color="#0f1117")

    def _construir_header(self):
        frame = ctk.CTkFrame(self, fg_color="#1a1d27", corner_radius=12)
        frame.pack(fill="x", padx=16, pady=(16, 8))

        ctk.CTkLabel(
            frame,
            text="OSRS Bot Manager",
            font=ctk.CTkFont(family="Courier New", size=20, weight="bold"),
            text_color="#4ade80"
        ).pack(pady=(14, 2))

        ctk.CTkLabel(
            frame,
            text="Solo con fines educativos",
            font=ctk.CTkFont(size=11),
            text_color="#6b7280"
        ).pack(pady=(0, 12))

    def _construir_selector(self):
        frame = ctk.CTkFrame(self, fg_color="#1a1d27", corner_radius=12)
        frame.pack(fill="x", padx=16, pady=8)

        ctk.CTkLabel(
            frame, text="Bot",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#9ca3af"
        ).pack(anchor="w", padx=16, pady=(12, 4))

        self.selector = ctk.CTkOptionMenu(
            frame,
            values=self.manager.nombres(),
            font=ctk.CTkFont(family="Courier New", size=13),
            fg_color="#252836",
            button_color="#2d3148",
            button_hover_color="#383d5a",
            dropdown_fg_color="#1e2030",
            text_color="#e2e8f0",
            command=self._on_bot_seleccionado
        )
        self.selector.pack(fill="x", padx=16, pady=(0, 14))
        self.bot_activo = self.selector.get()

    def _construir_controles(self):
        frame = ctk.CTkFrame(self, fg_color="#1a1d27", corner_radius=12)
        frame.pack(fill="x", padx=16, pady=8)

        ctk.CTkLabel(
            frame, text="Control",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#9ca3af"
        ).pack(anchor="w", padx=16, pady=(12, 8))

        fila = ctk.CTkFrame(frame, fg_color="transparent")
        fila.pack(fill="x", padx=16, pady=(0, 14))

        self.btn_start = ctk.CTkButton(
            fila,
            text="▶  Iniciar",
            font=ctk.CTkFont(family="Courier New", size=14, weight="bold"),
            fg_color="#166534",
            hover_color="#15803d",
            text_color="#bbf7d0",
            corner_radius=8,
            command=self._iniciar
        )
        self.btn_start.pack(side="left", expand=True, fill="x", padx=(0, 6))

        self.btn_stop = ctk.CTkButton(
            fila,
            text="■  Detener",
            font=ctk.CTkFont(family="Courier New", size=14, weight="bold"),
            fg_color="#7f1d1d",
            hover_color="#991b1b",
            text_color="#fecaca",
            corner_radius=8,
            state="disabled",
            command=self._detener
        )
        self.btn_stop.pack(side="left", expand=True, fill="x", padx=(6, 0))

        # Indicador de estado
        self.label_estado = ctk.CTkLabel(
            frame,
            text="⬤  Detenido",
            font=ctk.CTkFont(family="Courier New", size=12),
            text_color="#ef4444"
        )
        self.label_estado.pack(pady=(0, 12))

    def _construir_stats(self):
        frame = ctk.CTkFrame(self, fg_color="#1a1d27", corner_radius=12)
        frame.pack(fill="x", padx=16, pady=8)

        ctk.CTkLabel(
            frame, text="Estadísticas",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#9ca3af"
        ).pack(anchor="w", padx=16, pady=(12, 8))

        fila = ctk.CTkFrame(frame, fg_color="transparent")
        fila.pack(fill="x", padx=16, pady=(0, 14))

        # Vueltas
        col1 = ctk.CTkFrame(fila, fg_color="#252836", corner_radius=8)
        col1.pack(side="left", expand=True, fill="x", padx=(0, 6))
        ctk.CTkLabel(col1, text="Vueltas", font=ctk.CTkFont(size=11), text_color="#6b7280").pack(pady=(8,2))
        self.label_vueltas = ctk.CTkLabel(
            col1, text="0",
            font=ctk.CTkFont(family="Courier New", size=22, weight="bold"),
            text_color="#4ade80"
        )
        self.label_vueltas.pack(pady=(0, 8))

        # Errores
        col2 = ctk.CTkFrame(fila, fg_color="#252836", corner_radius=8)
        col2.pack(side="left", expand=True, fill="x", padx=(6, 0))
        ctk.CTkLabel(col2, text="Errores", font=ctk.CTkFont(size=11), text_color="#6b7280").pack(pady=(8,2))
        self.label_errores = ctk.CTkLabel(
            col2, text="0",
            font=ctk.CTkFont(family="Courier New", size=22, weight="bold"),
            text_color="#f87171"
        )
        self.label_errores.pack(pady=(0, 8))

    def _construir_log(self):
        frame = ctk.CTkFrame(self, fg_color="#1a1d27", corner_radius=12)
        frame.pack(fill="both", expand=True, padx=16, pady=(8, 16))

        ctk.CTkLabel(
            frame, text="Log",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#9ca3af"
        ).pack(anchor="w", padx=16, pady=(12, 4))

        self.log_box = ctk.CTkTextbox(
            frame,
            font=ctk.CTkFont(family="Courier New", size=11),
            fg_color="#0d1117",
            text_color="#86efac",
            border_width=1,
            border_color="#1f2937",
            corner_radius=8,
            state="disabled"
        )
        self.log_box.pack(fill="both", expand=True, padx=12, pady=(0, 12))

    # ──────────────────────────────────────
    # Lógica de botones
    # ──────────────────────────────────────

    def _on_bot_seleccionado(self, nombre: str):
        self.bot_activo = nombre

    def _iniciar(self):
        if not self.bot_activo:
            return
        self.log(f"Iniciando {self.bot_activo}... (tienes 3s para cambiar al juego)")
        self.manager.iniciar(self.bot_activo, log_callback=self.log)
        self._set_estado_corriendo(True)

    def _detener(self):
        if self.bot_activo:
            self.manager.detener(self.bot_activo)
        self._set_estado_corriendo(False)

    def _set_estado_corriendo(self, corriendo: bool):
        if corriendo:
            self.btn_start.configure(state="disabled")
            self.btn_stop.configure(state="normal")
            self.label_estado.configure(text="⬤  Corriendo", text_color="#4ade80")
        else:
            self.btn_start.configure(state="normal")
            self.btn_stop.configure(state="disabled")
            self.label_estado.configure(text="⬤  Detenido", text_color="#ef4444")

    # ──────────────────────────────────────
    # Log (thread-safe via after())
    # ──────────────────────────────────────

    def log(self, mensaje: str):
        """Agrega una línea al log de forma thread-safe."""
        self.after(0, self._log_insert, mensaje)

    def _log_insert(self, mensaje: str):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", mensaje + "\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    # ──────────────────────────────────────
    # Actualización de stats
    # ──────────────────────────────────────

    def _actualizar_stats_loop(self):
        """Actualiza las estadísticas cada segundo."""
        if self.bot_activo:
            stats = self.manager.stats(self.bot_activo)
            self.label_vueltas.configure(text=str(stats.get("vueltas", 0)))
            self.label_errores.configure(text=str(stats.get("errores", 0)))

            # Detectar si el bot se detuvo solo (por error)
            if not self.manager.estado(self.bot_activo):
                self._set_estado_corriendo(False)

        self.after(1000, self._actualizar_stats_loop)

    # ──────────────────────────────────────
    # Cierre limpio
    # ──────────────────────────────────────

    def on_close(self):
        self.manager.detener_todos()
        self.destroy()


# ──────────────────────────────────────────
# Punto de entrada
# ──────────────────────────────────────────

if __name__ == "__main__":
    app = OSRSBotApp()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()
