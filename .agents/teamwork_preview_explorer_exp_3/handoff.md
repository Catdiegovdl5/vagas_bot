# Handoff Report: Test Suite Analysis & `test_experience.py` Specification

**Explorer**: Explorer 3 (Milestone 1 — Test Suite & `test_experience.py`)  
**Working Directory**: `C:\Users\99196\OneDrive\Documentos\vagas_bot\.agents\teamwork_preview_explorer_exp_3`  
**Date**: 2026-07-21  

---

## 1. Observation

1. **Repository & File Structure**:
   - Project Root: `C:\Users\99196\OneDrive\Documentos\vagas_bot\`
   - E2E Test Suite Directory: `C:\Users\99196\OneDrive\Documentos\vagas_bot\tests\`
   - E2E Specification Docs: `TEST_INFRA.md` (79 lines), `TEST_READY.md` (65 lines), `PROJECT.md` (40 lines).
   - Core Bot Logic File: `bot.py` (1662 lines), specifically `global_title_blacklist` at line 478 (`"voluntario"`, `"voluntary"` at line 492) and `is_job_relevant` at lines 949-1066.

2. **Existing Test Inventory & Execution Mechanisms**:
   - **Pytest E2E Suite** (Runner: `python run_tests.py` or `pytest tests/`):
     - `tests/conftest.py`: Database sandbox (`jobs_test.db`), Playwright mocks, Groq AI mocks, Mock ATS server lifecycle (`http://127.0.0.1:8081`).
     - `tests/test_tier1.py` (496 lines, 20 tests): Feature coverage (LinkedIn, Glassdoor, InfoJobs, Indeed, Jooble schema, snippet bypass, AI ranking, Auto-Apply).
     - `tests/test_tier2.py` (496 lines, 20 tests): Boundary cases (pagination, timeouts, rate limits 429, DB locks).
     - `tests/test_tier3.py` (120 lines, 4 tests): Cross-feature pairwise combinations.
     - `tests/test_tier4.py` (170 lines, 5 tests): Real-world workflows (`/api/trigger`, `/api/jobs`, `/api/webhook/n8n`, `/api/logs`, Full Cycle).
     - Auxiliary E2E tests: `test_adversarial_challenges.py`, `test_relevance_stress.py`, `test_sanity_battery.py`, `test_seniority_harness.py`, `test_verify_multi_niche.py`, `test_workana_settings.py`.
   - **Standalone Root Scripts** (Runner: `python <script_name>.py`):
     - `test_motor.py` (200 lines): Search motor co-occurrence rules (`CO_OCCURRENCE_RULES`) & false-positive blocking.
     - `test_keywords.py` (115 lines): Unit tests for `is_job_relevant` (approved, rejected, boundary cases).
     - `test_seniority_filter.py` (49 lines): Seniority checks in title vs description.
     - `test_relevance_fixed.py` (61 lines): Niche blacklist checks.
     - `test_filter_validation.py` (85 lines): Live/mock scraper filter verification.
     - Additional scripts: `test_boolean_scrapers.py`, `test_clt_scrapers_live.py`, `test_all_platforms.py`, `test_menu_expansion.py`, `stress_test_safety.py`.

3. **Current `is_job_relevant` Implementation Gap**:
   - `bot.py` lines 955-957 normalizes setting `level`: `user_level = normalize_str(settings.get('level', 'Todos'))`.
   - `bot.py` lines 1016-1027 handles `user_level == 'junior'`, `'pleno'`, `'senior'`, and `'jovem aprendiz'`, but **lacks an explicit `elif user_level == 'ganhar experiencia':` block**.
   - `bot.py` line 492 includes `"voluntario"` in `global_title_blacklist`, causing any job with "voluntário" in the title to be rejected by default, which violates candidate requirements when `user_level = 'ganhar experiência'`.

---

## 2. Logic Chain

1. **Step 1 (Test Suite Cataloging)**: Inspecting `TEST_INFRA.md`, `TEST_READY.md`, `run_tests.py`, and `tests/` confirmed that `python run_tests.py` executes 49 systematic E2E tests using `pytest` against mocked dependencies. Standalone scripts (`test_motor.py`, `test_keywords.py`, etc.) execute direct Python assertions for filtering logic.
2. **Step 2 (Baseline Verification)**: Reviewing test assertions in `test_keywords.py`, `test_seniority_filter.py`, and `tests/test_tier1.py` demonstrates that baseline tests mandate 100% pass rate (exit code 0) for code stability.
3. **Step 3 (Relevance Logic Tracing)**: Tracing `is_job_relevant` in `bot.py` revealed that when `user_level = 'ganhar experiência'`, `normalize_str('ganhar experiência')` produces `'ganhar experiencia'`.
4. **Step 4 (Gap Identification)**:
   - For Acceptance Criteria 1 ("Dev Voluntário em ONG"): Currently rejected because `"voluntario"` is in `global_title_blacklist` (line 492).
   - For Acceptance Criteria 3 ("Dev Júnior 1 ano de experiência"): Currently not filtered out specifically for experience-seekers because `bot.py` lacks a experience requirement parsing check for `user_level == 'ganhar experiencia'`.
5. **Step 5 (Script Design & Specification)**: To validate `user_level = 'ganhar experiência'`, `test_experience.py` is designed as a standalone script executing 4 acceptance criteria test cases + 4 boundary test cases, giving precise pass/fail feedback.

---

## 3. Caveats

1. **Read-Only Constraint**: As Explorer 3, direct edits to `bot.py` or main codebase files were not performed. Implementation code changes for `bot.py` and creation of `test_experience.py` in the root repository are provided as templates/recommendations for the implementer agent.
2. **Execution Permissions**: Permission prompt for terminal execution timed out during exploration turn; baseline status was verified by deep static code inspection of test harnesses, contracts, and runner scripts.
3. **Mock Dependencies**: Pytest E2E tests target local mocks (`jobs_test.db`, HTTP/Playwright stubs) as specified in `TEST_INFRA.md` to guarantee zero network dependency.

---

## 4. Conclusion

- **Baseline Test Suite Status**: Fully audited. E2E tests are executed via `python run_tests.py` (running `pytest tests/`). Standalone motor and relevance scripts are executed via `python <script>.py`.
- **`test_experience.py` Design**: Fully designed and documented in `analysis.md` with 8 test cases (4 Acceptance Criteria + 4 Boundary Cases).
- **Required `bot.py` Updates for Implementer**:
  1. Exception for `"voluntario"` in `active_global_blacklist` when `user_level == 'ganhar experiencia'`.
  2. Addition of `elif user_level == 'ganhar experiencia':` in `is_job_relevant` to block Pleno/Senior roles and positions requiring >= 1 year of prior experience without entry-level suitability.

---

## 5. Verification Method

1. **Run Pytest E2E Baseline**:
   ```bash
   python run_tests.py
   ```
2. **Run Standalone Motor & Keyword Baseline**:
   ```bash
   python test_motor.py
   python test_keywords.py
   ```
3. **Run Experience Test Script (after creation of `test_experience.py`)**:
   ```bash
   python test_experience.py
   ```
   *Expected Output*: `RESULTS SUMMARY: 8/8 tests passed` and exit code `0`.
