"""
Ejecuta este script para obtener tu chat_id de Telegram.
Pasos:
  1. Abre Telegram y escribe /start a @misgangas_bot
  2. Ejecuta: python get_chat_id.py
"""

import os
import requests

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
if not TOKEN:
    print("Falta TELEGRAM_BOT_TOKEN. Ejecútalo así:")
    print("  Windows: set TELEGRAM_BOT_TOKEN=tu_token && python get_chat_id.py")
    print("  Linux/Mac: TELEGRAM_BOT_TOKEN=tu_token python get_chat_id.py")
    exit(1)

url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
resp = requests.get(url, timeout=10)
data = resp.json()

if not data.get("ok"):
    print("Error al conectar con el bot:", data)
    exit(1)

results = data.get("result", [])
if not results:
    print("No hay mensajes. Abre Telegram, busca @misgangas_bot y escribe /start. Luego vuelve a ejecutar este script.")
    exit(0)

for update in results:
    msg = update.get("message", {})
    chat = msg.get("chat", {})
    chat_id = chat.get("id")
    name = chat.get("first_name", "") + " " + chat.get("last_name", "")
    print(f"Chat ID encontrado: {chat_id}  (usuario: {name.strip()})")
    print(f"\nPega este número en config.py como TELEGRAM_CHAT_ID = \"{chat_id}\"")
    break
