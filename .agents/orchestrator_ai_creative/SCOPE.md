# Scope: AI Creative Job Filtering

## Architecture
- `bot.py`: Handles Telegram interface, job hunting flow, search keywords/dictionaries, and filtering rules.
- `verify_ai_creative_jobs.py`: Verification script mocking 5 creative AI jobs and 5 non-AI jobs to assert filtering behaves correctly.

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| 1 | Exploration & Planning | Retrieve and analyze current filtering logic in bot.py, identify where rules are defined, and formulate specific regex/filter modifications. | none | DONE |
| 2 | Implementation | Modify `bot.py` or search dictionaries to accept creative/marketing jobs utilizing AI. | M1 | DONE |
| 3 | Verification | Create `verify_ai_creative_jobs.py` and run it to verify 5 approved and 5 rejected job mocks with 100% green output. | M2 | DONE |

## Interface Contracts
- The filtering rules must return boolean outcomes or conform to standard structures within `bot.py`.
- `verify_ai_creative_jobs.py` runs and verifies the logic.
