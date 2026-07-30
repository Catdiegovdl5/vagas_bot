## 2026-07-17T17:49:32Z
Create a live verification test script (`test_clt_scrapers_live.py`) in the project root to verify the CLT scrapers and ensure Workana is not broken.
Working directory: C:/Users/99196/OneDrive/Documentos/vagas_bot/.agents/worker_m4

Instructions:
1. Read the plan at `C:/Users/99196/OneDrive/Documentos/vagas_bot/.agents/worker_m4/plan.md`.
2. Create `test_clt_scrapers_live.py` in the root of the repository. It must run the newly refactored scrapers asynchronously (Gupy, Catho, Vagas.com, InfoJobs, and Workana) against the actual live web servers.
3. Validate that each scraper returns a list of dictionaries, and each dictionary has the standard schema keys: `platform`, `title`, `company`, `budget`, `link`, `job_type`, `profession`, `level`, `requirements`.
4. Run the script using the system python interpreter. Confirm that the scrapers successfully return real vacancies (length > 0) without 403, 429, or other failures, and that Workana scraper remains stable and functional.
5. Also run the standard test suite: `python run_tests.py` to ensure no regressions were introduced.
6. Write the results, including command execution outputs, in your handoff report at `C:/Users/99196/OneDrive/Documentos/vagas_bot/.agents/worker_m4/handoff.md`.
