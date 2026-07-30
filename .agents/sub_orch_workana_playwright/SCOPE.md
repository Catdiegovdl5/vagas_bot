# Scope: Workana Playwright Refactoring

## Architecture
- `scrapers/workana.py`: Scrapes Workana using Playwright, returning listings matching search terms.
- `bot.py`: Coordinates hunts, invokes scrapers concurrently, filters results, and logs to `jobs.db`.
- `jobs.db`: Local SQLite database storing fetched jobs and candidacy status.

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| 1 | Exploration & Analysis | Analyze `scrapers/workana.py`, `bot.py` interaction, Playwright installation status, and `CO_OCCURRENCE_RULES`. | None | DONE |
| 2 | Implementation | Refactor `scrapers/workana.py` to use Playwright (headless Chromium), implement paginated scraping, apply Group A expansion terms, and ensure no event loop blocking. | M1 | IN_PROGRESS (see worker_workana_playwright) |
| 3 | Verification | Verify code correctness, build/test execution, zero resource leakage, clean audit, and integration with `jobs.db` and bot UI. | M2 | PLANNED |

## Interface Contracts
### `scrapers/workana.py` ↔ `bot.py`
- `async def scrape(keyword: str, max_pages: int = 3) -> List[Dict[str, Any]]`
- Output Format: List of dicts, each with:
  - `title`: str
  - `link`: str
  - `description`: str
  - `budget`: str
  - `platform`: "Workana"
