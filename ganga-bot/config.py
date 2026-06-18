PHONES = [
    {"name": "Google Pixel 10 Pro", "keywords": ["pixel 10 pro"], "max_price": 850},
    {"name": "Google Pixel 9 Pro",  "keywords": ["pixel 9 pro"],  "max_price": 600},
    {"name": "Google Pixel 8 Pro",  "keywords": ["pixel 8 pro"],  "max_price": 380},
    {"name": "Samsung Galaxy S25",  "keywords": ["galaxy s25", "s25 ultra", "s25+"], "max_price": 700},
    {"name": "Samsung Galaxy S24",  "keywords": ["galaxy s24", "s24 ultra", "s24+"], "max_price": 480},
]

# Ubicación para Wallapop (Madrid por defecto, 0 = toda España)
LATITUDE  = 40.4168
LONGITUDE = -3.7038
MAX_DISTANCE_KM = 0

# Intervalo entre búsquedas (minutos)
CHECK_INTERVAL_MINUTES = 20

# Condición mínima aceptable en Wallapop
# Opciones: "new", "as_good_as_new", "good", "fair", "has_given_it_all"
MIN_CONDITION = "good"

# --- Notificaciones por Telegram (opcional) ---
# 1. Crea un bot en @BotFather y pega el token
# 2. Escribe /start al bot y obtén tu chat_id con @userinfobot
import os

TELEGRAM_ENABLED   = True
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID   = os.environ.get("TELEGRAM_CHAT_ID", "")

# --- Notificaciones por email (opcional) ---
EMAIL_ENABLED  = False
EMAIL_FROM     = "tubot@gmail.com"
EMAIL_TO       = "tu@email.com"
EMAIL_PASSWORD = "tu_contraseña_de_app"  # Contraseña de aplicación Gmail
EMAIL_SMTP     = "smtp.gmail.com"
EMAIL_PORT     = 587
