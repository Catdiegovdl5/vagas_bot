# Forensic Audit Report

**Work Product**: 9 Scrapers (Jsearch, Workana, Remotar, Glassdoor, Gupy, Vagas Com, Programathor, Coodesh, Geekhunter), `bot.py`, `test_scrapers.py`
**Profile**: General Project
**Verdict**: CLEAN

### Phase Results
- **Hardcoded test results check**: PASS — Source code files do not contain hardcoded test results or pre-fabricated status checks.
- **Facade detection check**: PASS — Scrapers implement full parsing logic (JSON, BeautifulSoup, Playwright) instead of returning simple static constants.
- **Fabricated verification outputs check**: PASS — No pre-populated execution logs or result files exist. All tests run dynamically.
- **Self-certifying tests check**: PASS — Scrapers do not self-certify; test files define independent assertions.
- **Execution delegation check**: PASS — Scrapers directly fetch and extract job details from the target platform APIs or websites, rather than delegating the core task to pre-built external tools.

---

### Phase 1: Source Code Analysis

1. **Jsearch (`scrapers/jsearch.py`)**: Genuinely builds query requests targeting `jsearch.p.rapidapi.com` with API key headers. Parses JSON data and extracts attributes matching schema.
2. **Workana (`scrapers/workana.py`)**: Performs request to `workana.com/jobs`, parses search elements using `BeautifulSoup`, decodes Vue initial JSON payload (`:results-initials`), and extracts projects.
3. **Remotar (`scrapers/remotar.py`)**: Consumes the public REST API `api.remotar.com.br/jobs` using standard client and BeautifulSoup tag cleaning.
4. **Glassdoor (`scrapers/glassdoor.py`)**: Uses Playwright browser automation to load vacancy endpoints, bypass basic anti-bot, query element trees via selectors, and click cards to reveal details.
5. **Gupy (`scrapers/gupy.py`)**: Fetches Gupy employability-portal REST API or parses Next.js JSON state block (`__NEXT_DATA__`) inside page HTML.
6. **Vagas.com (`scrapers/vagas_com.py`)**: Queries vagas.com.br list page and crawls job cards matching class pattern `vaga` dynamically.
7. **Programathor (`scrapers/programathor.py`)**: Searches text criteria on programathor.com.br and iterates through `.cell-list` divisions.
8. **Coodesh (`scrapers/coodesh.py`)**: Queries JSON-based Coodesh REST API endpoint (`api.coodesh.com/v2/jobs`) with headers.
9. **Geekhunter (`scrapers/geekhunter.py`)**: Scrapes job listings dynamically from geekhunter.com HTML tags using BeautifulSoup classes.
10. **Bot.py (`bot.py`)**: Handles TG message commands. Dynamically resolves scrapers and passes configurations (location, seniority level, contract mode) without hardcoding results.

### Phase 2: Behavioral Verification

#### 1. Pytest suite execution (`python run_tests.py`)
- **Status**: PASSED
- **Exit Code**: 0
- **Total Tests**: 56 passed in 21.65 seconds.
- **Selected Outputs**:
```
tests/test_adversarial_challenges.py::test_senior_candidate_with_experience_job PASSED
tests/test_adversarial_challenges.py::test_graduate_candidate_with_degree_job PASSED
tests/test_adversarial_challenges.py::test_foreign_currency_and_english_leakage PASSED
tests/test_sanity_battery.py::test_sanity_battery_zero_approval PASSED
tests/test_seniority_harness.py::test_do_hunt_keyword_transformation_levels PASSED
tests/test_seniority_harness.py::test_do_hunt_concurrency_and_performance PASSED
tests/test_tier1.py::... PASSED
tests/test_tier2.py::... PASSED
tests/test_tier3.py::... PASSED
tests/test_tier4.py::... PASSED
============================= 56 passed in 21.65s =============================
```

#### 2. Scrapers integration execution (`python test_scrapers.py`)
- **Status**: PASSED
- **Exit Code**: 0
- **Selected Outputs**:
```
--- Running Jsearch Scraper ---
[Jsearch] Found 1 jobs.
[Jsearch] PASS

--- Running Workana Scraper ---
[Workana] Found 2 jobs.
[Workana] PASS

--- Running Remotar Scraper ---
[Remotar] Found 1 jobs.
[Remotar] PASS

--- Running Glassdoor Scraper ---
[Glassdoor] Found 1 jobs.
[Glassdoor] PASS

--- Running Gupy Scraper ---
[Gupy] Found 1 jobs.
[Gupy] PASS

--- Running Vagas Com Scraper ---
[Vagas Com] Found 1 jobs.
[Vagas Com] PASS

--- Running Programathor Scraper ---
[Programathor] Found 1 jobs.
[Programathor] PASS

--- Running Coodesh Scraper ---
[Coodesh] Found 1 jobs.
[Coodesh] PASS

--- Running Geekhunter Scraper ---
[Geekhunter] Found 1 jobs.
[Geekhunter] PASS

All scrapers verified successfully! Verification finished without errors.
```

---

### Evidence
The audit was performed on a clean local clone of `vagas_bot`. Below are the actual execution logs of the test suites running under local system environment:
- Pytest task logs location: `file:///C:/Users/99196/.gemini/antigravity/brain/755e13ce-c543-4318-8bec-d38e05fbca16/.system_generated/tasks/task-21.log`
- Git status output: Shows modifications only in scraper files and test scripts, matching expectations without dirty tricks or test-result pre-generation.
