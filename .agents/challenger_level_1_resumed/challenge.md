## Challenge Summary

**Overall risk assessment**: HIGH

While the core seniority level filtering and keyword mapping logic works under ideal conditions, the implementation contains several architectural assumptions and bugs that expose it to failure under concurrency, network failure, or edge-case settings.

---

## Challenges

### [High] Challenge 1: Concurrency and SQLite Database Locks

- **Assumption challenged**: The system assumes that running `_do_hunt` concurrently or executing multiple scrapers in parallel is safe because it uses SQLite's WAL mode.
- **Attack scenario**: When multiple scraping processes finish at similar times, they call `database.insert_jobs` concurrently. Since SQLite only supports serialized writes and locks the database during write transactions, concurrent write requests will fail with `sqlite3.OperationalError: database is locked`. This is verified by the existing E2E test suite error `OperationalError: database is locked`.
- **Blast radius**: Scraping tasks will fail to save their results, throwing exceptions and causing loss of retrieved job data.
- **Mitigation**: Implement a retry loop with exponential backoff for database writes in `database.py`, or use a centralized database connection queue / write lock to serialize write operations.

### [Medium] Challenge 2: Literal Search Keyword Leakage for "None" and Empty String Levels

- **Assumption challenged**: The system assumes that any level other than `"Todos"` is a valid seniority term that should be appended to the search query.
- **Attack scenario**: If a user's seniority level is set to `None` or `""` (empty string), the keyword transformation constructs queries like `"Python Backend None"` or `"Python Backend "`. Passing these directly to the scrapers causes search engines to look for the literal word "None" or include trailing whitespace, resulting in poor or empty search results.
- **Blast radius**: The user will receive highly degraded search results or zero vacancies when their level is not set to standard values.
- **Mitigation**: Explicitly validate and sanitize `actual_level` before appending it to `search_keyword`. Only append if it is a non-empty string and not `"None"`.

### [High] Challenge 3: Incomplete Mock Server Lifecycle and Port Conflicts in Tests

- **Assumption challenged**: The E2E tests assume that starting Uvicorn in a daemon thread is sufficient to keep the Mock ATS server alive and accessible on port 8081.
- **Attack scenario**: Running pytest on Windows with the `pytest-asyncio` plugin changes the event loop policy and can prevent the background Uvicorn server thread from initializing its event loop, leading to silent startup failure. This causes `WinError 10061` (connection refused) when `auto_apply` attempts to submit applications.
- **Blast radius**: Multiple integration tests (Tiers 3 and 4) fail because the mock ATS server is unreachable.
- **Mitigation**: Use a process-based mock server (e.g., using `multiprocessing`) or configure uvicorn to run on a free port dynamically. Alternatively, configure pytest-asyncio to share the event loop correctly.

### [Medium] Challenge 4: Glassdoor Scraper Parser Failure under Mock HTTP Content

- **Assumption challenged**: The Glassdoor scraper assumes that it will always receive real HTML with class names or patterns it expects, or that a mocked HTTP client will bypass it.
- **Attack scenario**: The global `requests` mock in `tests/conftest.py` returns generic HTML for all requests. The Glassdoor scraper (`scrapers/glassdoor.py`) tries to parse this page and returns an empty list `[]` instead of raising or handling the mock scenario. This causes `test_glassdoor_scraper_returns_valid_schema` to fail.
- **Blast radius**: E2E verification of Glassdoor scraper fails under mock conditions.
- **Mitigation**: Implement a dedicated mock handler for Glassdoor endpoints in `conftest.py` that returns realistic HTML structure, or use the mock Glassdoor module (`tests/mock_glassdoor.py`) as a fallback in tests.

---

## Stress Test Results

- **Scenario 1: Seniority keyword transformation**
  - Expected behavior: `"Todos"` does not append a suffix. `"Júnior"`, `"Pleno"`, and `"Sênior"` append their respective suffixes. `"None"` and `""` are handled safely without injecting literal search noise.
  - Actual/predicted behavior: `"Todos"` constructs `"Python Backend"`. `"Júnior"`, `"Pleno"`, and `"Sênior"` construct `"Python Backend Júnior"`, etc. `"None"` constructs `"Python Backend None"` (literal noise) and `""` constructs `"Python Backend "` (trailing space).
  - Status: **FAIL** (due to `"None"` and `""` leakages)

- **Scenario 2: Concurrent _do_hunt execution**
  - Expected behavior: 5 parallel hunter tasks run concurrently without throwing exceptions or blocking for more than 3 seconds.
  - Actual/predicted behavior: Concurrent tasks executed successfully in ~0.20s under mock scraper conditions.
  - Status: **PASS** (under mocked scrapers)

- **Scenario 3: SQLite Write Concurrency**
  - Expected behavior: Multiple concurrent writes to database succeed without locking issues.
  - Actual/predicted behavior: SQLite throws `database is locked` OperationalErrors.
  - Status: **FAIL**

---

## Unchallenged Areas

- **AI Ranking Model Accuracy** — Out of scope. We assumed that the AsyncGroq chat completion mock returns valid `JobEvaluation` JSON structures without evaluating the AI's actual semantic matching quality.
- **Form Auto-fill DOM Selection** — Out of scope. We did not challenge the DOM element selector matching logic in `auto_apply.py` against live dynamic ATS forms (only tested against the static Mock ATS server).
