import requests
import time

BASE_URL = "https://api.wallapop.com/api/v3/general/search"

CONDITION_ORDER = ["new", "as_good_as_new", "good", "fair", "has_given_it_all"]

HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "es-ES,es;q=0.9",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Referer": "https://es.wallapop.com/",
    "Origin": "https://es.wallapop.com",
}


class WallapopScraper:
    name = "Wallapop"

    def __init__(self, latitude=40.4168, longitude=-3.7038, distance=0, min_condition="good"):
        self.latitude = latitude
        self.longitude = longitude
        self.distance = distance
        self.min_condition_idx = CONDITION_ORDER.index(min_condition) if min_condition in CONDITION_ORDER else 4

    def search(self, keywords: list[str], max_price: int) -> list[dict]:
        results = []
        for keyword in keywords:
            items = self._query(keyword, max_price)
            results.extend(items)
            time.sleep(1)
        # Deduplicate by item id
        seen = set()
        unique = []
        for item in results:
            if item["id"] not in seen:
                seen.add(item["id"])
                unique.append(item)
        return unique

    def _query(self, keyword: str, max_price: int) -> list[dict]:
        params = {
            "keywords": keyword,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "distance": self.distance,
            "order_by": "price_low_to_high",
            "max_sale_price": max_price * 100,  # Wallapop uses cents
            "min_sale_price": 100,
            "filters_source": "search_box",
        }
        try:
            resp = requests.get(BASE_URL, headers=HEADERS, params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            raise RuntimeError(f"Wallapop API error: {e}")

        items = []
        # Navigate the response structure
        search_objects = (
            data.get("data", {})
                .get("section", {})
                .get("payload", {})
                .get("items", [])
        )
        for obj in search_objects:
            content = obj.get("content", {})
            condition = content.get("condition", "")
            condition_idx = CONDITION_ORDER.index(condition) if condition in CONDITION_ORDER else 99

            if condition_idx > self.min_condition_idx:
                continue

            price = content.get("price", 0)
            if price > max_price:
                continue

            item_id = str(content.get("id", ""))
            title = content.get("title", "Sin título")
            url = f"https://es.wallapop.com/item/{content.get('web_slug', item_id)}"
            description = content.get("description", "")
            images = content.get("images", [])
            image_url = images[0].get("medium", "") if images else ""

            items.append({
                "id": item_id,
                "title": title,
                "price": price,
                "condition": condition,
                "platform": self.name,
                "url": url,
                "description": description,
                "image": image_url,
            })

        return items
