# BRIEFING — 2026-07-29T11:30:00Z

## Mission
Refactor scrapers in `scrapers/` and category dispatch in `bot.py` to natively support the 6 new profession categories with accurate term injection, payload formatting (`profession` and `category`), test coverage, and passing tests via `python run_tests.py`.

## 🔒 My Identity
- Archetype: implementer / qa / specialist
- Roles: implementer, qa, specialist
- Working directory: C:\Users\99196\OneDrive\Documentos\vagas_bot\.agents\teamwork_preview_worker_scrapers
- Original parent: f250d8ce-e5a1-428d-b29d-c9ab8eeb5381
- Milestone: 6 New Profession Categories Scraper Support

## 🔒 Key Constraints
- Refactor scrapers in `scrapers/` and `bot.py` (`MAGIC_CATEGORIES`, `SEARCH_MAPPING`, `CO_OCCURRENCE_RULES`, `BLACKLIST_PROFILES`, `vagas_com_mapping`, etc.) for 6 categories:
  1. Operações Físicas
  2. Logística
  3. Administrativo
  4. Criativos de Performance
  5. Inteligência de Vendas
  6. Engenharia de IA/Dados
- Prevent generic bulk scraping by injecting native key terms into native search/API queries for all 6 new categories.
- Returned job dictionaries must have `profession` and `category` fields accurately populated and formatted to match downstream database insertion flows (`database.py`).
- Adapt or create programmatic tests under `tests/` verifying scrapers using queries from the 6 new categories.
- Run `python run_tests.py` and ensure 100% pass with 0 errors.
- DO NOT CHEAT or hardcode test results. Genuine logic only.

## Current Parent
- Conversation ID: f250d8ce-e5a1-428d-b29d-c9ab8eeb5381
- Updated: 2026-07-29T11:30:00Z

## Task Summary
- **What to build**: Comprehensive refactoring of scrapers & category mappings for 6 new profession categories, downstream payload schema compatibility, and test suite verification.
- **Success criteria**: All 6 categories supported natively in search, valid profession/category payloads, test coverage across scrapers, `python run_tests.py` passing with 0 errors.

## Key Decisions Made
- Starting codebase investigation.

## Artifact Index
- `.agents/teamwork_preview_worker_scrapers/progress.md` — Progress tracker
- `.agents/teamwork_preview_worker_scrapers/ORIGINAL_REQUEST.md` — User request

## Change Tracker
- **Files modified**: None yet
- **Build status**: Untested
- **Pending issues**: None

## Quality Status
- **Build/test result**: Pending
- **Lint status**: Pending
- **Tests added/modified**: None

## Loaded Skills
- None
