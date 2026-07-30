# BRIEFING — 2026-07-21T19:56:00Z

## Mission
Audit Requirement R2: City / State / Region Filter and Quick Pills in static/index.html and app.py.

## 🔒 My Identity
- Archetype: teamwork_preview_explorer
- Roles: Explorer / Auditor for Requirement R2
- Working directory: C:\Users\99196\OneDrive\Documentos\vagas_bot\.agents\teamwork_preview_explorer_filtering_2
- Original parent: aafc53e1-88de-43a7-9889-1bb700149ead
- Milestone: Requirement R2 Audit

## 🔒 Key Constraints
- Read-only investigation — do NOT implement code changes in app code
- All outputs in agent directory

## Current Parent
- Conversation ID: aafc53e1-88de-43a7-9889-1bb700149ead
- Updated: 2026-07-21T19:56:00Z

## Investigation State
- **Explored paths**: `static/index.html`, `app.py`, `database.py`, `bot.py`
- **Key findings**:
  1. Quick pills ('Todas', 'São Paulo', 'Rio de Janeiro', 'Curitiba', 'Exterior') in `static/index.html` update `#loc-input` and trigger instant filtering via `setLocFilter(city)` -> `filterData()`.
  2. Text input `#loc-input` uses `oninput="debounceFilter()"` (200ms delay) before executing `filterData()`.
  3. Case-insensitivity is implemented (`.toLowerCase()`), but **accent normalization is missing** in JS frontend filtering. Searching "Sao Paulo" will not match "São Paulo" and vice-versa.
  4. Database `/api/jobs` endpoint does not return a dedicated `location` column in the JSON response payload. Frontend location filter checks `title`, `requirements`, and `company` text.
  5. Pill 'Exterior' relies on literal keyword matching of "exterior", which won't match international locations like "Portugal", "USA", etc.
  6. Backend `/api/trigger` passes `location` to `is_job_relevant` in `bot.py`, which normalizes accents via `NFD`.
- **Unexplored areas**: None for R2.

## Key Decisions Made
- Completed systematic code trace of HTML, JS, API, and backend for R2.

## Artifact Index
- ORIGINAL_REQUEST.md — Initial request copy
- BRIEFING.md — Context and identity tracking
- progress.md — Liveness heartbeat and step tracking
- handoff.md — Final audit report
