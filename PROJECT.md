# Project: vagas_bot

## Architecture
- FastAPI web server (`prioriti/app.py`) running on port 8000.
- Unified launcher process (`launcher.py`) managing web server and background workers/bots.
- Batch scripts (`iniciar_tudo.bat`, `start_bot.bat`, `start.bat`) wrapping `launcher.py`.
- SQLite database (`jobs.db`) with category search and strict `NOT LIKE` exclusions.
- SEO & Schema.org endpoints (`/sitemap.xml`, `/api/job/{job_id}/schema.json`) synced with `static/index.html` JSON-LD.
- Frontend Single-Page App dashboard (`static/index.html`) on `http://localhost:8000/`.
- Error Reporter middleware (`middleware/error_reporter.py`) logging to `logs/` & AI Self-Healer (`core/ai_self_healer.py`) generating patches in `patches/`.

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | Fix Launcher Restart Loop & Telegram Token Handling | `launcher.py` handles missing Telegram token without infinite restart loop, uses `load_dotenv()`, checks `TELEGRAM_TOKEN`/`TELEGRAM_BOT_TOKEN`, adds backoff/delay, ensures FastAPI starts on port 8000 | M1 | R1 |
| 2 | Batch Scripts Unification | `iniciar_tudo.bat`, `start_bot.bat`, `start.bat` correctly launch `launcher.py` | M1 | R1 |
| 3 | SEO & Schema.org Integration | `/sitemap.xml` & `/api/job/{job_id}/schema.json` active and synced with static `index.html` JSON-LD | M2 | R2 |
| 4 | Category Integrity & Strict Exclusion | 0% category leakage using NOT LIKE exclusions in SQLite, total job counts match database strictly | M3 | R3 |
| 5 | Frontend Dashboard & DOM Cleanliness | `http://localhost:8000/` clean console, remove duplicate `#slideover-copilot` block, no undefined JS variables or broken API calls | M4 | R4 |
| 6 | Error Reporter & AI Self-Healer Module | `middleware/error_reporter.py` traps 500 errors to `logs/` and `core/ai_self_healer.py` generates patches in `patches/` | M5 | R5 |
| 7 | E2E Test Suite & Branch Delivery | 100% pass rate on E2E test suite, changes committed/verified on git branch `refactor/organizacao-e-limpeza` | M6 | Acceptance Criteria |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | Launcher & Batch Script Repair | Fix `launcher.py` restart loop, `load_dotenv()`, Telegram token optionality, port 8000 FastAPI launch, batch scripts alignment | none | IN_PROGRESS |
| M2 | SEO & Schema.org Verification | Verify and harden `/sitemap.xml` & `/api/job/{job_id}/schema.json` and JSON-LD sync | M1 | PLANNED |
| M3 | Category Integrity & NOT LIKE Exclusions | Verify SQL category queries, 0% leakage, exact SQLite total count match | M1 | PLANNED |
| M4 | Frontend Dashboard Cleanliness | Remove duplicate `#slideover-copilot` in `static/index.html`, verify JavaScript console cleanliness | M1 | PLANNED |
| M5 | Error Reporter & Self-Healer Audit | Verify `middleware/error_reporter.py` logging to `logs/` and `core/ai_self_healer.py` patch generation in `patches/` | M1 | PLANNED |
| M6 | E2E Testing & Final Victory Verification | Execute full E2E test suite (Tiers 1-4 + Tier 5 hardening), verify git branch `refactor/organizacao-e-limpeza` | M1, M2, M3, M4, M5 | PLANNED |

## Interface Contracts
### Launcher ↔ FastAPI Server
- FastAPI server executed via `uvicorn prioriti.app:app --host 0.0.0.0 --port 8000` or direct python launch.
- Port 8000 must be verified available before launch or handled gracefully.
- Telegram Bot service failure or missing token MUST NOT crash or trigger infinite restart loops for FastAPI server.

### Backend ↔ Frontend SEO / Schema.org
- `/sitemap.xml` returns valid XML sitemap of all job pages.
- `/api/job/{job_id}/schema.json` returns valid Schema.org `JobPosting` JSON.
- `static/index.html` dynamically updates `<script type="application/ld+json">` on job navigation.

## Code Layout
- `launcher.py`: Main process launcher & process monitor.
- `iniciar_tudo.bat`, `start_bot.bat`, `start.bat`: Batch entry points.
- `prioriti/app.py`: Main FastAPI application & route definitions.
- `static/index.html`: Frontend dashboard Single Page Application.
- `middleware/error_reporter.py`: Error reporter middleware.
- `core/ai_self_healer.py`: AI self-healing module.
- `scripts/verify_category_integrity_qa.py`: Empirical QA script for category leakage verification.
- `logs/`: Directory for JSON & MD error log reports.
- `patches/`: Directory for AI-generated code patches.
