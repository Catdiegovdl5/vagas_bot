# Changes Log - Milestone 2

Documenting the implementation of the fixes and the High-Precision Filtering Engine (HPFE).

## 1. Startup Exception Fix (`bot.py`)
- Wrapped `await bot.set_chat_menu_button()` in a `try/except` block inside the `main()` async function to prevent startup crashes when token or network issues occur.

## 2. AI Filter Restoration & Hard-Locks (`scrapers/ai_filter.py`)
- Restored `scrapers/ai_filter.py` to its original version to recover the Groq LLM integration.
- Defined and exported `API_KEYS` to support API key rotation.
- Handled hard-lock checks for:
  - Foreign currency filter (USD/Euro) detection.
  - Fluent English requirements specifically for junior level candidates.

## 3. High-Precision Filtering Engine (HPFE) (`bot.py` & `app.py`)
- Created `match_exact_word(text, word)` inside `bot.py` using proper regex boundary checks `(?<![a-z0-9])term(?![a-z0-9])` to avoid partial matching (e.g. JavaScript matching Java).
- Implemented `CO_OCCURRENCE_RULES` allowlists to support word-order variations and niche keywords (e.g., "Backend Python" matching "Desenvolvedor Python").
- Implemented `check_co_occurrence(text_norm, kw_norm)` with a fallback to significant words check.
- Integrated `is_job_relevant` inside `bot.py` to filter vacancies using the HPFE.
- Integrated HPFE filtering inside `app.py`'s `/api/trigger` endpoint so that web app triggers also filter jobs using `is_job_relevant` before database insertion.

## 4. SQLite Write Locks in Tests (`tests/test_tier*.py`)
- Wrapped all manual SQLite connections inside the test files (`tests/test_tier1.py`, `tests/test_tier2.py`, `tests/test_tier3.py`, `tests/test_tier4.py`) in `try/finally` blocks to guarantee `conn.close()` execution even on assertion or test failure.
