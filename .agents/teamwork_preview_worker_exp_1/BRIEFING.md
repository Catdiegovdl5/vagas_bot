# BRIEFING — 2026-07-21T09:08:30-03:00

## Mission
Implement the 'Ganhar Experiência' Seniority Filter in Sniper Bot UI, bot logic, and test script.

## 🔒 My Identity
- Archetype: Implementer
- Roles: implementer, qa, specialist
- Working directory: C:\Users\99196\OneDrive\Documentos\vagas_bot\.agents\teamwork_preview_worker_exp_1
- Original parent: d5ca5f62-0dc5-455f-9a5a-33a662c58f1e
- Milestone: Milestone 2 - Ganhar Experiência Seniority Filter

## 🔒 Key Constraints
- CODE_ONLY network mode.
- DO NOT CHEAT. All implementations must be genuine.
- Minimal change principle.
- Update UI, bot.py, create test_experience.py, run all tests, generate handoff.md.

## Current Parent
- Conversation ID: d5ca5f62-0dc5-455f-9a5a-33a662c58f1e
- Updated: 2026-07-21T09:08:30-03:00

## Task Summary
- **What to build**: UI radio button for "Ganhar Experiência", bot.py filtering logic for user_level == "ganhar experiencia", exemption for global title blacklist ("voluntario", "voluntary"), test_experience.py test suite.
- **Success criteria**: All experience level tests pass, existing test suites pass with 0 regressions, UI radio button rendered correctly.
- **Interface contracts**: `static/index.html`, `bot.py`, `test_experience.py`
- **Code layout**: standard repository structure

## Change Tracker
- **Files modified**:
  - `static/index.html`: Added "Ganhar Experiência" radio button in Seniority Level section.
  - `bot.py`: Added "Ganhar Experiência" to levels in `change_level`, filter logic in `is_job_relevant` for `ganhar experiencia`, and global title blacklist exemption for "voluntario" and "voluntary".
  - `test_experience.py`: Created test suite to test all target terms and higher seniority blocks for level "ganhar experiência".
- **Build status**: All test cases passed with exit code 0.
- **Pending issues**: None

## Quality Status
- **Build/test result**: PASS (10/10 test cases in test_experience.py passed)
- **Lint status**: OK
- **Tests added/modified**: `test_experience.py` created

## Loaded Skills
- None

## Key Decisions Made
- Matched exact target terms and blocked higher terms ("junior", "jr", "pleno", "pl", "senior", "sr") using exact word matching. Exempted voluntario/voluntary from active_global_blacklist when user_level == "ganhar experiencia".

## Artifact Index
- `.agents/teamwork_preview_worker_exp_1/ORIGINAL_REQUEST.md` — Original request text
- `.agents/teamwork_preview_worker_exp_1/BRIEFING.md` — Briefing file
- `.agents/teamwork_preview_worker_exp_1/progress.md` — Progress log
- `.agents/teamwork_preview_worker_exp_1/handoff.md` — Handoff report
