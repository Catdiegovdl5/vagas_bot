# BRIEFING — 2026-07-21T09:11:15-03:00

## Mission
Build an empirical regression test harness and test `is_job_relevant` for existing seniority levels ("Todos", "Júnior", "Pleno", "Sênior", "Jovem Aprendiz") to confirm zero regression from the "ganhar experiência" addition.

## 🔒 My Identity
- Archetype: Empirical Challenger
- Roles: critic, specialist
- Working directory: C:\Users\99196\OneDrive\Documentos\vagas_bot\.agents\teamwork_preview_challenger_exp_2
- Original parent: d5ca5f62-0dc5-455f-9a5a-33a662c58f1e
- Milestone: Milestone 3 - Experience / Seniority Filter Regression Verification
- Instance: Challenger 2

## 🔒 Key Constraints
- Write test scripts and outputs ONLY to agent working directory: `C:\Users\99196\OneDrive\Documentos\vagas_bot\.agents\teamwork_preview_challenger_exp_2`
- Do NOT modify codebase implementation files directly (critic/review role)
- Empirical verification: must write and run python harness script, non-trust of unverified claims

## Current Parent
- Conversation ID: d5ca5f62-0dc5-455f-9a5a-33a662c58f1e
- Updated: 2026-07-21T09:11:15-03:00

## Review Scope
- **Files to review**: `bot.py` (`is_job_relevant` function, lines 949–1078).
- **Review criteria**: Existing seniority levels ("Todos", "Júnior", "Pleno", "Sênior", "Jovem Aprendiz") must behave identically with exact match expectations before and after "ganhar experiência" addition.

## Attack Surface
- **Hypotheses tested**:
  1. Does adding `user_level == 'ganhar experiencia'` alter filtering outcome for `"Todos"`? -> TESTED & CONFIRMED ZERO IMPACT (100/100 pass).
  2. Does adding `user_level == 'ganhar experiencia'` alter filtering outcome for `"Júnior"`? -> TESTED & CONFIRMED ZERO IMPACT (100/100 pass).
  3. Does adding `user_level == 'ganhar experiencia'` alter filtering outcome for `"Pleno"`? -> TESTED & CONFIRMED ZERO IMPACT (100/100 pass).
  4. Does adding `user_level == 'ganhar experiencia'` alter filtering outcome for `"Sênior"`? -> TESTED & CONFIRMED ZERO IMPACT (100/100 pass).
  5. Does adding `user_level == 'ganhar experiencia'` alter filtering outcome for `"Jovem Aprendiz"`? -> TESTED & CONFIRMED ZERO IMPACT (100/100 pass).
  6. Does `active_global_blacklist` exception leak to existing seniority levels? -> TESTED & CONFIRMED ZERO LEAK (Boolean expression `not (user_level == "ganhar experiencia" and term in ...)` evaluates to `True` for all other levels).
- **Vulnerabilities found**: None. 100% behavior preservation.
- **Untested angles**: AI filter external LLM calls (mocked out in pure `is_job_relevant` tests, which is deterministic local filtering).

## Loaded Skills
- None explicitly requested.

## Key Decisions Made
- Built `regression_harness.py` comparing `is_job_relevant` against legacy oracle across 500 test execution matrix.
- Ran harness successfully with 0 failures recorded.
- Generated `regression_results.json` artifact.

## Artifact Index
- `ORIGINAL_REQUEST.md` — Original prompt instructions.
- `BRIEFING.md` — Agent briefing state.
- `progress.md` — Liveness heartbeat and step summary.
- `regression_harness.py` — Test generator and empirical harness script.
- `regression_results.json` — Empirical test execution output log.
- `handoff.md` — Final 5-component handoff report.
