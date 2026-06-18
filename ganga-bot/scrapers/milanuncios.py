import requests
import time
from bs4 import BeautifulSoup
import urllib.parse

BASE_URL = "https://www.milanuncios.com/moviles-segunda-mano/"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9",
    "Referer": "https://www.milanuncios.com/",
}


class MilanunciosScraper:
    name = "Milanuncios"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)

    def search(self, keywords: list[str], max_price: int) -> list[dict]:
        results = []
        for keyword in keywords:
            items = self._query(keyword, max_price)
            results.extend(items)
            time.sleep(2)
        seen = set()
        unique = []
        for item in results:
            if item["id"] not in seen:
                seen.add(item["id"])
                unique.append(item)
        return unique

    def _query(self, keyword: str, max_price: int) -> list[dict]:
        params = {
            "titulo": keyword,
            "precio-hasta": max_price,
            "orden": "price_asc",
        }
        url = BASE_URL + "?" + urllib.parse.urlencode(params)
        try:
            resp = self.session.get(url, timeout=15)
            resp.raise_for_status()
        except Exception as e:
            raise RuntimeError(f"Milanuncios error: {e}")

        soup = BeautifulSoup(resp.text, "html.parser")
        items = []

        # Milanuncios uses article tags for listings
        for article in soup.select("article.ma-AdCard"):
            try:
                title_el = article.select_one(".ma-AdCard-title")
                price_el = article.select_one(".ma-AdPrice-value")
                link_el  = article.select_one("a.ma-AdCard-titleLink")
                img_el   = article.select_one("img.ma-AdCard-photo")
                desc_el  = article.select_one(".ma-AdCard-description")

                if not title_el or not price_el or not link_el:
                    continue

                title = title_el.get_text(strip=True)
                href  = link_el.get("href", "")
                url   = f"https://www.milanuncios.com{href}" if href.startswith("/") else href
                item_id = href.strip("/").split("/")[-1]

                price_text = price_el.get_text(strip=True).replace(".", "").replace(",", ".").replace("€", "").strip()
                try:
                    price = float(price_text)
                except ValueError:
                    continue

                if price > max_price:
                    continue

                image = img_el.get("src", "") if img_el else ""
                description = desc_el.get_text(strip=True) if desc_el else ""

                items.append({
                    "id": item_id or url,
                    "title": title,
                    "price": price,
                    "condition": "unknown",
                    "platform": self.name,
                    "url": url,
                    "description": description,
                    "image": image,
                })
            except Exception:
                continue

        return items
