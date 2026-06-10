---
name: debug-scraper
description: "Diagnose and fix a flight scraper that returns 0 results or wrong data. Use when a site in scrapers/ stops returning flights, a CSS selector breaks, or a DOM change is suspected. Covers headful inspection, fallback-selector repair, and schema verification."
argument-hint: "Scraper name (e.g. Ixigo) and the route/date that fails"
---

# Debug a Flight Scraper

Scraper DOMs change often, so a scraper that worked yesterday may silently return `[]` today. This skill walks through isolating the failure and repairing selectors without breaking the [scraper contract](../../instructions/scrapers.instructions.md).

## When to Use

- A scraper prints "No results found" or "0 results" for a route that should have flights.
- Prices come back as `999999` (the missing-price sentinel) for every card.
- A site redesign is suspected after `undetected-chromedriver` updates.

## Procedure

1. **Reproduce in isolation.** Run only the failing scraper, not the full `main.py` flow:

   ```python
   from scrapers.ixigo_scraper import IxigoScraper
   print(IxigoScraper().scrape("DEL", "BOM", "2026-07-15"))
   ```

2. **Disable headless to watch the page.** Temporarily set `HEADLESS_MODE = False` in `config` (or comment the `--headless=new` path in [utils/helpers.py](../../utils/helpers.py)) so you can see captchas, popups, or empty result panes.

3. **Confirm the URL still resolves.** Each scraper reformats `date` differently (Ixigo `YYYYMMDD`, MakeMyTrip `MM/DD/YYYY`). Print the built URL and open it manually — a changed query-param contract is a common break.

4. **Diagnose: load vs. parse.** Determine which half failed:
   - **Container/timeout** → the `WebDriverWait` selector list no longer matches. Update the result-container selectors.
   - **Container found, 0 cards** → the per-card selector list is stale. Update `find_elements` card selectors.
   - **Cards found, fields empty** → individual field selectors in `_safe_find`/`_safe_extract` are stale.

5. **Repair selectors the resilient way.** Inspect the live DOM (DevTools) and **prepend** new selectors to the existing fallback list — keep the old ones as backups. Never replace the list with a single selector.

6. **Walk the [debugging checklist](./references/checklist.md)** to confirm anti-bot, `driver.quit()`, and schema rules still hold.

7. **Verify the schema.** Every returned dict must have `source, airline, price (int), price_raw, departure_time, arrival_time, duration, stops, rank`, with `clean_price()` applied. Re-run step 1 and confirm real prices (not `999999`) come back.

8. **Restore settings.** Revert `HEADLESS_MODE` and any debug prints before finishing.
