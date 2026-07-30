# Project: vagas_bot Expansion — New Profession Taxonomy & Scraper Macro-Searches

## Architecture
- **Data Flow**:
  - Frontend (`static/index.html`): Mega-menu drawers for broad categories (Operações Físicas, Logística, Administrativo, Criativos, Inteligência de Vendas, Engenharia de Dados, etc.). Sends macro-search or category search requests to backend.
  - Backend (`app.py` & `bot.py`):
    - Macro-searches execute queries for broad domain keywords (e.g., "Indústria", "Logística", "Administrativo", "Vendas", "Dados", "Design").
    - Local classification & filtering via `CO_OCCURRENCE_RULES` and `is_job_relevant` in `bot.py` matches specific sub-professions (e.g. "Pintor Industrial", "Almoxarife", "Assistente de Logística").
  - Scrapers (`scrapers/*.py`): Receive macro-search terms, fetch job postings, and return normalized lists.
  - Database (`database.py`): Persists jobs with assigned professions, levels, locations, and AI/rule scores.

## Code Layout
- `static/index.html`: Web dashboard UI, mega-menu drawers, JS constants for profession mappings.
- `bot.py`: Telegram Bot logic, `CO_OCCURRENCE_RULES`, `blacklist`, `is_job_relevant()` filtering logic, and sub-profession classification.
- `app.py`: FastAPI server, `/api/trigger`, `/api/search`, seed search loops, periodic background hunt loops.
- `scrapers/`: Individual platform scrapers (`linkedin.py`, `gupy.py`, `catho.py`, `infojobs.py`, `workana.py`, etc.).

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| 1 | UI Taxonomy Update | Update `static/index.html` mega-menu drawers and JS profession mapping constants | None | DONE |
| 2 | Scraper Config & Macro-Searches | Update `bot.py`, `app.py`, and scraper keyword mapping (`CO_OCCURRENCE_RULES`, macro-search terms, local filtering) | M1 | DONE |
| 3 | Final Verification & Integration Gate | Pass `py_compile`, unit/filter test suite, Reviewers, Challengers, and Forensic Audit | M1, M2 | DONE |

## Interface Contracts
### `static/index.html` ↔ `app.py`
- Category/Drawer selection triggers `/api/search` or `/api/trigger` with macro keyword or category name.
- Profession filter dropdowns map category IDs to human-readable names and sub-profession lists.

### `bot.py` (`is_job_relevant`) ↔ `scrapers/*`
- Scrapers accept broad macro-search keywords (e.g., "Indústria", "Logística", "Dados").
- `is_job_relevant(job, keyword, settings)` filters and classifies jobs for specific sub-professions using `CO_OCCURRENCE_RULES` and `blacklist`.
