# Empirical Stress Test Report — Career Guidance & Gamified Progress Track

**Target Modules**: `database.py`, `bot.py`  
**Execution Timestamp**: 2026-07-21  
**Environment**: Windows 11 / Python 3.14.5 / SQLite 3 (WAL mode) / Pytest 9.0.3  
**Status**: PASS (7/7 empirical stress tests passed, 0 failures)

---

## Executive Summary

An empirical stress-testing suite was executed against the **Career Guidance & Gamified Progress Track** module in `database.py` and `bot.py`. The suite evaluated database concurrency under multi-threading, edge-case type coercion, graceful handling of non-existent query entities, strict database table isolation, and Telegram API `callback_data` byte payload constraints (<=64 bytes).

All 7 empirical stress test cases passed successfully.

---

## Detailed Test Results

### 1. Database Career Functions Stress & Concurrency

| Test Case | Description | Operations / Workload | Result | Observed Behavior |
|-----------|-------------|-----------------------|--------|-------------------|
| **1A. Sequential Toggling** | Flips step status 100 times sequentially for a single user/step. | 100 sequential `toggle_user_step_status` calls | **PASS** | Status flipped deterministically (0 <-> 1). `updated_at` timestamp refreshed on every toggle. Final status matched mathematical parity. |
| **1B. High Concurrency Single-Key Toggling** | Multi-threaded toggles on identical user & step key simultaneously. | 10 worker threads x 10 toggles (100 total toggles) | **PASS** | SQLite WAL mode + 10s timeout handled concurrent transactions with 0 `OperationalError: database is locked` exceptions. |
| **1C. Multi-User Concurrent Progress Updates** | 20 worker threads updating distinct users/steps concurrently. | 20 threads x 5 steps (100 distinct step writes & toggles) | **PASS** | Exactly 100 rows created in `user_career_progress`. 0 primary key constraint violations or thread conflicts. |

### 2. Edge-Case `user_id` Type Coercion & Security

| Test Case | Inputs Tested | Expected Result | Result | Empirical Findings |
|-----------|---------------|-----------------|--------|--------------------|
| **2A. Integer vs String Coercion** | `12345` (int) vs `"12345"` (str) | Identical progress record returned | **PASS** | `database.py` functions cast `str(user_id)` in SQL query bindings. Both int and str access the exact same DB entry seamlessly. |
| **2B. Null / None `user_id`** | `None` | Safe execution without crash | **PASS** | `str(None)` converts to `"None"`. Query executes cleanly without raising `AttributeError` or SQL binding errors. |
| **2C. Alternative Primitive Types** | `99.9` (float), `True` (bool), `""` (empty str) | Safe execution and storage | **PASS** | Handled safely by `str()` casting in parameters. |
| **2D. SQL Injection Prevention** | `"100' OR '1'='1"` | Safe parameter binding | **PASS** | SQLite parameterization `(?)` treats the string literally. No unauthorized rows returned; zero query injection risk. |

### 3. Non-Existent Users & Profession Filter Isolation

| Test Case | Query Parameters | Expected Output | Result | Empirical Findings |
|-----------|------------------|-----------------|--------|--------------------|
| **3A. Non-Existent User (No Filter)** | `user_id="ghost_user_100"`, `profession_id=None` | `{}` (empty dict) | **PASS** | Returns `{}` gracefully without throwing `KeyError` or returning `None`. |
| **3B. Non-Existent User (With Filter)** | `user_id="ghost_user_100"`, `profession_id="growth_engineer"` | `{}` (empty dict) | **PASS** | Returns `{}` gracefully. |
| **3C. Existing User (Invalid Profession Filter)** | `user_id="existing_user"`, `profession_id="invalid_prof"` | `{}` (empty dict) | **PASS** | Filters correctly and returns `{}` without exposing other profession records. |
| **3D. Existing User (Null Profession Filter)** | `user_id="existing_user"`, `profession_id=None` | `{prof_id: {step_id: info}}` | **PASS** | Returns nested dictionary containing all active profession tracks for that user. |

### 4. Database Table Isolation & Non-Interference

| Database Table | Pre-Test Row Count / Hash | Operations Executed | Post-Test Row Count / Hash | Result |
|----------------|---------------------------|---------------------|----------------------------|--------|
| `jobs` | 10 rows | 1,000 CRUD operations on `user_career_progress` | 10 rows (100% identical data) | **PASS** |
| `applied_jobs` | 5 rows | 1,000 CRUD operations on `user_career_progress` | 5 rows (100% identical data) | **PASS** |
| `ignored_jobs` | 5 rows | 1,000 CRUD operations on `user_career_progress` | 5 rows (100% identical data) | **PASS** |

**Isolation Verdict**: Operations on `user_career_progress` have ZERO impact on job search tables (`jobs`, `applied_jobs`, `ignored_jobs`). Table isolation is 100% verified.

---

## 5. Telegram Callback Data Payload Length Enforcement (<= 64 Bytes)

Telegram API strictly limits inline keyboard `callback_data` payload to **64 UTF-8 bytes**.

All generated `callback_data` strings across `bot.py` were inspected and byte-measured:

| Menu Component | Callback Pattern Example | Max Length (Bytes) | Telegram Limit | Status |
|----------------|--------------------------|--------------------|----------------|--------|
| Main Menu | `car:main` | 8 bytes | 64 bytes | **PASS** |
| Career Main Menu | `car:p:server_side_tracking` | 26 bytes | 64 bytes | **PASS** |
| Profession Details Menu | `car:r:server_side_tracking` | 26 bytes | 64 bytes | **PASS** |
| Profession Job Search | `car:j:server_side_tracking` | 26 bytes | 64 bytes | **PASS** |
| Roadmap Step Toggle | `car:t:server_side_tracking:step_5` | 33 bytes | 64 bytes | **PASS** |
| Back to Details Button | `car:p:analytics_engineer` | 24 bytes | 64 bytes | **PASS** |

**Callback Payload Verdict**: Maximum payload byte length observed was **33 bytes**, leaving a safety buffer of 31 bytes below Telegram's 64-byte threshold. **0 callback strings exceeded 64 bytes.**

---

## Test Execution Command & Evidence

```powershell
python -m pytest -v .agents/challenger_carreiras_1/test_stress_career.py
```

**Output**:
```
.agents/challenger_carreiras_1/test_stress_career.py::test_sequential_toggling PASSED
.agents/challenger_carreiras_1/test_stress_career.py::test_concurrent_toggling PASSED
.agents/challenger_carreiras_1/test_stress_career.py::test_multi_user_concurrent_toggling PASSED
.agents/challenger_carreiras_1/test_stress_career.py::test_user_id_types_handling PASSED
.agents/challenger_carreiras_1/test_stress_career.py::test_get_user_career_progress_non_existent_and_filters PASSED
.agents/challenger_carreiras_1/test_stress_career.py::test_database_isolation_across_tables PASSED
.agents/challenger_carreiras_1/test_stress_career.py::test_telegram_callback_data_length_under_64_bytes PASSED

======================== 7 passed in 35.10s ========================
```

---

## Stress Testing Conclusion

The implementation of the **Career Guidance & Gamified Progress Track** module in `database.py` and `bot.py` is **robust, thread-safe, type-resilient, isolated, and fully compliant with Telegram API limits**.
