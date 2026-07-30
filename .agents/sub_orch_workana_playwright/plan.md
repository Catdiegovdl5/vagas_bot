# Refactoring Plan: Workana Playwright Integration

## Milestone 1: Exploration & Analysis (DONE)
- [x] Analyze `scrapers/workana.py` and its limitations (Cloudflare, JS-rendering, Vue bootstrap tag changes).
- [x] Analyze `bot.py` scraper invocation and keyword expansion pipeline.
- [x] Check environment Playwright availability and test mocks.

## Milestone 2: Implementation (IN_PROGRESS)
- [ ] Add `playwright` and `playwright-stealth` to `requirements.txt`.
- [ ] Refactor `scrapers/workana.py` to use `playwright.async_api` and expose `async def scrape(...)`.
- [ ] Implement robust card selector parsing (`.job-item`, `.project-item`, `.project-card`) and field extraction.
- [ ] Fix search scope expansion gap using `MAPPED_KEYS` to align `search_mapping` with `CO_OCCURRENCE_RULES` keys.
- [ ] Modify `bot.py` to inspect if `module.scrape` is a coroutine function and await it directly.
- [ ] Refactor `tests/test_workana_settings.py` unit test to support async scrape execution and mock Playwright async calls.

## Milestone 3: Verification
- [ ] Run `pytest tests/test_workana_settings.py` and ensure they pass.
- [ ] Perform comprehensive test suite runs via `run_tests.py` or `pytest`.
- [ ] Spawn Reviewers, Challengers, and Forensic Auditor to gate completion.
