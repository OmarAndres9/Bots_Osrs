"""
OSRS Agility Bot - Con Visión Computacional
============================================
Versión mejorada que usa OpenCV para encontrar obstáculos
dinámicamente en pantalla en lugar de coordenadas fijas.

Librerías necesarias:
    pip install pyautogui pillow opencv-python numpy

Estructura de archivos esperada:
    /templates/
        log_balance.png
        obstacle_net_1.png
        tree_branch_1.png
        balancing_rope.png
        tree_branch_2.png
        obstacle_net_2.png
        obstacle_pipe.png
        xp_bar.png          ← recorte de la barra de XP ganando exp

¿Cómo crear los templates?
    1. Abre OSRS
    2. Haz un screenshot (Win+Shift+S en Windows)
    3. Recorta solo el obstáculo (sin fondo extra)
    4. Guárdalo como .png en la carpeta /templates/

⚠️  DISCLAIMER: Solo con fines educativos.
    Usar bots viola los ToS de Jagex.
"""

import cv2
import numpy as np
import pyautogui
import time
import random
from PIL import ImageGrab
from pathlib import Path


# ============================================================
# CONFIGURACIÓN
# ============================================================

pyautogui.FAILSAFE = True  # Esquina superior izquierda = detener bot

TEMPLATES_DIR = Path("templates")  # Carpeta con las imágenes de referencia

# Umbral de confianza para considerar que encontró el obstáculo
# 0.0 = acepta cualquier cosa, 1.0 = coincidencia perfecta
# 0.8 es un buen balance — ajusta si hay falsos positivos/negativos
CONFIANZA_MINIMA = 0.8

# Cuántas veces reintentar si no encuentra un obstáculo
MAX_REINTENTOS = 5

# Tiempo entre reintentos (segundos)
ESPERA_REINTENTO = 1.5


# ============================================================
# SECUENCIA DE OBSTÁCULOS
# Cada obstáculo tiene:
#   - template: nombre del archivo .png de referencia
#   - espera:   tiempo base que tarda el personaje en completarlo
# ============================================================

OBSTACULOS = [
    {"nombre": "Log Balance",       "template": "log_balance.png",      "espera": 3.5},
    {"nombre": "Obstacle Net (1)",  "template": "obstacle_net_1.png",   "espera": 2.0},
    {"nombre": "Tree Branch (1)",   "template": "tree_branch_1.png",    "espera": 2.5},
    {"nombre": "Balancing Rope",    "template": "balancing_rope.png",   "espera": 3.0},
    {"nombre": "Tree Branch (2)",   "template": "tree_branch_2.png",    "espera": 2.5},
    {"nombre": "Obstacle Net (2)",  "template": "obstacle_net_2.png",   "espera": 2.0},
    {"nombre": "Obstacle Pipe",     "template": "obstacle_pipe.png",    "espera": 3.0},
]


# ============================================================
# MÓDULO 1: CAPTURA DE PANTALLA
# ============================================================

def capturar_pantalla() -> np.ndarray:
    """
    Toma un screenshot de toda la pantalla y lo convierte
    al formato que OpenCV puede procesar (BGR numpy array).

    PIL captura en formato RGB → OpenCV trabaja en BGR
    por eso se hace la conversión con cvtColor.
    """
    screenshot = ImageGrab.grab()                        # PIL screenshot
    frame = np.array(screenshot)                         # PIL → NumPy
    frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)  # RGB → BGR
    return frame_bgr


# ============================================================
# MÓDULO 2: TEMPLATE MATCHING (el corazón del bot)
# ============================================================

def buscar_en_pantalla(nombre_template: str) -> tuple[int, int] | None:
    """
    Busca una imagen (template) dentro de la pantalla actual.

    ¿Cómo funciona template matching?
    ─────────────────────────────────
    OpenCV desliza el template pixel por pixel sobre la
    pantalla completa y calcula en cada posición qué tan
    similar es. El resultado es un mapa de calor:

        pantalla:           mapa de confianza:
        ┌─────────┐         ┌─────────┐
        │  🌳     │  ──►   │ 0.1 0.9 │  ← 0.9 = alta similitud
        │         │         │ 0.2 0.1 │
        └─────────┘         └─────────┘

    cv2.minMaxLoc() encuentra el punto de mayor confianza.

    Retorna:
        (x, y) del centro del objeto encontrado, o None si
        no lo encontró con suficiente confianza.
    """
    ruta_template = TEMPLATES_DIR / nombre_template

    # Verificar que el template existe
    if not ruta_template.exists():
        print(f"  ⚠️  Template no encontrado: {ruta_template}")
        return None

    # Cargar el template (imagen de referencia)
    template = cv2.imread(str(ruta_template))
    if template is None:
        print(f"  ❌ No se pudo leer: {ruta_template}")
        return None

    alto_t, ancho_t = template.shape[:2]

    # Capturar pantalla actual
    pantalla = capturar_pantalla()

    # Ejecutar template matching
    # TM_CCOEFF_NORMED: método normalizado, devuelve valores entre -1 y 1
    resultado = cv2.matchTemplate(pantalla, template, cv2.TM_CCOEFF_NORMED)

    # Obtener la posición y confianza del mejor match
    _, confianza_max, _, ubicacion_top_left = cv2.minMaxLoc(resultado)

    print(f"  🔍 '{nombre_template}' → confianza: {confianza_max:.3f}", end="")

    if confianza_max >= CONFIANZA_MINIMA:
        # Calcular el centro del objeto encontrado
        # (ubicacion_top_left es la esquina superior izquierda)
        centro_x = ubicacion_top_left[0] + ancho_t // 2
        centro_y = ubicacion_top_left[1] + alto_t // 2
        print(f" ✅ encontrado en ({centro_x}, {centro_y})")
        return (centro_x, centro_y)
    else:
        print(f" ❌ no encontrado (mínimo requerido: {CONFIANZA_MINIMA})")
        return None


# ============================================================
# MÓDULO 3: DETECCIÓN DE BARRA DE XP
# ============================================================

def xp_ganado() -> bool:
    """
    Verifica si la barra de XP está visible en pantalla.

    En OSRS, cuando ganas XP aparece brevemente un contador
    flotante con la experiencia ganada. Si lo detectamos,
    sabemos que el obstáculo fue completado exitosamente.

    ¿Por qué es importante?
    ───────────────────────
    En Agility, el personaje puede FALLAR un obstáculo.
    Sin esta verificación, el bot seguiría al siguiente
    obstáculo aunque el personaje no haya avanzado,
    desincronizándose completamente.

    Retorna:
        True  → se ganó XP (obstáculo completado)
        False → no se detectó XP (posible fallo)
    """
    ruta_xp = TEMPLATES_DIR / "xp_bar.png"

    if not ruta_xp.exists():
        # Si no hay template de XP, asumir éxito (modo degradado)
        print("  ⚠️  Sin template de XP, asumiendo éxito...")
        return True

    pantalla = capturar_pantalla()
    template_xp = cv2.imread(str(ruta_xp))

    resultado = cv2.matchTemplate(pantalla, template_xp, cv2.TM_CCOEFF_NORMED)
    _, confianza_max, _, _ = cv2.minMaxLoc(resultado)

    if confianza_max >= CONFIANZA_MINIMA:
        print(f"  ✨ XP detectada (confianza: {confianza_max:.3f})")
        return True
    else:
        print(f"  ⚠️  XP no detectada (confianza: {confianza_max:.3f})")
        return False


# ============================================================
# MÓDULO 4: ACCIÓN (mover mouse y clickear)
# ============================================================

def mover_y_clickear(x: int, y: int) -> None:
    """
    Mueve el mouse a (x, y) con pequeño desvío aleatorio
    y hace click, simulando comportamiento humano.
    """
    desvio_x = random.randint(-2, 2)
    desvio_y = random.randint(-2, 2)
    duracion = random.uniform(0.15, 0.30)

    pyautogui.moveTo(x + desvio_x, y + desvio_y, duration=duracion)
    time.sleep(random.uniform(0.05, 0.12))  # pausa antes de clickear
    pyautogui.click()


def espera_aleatoria(base: float, variacion: float = 0.4) -> None:
    tiempo = base + random.uniform(-variacion, variacion)
    tiempo = max(0.5, tiempo)
    time.sleep(tiempo)


# ============================================================
# MÓDULO 5: MANEJO DE ERRORES
# ============================================================

def manejar_obstaculo(obstaculo: dict) -> bool:
    """
    Intenta completar un obstáculo con reintentos.

    Flujo:
    ┌─────────────────────────────────────────┐
    │  Buscar obstáculo en pantalla           │
    │       ↓ encontrado?                     │
    │  Sí → Clickear → Esperar → Ver XP      │
    │           ↓ XP ganada?                  │
    │       Sí → ✅ éxito                     │
    │       No → 🔁 reintentar click          │
    │  No → 🔁 reintentar búsqueda            │
    │       (hasta MAX_REINTENTOS veces)      │
    │       Si agota reintentos → ❌ fallo    │
    └─────────────────────────────────────────┘

    Retorna:
        True  → obstáculo completado
        False → falló después de todos los reintentos
    """
    nombre   = obstaculo["nombre"]
    template = obstaculo["template"]
    espera   = obstaculo["espera"]

    print(f"\n  🎯 Obstáculo: {nombre}")

    for intento in range(1, MAX_REINTENTOS + 1):

        if intento > 1:
            print(f"  🔁 Reintento {intento}/{MAX_REINTENTOS}...")
            time.sleep(ESPERA_REINTENTO)

        # --- PASO 1: Buscar el obstáculo en pantalla ---
        coordenadas = buscar_en_pantalla(template)

        if coordenadas is None:
            print(f"  ❌ No se encontró '{nombre}' en pantalla")
            continue  # Reintentar la búsqueda

        # --- PASO 2: Clickear el obstáculo ---
        x, y = coordenadas
        mover_y_clickear(x, y)

        # --- PASO 3: Esperar a que el personaje lo complete ---
        espera_aleatoria(espera)

        # --- PASO 4: Verificar que se ganó XP ---
        if xp_ganado():
            print(f"  ✅ '{nombre}' completado!")
            return True  # Éxito, pasar al siguiente obstáculo
        else:
            # El personaje falló el obstáculo — reintentar el click
            print(f"  ⚠️  '{nombre}' posiblemente falló, reintentando...")
            continue

    # Agotó todos los reintentos
    print(f"  ❌ FALLO TOTAL en '{nombre}' tras {MAX_REINTENTOS} intentos")
    print(f"  🛑 Deteniendo bot para revisión manual...")
    return False


# ============================================================
# LOOP PRINCIPAL
# ============================================================

def correr_curso(vueltas: int = 10) -> None:
    """
    Loop principal del bot.
    Corre el curso de agilidad N veces usando visión computacional.
    """
    print("=" * 55)
    print("  👁️  OSRS Agility Bot - Visión Computacional")
    print("=" * 55)
    print(f"  Obstáculos cargados : {len(OBSTACULOS)}")
    print(f"  Confianza mínima    : {CONFIANZA_MINIMA}")
    print(f"  Máx reintentos      : {MAX_REINTENTOS}")
    print(f"  Vueltas programadas : {vueltas}")
    print("=" * 55)
    print("  Tienes 3 segundos para poner el foco en OSRS...")
    time.sleep(3)

    vueltas_completadas = 0
    vueltas_fallidas    = 0

    for vuelta in range(1, vueltas + 1):

        print(f"\n{'='*55}")
        print(f"  🔄 VUELTA {vuelta}/{vueltas}")
        print(f"{'='*55}")

        vuelta_exitosa = True

        for obstaculo in OBSTACULOS:

            exito = manejar_obstaculo(obstaculo)

            if not exito:
                # Si un obstáculo falla por completo, abortar la vuelta
                vuelta_exitosa = False
                break

        if vuelta_exitosa:
            vueltas_completadas += 1
            print(f"\n  🏁 Vuelta {vuelta} completada exitosamente!")
        else:
            vueltas_fallidas += 1
            print(f"\n  💀 Vuelta {vuelta} abortada por fallo crítico.")
            break  # Detener el bot completamente para revisión

        # Pausa entre vueltas (simula que el jugador mira la pantalla)
        pausa = random.uniform(0.5, 1.5)
        print(f"  💨 Pausa entre vueltas: {pausa:.2f}s")
        time.sleep(pausa)

    # Reporte final
    print(f"\n{'='*55}")
    print(f"  📊 RESUMEN DE SESIÓN")
    print(f"{'='*55}")
    print(f"  Vueltas completadas : {vueltas_completadas}")
    print(f"  Vueltas fallidas    : {vueltas_fallidas}")
    print(f"  Tasa de éxito       : {vueltas_completadas/vuelta*100:.1f}%")
    print(f"{'='*55}")


# ============================================================
# PUNTO DE ENTRADA
# ============================================================

if __name__ == "__main__":
    correr_curso(vueltas=5)