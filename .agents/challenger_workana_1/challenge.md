# Verification and Challenge Report: Workana Pagination and Settings

**Overall Risk Assessment**: LOW

This report documents the empirical verification and adversarial review of the Workana pagination scraping logic and the Telegram bot settings (including the language shield toggle).

---

## 1. Workana Pagination & Rate Limit Prevention

### Implementation Analysis
In `scrapers/workana.py` (lines 25-57):
1. **Loop Termination**:
   - The loop runs for page numbers up to `max_pages` (`for page in range(1, max_pages + 1):`).
   - If 30 or more jobs are accumulated, it breaks (`if len(jobs) >= 30: break`).
   - If the HTTP response status code is `429` (Too Many Requests), it immediately terminates (`break`).
   - If the `<search>` tag or the `:results-initials` attribute is missing from the parsed HTML, it terminates (`break`).
   - If the parsed JSON results list is empty, it terminates (`break`).
2. **Random Delays**:
   - For all pages after page 1 (`page > 1`), a sleep of `random.uniform(2.0, 4.5)` seconds is performed to mimic human browsing intervals.

### Empirical Verification
The test `test_workana_scraper_pagination_delays_and_termination` in `tests/test_workana_settings.py` simulates:
- A search yielding results on Page 1 and an empty result set on Page 2. The scraper correctly requested Page 1 and Page 2, but terminated without requesting Page 3.
- The execution of `time.sleep` with a value between 2.0 and 4.5 seconds for page 2.
- A 429 status code on page 2, confirming immediate loop termination.

---

## 2. Language Shield Toggle & Gringo Job Preservation

### Implementation Analysis
In `bot.py`:
1. **Toggle State Changes**:
   - The handler `toggle_escudo_ptbr` toggles the value of `settings["escudo_ptbr"]` to the logical opposite (defaulting to `True` if not set).
   - In-memory modification is reflected in `user_settings_db[chat_id]`.
2. **Gringo Job Filtering & Preservation**:
   - When the shield is **ON** (`settings["escudo_ptbr"] == True`), jobs from non-freelance platforms are checked using `langdetect.detect(text) == 'pt'`. English jobs are filtered out.
   - Freelance platforms (e.g. Workana, 99Freelas) are exempted from the shield and always preserved.
   - When the shield is **OFF** (`settings["escudo_ptbr"] == False`), all jobs (including English/gringo jobs from Indeed/LinkedIn) bypass language detection and are preserved.

### Empirical Verification
The tests verify both scenarios:
- `test_escudo_ptbr_toggle_changes_setting_in_memory` asserts that calling the callback handler changes `escudo_ptbr` from `True` to `False` and back to `True`.
- `test_escudo_ptbr_false_retains_gringo_jobs` runs `_do_hunt` with a mock Indeed job in English:
  - When `escudo_ptbr` is `False`, the job is preserved in the output list.
  - When `escudo_ptbr` is `True`, the job is filtered out because it is in English.

---

## 3. Test Execution Results

The test suite was run via `pytest tests/test_workana_settings.py` with 100% success rate:

```log
============================= test session starts =============================
platform win32 -- Python 3.14.5, pytest-9.0.3, pluggy-1.6.0
rootdir: C:\Users\99196\OneDrive\Documentos\vagas_bot
plugins: anyio-4.13.0, Flask-Dance-7.1.0, asyncio-1.4.0, mock-3.15.1
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 4 items

tests\test_workana_settings.py ....                                      [100%]

============================== warnings summary ===============================
..\..\..\AppData\Roaming\Python\Python314\site-packages\PyPDF2\__init__.py:21
  C:\Users\99196\AppData\Roaming\Python\Python314\site-packages\PyPDF2\__init__.py:21: DeprecationWarning: PyPDF2 is deprecated. Please move to the pypdf library instead.
    warnings.warn(

tests/test_workana_settings.py::test_escudo_ptbr_toggle_changes_setting_in_memory
  C:\Users\99196\AppData\Roaming\Python\Python314\site-packages\websockets\legacy\__init__.py:6: DeprecationWarning: websockets.legacy is deprecated; see https://websockets.readthedocs.io/en/stable/howto/upgrade.html for upgrade instructions
    warnings.warn(  # deprecated in 14.0 - 2024-11-09

tests/test_workana_settings.py::test_escudo_ptbr_toggle_changes_setting_in_memory
  C:\Users\99196\AppData\Roaming\Python\Python314\site-packages\uvicorn\protocols\websockets\websockets_impl.py:17: DeprecationWarning: websockets.server.WebSocketServerProtocol is deprecated
    from websockets.server import WebSocketServerProtocol

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
======================== 4 passed, 3 warnings in 9.26s ========================
```

---

## 4. Adversarial Review & Attack Surface Analysis

### Challenge 1: Lack of Setting Persistence
- **Assumption Challenged**: User settings are saved between bot restarts.
- **Attack Scenario**: If the Telegram bot restarts (due to crash or update), `user_settings_db` (an in-memory dictionary) is completely reset. This will reset the `escudo_ptbr` setting of all users back to `True`.
- **Blast Radius**: Low/Medium (Users will have to toggle settings again on restart, and gringo jobs might be silently filtered out for users who had disabled the shield).
- **Mitigation**: Move user settings storage to the existing database layer (using SQLite/PostgreSQL) instead of an in-memory dictionary.

### Challenge 2: HTML Structure Dependency
- **Assumption Challenged**: Workana will continue using the `<search :results-initials="...">` structure indefinitely.
- **Attack Scenario**: If Workana updates its Vue.js payload structure or class names, the scraper will fail to parse results, leading to `results` being empty, causing a clean loop termination but returning 0 jobs.
- **Blast Radius**: Medium (Scraper returns 0 results for Workana silently).
- **Mitigation**: Implement alerting/logging when a scraper repeatedly yields 0 results for queries that are expected to return hits.

### Challenge 3: Language Detection Flaws
- **Assumption Challenged**: Language detection of job description text is accurate.
- **Attack Scenario**: A Portuguese job containing some English terms or code blocks could be incorrectly detected as English, leading to it being filtered out when `escudo_ptbr` is ON. Conversely, a gringo job with poor English or multi-lingual content could be detected as Portuguese.
- **Blast Radius**: Low.
- **Mitigation**: Set a higher threshold or use a fallback logic checking for common Portuguese keywords if language detection fails.
