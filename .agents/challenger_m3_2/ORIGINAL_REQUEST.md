## 2026-07-29T11:02:30Z
You are Challenger M3_2 (teamwork_preview_challenger) for Milestone 3 (Final Integration Gate) of the Vagas Sniper Bot project.
Your working directory is: C:\Users\99196\OneDrive\Documentos\vagas_bot\.agents\challenger_m3_2
Parent Orchestrator: 142d139e-4e7b-46c4-95f0-eaa412b7aeef

Your Task:
1. Write and run empirical stress test scripts against `bot.py`:
   - Test `classify_job_profession()` with realistic job titles across all 14 categories (Industrial, Logística, Administrativo, Criativos, Vendas, Dados/IA, etc.).
   - Test `is_job_relevant()` for edge cases, false positives, false negatives, and blacklisted titles (e.g. "Gerente de TI" vs "Operador de Máquinas CNC").
   - Test macro-search keyword expansions in `app.py` and `bot.py` (`SEARCH_MAPPING`).
2. Verify zero unhandled exceptions, zero logic regressions, and 100% classification accuracy.
3. Write your empirical challenge report to `C:\Users\99196\OneDrive\Documentos\vagas_bot\.agents\challenger_m3_2\handoff.md`.
4. Send a completion message with empirical verification results to parent 142d139e-4e7b-46c4-95f0-eaa412b7aeef.
