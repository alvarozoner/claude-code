"""
Bot de Gangas — Wallapop + Vinted + Milanuncios
Instalar dependencias: pip install requests beautifulsoup4 schedule
Ejecutar: python bot_gangas.py
"""

import requests
import schedule
import time
import urllib.parse
from datetime import datetime
from bs4 import BeautifulSoup

# ============================================================
#  CONFIGURACION
# ============================================================
TELEGRAM_TOKEN   = "TU_TOKEN_AQUI"   # pega tu token de @BotFather
TELEGRAM_CHAT_ID = "TU_CHAT_ID_AQUI" # pega tu chat_id

PHONES = [
    {"name": "Google Pixel 10 Pro", "keywords": ["pixel 10 pro"],               "max_price": 850},
    {"name": "Google Pixel 9 Pro",  "keywords": ["pixel 9 pro"],                "max_price": 600},
    {"name": "Google Pixel 8 Pro",  "keywords": ["pixel 8 pro"],                "max_price": 380},
    {"name": "Samsung Galaxy S25",  "keywords": ["galaxy s25", "s25 ultra"],    "max_price": 700},
    {"name": "Samsung Galaxy S24",  "keywords": ["galaxy s24", "s24 ultra"],    "max_price": 480},
]

CHECK_EVERY_MINUTES = 20
# ============================================================

seen_ids = set()

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "es-ES,es;q=0.9",
}


def send_telegram(deal):
    msg = (
        f"GANGA en {deal['platform']}\n"
        f"{deal['title']}\n"
        f"Precio: {deal['price']}EUR\n"
        f"{deal['url']}"
    )
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            json={"chat_id": TELEGRAM_CHAT_ID, "text": msg},
            timeout=10,
        )
    except Exception as e:
        print(f"  [Telegram] Error: {e}")


def search_wallapop(keyword, max_price):
    params = {
        "keywords": keyword,
        "latitude": 40.4168,
        "longitude": -3.7038,
        "distance": 0,
        "order_by": "price_low_to_high",
        "max_sale_price": max_price * 100,
        "min_sale_price": 100,
    }
    try:
        r = requests.get(
            "https://api.wallapop.com/api/v3/general/search",
            headers={**HEADERS, "Accept": "application/json", "Referer": "https://es.wallapop.com/"},
            params=params, timeout=15,
        )
        r.raise_for_status()
        items = (
            r.json()
             .get("data", {})
             .get("section", {})
             .get("payload", {})
             .get("items", [])
        )
        results = []
        for obj in items:
            c = obj.get("content", {})
            price = c.get("price", 0)
            if price > max_price:
                continue
            results.append({
                "id": f"wallapop_{c.get('id','')}",
                "title": c.get("title", ""),
                "price": price,
                "platform": "Wallapop",
                "url": f"https://es.wallapop.com/item/{c.get('web_slug', c.get('id',''))}",
            })
        return results
    except Exception as e:
        print(f"  [Wallapop] Error ({keyword}): {e}")
        return []


def search_vinted(keyword, max_price):
    session = requests.Session()
    session.headers.update(HEADERS)
    try:
        session.get("https://www.vinted.es", timeout=10)
    except Exception:
        pass
    params = {
        "search_text": keyword,
        "price_to": max_price,
        "order": "price_high_to_low",
        "per_page": 48,
        "country_id": "16",
    }
    try:
        r = session.get("https://www.vinted.es/api/v2/catalog/items", params=params, timeout=15)
        r.raise_for_status()
        results = []
        for obj in r.json().get("items", []):
            try:
                price = float(obj.get("price", 0))
            except (TypeError, ValueError):
                continue
            if price > max_price:
                continue
            results.append({
                "id": f"vinted_{obj.get('id','')}",
                "title": obj.get("title", ""),
                "price": price,
                "platform": "Vinted",
                "url": obj.get("url", ""),
            })
        return results
    except Exception as e:
        print(f"  [Vinted] Error ({keyword}): {e}")
        return []


def search_milanuncios(keyword, max_price):
    url = (
        "https://www.milanuncios.com/moviles-segunda-mano/?"
        + urllib.parse.urlencode({"titulo": keyword, "precio-hasta": max_price, "orden": "price_asc"})
    )
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        results = []
        for article in soup.select("article.ma-AdCard"):
            title_el = article.select_one(".ma-AdCard-title")
            price_el = article.select_one(".ma-AdPrice-value")
            link_el  = article.select_one("a.ma-AdCard-titleLink")
            if not (title_el and price_el and link_el):
                continue
            price_text = price_el.get_text(strip=True).replace(".", "").replace(",", ".").replace("€", "").strip()
            try:
                price = float(price_text)
            except ValueError:
                continue
            if price > max_price:
                continue
            href = link_el.get("href", "")
            full_url = f"https://www.milanuncios.com{href}" if href.startswith("/") else href
            item_id = href.strip("/").split("/")[-1]
            results.append({
                "id": f"mila_{item_id}",
                "title": title_el.get_text(strip=True),
                "price": price,
                "platform": "Milanuncios",
                "url": full_url,
            })
        return results
    except Exception as e:
        print(f"  [Milanuncios] Error ({keyword}): {e}")
        return []


def find_deals():
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Buscando gangas...")
    new_deals = []

    for phone in PHONES:
        for keyword in phone["keywords"]:
            for fn in [search_wallapop, search_vinted, search_milanuncios]:
                for item in fn(keyword, phone["max_price"]):
                    if item["id"] not in seen_ids:
                        seen_ids.add(item["id"])
                        new_deals.append(item)
                time.sleep(1)

    if new_deals:
        print(f"  {len(new_deals)} ganga(s) nuevas!")
        for deal in new_deals:
            print(f"  [{deal['platform']}] {deal['title']} — {deal['price']}EUR")
            print(f"  {deal['url']}")
            send_telegram(deal)
    else:
        print("  Sin novedades.")


if __name__ == "__main__":
    print("=" * 50)
    print("  BOT DE GANGAS INICIADO")
    print(f"  Busca cada {CHECK_EVERY_MINUTES} minutos")
    print("=" * 50)
    find_deals()
    schedule.every(CHECK_EVERY_MINUTES).minutes.do(find_deals)
    while True:
        schedule.run_pending()
        time.sleep(10)
