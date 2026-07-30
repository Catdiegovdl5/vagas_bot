## 2026-07-16T17:57:25Z
You are worker_m2_1.
Your working directory is C:\Users\99196\OneDrive\Documentos\vagas_bot\.agents\worker_m2_1.
Your task is to implement the fixes and the High-Precision Filtering Engine (HPFE) based on the Milestone 1 reports.

Specifically, you must:
1. Fix the startup exception in `bot.py` by ensuring `await bot.set_chat_menu_button()` is wrapped in a try/except or handled safely so it does not crash on startup when token or network issues occur.
2. Update `scrapers/ai_filter.py` to:
   - Define and export the `API_KEYS` variable.
   - Implement the hard-locks (foreign currency filter for USD/Euro, and fluent English requirement for junior level candidates).
3. Implement the High-Precision Filtering Engine (HPFE):
   - Create a robust exact-word matching function with proper word boundary regex checking (to avoid Javascript matching Java, etc.).
   - Support allowlists (using co-occurrence group logic to handle word order variations, e.g. "Desenvolvedor Python" matching "Backend Python") and global/niche-specific blocklists.
   - Integrate this HPFE filter inside `bot.py` (`is_job_relevant` function) and in `app.py`'s `/api/trigger` endpoint so that web app triggers also filter jobs before inserting them into the database.
4. Resolve SQLite write locks in tests:
   - Make sure manual SQLite connections opened in tests (like `test_auto_apply_skips_low_score_jobs`, `test_auto_apply_updates_database_applied`, etc.) are wrapped in context managers or `finally` blocks to ensure they are always closed and don't lock `jobs_test.db`.
5. Run the build and test commands (like `python run_tests.py` or `pytest tests/`) to verify all 57 tests pass.

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A Forensic Auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Please document all your changes in C:\Users\99196\OneDrive\Documentos\vagas_bot\.agents\worker_m2_1\changes.md. When completed, write handoff.md and send a message back.
