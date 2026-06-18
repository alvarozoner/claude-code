"""
Bot de gangas para Wallapop, Vinted y Milanuncios.
Busca los teléfonos configurados en config.py y avisa cuando
encuentra anuncios por debajo del precio máximo definido.
"""

import time
import schedule
from datetime import datetime

from config import PHONES, CHECK_INTERVAL_MINUTES, LATITUDE, LONGITUDE, MAX_DISTANCE_KM, MIN_CONDITION
from scrapers.wallapop import WallapopScraper
from scrapers.vinted import VintedScraper
from scrapers.milanuncios import MilanunciosScraper
from notifier import notify

seen_ids: set[str] = set()


def print_deal(deal: dict):
    sep = "=" * 55
    print(f"\n{sep}")
    print(f"  GANGA DETECTADA en {deal['platform']}")
    print(f"  {deal['title']}")
    print(f"  Precio: {deal['price']}€")
    print(f"  Link:   {deal['url']}")
    if deal.get("description"):
        print(f"  Desc:   {deal['description'][:120]}")
    print(sep)


def find_deals():
    now = datetime.now().strftime("%H:%M:%S")
    print(f"\n[{now}] Iniciando búsqueda en las 3 plataformas...")

    scrapers = [
        WallapopScraper(latitude=LATITUDE, longitude=LONGITUDE, distance=MAX_DISTANCE_KM, min_condition=MIN_CONDITION),
        VintedScraper(min_condition=MIN_CONDITION),
        MilanunciosScraper(),
    ]

    new_deals = []

    for phone in PHONES:
        keywords  = phone["keywords"]
        max_price = phone["max_price"]
        label     = phone["name"]

        print(f"  Buscando: {label} (máx. {max_price}€)")

        for scraper in scrapers:
            try:
                items = scraper.search(keywords, max_price)
                for item in items:
                    uid = f"{scraper.name}_{item['id']}"
                    if uid not in seen_ids:
                        seen_ids.add(uid)
                        item["search_name"] = label
                        new_deals.append(item)
            except Exception as e:
                print(f"    [ERROR] {scraper.name}: {e}")

    if new_deals:
        print(f"\n  {len(new_deals)} nueva(s) ganga(s) encontrada(s):")
        for deal in new_deals:
            print_deal(deal)
            notify(deal)
    else:
        print("  Sin novedades desde la última comprobación.")

    next_check = datetime.now().strftime("%H:%M:%S")
    print(f"\n  Próxima búsqueda en {CHECK_INTERVAL_MINUTES} minutos. Esperando...")


def main():
    print("=" * 55)
    print("  BOT DE GANGAS — Wallapop / Vinted / Milanuncios")
    print("=" * 55)
    print(f"  Teléfonos buscados:")
    for p in PHONES:
        print(f"    • {p['name']} → máx. {p['max_price']}€")
    print(f"  Intervalo: cada {CHECK_INTERVAL_MINUTES} minutos")
    print("=" * 55)

    # Primera ejecución inmediata
    find_deals()

    schedule.every(CHECK_INTERVAL_MINUTES).minutes.do(find_deals)

    while True:
        schedule.run_pending()
        time.sleep(10)


if __name__ == "__main__":
    main()
