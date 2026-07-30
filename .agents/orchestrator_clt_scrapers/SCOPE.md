# Scope: CLT Scrapers Implementation and Integration

## Architecture
- **Data Flow**:
  - Main Telegram bot (`bot.py`) receives a query and calls the scrapers.
  - Selected CLT scrapers (among Gupy, Catho, InfoJobs, and Vagas.com.br) will run asynchronously inside `scrapers/` to fetch jobs.
  - The scrapers return lists of job dictionaries.
  - The bot filters jobs using `is_job_relevant`.
  - Filtered jobs are stored in the SQLite database (`jobs.db`).
- **Code Layout**:
  - `bot.py`: Main bot code to integrate and trigger the scrapers.
  - `scrapers/`: Contains scraper modules (e.g., `gupy.py`, `catho.py`, `infojobs.py`, `vagas_com.py`).
  - `test_clt_scrapers.py`: Independent test script to invoke the new/updated CLT scrapers and verify their format and functionality.

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| 1 | Platform Evaluation & Code Review | Analyze existing scrapers, bot.py, and how job relevance filtering is done. Evaluate Gupy, Catho, InfoJobs, and Vagas.com.br. | none | DONE |
| 2 | Scraper Implementation (Async) | Implement/refactor selected CLT scrapers inside `scrapers/` to match `async def scrape(keyword, level="Todos", max_pages=...)` | M1 | DONE |
| 3 | Bot Integration & Filtering | Integrate CLT scrapers into `bot.py`'s hunting loop. Ensure they are filtered using `bot.is_job_relevant`. | M2 | DONE |
| 4 | Verification & Testing | Create a test script (`test_clt_scrapers_live.py`) and verify that all scrapers work, return correct structure, and do not break Workana. | M3 | DONE |

## Interface Contracts
### `scrapers/*` ↔ `bot.py`
- Function signature: `async def scrape(keyword: str, level: str = "Todos", max_pages: int = 1) -> List[dict]`
- Return format: A list of dictionaries representing jobs:
  ```python
  {
      "platform": str,      # e.g., "Gupy"
      "title": str,         # Job title
      "company": str,       # Company name
      "budget": str,        # "A Combinar" or salary/budget details
      "link": str,          # URL to the job listing
      "job_type": str,      # "CLT" (as these are CLT scrapers)
      "profession": str,   # keyword/profession
      "level": str,         # Seniority level
      "requirements": str   # Full vacancy text / description (should be detailed)
  }
  ```
- Errors: Catch and log inside the scrapers, returning `[]` on failure instead of raising unhandled exceptions.
