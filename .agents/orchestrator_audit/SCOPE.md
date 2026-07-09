# Scope: vagas_bot Codebase Audit

## Architecture
- The bot is an asynchronous python application using python-telegram-bot or similar.
- `bot.py` is the main entry point, managing Telegram UI interaction, running scrapers concurrently, and updating database.
- `app.py` serves a web server (likely Flask/FastAPI/Sanic/etc) for monitoring dashboard.
- `database.py` manages jobs SQLite database.
- `auto_apply.py` parses cv, fills job applications.
- `scrapers/` contains modules for different platforms, called dynamically or imported by `bot.py`, plus AI-based filter `ai_filter.py`.

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| 1 | Core System Audit | `bot.py`, `app.py`, `database.py`, `auto_apply.py` | None | DONE (Report: `.agents/explorer_core_system/analysis.md`) |
| 2 | Primary Scrapers & Filter Audit | `scrapers/ai_filter.py`, `scrapers/indeed.py`, `scrapers/linkedin.py`, `scrapers/glassdoor.py`, `scrapers/infojobs.py`, `scrapers/jooble.py` | None | DONE (Report: `.agents/explorer_primary_scrapers/analysis.md`) |
| 3 | Helper Scrapers & Launchers Audit | `scrapers/remotar.py`, `scrapers/novenove.py`, `scrapers/freelancer.py`, `scrapers/meta_ads.py`, `scrapers/gmail.py`, `scrapers/workana.py`, `scrapers/jsearch.py`, `launcher.py`, `render_bot.py` | None | DONE (Report: `.agents/explorer_helper_scrapers/analysis.md`) |

## Interface Contracts
- Dynamic scrapers should follow a consistent signature or class interface expected by `bot.py`.
- `ai_filter.py` provides async evaluation interface for filtering jobs using Groq.
