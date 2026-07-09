# Project: vagas_bot_fixes

## Architecture
- **Dashboard Status Loop**:
  - `bot.py` contains `status_updater()` which updates the Telegram dashboard status message while scrapers run.
  - Currently, when scrapers finish, `status_updater()` may exit before rendering the final status of all platforms (like Indeed remaining at "⏳ Buscando...").
  - The fix requires ensuring that after all scrapers complete (or `is_hunting` becomes False), a final status update is explicitly pushed to Telegram.
- **Freelance Platform Config**:
  - `bot.py` initiates hunts for "Freelance" jobs using a list of scrapers.
  - The `novenove` (99Freelas) scraper needs to be disabled/removed from active freelance search lists.

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| 1 | Explorer Analysis | Explore `bot.py` and analyze indeed status updater bug + novenove disablement | none | PLANNED |
| 2 | Worker Implementation | Implement fixes in `bot.py` to send final status update and disable novenove | M1 | PLANNED |
| 3 | Review & Challenge | Review code correctness, run tests/checks, and verify indeed dashboard & novenove status | M2 | PLANNED |
| 4 | Audit & Signoff | Perform forensic audit of changes and signoff | M3 | PLANNED |

## Interface Contracts
- No new interfaces. Clean modification of Telegram bot startup/hunt routines in `bot.py`.
