# Plan - Fast Audit Milestone

## Architecture
- The bot utilizes several scraping modules under the `scrapers/` folder.
- Scraping runs concurrently/async.
- Telegram dashboard is updated in `bot.py` and `app.py` coordinates integrations.

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| 1 | Fast Audit | Perform read-only audit of scrapers and app.py/bot.py | None | PLANNED |

## Interface Contracts
- Scrapers should implement standard interfaces if expected by bot.py/app.py.
- Calls should not block the event loop.
