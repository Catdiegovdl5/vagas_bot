# Scope: Workana Pagination and Language Shield Toggle

## Architecture
- **Language Shield Toggle**:
  - The Telegram bot configuration menu must offer a button to toggle "🛡️ Escudo PT-BR: ON/OFF".
  - Toggle state must be persistent (either in SQLite `jobs.db` or config file/state) and checkable during the filtering process.
  - If language shield is OFF, `langdetect` checks in `scrapers/ai_filter.py` or `bot.py` are bypassed, allowing English/Spanish vacancies.
- **Workana Deep Search (Pagination)**:
  - `scrapers/workana.py` must be enhanced to accept/handle pages or run requests for multiple pages.
  - Rate limiting / block handling: pagination requests should have sensible delays to avoid HTTP 429.
- **Already-Applied Check**:
  - Keep track of applied jobs using database state (e.g. SQLite tables `jobs` / `applied`).
  - Workana projects that the user has already applied to must be highlighted with a Telegram inline button showing "✅ Já me candidatei".
  - Prevent duplicate applications when doing pagination/deep searching.

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| 1 | Test Specifications & Setup | Design E2E/Unit test cases covering R1, R2, and R3 | none | DONE |
| 2 | Language Shield Toggle Implementation | Add menu button, save state, and bypass `langdetect` logic if OFF | M1 | DONE |
| 3 | Workana Pagination Implementation | Implement page loop, delay handling, and return combined results | M1 | DONE |
| 4 | Already-Applied Status Integration | Database status check optimization, UI button update, duplication prevention | M2, M3 | DONE |
| 5 | final_milestone | Verification (Run E2E/unit tests, challenger validation, and audit) | M1, M2, M3, M4 | DONE |

## Interface Contracts
### Language Shield Configuration
- Settings dictionary (or DB table) holds `escudo_pt_br` (boolean).
- If `escudo_pt_br` is `False`, the bot/filter accepts English/Spanish jobs.

### Workana Scraper
- Function `scrape(keyword, pages=3)` or similar signature.
- Must return list of job dicts matching the schema: `title`, `company`, `budget`, `link`, `platform`, `requirements`.
