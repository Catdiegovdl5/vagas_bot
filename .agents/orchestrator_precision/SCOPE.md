# Scope: vagas_bot Precision Phase

## Architecture
- **Filtering Engine (`scrapers/ai_filter.py` or new module `job_filter.py`)**:
  - Exact keyword matching as baseline.
  - Allowlist/Blocklist of job titles to filter out false positives from unrelated areas (e.g. "Enfermeira que sabe Python").
- **Telegram Bot (`bot.py`)**:
  - Integration of the filter engine to screen fetched jobs before posting/storing.
  - Runtime exception fixes (ensure startup and E2E runs don't throw exceptions).

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|---|---|---|---|
| 1 | M1: Exploration & Diagnosis | Codebase analysis, finding bot runtime exceptions, designing high-precision matching engine | none | DONE |
| 2 | M2: Implementation & Refactoring | Implement high-precision engine, integrate with bot, fix all startup/runtime exception bugs | M1 | DONE |
| 3 | M3: Verification & Auditing | Create `test_motor.py` with 10+ tricky false positives, ensure 100% rejection, verify bot runs, run forensic audit | M2 | DONE |

## Interface Contracts
- **`job_filter.py` or new engine interface**:
  - `filter_job(job_title: str, job_description: str, keywords: List[str]) -> bool`: returns True if job is a valid match, False otherwise.
  - Uses exact keyword match and allow/block lists of title patterns.
