# Seniority Level Filtering Challenge Report

## Challenge Summary

**Overall risk assessment**: LOW

The centralized seniority level filtering implementation in `bot.py` is generally robust and handles the primary levels (`"Todos"`, `"Júnior"`, `"Pleno"`, `"Sênior"`) correctly. It successfully performs keyword transformation, passes `"Todos"` to the downstream scraping processes, and correctly persists the original seniority level in the database. Furthermore, it operates exception-free under concurrent execution. 

However, two notable edge cases and environmental issues were identified during verification.

---

## Challenges

### [Medium] Challenge 1: Invalid/Empty Seniority Settings Appended as Literal Strings

- **Assumption challenged**: The system assumes the user's seniority level setting is either `"Todos"` or a valid seniority level, and that other values are either impossible or handled gracefully.
- **Attack scenario**: If a user's setting for `level` is set to `"None"` (string), `None` (Python object), or `""` (empty string), `_do_hunt` does not validate it against a list of known seniority levels. Instead, it checks:
  ```python
  if actual_level != "Todos":
      search_keyword = f"{search_keyword} {actual_level}"
  ```
  This causes the search keyword to become:
  - `"Python None"` (when level is `"None"` or `None`)
  - `"Python "` (when level is `""`)
  
  Searching for `"Python None"` on job scrapers will search for jobs containing the literal word "None", leading to highly degraded search results or zero hits.
- **Blast radius**: MEDIUM. It degrades the search capability and returns no results for affected users, though it does not raise exceptions.
- **Mitigation**: Restrict keyword modification to a whitelist of known seniority levels:
  ```python
  VALID_LEVELS = ["Júnior", "Pleno", "Sênior"]
  if actual_level in VALID_LEVELS:
      search_keyword = f"{search_keyword} {actual_level}"
  ```

### [High] Challenge 2: Background ATS Server Port Bind Failure Crashes Test Runner

- **Assumption challenged**: The test environment assumes port 8081 is always available and can be bound unconditionally by `uvicorn` in `tests/conftest.py`.
- **Attack scenario**: If port 8081 is already in use by another process (such as a running instance of the dashboard, or another local application), the uvicorn server in the background thread fails to startup. It calls `sys.exit(1)` inside uvicorn's startup failure routine, which immediately terminates the entire `pytest` process.
- **Blast radius**: HIGH. It prevents the verification suite from running at all on developer machines or CI environments where port 8081 is occupied.
- **Mitigation**: Modify the test fixture `start_mock_ats_server` in `conftest.py` to dynamically allocate a free port (port `0`) or handle the bind error gracefully instead of terminating the process.

---

## Stress Test Results

- **Scenario 1: Hunt with level 'Todos'** → Keyword remains `"Python"`; original level in DB is `"Todos"` → **PASS**
- **Scenario 2: Hunt with level 'Júnior'** → Keyword becomes `"Python Júnior"`; original level in DB is `"Júnior"` → **PASS**
- **Scenario 3: Hunt with level 'Pleno'** → Keyword becomes `"Python Pleno"`; original level in DB is `"Pleno"` → **PASS**
- **Scenario 4: Hunt with level 'Sênior'** → Keyword becomes `"Python Sênior"`; original level in DB is `"Sênior"` → **PASS**
- **Scenario 5: Hunt with level 'None'** → Keyword becomes `"Python None"`; original level in DB is `"None"` → **PASS (Matches actual implementation but constitutes a bug)**
- **Scenario 6: Hunt with level '' (empty string)** → Keyword becomes `"Python "`; original level in DB is `""` → **PASS (Matches actual implementation but constitutes a bug)**
- **Scenario 7: 5 Concurrent Hunts (Concurrency Stress Test)** → Runs concurrently without exceptions or locks in `1.79` seconds (expected < 5.0s) → **PASS**

---

## Unchallenged Areas

- **Real Scraper API Endpoints** — Scrapers were mocked to return local mock data immediately. Live network latency, API rate-limiting, and network-level stability of external scrapers (like Jooble, Glassdoor, LinkedIn) were not stress-tested.
