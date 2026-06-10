# ✈️ flight_rate_checker

An interactive command-line tool that scrapes Indian domestic flight prices from
multiple booking sites and uses an LLM (OpenAI or Gemini) to recommend the best
deal. Results are rendered as rich tables/panels and can be saved to CSV + JSON.

> For AI-agent contribution guidance, conventions, and the scraper contract, see
> [AGENTS.md](AGENTS.md).

## Features

- 🔎 Scrapes **Google Flights**, **Ixigo**, and **MakeMyTrip** (one class per site).
- 🧭 Guided 7-step interactive input (source/destination, one-way/round-trip,
  dates, time-of-day, passengers, travel class, preferences) with a built-in
  Indian airport directory — see [user_input/input_handler.py](user_input/input_handler.py).
- 🤖 LLM analysis (best overall, cheapest, price insights, savings tips) that
  **falls back to rule-based analysis** when no API key/network is available.
- 🔁 Round-trip support with a combined cost summary.
- 🎯 Client-side filtering by departure time-frame, non-stop, budget, and airline.
- 💾 Saves outbound/return flights to CSV and the full result to JSON.
- 🕵️ Anti-bot scraping via `undetected-chromedriver` with stealth flags and
  randomized delays; scrapers run **sequentially** to reduce blocking.

## Architecture

```
collect_all_inputs()  →  run_scrapers()  →  filter/display  →  FlightAnalyzer  →  save
   (input_handler)        (scrapers/*)       (rich tables)      (llm/analyzer)    (CSV/JSON)
```

| Path                                                       | Responsibility                                        |
| ---------------------------------------------------------- | ----------------------------------------------------- |
| [main.py](main.py)                                         | Orchestration, filtering, `rich` display, saving      |
| [user_input/input_handler.py](user_input/input_handler.py) | Interactive prompts + airport directory               |
| [scrapers/](scrapers)                                      | One Selenium scraper class per site                   |
| [llm/analyzer.py](llm/analyzer.py)                         | OpenAI/Gemini analysis + rule-based fallback          |
| [utils/helpers.py](utils/helpers.py)                       | `setup_driver`, `clean_price`, date helpers           |
| `config.py`                                                | Settings + secrets loaded from `.env` (not committed) |

## Setup

Requires **Python 3.10+** and a local **Google Chrome** install (the driver is
auto-managed by `undetected-chromedriver`).

```pwsh
# 1. Create & activate a virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2. Install dependencies
pip install -r requirements.txt
```

### Configuration

The app loads settings from a top-level `config.py`, which in turn reads secrets
from a `.env` file (via `python-dotenv`). **Never commit `.env` or hardcode keys.**

`config.py` must define the names the code imports:

- Scrapers + helpers: `WAIT_TIME`, `CHROME_OPTIONS` (list of Chrome flags),
  `HEADLESS_MODE` (bool), `AIRPORT_CODES` (dict, e.g. `{"delhi": "DEL"}`).
- LLM: `LLM_PROVIDER` (`"openai"` | `"gemini"`), `OPENAI_API_KEY`,
  `GEMINI_API_KEY`, `LLM_MODEL_OPENAI`, `LLM_MODEL_GEMINI`.

> The LLM analyzer reads these defensively — missing LLM names fall back to safe
> defaults and the analyzer degrades to rule-based output, so the app still runs
> without an API key.

Example `.env`:

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...
LLM_MODEL_OPENAI=gpt-4o-mini
LLM_MODEL_GEMINI=gemini-1.5-flash
HEADLESS_MODE=true
```

## Usage

```pwsh
python main.py
```

Follow the interactive prompts. After scraping, the tool prints all flights, an
AI recommendation, and offers to save results as:

- `outbound_<SRC>_<DST>_<timestamp>.csv`
- `return_<DST>_<SRC>_<timestamp>.csv` (round-trip only)
- `flight_search_<SRC>_<DST>_<timestamp>.json`

## Known limitations & recommended improvements

- **Volatile selectors**: scraper CSS selectors break when sites redesign. Use
  the [`debug-scraper`](.github/skills/debug-scraper/SKILL.md) workflow to repair
  the fallback-selector lists.
- **Unused search params**: `passengers`, `travel_class`, and `time_frame` are
  collected but the scraper `scrape(from, to, date)` signature ignores them; the
  filters are applied client-side only. Passing them into the scrapers' URLs
  would yield more accurate fares.
- **Dependency pins**: `requirements.txt` now uses minimum (`>=`) versions so it
  installs on modern Python (the old exact pins failed to build on 3.12+/3.14).
  Consider a lock file (`pip-tools`/`uv`) for reproducible builds.
- **Error handling**: several bare `except:` clauses swallow errors; narrowing
  them would aid debugging.
- **No tests**: there is no automated test suite yet — unit tests for
  `clean_price`, `filter_flights`, and the analyzer fallback would be high value.

## License

See [LICENSE](LICENSE).

