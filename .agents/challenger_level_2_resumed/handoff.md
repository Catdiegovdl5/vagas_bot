# Handoff Report

## 1. Observation

- **Standalone verification harness run**:
  - Command: `python verify_seniority.py`
  - Output:
    ```
    Running Standalone Seniority Filtering Harness
    ==================================================

    --- Testing Level: 'Todos' ---
    Scraper keyword captured: 'Python'
    DB level persisted: 'Todos'

    --- Testing Level: 'Júnior' ---
    Scraper keyword captured: 'Python Júnior'
    DB level persisted: 'Júnior'

    --- Testing Level: 'Pleno' ---
    Scraper keyword captured: 'Python Pleno'
    DB level persisted: 'Pleno'

    --- Testing Level: 'Sênior' ---
    Scraper keyword captured: 'Python Sênior'
    DB level persisted: 'Sênior'

    --- Testing Level: 'None' ---
    Scraper keyword captured: 'Python None'
    DB level persisted: 'None'

    --- Testing Level: '' ---
    Scraper keyword captured: 'Python '
    DB level persisted: ''

    --- Testing Concurrent Execution (Concurrency & Safety) ---
    Concurrent executions completed in 1.7971 seconds.

    ==================================================
    Verification Test Harness: PASSED
    ```
- **Port Conflict in conftest.py**:
  - Test task id "8cdf0d7c-16b3-44fb-bd07-3d79bda85720/task-49" returned uvicorn startup failure:
    ```
    OSError: [Errno 10048] error while attempting to bind on address ('127.0.0.1', 8081): [winerror 10048] normalmente é permitida apenas uma utilização de cada endereço de soquete (protocolo/endereço de rede/porta)
    ```
  - This error caused a `SystemExit: 1` which crashed the pytest process.

- **Centralized filtering code in bot.py** (lines 528-532):
  ```python
  actual_level = settings.get("level", "Todos")
  search_keyword = search_mapping.get(keyword, keyword)
  if actual_level != "Todos":
      search_keyword = f"{search_keyword} {actual_level}"
  ```

---

## 2. Logic Chain

1. From the standalone verification run output, we observed that:
   - Level `"Todos"` outputs keyword `"Python"`.
   - Levels `"Júnior"`, `"Pleno"`, and `"Sênior"` successfully append the level, e.g. `"Python Júnior"`.
   - The database stores the original level correctly for all test cases (e.g. `db_level == level`).
   - Concurrency stress tests finish in `1.80` seconds without exceptions.
2. However, for level `"None"`, the constructed keyword is `"Python None"`. For level `""` (empty string), the constructed keyword is `"Python "`.
3. Tracing back to the code in `bot.py`, the condition `if actual_level != "Todos"` triggers keyword mutation for any value that isn't `"Todos"`. This confirms that any custom level (such as `None` or empty strings) is literally formatted and appended to the search query.
4. From the port conflict trace, we observed that the pytest suite failed due to `OSError: [Errno 10048]` since port 8081 was already in use. This caused `sys.exit(1)` in the background thread, crashing the test process.

---

## 3. Caveats

- We did not verify live network interactions with the scraper APIs; all scraper actions were mocked to return local mock jobs.
- The test harness assumes the local directory layout is intact and that Python 3.14/sqlite3 are correctly configured on the machine.

---

## 4. Conclusion

The centralized seniority level filtering works correctly for valid levels. The original seniority level is properly saved into the database, and concurrent execution is safe and highly performant. 
However, two bugs were discovered:
1. **Keyword transformation bug**: If the level setting is `"None"`, `None` (object), or `""` (empty string), the query string is mutated to `"Python None"` or `"Python "`, causing bad search parameters.
2. **Test harness bug**: If port 8081 is busy, the test suite process crashes abruptly with exit code 1.

---

## 5. Verification Method

To verify these results independently:
1. Ensure you are in the root directory `C:\Users\99196\OneDrive\Documentos\vagas_bot`.
2. Run the verification script:
   `python verify_seniority.py`
3. Inspect the stdout: it should print the transformed keyword results and end with `Verification Test Harness: PASSED`.
