---
description: "Scaffold a new flight scraper class following the project's scraper contract"
argument-hint: "Site name and search URL (e.g. Cleartrip https://www.cleartrip.com/flights/...)"
agent: "agent"
---

Create a new scraper class in `scrapers/` for the site the user names, following the existing pattern in [scrapers/ixigo_scraper.py](../../scrapers/ixigo_scraper.py) and [scrapers/google_flights.py](../../scrapers/google_flights.py). See [AGENTS.md](../../AGENTS.md) for the full contract.

Requirements:

- Class sets `self.source` (display name) and `self.base_url`, and implements `scrape(from_city, to_city, date) -> list[dict]`.
- `from_city`/`to_city` are IATA codes; `date` arrives as `YYYY-MM-DD` — reformat it to whatever the target site's URL expects and document the format in the method docstring.
- Build the driver with `setup_driver()` from [utils/helpers.py](../../utils/helpers.py); always call `driver.quit()` in a `finally` block.
- Add `time.sleep(random.uniform(...))` waits and use `WebDriverWait` with `WAIT_TIME` from config. Scrapers must remain resilient: wrap per-card parsing in `try/except` and skip failures instead of aborting.
- Extract fields with a `_safe_find`/`_safe_extract` helper that accepts a **list of fallback CSS selectors** (site DOMs change often).
- Return dicts matching the schema exactly: `source, airline, price (int via clean_price), price_raw, departure_time, arrival_time, duration, stops, rank`. Use `999999` as the sentinel for a missing price.
- Limit results to the first ~10 cards.
- All console output goes through the shared `rich` `Console` with the existing emoji/markup style — no bare `print()`.

After creating the class, register it by adding it to the `scrapers` list in `run_scrapers()` in [main.py](../../main.py), and add its import alongside the other scraper imports.
