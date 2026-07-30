# BRIEFING — 2026-07-21

## Mission
Implement Requirement 1 (R1) backend location parameter passing and Requirement 2 (R2) frontend UF mapping & 100% remote job preservation, plus unit integration test suite `test_location_state.py`.

## 🔒 My Identity
- Archetype: Worker 1
- Roles: implementer, qa, specialist
- Working directory: C:/Users/99196/OneDrive/Documentos/vagas_bot/.agents/teamwork_preview_worker_state_fix
- Original parent: 772dddf2-e75a-4b9a-86b9-c75f58040b99
- Milestone: State Search Implementation & Verification

## 🔒 Key Constraints
- Genuine implementation only, no cheating or hardcoding test outputs.
- Backend location passing via `inspect.signature` or kwargs check in `app.py` and updating scrapers in `scrapers/*.py`.
- Frontend UF mapping (27 Brazilian UFs + Exterior + Todos) in `static/index.html`, 100% remote jobs visible unconditionally for state filters, word boundary regex for state matching.
- Create `test_location_state.py` at project root and ensure 100% tests pass.

## Current Parent
- Conversation ID: 772dddf2-e75a-4b9a-86b9-c75f58040b99
- Updated: 2026-07-21

## Task Summary
- **What to build**: R1 backend location parameter passing in `app.py` and scrapers, R2 frontend state selector, `UF_MAP`, regex matching, remote preservation in `static/index.html`, and `test_location_state.py` test suite.
- **Success criteria**: All scrapers handle location parameter gracefully, app.py passes location parameter when launching scrapes, index.html correctly handles state selection and remote filter preservation, `python test_location_state.py` passes 100%.

## Change Tracker
- **Files modified**:
  - `app.py`: Updated `run_hunt_background` to use `inspect.signature` dynamically building `kwargs` with `location`.
  - `scrapers/*.py` (`geekhunter.py`, `github_vagas.py`, `glassdoor.py`, `gmail.py`, `indeed.py`, `jooble.py`, `jsearch.py`, `linkedin.py`, `meta_ads.py`, `novenove.py`, `programathor.py`, `remotar.py`, `workana.py`, etc.): Updated `scrape` signatures to accept `location: str = "Todos"` and `**kwargs`, passing location to search queries where applicable.
  - `static/index.html`: Verified `<select id="state-select">` with 27 UFs + Exterior + Todos, added JS `UF_MAP`, `isJobInState` regex helper, and updated `filterData()` to unconditionally match 100% remote jobs (`isRemote`).
  - `test_location_state.py`: Created at project root.
- **Build status**: PASS (100% tests passing)
- **Pending issues**: None

## Quality Status
- **Build/test result**: PASS (`python test_location_state.py` -> 100% pass; `python test_location_uf.py` -> 21/21 pass)
- **Lint status**: Clean
- **Tests added/modified**: `test_location_state.py` added at project root.

## Loaded Skills
- None

## Artifact Index
- `.agents/teamwork_preview_worker_state_fix/ORIGINAL_REQUEST.md` — Original instruction log
- `.agents/teamwork_preview_worker_state_fix/BRIEFING.md` — Briefing document
- `.agents/teamwork_preview_worker_state_fix/progress.md` — Progress log
- `.agents/teamwork_preview_worker_state_fix/handoff.md` — Handoff report
- `test_location_state.py` — Location test suite at project root
