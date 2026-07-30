# BRIEFING — 2026-07-21T12:11:00Z

## Mission
Stress test `is_job_relevant` from `bot.py` with `user_level = 'ganhar experiência'` across tricky edge cases by building and executing an empirical test harness.

## 🔒 My Identity
- Archetype: empirical_challenger
- Roles: critic, specialist
- Working directory: C:\Users\99196\OneDrive\Documentos\vagas_bot\.agents\teamwork_preview_challenger_exp_1
- Original parent: d5ca5f62-0dc5-455f-9a5a-33a662c58f1e
- Milestone: Milestone 3
- Instance: 1 of 1

## 🔒 Key Constraints
- Review-only for main repo codebase — do NOT modify implementation code (`bot.py`).
- All test scripts and outputs must reside in working directory (`C:\Users\99196\OneDrive\Documentos\vagas_bot\.agents\teamwork_preview_challenger_exp_1`).

## Current Parent
- Conversation ID: d5ca5f62-0dc5-455f-9a5a-33a662c58f1e
- Updated: 2026-07-21T12:11:00Z

## Attack Surface
- **Hypotheses tested**: `is_job_relevant` filtering logic under `user_level = 'ganhar experiência'`.
- **Vulnerabilities found**:
  1. Substring false positive on `voluntario` inside `involuntario`.
  2. Substring false positive on `ong` inside `congresso`, `longo`, etc.
  3. Word-boundary regex collision in `higher_terms` check on `pl` inside `PL/SQL`.
- **Untested angles**: Other user_level settings (e.g. 'pleno', 'senior') in combination with complex contracts or multi-word locations.

## Loaded Skills
- None explicitly assigned.

## Artifact Index
- `stress_test.py` — Test harness script (14 stress test scenarios)
- `handoff.md` — Final handoff report
