# Scraper Debugging Checklist

Verify each item after repairing a scraper. See the [scraper instructions](../../../instructions/scrapers.instructions.md) for the authoritative rules.

## Selectors
- [ ] New selectors were **prepended** to the existing fallback list, not replacing it.
- [ ] Result-container, per-card, and per-field selector lists were each checked.
- [ ] Per-card parsing is wrapped in `try/except` with `continue` on failure.

## Schema
- [ ] Each dict has all keys: `source, airline, price, price_raw, departure_time, arrival_time, duration, stops, rank`.
- [ ] `price` is an `int` produced by `clean_price()`; missing price is `999999`.
- [ ] Results are limited to the first ~10 cards.

## Driver & anti-bot
- [ ] Driver is built with `setup_driver()`.
- [ ] `driver.quit()` runs in a `finally` block on every path.
- [ ] `WebDriverWait` uses `WAIT_TIME` from `config`.
- [ ] Random `time.sleep(random.uniform(...))` / `random_delay()` waits are present.

## Output & cleanup
- [ ] All output goes through the shared `rich` `Console` (no bare `print()`).
- [ ] `HEADLESS_MODE` restored to its original value.
- [ ] Temporary debug prints / hardcoded routes removed.

## Common root causes
- Site changed query-param names or date format in the URL.
- Cloudflare/captcha interstitial — needs longer waits or a fresh user agent.
- Popup/modal covering results (MakeMyTrip) — close it before scraping.
- `undetected-chromedriver` / Chrome version mismatch — let `version_main=None` auto-detect.
