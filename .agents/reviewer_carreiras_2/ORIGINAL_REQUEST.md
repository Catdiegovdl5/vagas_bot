## 2026-07-21T17:15:32Z
Working directory: C:\Users\99196\OneDrive\Documentos\vagas_bot\.agents\reviewer_carreiras_2

You are an Independent Reviewer specialist for the vagas_bot project.

Task:
Perform independent quality, safety, and integration review of the Career Guidance & Gamified Progress Track module in `bot.py`, `database.py`, and `test_carreiras.py`.

Instructions:
1. Independently inspect `bot.py`, `database.py`, and `test_carreiras.py`.
2. Run `python run_tests.py` and `python -m pytest test_carreiras.py` to confirm test execution and zero failures.
3. Verify that `jobs`, `applied_jobs`, and `ignored_jobs` tables are completely isolated from `user_career_progress`.
4. Verify that all 5 elite professions (Server-Side Tracking, Growth Engineer, Analytics Engineer, IA-Ops, SDR Técnico) have thorough explanations and active certification links.
5. Write your detailed review report to `C:\Users\99196\OneDrive\Documentos\vagas_bot\.agents\reviewer_carreiras_2\review.md` and handoff report to `handoff.md`. Send completion message when done.
