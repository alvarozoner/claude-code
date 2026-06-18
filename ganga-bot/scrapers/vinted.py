import requests
import time

BASE_URL = "https://www.vinted.es/api/v2/catalog/items"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
    "Accept-Language": "es-ES,es;q=0.9",
}

# Vinted condition IDs: 6=Nuevo con etiquetas, 1=Muy buen estado, 2=Buen estado, 3=Satisfactorio
VINTED_CONDITIONS = {
    "new": [6],
    "as_good_as_new": [6, 1],
    "good": [6, 1, 2],
    "fair": [6, 1, 2, 3],
    "has_given_it_all": [6, 1, 2, 3],
}


class VintedScraper:
    name = "Vinted"

    def __init__(self, min_condition="good"):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self._get_session_cookie()
        self.allowed_conditions = VINTED_CONDITIONS.get(min_condition, [6, 1, 2])

    def _get_session_cookie(self):
        """Vinted requires a session cookie obtained from the main page."""
        try:
            self.session.get("https://www.vinted.es", timeout=10)
        except Exception:
            pass

    def search(self, keywords: list[str], max_price: int) -> list[dict]:
        results = []
        for keyword in keywords:
            items = self._query(keyword, max_price)
            results.extend(items)
            time.sleep(1.5)
        seen = set()
        unique = []
        for item in results:
            if item["id"] not in seen:
                seen.add(item["id"])
                unique.append(item)
        return unique

    def _query(self, keyword: str, max_price: int) -> list[dict]:
        params = {
            "search_text": keyword,
            "price_to": max_price,
            "order": "price_high_to_low",  # reversed so we get all under max
            "per_page": 96,
            "country_id": "16",  # Spain
        }
        try:
            resp = self.session.get(BASE_URL, params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            raise RuntimeError(f"Vinted API error: {e}")

        items = []
        for obj in data.get("items", []):
            condition_id = obj.get("status_id")
            if self.allowed_conditions and condition_id not in self.allowed_conditions:
                continue

            price_raw = obj.get("price", "0")
            try:
                price = float(price_raw)
            except (TypeError, ValueError):
                price = 0.0

            if price > max_price:
                continue

            item_id = str(obj.get("id", ""))
            title = obj.get("title", "Sin título")
            url = obj.get("url", f"https://www.vinted.es/items/{item_id}")
            image_url = obj.get("photo", {}).get("url", "")

            items.append({
                "id": item_id,
                "title": title,
                "price": price,
                "condition": str(condition_id),
                "platform": self.name,
                "url": url,
                "description": obj.get("description", ""),
                "image": image_url,
            })

        return items
