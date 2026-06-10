---
description: "Use when writing or editing flight scraper classes in scrapers/. Covers the scrape() contract, flight-dict schema, resilient extraction, and anti-bot rules."
applyTo: "scrapers/**/*.py"
---

# Scraper Guidelines

See [AGENTS.md](../../AGENTS.md) for the full architecture.

## Class contract

- Set `self.source` (display name) and `self.base_url` in `__init__`.
- Implement `scrape(from_city, to_city, date) -> list[dict]`.
- `from_city`/`to_city` are IATA codes (`DEL`); `date` arrives as `YYYY-MM-DD`. Reformat it per site (Ixigo `YYYYMMDD`, MakeMyTrip `MM/DD/YYYY`) and note the format in the docstring.
- After adding a class, register it in the `scrapers` list in `run_scrapers()` in [main.py](../../main.py).

## Flight dict schema

Return dicts with exactly these keys: `source, airline, price (int), price_raw, departure_time, arrival_time, duration, stops, rank`.

- Convert price with `clean_price()` from [utils/helpers.py](../../utils/helpers.py); missing price = `999999` (the "N/A" sentinel, filtered out on display).

## Resilient extraction

- Extract every field via a `_safe_find`/`_safe_extract` helper that takes a **list of fallback CSS selectors** — site DOMs change often.
- Wrap per-card parsing in `try/except` and `continue` on failure; never abort the whole scrape for one bad card.
- Limit to the first ~10 cards.

## Driver & anti-bot

- Build the driver with `setup_driver()`; always `driver.quit()` in a `finally` block.
- Use `WebDriverWait` with `WAIT_TIME` from `config`, plus `time.sleep(random.uniform(...))` / `random_delay()`.
- Scrapers run sequentially (never parallel) to avoid IP blocking.

## Output

All user-facing output goes through the shared `rich` `Console` with emoji/markup styling — never bare `print()`.
