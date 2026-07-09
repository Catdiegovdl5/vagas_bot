## 2026-07-07T18:33:51Z

You are a teamwork_preview_worker. Your task is to implement the centralized seniority level filtering logic in bot.py.

### Context & Requirements
- File to modify: `C:\Users\99196\OneDrive\Documentos\vagas_bot\bot.py`
- Goal: If `settings["level"]` is not "Todos", append the level to the search keyword.
- Universal/Clean approach:
  1. Around line 528, locate:
     `search_keyword = search_mapping.get(keyword, keyword)`
     Modify it to also check the user's level (from `settings` or `settings.get("level", "Todos")`). If it is not `"Todos"`, concatenate it (e.g. `search_keyword = f"{search_keyword} {settings['level']}"`).
  2. Inside the `fetch_plat(plat)` function (around lines 530-553), when calling `module.scrape`, pass `level="Todos"` instead of `level=settings["level"]`. This prevents the scrapers from performing their own internal appends, which would duplicate the level suffix (avoiding `"Júnior Júnior"`).
  3. Immediately after `res = await asyncio.to_thread(...)`, if `res` is a non-empty list of jobs, iterate through them and set/overwrite `job["level"]` to the original level settings (`settings["level"]` or `actual_level`) so that database integrity is maintained.
     For example:
     ```python
     if res:
         for job in res:
             job["level"] = actual_level
     ```
  4. Ensure `actual_level` is stored (e.g., `actual_level = settings.get("level", "Todos")`) before we override the keyword or invoke the scrapers.

### Verification
- Run the test suite using `python run_tests.py` in the project root to ensure no syntax/import errors or regressions.
- Verify that `python scrapers/run_test.py` also runs successfully.
- Record the output of the tests in your handoff report.

### MANDATORY INTEGRITY WARNING
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A Forensic Auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Please save your changes, verify them, and write your handoff report to `C:\Users\99196\OneDrive\Documentos\vagas_bot\.agents\worker_level\handoff.md`. Send a message back to me (conversation ID: 5cb4152d-4810-4c8d-8709-f0d9655e30c6) once complete.
