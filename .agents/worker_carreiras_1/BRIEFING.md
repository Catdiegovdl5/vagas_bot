# BRIEFING — 2026-07-21T14:15:30-03:00

## Mission
Implement interactive Career Guidance & Gamified Progress Track module ('Guia de Profissionalização e Trilha de Carreira') for 5 elite professions in bot.py, database.py, and create test_carreiras.py.

## 🔒 My Identity
- Archetype: implementer
- Roles: implementer, qa, specialist
- Working directory: C:\Users\99196\OneDrive\Documentos\vagas_bot\.agents\worker_carreiras_1
- Original parent: 49a4dc06-6b50-45ed-a780-8ef1452a6df5
- Milestone: Carreiras Module Implementation

## 🔒 Key Constraints
- CODE_ONLY network mode: no external HTTP calls/websites.
- Minimal change principle: edit only what is needed.
- Telegram callback_data length limit: strictly < 64 bytes.
- SQLite DB isolation: `user_career_progress` must not break or overwrite existing tables (`jobs`, `applied_jobs`, `ignored_jobs`, `user_preferences`).
- Non-breaking integration: all existing tests must pass.

## Current Parent
- Conversation ID: 49a4dc06-6b50-45ed-a780-8ef1452a6df5
- Updated: 2026-07-21T14:15:30-03:00

## Task Summary
- **What to build**: Career guidance and gamified track in bot.py & database.py for 5 elite professions (server_side_tracking, growth_engineer, analytics_engineer, ia_ops, sdr_tecnico).
- **Success criteria**:
  - database.py updated with user_career_progress schema & CRUD functions (save_user_step_status, get_user_career_progress, toggle_user_step_status, init_career_db).
  - bot.py updated with career metadata, handlers for `/carreiras`, `🎓 Trilha de Carreiras`, and `car:*` callback queries.
  - test_carreiras.py created and 100% passing (8/8 passed).
  - All existing tests pass (`run_tests.py` 69/69 passed, `test_menu_expansion.py` 3/3 passed, `test_iniciantes.py` 3/3 passed).
- **Interface contracts**: PROJECT.md
- **Code layout**: Root directory (bot.py, database.py, test_carreiras.py).

## Change Tracker
- **Files modified**:
  - `database.py`: Added `user_career_progress` table DDL, `init_career_db()`, `save_user_step_status()`, `get_user_career_progress()`, `toggle_user_step_status()`, `get_career_step_status()`.
  - `bot.py`: Added `CAREER_GUIDANCE_DATA` for 5 elite professions, markups (`get_carreiras_main_markup`, `get_profession_detail_markup`, `get_profession_roadmap_markup`), `/carreiras` & `🎓 Trilha de Carreiras` message handlers, `car:*` callback query handlers.
  - `test_carreiras.py`: Created comprehensive 8-test suite.
- **Build status**: PASS (All 83 tests passing across unit, integration, and E2E suites)
- **Pending issues**: None

## Quality Status
- **Build/test result**: 83/83 tests PASS (8 in `test_carreiras.py`, 69 in `run_tests.py`, 3 in `test_menu_expansion.py`, 3 in `test_iniciantes.py`)
- **Lint status**: 0 syntax/lint errors
- **Tests added/modified**: `test_carreiras.py` added

## Loaded Skills
- None

## Key Decisions Made
- Used prefix `car:` for all career callback queries (`car:main`, `car:p:<pid>`, `car:r:<pid>`, `car:t:<pid>:<step_id>`, `car:j:<pid>`), keeping max callback length at 33 bytes (< 64 bytes limit).
- Maintained strict database isolation by placing career progress tracking in a separate table `user_career_progress` without foreign key constraints or queries referencing `jobs`, `applied_jobs`, or `ignored_jobs`.
- Supported both short numeric IDs ("1".."5") and canonical string identifiers ("server_side_tracking".."sdr_tecnico") via `resolve_profession_id()`.

## Artifact Index
- ORIGINAL_REQUEST.md — Original user prompt and task specification.
- handoff.md — Final 5-component handoff report.
