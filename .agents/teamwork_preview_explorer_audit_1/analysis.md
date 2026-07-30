# Forensic Audit Integrity Remediation Plan

## Executive Summary
This document provides a comprehensive root cause analysis and step-by-step remediation guide to resolve the Forensic Audit INTEGRITY VIOLATION in `python run_tests.py`. By addressing database schema discrepancies, expanding Playwright mocks, fixing Python 3.14 asyncio event loop lifecycle management, and fixing AI filter response validation and missing imports, `python run_tests.py` will achieve 100% pass rate (49/49 passed, exit code 0).

---

## Root Cause Analysis & Evidence Chain

### 1. Database Schema & Missing Table Discrepancies (`database.py`)
- **Observation**:
  - Direct SQL insertions into `jobs` referencing `score` or `status` columns fail with `sqlite3.OperationalError: table jobs has no column named score`.
  - Calling `database.get_jobs()` or FastAPI endpoint `/api/jobs` fails with `sqlite3.OperationalError: no such table: ignored_jobs`.
- **Cause**:
  - `database.py` `init_db()` creates `jobs`, `applied_jobs`, and `processed_payments` tables. It alters `jobs` to add `job_type`, `profession`, `level`, `requirements`, `location`, `lat`, `lon`, `lang`. However, it omits `score`, `status`, `reason`, and `ai_*` columns as well as the `ignored_jobs` table.
- **Evidence**:
  - `database.py:51-76` creates `jobs` table without `score`, `status`, `reason`, `ai_aprovado`, `ai_score`, etc.
  - `database.py:160` executes `LEFT JOIN ignored_jobs i ON j.link = i.link`, but `ignored_jobs` table is never created by `init_db()`.

### 2. Incomplete Playwright Mock (`tests/conftest.py`)
- **Observation**:
  - Playwright scrapers (`scrapers/glassdoor.py`, `scrapers/infojobs.py`, `scrapers/workana.py`) hit `AttributeError` or missing mock method errors.
- **Cause**:
  - `MockPage` in `tests/conftest.py` lacked `query_selector_all` and `query_selector` methods in earlier stubs.
  - `MockElement` lacks the `inner_text()` method expected by scrapers (e.g. `workana.py`).
- **Evidence**:
  - `scrapers/glassdoor.py:148`: `page.query_selector_all(sel)`.
  - `scrapers/infojobs.py:124`: `await page.query_selector_all(...)`.
  - `scrapers/workana.py:115`: `await title_el.inner_text()`.

### 3. Python 3.14 Asyncio Event Loop (`tests/conftest.py` & Test Files)
- **Observation**:
  - Executing async functions in tests using `loop = asyncio.get_event_loop()` raises `RuntimeError: There is no current event loop in thread 'MainThread'` or `RuntimeError: Event loop is closed`.
- **Cause**:
  - Python 3.14 strict event loop policy raises `RuntimeError` when `asyncio.get_event_loop()` is called without an active event loop in thread.
  - The monkeypatched `_patched_get_event_loop()` in `conftest.py` calls `_original_get_event_loop()` without checking if the returned loop is closed.
- **Evidence**:
  - `tests/conftest.py:15-26`: `_patched_get_event_loop()` returns a closed loop if previously set.
  - `tests/test_tier1.py`, `tests/test_tier2.py`, `tests/test_tier3.py`, `tests/test_tier4.py`: multiple calls to `asyncio.get_event_loop()` and `loop.run_until_complete()`.

### 4. AI Filter Validation & Missing Imports (`scrapers/ai_filter.py` & `conftest.py`)
- **Observation**:
  - Running AI ranking tests triggers `NameError: name 'random' is not defined` in `extract_hunt_intent`.
  - `test_ia_ranking_groq_client_no_api_keys` throws `ImportError: cannot import name 'API_KEYS' from 'scrapers.ai_filter'`.
  - AI evaluation parsing fails with `Pydantic ValidationError: 1 validation error for JobEvaluation - proposal: Input should be a valid string`.
- **Cause**:
  - `scrapers/ai_filter.py` missing `import random` and `API_KEYS` module variable export.
  - `MockChatCompletions` default JSON responses in `tests/conftest.py` did not include the required `"proposal"` string field.

---

## Step-by-Step Remediation Plan for Worker Agent

### Step 1: Update `database.py`
In `database.py` `init_db()`:
1. Add table creation for `ignored_jobs`:
   ```python
   c.execute('''
       CREATE TABLE IF NOT EXISTS ignored_jobs (
           link TEXT PRIMARY KEY,
           reason TEXT,
           ignored_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
       )
   ''')
   ```
2. Add ALTER TABLE statements for missing columns on `jobs`:
   ```python
   for col, col_type in [
       ("score", "INTEGER"),
       ("status", "TEXT"),
       ("reason", "TEXT"),
       ("ai_aprovado", "INTEGER"),
       ("ai_score", "INTEGER"),
       ("ai_reason", "TEXT"),
       ("ai_reqs", "TEXT"),
       ("ai_bonus", "TEXT"),
       ("ai_benefits", "TEXT"),
       ("ai_model", "TEXT")
   ]:
       try: c.execute(f'ALTER TABLE jobs ADD COLUMN {col} {col_type}')
       except: pass
   ```

### Step 2: Fix `scrapers/ai_filter.py`
1. Add `import random` at the top of `scrapers/ai_filter.py`.
2. Ensure `API_KEYS` is defined and accessible at module level in `scrapers/ai_filter.py` (e.g. `API_KEYS = os.getenv("GROQ_API_KEYS", "...").split(",")`).

### Step 3: Update `tests/conftest.py`
1. Update `_patched_get_event_loop()` to check `not loop.is_closed()`:
   ```python
   def _patched_get_event_loop():
       try:
           loop = asyncio.get_running_loop()
           if not loop.is_closed():
               return loop
       except RuntimeError:
           pass
       try:
           loop = _original_get_event_loop()
           if not loop.is_closed():
               return loop
       except RuntimeError:
           pass
       loop = asyncio.new_event_loop()
       asyncio.set_event_loop(loop)
       return loop
   ```
2. In `MockElement`, add `inner_text`:
   ```python
   def inner_text(self, *args, **kwargs):
       return self.text_content(*args, **kwargs)
   ```
3. In `MockPage` and `MockAsyncPage`, ensure `query_selector` and `query_selector_all` return `MockElement` (or list of `MockElement`).
4. In `MockChatCompletions._default_create` (and mock Groq responses), add `"proposal": "Proposta de candidatura para a vaga."` to all mock JSON dictionary responses.

### Step 4: Update Test Files for Event Loop Robustness
In `tests/test_tier1.py`, `tests/test_tier2.py`, `tests/test_tier3.py`, and `tests/test_tier4.py`:
- Replace `loop = asyncio.get_event_loop(); result = loop.run_until_complete(coro)` with `result = asyncio.run(coro)` (or safe loop retrieval).

### Step 5: Verification & Execution
Run `python run_tests.py` from root workspace directory `C:\Users\99196\OneDrive\Documentos\vagas_bot`.
Verify exit code is 0 and output confirms 100% pass (49/49 passed, 0 failures).

---

## Invalidation Conditions
- If `python run_tests.py` exits with non-zero exit code or < 100% test pass.
- If existing features in `app.py`, `bot.py`, or database multi-tenancy are altered or broken.
