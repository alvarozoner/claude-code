# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## ganga-bot

The `ganga-bot/` directory contains a Python price-alert bot that polls Wallapop, Vinted, and Milanuncios for second-hand phone listings below configured price thresholds, then sends notifications via Telegram (or optionally email).

### Setup and running

```bash
cd ganga-bot
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
# Edit .env: set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID
```

Run the bot:

```bash
python main.py
```

To get your Telegram `chat_id` (after sending `/start` to your bot):

```bash
TELEGRAM_BOT_TOKEN=your_token python get_chat_id.py
```

### Credentials

`TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` must come from environment variables (loaded via `.env` or set in the shell). The `.env` file is gitignored. The `bot_gangas.py` file at the root of `ganga-bot/` is the original monolithic prototype — it hardcodes credentials and should not be used or extended; use `main.py` instead.

### Architecture

**`config.py`** — Single source of truth for what to search. `PHONES` is a list of dicts, each with `name`, `keywords` (list of search terms), and `max_price` (integer euros). Also contains Wallapop geolocation settings (`LATITUDE`, `LONGITUDE`, `MAX_DISTANCE_KM`), `MIN_CONDITION` (Wallapop condition filter), and `CHECK_INTERVAL_MINUTES`. Telegram credentials are read from environment here.

**`main.py`** — Orchestrator. Instantiates all three scrapers, then on each tick loops over every phone in `PHONES` and every scraper, calling `scraper.search(keywords, max_price)`. Deduplicates across runs using an in-memory `seen_ids: set[str]` (format: `"{ScraperName}_{item_id}"`). New results are passed to `notify()`.

**`scrapers/`** — Each scraper exposes the same interface: `name: str` and `search(keywords: list[str], max_price: int) -> list[dict]`. Each dict has keys `id`, `title`, `price`, `condition`, `platform`, `url`, `description`, `image`.

- **`wallapop.py`** — Hits the JSON REST API at `api.wallapop.com/api/v3/general/search`. Prices are in cents in the API (`max_sale_price = max_price * 100`). Filters by condition using `CONDITION_ORDER` index comparison. Supports geolocation filtering.
- **`vinted.py`** — Hits `vinted.es/api/v2/catalog/items` JSON API. Requires a session cookie obtained by first GETting the Vinted homepage. Condition filtering uses numeric `status_id` values mapped in `VINTED_CONDITIONS`.
- **`milanuncios.py`** — HTML scraper using BeautifulSoup. Parses `article.ma-AdCard` elements. No condition data available; returns `"unknown"` for condition.

**`notifier.py`** — `notify(deal)` dispatches to `_send_telegram()` and/or `_send_email()` based on `TELEGRAM_ENABLED`/`EMAIL_ENABLED` flags from `config.py`. Email is disabled by default; if enabling it, `EMAIL_PASSWORD` must be moved to an environment variable (it is currently a plain string in `config.py`).
