---
description: "Scaffold the missing config.py and .env.example with all names the app imports"
argument-hint: "Optional: provider (openai|gemini) and any extra airport codes"
agent: "agent"
---

Create the top-level `config.py` and a matching `.env.example` that the codebase imports but does not yet contain. See [AGENTS.md](../../AGENTS.md) for the authoritative list of expected names.

Requirements:

- `config.py` loads secrets from `.env` via `python-dotenv` (`load_dotenv()`); **never hardcode API keys**.
- Define every name the modules import, with sensible defaults:
  - Scrapers + helpers: `WAIT_TIME` (int seconds), `CHROME_OPTIONS` (list of Chrome flags), `HEADLESS_MODE` (bool), `AIRPORT_CODES` (dict of lowercase city → IATA code, e.g. `{"delhi": "DEL", "mumbai": "BOM"}`).
  - LLM: `LLM_PROVIDER` (`"openai"` | `"gemini"`), `OPENAI_API_KEY`, `GEMINI_API_KEY`, `LLM_MODEL_OPENAI`, `LLM_MODEL_GEMINI`.
- Read API keys, `LLM_PROVIDER`, and `HEADLESS_MODE` from environment variables with `os.getenv`; keep `AIRPORT_CODES` and `CHROME_OPTIONS` as literals in `config.py`.
- Include the major Indian metro airports in `AIRPORT_CODES` (Delhi, Mumbai, Bangalore, Chennai, Kolkata, Hyderabad, Goa, Pune, Ahmedabad, Kochi) plus any extras the user requested.
- `CHROME_OPTIONS` should be stealth/anti-bot flags compatible with `undetected-chromedriver` (e.g. `--no-sandbox`, `--disable-blink-features=AutomationControlled`, `--disable-dev-shm-usage`). Do not add `--headless` here — that is handled by `HEADLESS_MODE` in [utils/helpers.py](../../utils/helpers.py).
- `.env.example` lists every secret/config env var with placeholder values and a short comment, but no real keys.

After creating the files, verify the imports resolve by checking each `from config import ...` statement across `main.py`, `scrapers/`, `llm/analyzer.py`, and `utils/helpers.py`.
