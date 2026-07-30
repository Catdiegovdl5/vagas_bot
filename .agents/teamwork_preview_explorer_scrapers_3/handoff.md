# Handoff Report — Scraper Test Suite & Macro-Search Exploration

## 1. Observation
Direct observations gathered during read-only code exploration of `tests/`, `scrapers/`, and project root:

- **Root Directory & Project Configuration**:
  - `run_tests.py:17-22`: Pytest runner invoking `pytest.main(["-v", "-p", "no:warnings", tests_dir])`.
  - `PROJECT.md:12-16`: Outlines data flow between UI drawers (`static/index.html`), backend (`app.py`, `bot.py`), scrapers (`scrapers/*.py`), and database (`database.py`).
  - `TEST_INFRA.md:47-60`: Documents 49 systematic tests across 4 tiers (Tier 1: Feature Coverage, Tier 2: Corner Cases, Tier 3: Pairwise Combinations, Tier 4: Real-world Workflows).

- **Primary Test Suite (`tests/`)**:
  - `tests/conftest.py:33-37`: Monkeypatches `database.DB_PATH` to `tests/jobs_test.db`.
  - `tests/conftest.py:99-288`: Mocks Playwright (`sync_playwright`, `async_playwright`) in `sys.modules`.
  - `tests/conftest.py:290-381`: Mocks Groq AI (`AsyncGroq`) returning JSON complying with `JobEvaluation`.
  - `tests/conftest.py:386-464`: Monkeypatches `requests.get`, `requests.post`, and `curl_cffi.requests`.
  - `tests/conftest.py:468-537`: Spins up background Mock ATS FastAPI server on `http://127.0.0.1:8081`.
  - `tests/test_tier1.py:8-46`: Uses helper functions (`get_linkedin()`, `get_infojobs()`, `SyncWrapper`) to wrap async scrapers for synchronous pytest functions.
  - `tests/test_milestone2_macro_searches.py:24-158`: Tests macro keywords for 6 categories, sub-profession classification (`classify_job_profession`), global blacklist exemptions (`Pintor Industrial`, `Mecânico Industrial`), and invalid cross-domain rejections.

- **Scrapers under Inspection (`scrapers/`)**:
  - `scrapers/gupy.py:11`: `async def scrape(keyword="Python", level="Todos", ...)` using `gupy_mapping` (lines 21-77). Returns dictionaries with keys `platform`, `title`, `company`, `budget`, `link`, `job_type`, `profession`, `level`, `requirements`.
  - `scrapers/infojobs.py:22`: `async def scrape(...)` using `infojobs_mapping` (lines 31-87), `async_playwright` (lines 104-186), and `curl_cffi` fallback (lines 203-215).
  - `scrapers/workana.py:12`: `async def scrape(...)` importing `bot.CO_OCCURRENCE_RULES` (lines 35-44) and searching Workana project cards `.project-item` (lines 92-168).
  - `scrapers/linkedin.py:7`: Sync `def scrape(...)` using `keyword_mapping` boolean queries (lines 41-97) and `curl_cffi` guest API requests (lines 160-252).

- **Taxonomy & Macro Keywords in `bot.py`**:
  - `bot.py:1512-1527`: `BLACKLIST_PROFILES` defines macro keyword blacklists for `operacoes fisicas`, `industria`, `logistica`, `administrativo`, `criativos`, `design`, `inteligencia de vendas`, `vendas`, `engenharia de dados`.
  - `bot.py:1749-1800`: `CO_OCCURRENCE_RULES` defines double-group co-occurrence rules for macro keywords and sub-professions.

---

## 2. Logic Chain
1. **Observation**: `run_tests.py` executes `pytest.main(...)` targeting `tests/`, while `tests/conftest.py` installs hermetic network, browser, and database mocks.
   - **Reasoning**: All tests under `tests/` execute offline in a sandboxed environment without external network flakiness.
2. **Observation**: `tests/test_tier1.py:8-46` uses `SyncWrapper` when `inspect.iscoroutinefunction(scraper.scrape)` is true.
   - **Reasoning**: Both synchronous scrapers (LinkedIn, Glassdoor) and asynchronous scrapers (Gupy, InfoJobs, Workana) can be uniformly tested within standard pytest test functions using `asyncio.run()`.
3. **Observation**: `bot.py` defines macro category keywords (`Indústria`, `Logística`, `Administrativo`, `Design`, `Vendas`, `Engenharia de Dados`) and classification rules (`classify_job_profession`, `is_job_relevant`).
   - **Reasoning**: Testing updated scrapers requires passing these exact macro keywords into scraper `scrape()` functions and verifying that the returned job schema passes local relevance filtering without triggering false-positive blacklist rejections.
4. **Observation**: Current test coverage in `tests/test_milestone2_macro_searches.py` validates `bot.py` filtering logic for the 6 broad categories, but does not explicitly iterate all updated scrapers against each category in a parameterized grid.
   - **Reasoning**: Adapting tests by adding a parameterized test module (`test_scrapers_macro_categories.py`) guarantees end-to-end verification across Gupy, InfoJobs, Workana, and LinkedIn for all 6 macro search domains.

---

## 3. Caveats
- **Read-Only Scope**: No code files outside `.agents/` were modified during this investigation.
- **Network Mode**: The investigation was conducted in `CODE_ONLY` mode. Real network calls to external job boards were not executed; verification relies on the mocked execution harness in `conftest.py`.
- **Live Scraper HTML Structure**: External job board HTML structure may change in production. Mocks reflect current HTML schemas documented in `TEST_INFRA.md`.

---

## 4. Conclusion
1. The project relies on `pytest` executed via `python run_tests.py` or `pytest tests/`, covering 49 systematic tests across 4 tiers.
2. Scrapers return a normalized dictionary schema (`title`, `company`, `budget`, `link`, `platform`, `requirements`). Testing is mocked at the network level (`requests`, `curl_cffi`), browser level (`playwright`), and AI level (`groq`).
3. To verify updated scrapers across the 6 new categories (`Operações Físicas/Indústria`, `Logística`, `Administrativo`, `Criativos/Design`, `Inteligência de Vendas/Vendas`, `Engenharia de Dados`), a parameterized Pytest module can pass macro terms into `gupy`, `infojobs`, `workana`, and `linkedin`, checking schema compliance and `bot.is_job_relevant()` classification.
4. Programmatic verification is fully specified and ready for implementation.

---

## 5. Verification Method
To verify this analysis independently:
1. **Inspect Test Configuration**:
   - `view_file` on `run_tests.py` and `tests/conftest.py`.
2. **Inspect Scraper Modules**:
   - `view_file` on `scrapers/gupy.py`, `scrapers/infojobs.py`, `scrapers/workana.py`, and `scrapers/linkedin.py`.
3. **Inspect Macro Category Logic**:
   - `view_file` on `tests/test_milestone2_macro_searches.py` and `bot.py` (lines 1512-1800).
4. **Run Existing Test Suite**:
   - Command: `python run_tests.py` (Expected: 49 tests pass with exit code 0).
