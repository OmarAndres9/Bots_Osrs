# OSRS Bot Manager

Sistema multi-bot educativo para OSRS con interfaz gráfica.

> ⚠️ Solo con fines educativos. Usar bots viola los ToS de Jagex.

---

## Instalación

```bash
pip install customtkinter opencv-python pillow pyautogui numpy
```

## Estructura del proyecto

```
osrs_bot/
├── ui.py               ← Punto de entrada. Ejecuta esto.
├── bot_manager.py      ← Registro central de bots
├── base_bot.py         ← Clase base que todos heredan
├── vision.py           ← Template matching + mouse Bézier
├── bots/
│   ├── agility_bot.py  ← Bot de agilidad (Gnome Stronghold)
│   ├── fishing_bot.py  ← (por implementar)
│   └── mining_bot.py   ← (por implementar)
└── templates/
    ├── agility/
    │   ├── log_balance.png
    │   ├── obstacle_net_1.png
    │   ├── tree_branch_1.png
    │   ├── balancing_rope.png
    │   ├── tree_branch_2.png
    │   ├── obstacle_net_2.png
    │   ├── obstacle_pipe.png
    │   └── xp_bar.png
    └── fishing/
        └── (tus templates aquí)
```

## Cómo ejecutar

```bash
python ui.py
```

Tendrás 3 segundos tras hacer click en "Iniciar" para cambiar al juego.

---

## Cómo agregar un bot nuevo

### Paso 1 — Crear el archivo del bot

```python
# bots/fishing_bot.py
from base_bot import BaseBot
from vision import buscar_template, click_humano

class FishingBot(BaseBot):
    def __init__(self):
        super().__init__("Fishing")

    def loop(self):
        # 1. Buscar el punto de pesca
        coords = buscar_template("templates/fishing/fishing_spot.png")
        if coords:
            click_humano(*coords)
            self.esperar(15.0, variacion=3.0)
            self.stats["vueltas"] += 1
        else:
            self.log("No encontré el spot, esperando...")
            self.esperar(2.0)
```

### Paso 2 — Registrarlo en bot_manager.py

```python
from bots.fishing_bot import FishingBot

class BotManager:
    def __init__(self):
        self.bots = {
            "Agility — Gnome Stronghold": AgilityBot(),
            "Fishing — Barbarian Village": FishingBot(),  # ← agregar aquí
        }
```

Eso es todo. Aparecerá automáticamente en el selector de la UI.

---

## Cómo crear los templates

1. Abre OSRS
2. Captura la pantalla (Win+Shift+S en Windows)
3. Recorta **solo** el obstáculo o elemento (sin fondo extra)
4. Guárdalo como `.png` en la carpeta correspondiente

Tip: el recorte debe ser pequeño y único — evita incluir
elementos del fondo que puedan cambiar.
