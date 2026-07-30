# Technical Context: Workana Scraper Refactoring

## Active Code Paths
- Scraper: `scrapers/workana.py`
- Main Orchestrator: `bot.py`
- Unit Tests: `tests/test_workana_settings.py`
- Global Mocks: `tests/conftest.py`

## Current Environment State
- Playwright Chromium binaries are cached in user profile `C:\Users\99196\AppData\Local\ms-playwright`.
- `playwright` python binding is NOT yet listed in `requirements.txt`.
- Scraper currently relies on `curl_cffi` or `requests` GET calls, which fail on Cloudflare verification page.

## Key Discoveries
- Naming gap: `search_mapping` in `bot.py` translates `"Especialista em IA"` -> `"Especialista IA"`. But `CO_OCCURRENCE_RULES` expects `"especialista em ia"`. Normalization in `workana.py` searches for `"especialista ia"`, which misses the rules and skips Group A expansion.
- Async transition: `bot.py` currently runs all scrapers in threads via `asyncio.to_thread`. Converting `workana.scrape` to `async def` requires `bot.py` to check for coroutine callable and await it directly.
