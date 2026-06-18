import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

try:
    import requests as _requests
    _HAS_REQUESTS = True
except ImportError:
    _HAS_REQUESTS = False

from config import (
    TELEGRAM_ENABLED, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID,
    EMAIL_ENABLED, EMAIL_FROM, EMAIL_TO, EMAIL_PASSWORD, EMAIL_SMTP, EMAIL_PORT,
)


def notify(deal: dict):
    if TELEGRAM_ENABLED:
        _send_telegram(deal)
    if EMAIL_ENABLED:
        _send_email(deal)


def _send_telegram(deal: dict):
    if not _HAS_REQUESTS:
        return
    msg = (
        f"🔔 *GANGA DETECTADA* en {deal['platform']}\n"
        f"📱 *{deal['title']}*\n"
        f"💶 Precio: *{deal['price']}€*\n"
        f"🔗 [Ver anuncio]({deal['url']})"
    )
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        _requests.post(url, json={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": msg,
            "parse_mode": "Markdown",
            "disable_web_page_preview": False,
        }, timeout=10)
    except Exception as e:
        print(f"  [Telegram] Error al enviar: {e}")


def _send_email(deal: dict):
    subject = f"Ganga: {deal['title']} — {deal['price']}€ en {deal['platform']}"
    body = (
        f"Se ha encontrado una posible ganga:\n\n"
        f"Título: {deal['title']}\n"
        f"Precio: {deal['price']}€\n"
        f"Plataforma: {deal['platform']}\n"
        f"Link: {deal['url']}\n"
        f"Descripción: {deal.get('description', '')}\n"
    )
    msg = MIMEMultipart()
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))
    try:
        with smtplib.SMTP(EMAIL_SMTP, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_FROM, EMAIL_PASSWORD)
            server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
    except Exception as e:
        print(f"  [Email] Error al enviar: {e}")
