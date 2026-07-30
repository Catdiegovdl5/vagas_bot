# Scope: Keyword Expansion and Refinement

## Architecture
- `bot.py` contains `search_mapping` (lines 654-733) which maps niche keyword selections (like "Especialista em IA Generativa") to search strings for scrapers.
- `bot.py` contains `blacklist` (lines 417-441) and `rules` (lines 460-592) in the `is_job_relevant` function.
- `is_job_relevant` determines if scraped jobs are relevant to the selected keyword and settings.
- `test_keywords.py` will be a new test script to run validation on the keywords, rules, and blacklist without starting the whole bot.

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| 1 | Exploration & Deconstruction | Analyze current search_mapping, rules, blacklist, and design expansions. | None | PLANNED |
| 2 | Implementation | Update bot.py (search_mapping, rules, blacklist) and create test_keywords.py | M1 | PLANNED |
| 3 | Verification & Review | Run test_keywords.py, verify syntax, review, and audit changes. | M2 | PLANNED |

## Interface Contracts
- None, we are updating the keyword mappings and rules within `bot.py` and creating `test_keywords.py`.
