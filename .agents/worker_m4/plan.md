# Plan: Creation and Execution of CLT Scrapers Live Verification Test

## Objective
Create an independent test script (`test_clt_scrapers_live.py`) to run the refactored CLT scrapers (Gupy, Catho, InfoJobs, and Vagas.com) against live platforms to verify that they work, return correct structures without errors/403/429/empty lists, and do not break Workana.

## Tasks
1. Create a script named `test_clt_scrapers_live.py` in the project root.
2. In this script:
   - Import `asyncio` and the CLT scraper modules: `gupy`, `catho`, `vagas_com`, `infojobs` from the `scrapers/` folder.
   - For each scraper, run the `scrape` function asynchronously with a standard keyword (e.g. `"Python"` or `"Desenvolvedor"`), `level="Todos"`, and `max_pages=1`.
   - Print the execution status (success/fail), count of jobs returned, and sample data from the first job.
   - Assert that:
     - The output is a list.
     - Each item in the list is a dictionary.
     - The dictionary has the required keys: `platform`, `title`, `company`, `budget`, `link`, `job_type`, `profession`, `level`, `requirements`.
     - `requirements` has some content (non-empty string).
     - At least one job is returned (if jobs exist for the keyword).
   - Also import and run the `workana` scraper as a sanity check to verify that it still works and is not broken by the CLT additions.
3. Run the script using the python interpreter on the system.
4. Document the command, stdout/stderr, and exit code in the handoff report.
