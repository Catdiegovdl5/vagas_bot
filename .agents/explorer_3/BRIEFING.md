# BRIEFING — 2026-07-21T12:40:45Z

## Mission
Inspect existing test suite in vagas_bot, analyze how `is_job_relevant` is tested, and design `test_iniciantes.py` to validate acceptance criteria for beginner profile criteria.

## 🔒 My Identity
- Archetype: Teamwork Explorer
- Roles: Read-only investigation, analysis, test design report
- Working directory: C:/Users/99196/OneDrive/Documentos/vagas_bot/.agents/explorer_3
- Original parent: e3c4ce43-cbeb-4fa3-90bf-c9ad509ee695
- Milestone: Test suite inspection & test_iniciantes.py design

## 🔒 Key Constraints
- Read-only investigation — do NOT implement code changes in project source/tests (write only to working dir)
- Output detailed report to C:/Users/99196/OneDrive/Documentos/vagas_bot/.agents/explorer_3/analysis.md
- Output handoff report to C:/Users/99196/OneDrive/Documentos/vagas_bot/.agents/explorer_3/handoff.md
- Send handoff message to parent (e3c4ce43-cbeb-4fa3-90bf-c9ad509ee695)

## Current Parent
- Conversation ID: e3c4ce43-cbeb-4fa3-90bf-c9ad509ee695
- Updated: 2026-07-21T12:45:00Z

## Investigation State
- **Explored paths**: `test_experience.py`, `test_motor.py`, `test_keywords.py`, `run_tests.py`, `test_seniority_filter.py`, `test_relevance_fixed.py`, `tests/conftest.py`, `tests/test_tier1.py`, `bot.py` (`is_job_relevant`).
- **Key findings**:
  1. `is_job_relevant` in `bot.py` handles beginner profiles via `settings['level']` (`"Ganhar Experiência"`, `"Jovem Aprendiz"`, `"Júnior"`).
  2. For `"Ganhar Experiência"`, jobs must contain target experience terms (`voluntario`, `ong`, `open source`, `sem experiencia`, `estagio inicial`) AND must NOT contain higher seniority terms (`junior`, `jr`, `pleno`, `pl`, `senior`, `sr`). In addition, `"voluntario"` is explicitly whitelisted from global title blacklist.
  3. For `"Jovem Aprendiz"`, jobs must contain `aprendiz_terms` (`aprendiz`, `jovem aprendiz`, `menor aprendiz`).
  4. Vaga "Dev Voluntário" under "Ganhar Experiência" returns `True`.
  5. Vaga "Jovem Aprendiz de TI" under "Jovem Aprendiz" returns `True`.
  6. Vaga "Dev Júnior 1 ano de experiência" under "Ganhar Experiência" or "Jovem Aprendiz" returns `False` (blocked by `"junior"` term under "Ganhar Experiência" and missing `"aprendiz"` term under "Jovem Aprendiz").
- **Unexplored areas**: None.

## Key Decisions Made
- Fully analyzed `is_job_relevant` mechanics for beginner profiles and designed `test_iniciantes.py` with dual-mode support (Pytest functions + standalone CLI execution).

## Artifact Index
- ORIGINAL_REQUEST.md — Original user request log
- BRIEFING.md — Working memory index
- analysis.md — Detailed investigation & test design report
- handoff.md — 5-component handoff report
