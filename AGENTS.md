# AGENTS.md

Guidance for AI coding agents working in **flight_rate_checker** — an interactive CLI that scrapes Indian domestic flight prices from multiple sites and uses an LLM to recommend the best deal. See [README.md](README.md).

## Architecture

Interactive CLI (`rich`) → run scrapers sequentially → aggregate flight dicts → LLM analysis → display + optional save.

- [main.py](main.py) — entry point. Prompts the user (`rich.Prompt`), orchestrates scraping/analysis, renders `rich` tables/panels, saves CSV + JSON. Run with `python main.py`.
- `scrapers/` — one class per site ([google_flights.py](scrapers/google_flights.py), [ixigo_scraper.py](scrapers/ixigo_scraper.py), [makemytrip.py](scrapers/makemytrip.py)). Selenium via `undetected-chromedriver`.
- [llm/analyzer.py](llm/analyzer.py) — `FlightAnalyzer`. Switches between OpenAI and Gemini via config; falls back to rule-based analysis on any error.
- [utils/helpers.py](utils/helpers.py) — `setup_driver`, `clean_price`, `validate_date`, `get_airport_code`, `random_delay`.

## Critical: missing `config.py`

Every module imports from a top-level `config` module that **does not exist in the repo** (also no `.env`). The app cannot run until it is created. When adding/using config, these names are expected:

- Scrapers + helpers: `WAIT_TIME`, `CHROME_OPTIONS` (list of Chrome flags), `HEADLESS_MODE` (bool), `AIRPORT_CODES` (dict `{"delhi": "DEL", ...}`).
- LLM: `LLM_PROVIDER` (`"openai"` | `"gemini"`), `OPENAI_API_KEY`, `GEMINI_API_KEY`, `LLM_MODEL_OPENAI`, `LLM_MODEL_GEMINI`.

Load secrets from `.env` via `python-dotenv`; never hardcode keys.

## Conventions

- **Scraper contract**: each class sets `self.source` (display name) and implements `scrape(from_city, to_city, date) -> list[dict]`. `from_city`/`to_city` are IATA codes (`DEL`); `date` is `YYYY-MM-DD` and each scraper reformats it (Ixigo `YYYYMMDD`, MakeMyTrip `MM/DD/YYYY`).
- **Flight dict schema**: `source, airline, price (int), price_raw, departure_time, arrival_time, duration, stops, rank`. Missing price = `999999` (sentinel for "N/A", filtered out on display). Keep new fields consistent with this shape.
- **Resilient extraction**: use the existing `_safe_extract` / `_safe_find` helpers with a *list of fallback CSS selectors* — site DOMs change often. Wrap per-card parsing in `try/except` and skip failures rather than aborting the scrape. Always `driver.quit()` in `finally`.
- **Anti-bot**: scrapers run sequentially (not parallel) to avoid IP blocking; use `time.sleep(random.uniform(...))` / `random_delay()`. `setup_driver()` already applies stealth flags and a random user agent.
- **Output**: all user-facing output goes through the shared `rich` `Console` with emoji + markup styling. Don't use bare `print()`.
- **Registering a scraper**: add the class to the `scrapers` list in `run_scrapers()` in [main.py](main.py).

## Setup & run

```pwsh
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt   # pinned versions
python main.py
```

Requires a local Chrome install (driver auto-managed by `undetected-chromedriver`). No test suite exists yet.
