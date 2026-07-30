# Orchestration Plan — Scraper Category Refactoring & Test Verification

## Project Goals
1. Refactor scrapers in `scrapers/` to natively support the 6 new categories:
   - Operações Físicas
   - Logística
   - Administrativo
   - Criativos de Performance
   - Inteligência de Vendas
   - Engenharia de IA/Dados
2. Ensure downstream payload format compatibility (proper `profession` / `category` fields matching DB schema).
3. Adapt/create tests in `tests/` verifying at least 3 updated scrapers against the new category queries.
4. Pass independent Reviewer, Challenger stress-test, and Forensic Integrity Audit.

## Phased Strategy

### Phase 1: Discovery & Architecture Exploration
- Dispatch 3 Explorers:
  - **Explorer 1 (`teamwork_preview_explorer_scrapers_1`)**: Inspect `scrapers/` directory to catalog all scrapers, their query methods, API endpoints, parameter structures, and how search keywords are passed.
  - **Explorer 2 (`teamwork_preview_explorer_scrapers_2`)**: Inspect backend job payload models, database schemas (`database.py`, `models.py`, `bot.py`, `app.py`), and verify expected payload fields (`profession`, `category`, `source`, etc.).
  - **Explorer 3 (`teamwork_preview_explorer_scrapers_3`)**: Inspect `tests/` folder to inventory existing scraper test scripts, fixtures, mock mechanisms, and execution frameworks.

### Phase 2: Refactoring & Implementation
- Dispatch Worker(s):
  - Refactor at least 3 (or all major) scrapers in `scrapers/` to inject term sets for the 6 new categories directly into native platform search queries / parameters.
  - Ensure payload formatting sets `profession`/`category` correctly.
  - Adapt/create unit & integration tests under `tests/` validating at least 3 scrapers with new category queries.

### Phase 3: Review, Stress Verification & Forensic Audit
- Dispatch Reviewers & Challengers to inspect code and run empirical stress tests.
- Dispatch `teamwork_preview_auditor` for Forensic Integrity verification (CLEAN verdict required).
