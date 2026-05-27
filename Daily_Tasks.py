import json
import random
from datetime import datetime

# 1. Cargar las listas y el histórico de estado
try:
    with open('listas.json', 'r', encoding='utf-8') as f:
        datos = json.load(f)
except FileNotFoundError:
    print("Error: No se encuentra el archivo listas.json")
    exit()

# Separamos las listas del estado del contador
diario = datos.get("diario", [])
salud = datos.get("salud", [])
ocio_habitual = datos.get("ocio_habitual", [])
ocio_nuevo = datos.get("ocio_nuevo", [])
caprichos = datos.get("caprichos", [])
tareas = datos.get("tareas", [])

dias_sin_capricho = datos.get("dias_sin_capricho", 0)
ultimo_gulp_fijo = datos.get("ultimo_gulp_fijo", 0)

# Obtener fecha actual para las lógicas temporales
hoy = datetime.now()
dia_semana = hoy.weekday() # 0 = Lunes, 2 = Miércoles, 6 = Domingo...

items_seleccionados = []

# ==========================================
# LÓGICA DE LAS LISTAS BÁSICAS
# ==========================================

# - Diario: Siempre todos
items_seleccionados.extend(diario)

# - Salud: 2 o 3 al azar
num_salud = min(random.randint(2, 3), len(salud))
items_seleccionados.extend(random.sample(salud, num_salud))

# Ocio: 1 nuevo y el resto habituales (Hasta 3 total)
    num_ocio_total = random.randint(1, 3)
    if datos["ocio_nuevo"]:
        items_seleccionados.append(random.choice(datos["ocio_nuevo"]))
        num_ocio_restante = num_ocio_total - 1
    else:
        num_ocio_restante = num_ocio_total

    if num_ocio_restante > 0 and datos["ocio_habitual"]:
        num_habitual = min(num_ocio_restante, len(datos["ocio_habitual"]))
        items_seleccionados.extend(random.sample(datos["ocio_habitual"], num_habitual))
        
# - Tareas: entre 1 y 3 al azar
num_tareas = min(random.randint(1, 3), len(tareas))
items_seleccionados.extend(random.sample(tareas, num_tareas))

# - Caprichos: 20% base. Si pasan 2 días sin salir, 100%.
if caprichos:
    probabilidad_capricho = 1.0 if dias_sin_capricho >= 2 else 0.20
    
    if random.random() < probabilidad_capricho:
        items_seleccionados.append(random.choice(caprichos))
        datos["dias_sin_capricho"] = 0  # Reseteamos contador
    else:
        datos["dias_sin_capricho"] += 1 # Sumamos un día sin capricho
else:
    datos["dias_sin_capricho"] = 0

# Mezclamos (shuffle) todos los ítems de las listas básicas
random.shuffle(items_seleccionados)

# ==========================================
# LÓGICA DE LAS VARIABLES ESPECIALES
# ==========================================

# - Max P: Número al azar entre 1 y 5
max_p = random.randint(1, 5)

# - Karaoke: SI miércoles (2) y domingos (6)
karaoke = "SI" if dia_semana in [2, 6] else "NO"

# - Gulp: SI cada 3 días. Resto, 50/50.
# Incrementamos el contador de días desde el último Gulp
dias_desde_ultimo_gulp = ultimo_gulp_fijo + 1

if dias_desde_ultimo_gulp >= 3:
    gulp = "SI"
    datos["ultimo_gulp_fijo"] = 0  # Reseteamos porque ya tocó por ciclo fijo
else:
    # No toca por ciclo, se decide al 50/50
    if random.random() < 0.5:
        gulp = "SI"
        datos["ultimo_gulp_fijo"] = 0  # <--- CORRECCIÓN: Al salir SI, reseteamos el ciclo
    else:
        gulp = "NO"
        datos["ultimo_gulp_fijo"] = dias_desde_ultimo_gulp  # Mantenemos el progreso

# Guardamos el estado actualizado en el JSON para el día siguiente
with open('listas.json', 'w', encoding='utf-8') as f:
    json.dump(datos, f, ensure_ascii=False, indent=2)

# ==========================================
# CONSTRUCCIÓN DEL OUTPUT (CHECKLIST)
# ==========================================

output = f"📋 **GESTIÓN DIARIA - {hoy.strftime('%d/%m/%Y')}**\n\n"

# Añadir las listas básicas mezcladas con formato de checklist
for item in items_seleccionados:
    output += f"[ ] {item}\n"

output += "\n" + "─" * 20 + "\n\n"
output += "⚙️ **VARIABLES ESPECIALES:**\n"
output += f"🔸 Max P: {max_p}\n"
output += f"🔸 Karaoke: {karaoke}\n"
output += f"🔸 Gulp: {gulp}\n"

# ==========================================
# ENVÍO A TELEGRAM (Sustituye el antiguo print)
# ==========================================
import requests

# Configura aquí tus datos reales
TELEGRAM_TOKEN = "8406001838:AAGwJqMT7iRSEjNQP_tue_SqurGWHJ_nul4"
TELEGRAM_CHAT_ID = "8013969980"

def enviar_a_telegram(texto):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": texto,
        "parse_mode": "Markdown"  # Permite que las negritas y emojis se vean bien
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("Mensaje enviado con éxito a Telegram.")
        else:
            print(f"Error al enviar: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error de conexión: {e}")

# Ejecutamos la función enviando el output generado
enviar_a_telegram(output)
