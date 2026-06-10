---
description: "Use when editing the LLM flight analyzer. Covers provider switching, JSON-only responses, and the mandatory rule-based fallback."
applyTo: "llm/**/*.py"
---

# LLM Analyzer Guidelines

See [AGENTS.md](../../AGENTS.md) for the full architecture.

## Provider switching

- `FlightAnalyzer` selects the backend from `LLM_PROVIDER` (`"openai"` | `"gemini"`) in `config`.
- Read models from `LLM_MODEL_OPENAI` / `LLM_MODEL_GEMINI` and keys from `OPENAI_API_KEY` / `GEMINI_API_KEY`. Never hardcode keys.
- Import the provider SDK lazily inside the setup/query branch (only when that provider is active).

## JSON contract

- Prompts must request the exact JSON shape consumed by `display_ai_recommendation()` in [main.py](../../main.py): `best_overall, cheapest, best_value, price_insights, savings_tips, booking_advice, overall_summary`.
- OpenAI: use `response_format={"type": "json_object"}`.
- Gemini: strip ` ```json ` / ` ``` ` fences and fall back to a `re.search(r'\{.*\}', ..., re.DOTALL)` extraction before `json.loads`.

## Fallback is mandatory

- Any LLM/setup error must degrade to `_fallback_analysis()` (rule-based), never raise to the caller.
- `_fallback_analysis()` must return the same dict shape so the display layer keeps working.

## Output

Status/errors go through the shared `rich` `Console`, not bare `print()`.
