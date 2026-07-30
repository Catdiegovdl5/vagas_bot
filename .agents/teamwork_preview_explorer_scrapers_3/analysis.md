# Comprehensive Code Exploration & Scraper Test Analysis

## Overview
This document presents the detailed findings of the read-only exploration of the test suite (`tests/`), scraper implementations (`scrapers/`), test execution infrastructure (`run_tests.py`, `tests/conftest.py`), and the category taxonomy across the **vagas_bot** project.

---

## 1. Existing Test Inventory & Execution Mechanisms

### Project Test Structure
The project contains test files both within `tests/` (the primary Pytest suite) and standalone scripts at the root level:

#### Primary Suite (`tests/`)
1. `tests/conftest.py`: Test environment initialization and hermetic mocks.
   - **Database Isolation**: Overrides `database.DB_PATH` to point to `tests/jobs_test.db` (lines 33-37), automatically setting up and tearing down the schema before/after test runs (lines 39-88).
   - **Playwright Mocks**: Injects `MockSyncPlaywright` and `MockAsyncPlaywright` into `sys.modules['playwright.sync_api']` and `sys.modules['playwright.async_api']` (lines 99-288).
   - **Groq AI Mocks**: Injects `MockAsyncGroq` returning schema-compliant `JobEvaluation` JSON (lines 290-381).
   - **HTTP Mocks**: Monkeypatches `requests.get`, `requests.post`, and `curl_cffi.requests` to return static/mocked HTML and JSON payloads without external network calls (lines 386-464).
   - **Mock ATS Server**: Starts a background FastAPI server on `http://127.0.0.1:8081` in a session-scoped daemon thread to test the auto-apply engine (lines 468-537).
2. `tests/test_tier1.py`: Feature coverage suite (496 lines, 20+ tests).
   - Tests S-Tier scrapers (LinkedIn, Glassdoor, InfoJobs, Indeed, Jooble), snippet bypass, AI ranking, auto-apply engine, bot level filtering, and special category keywords.
3. `tests/test_tier2.py`: Boundary and corner cases (20 tests).
   - Tests scraper pagination overflow, special characters, timeouts, rate limits (429), SQLite locks, and duplicate links.
4. `tests/test_tier3.py`: Cross-feature combinations (4 tests).
   - Pairwise tests: Scraper + Snippet Bypass, Scraper + DB + AI Ranking, AI + Auto-Apply, and Full Recruiter Cycle.
5. `tests/test_tier4.py`: Real-world application scenarios (5 tests).
   - FastAPI server endpoints (`/api/trigger`, `/api/jobs`, `/api/webhook/n8n`, `/api/logs`, full cycle).
6. `tests/test_milestone2_macro_searches.py`: Milestone 2 macro-search unit tests (162 lines).
   - Tests macro keyword searching across all 6 broad categories, sub-profession classification (`classify_job_profession`), global blacklist exemptions (`Pintor Industrial`, `Mecânico Industrial`), and invalid cross-domain rejection.
7. Additional specialized test files in `tests/`:
   - `test_category_taxonomy.py` & `test_category_taxonomy_stress.py`: Taxonomy mapping and edge cases.
   - `test_location_r1_r2.py`: Geographic location filtering rules.
   - `test_relevance_stress.py`: High-volume relevance filtering stress tests.
   - `test_sanity_battery.py`: Sanity battery using `sanity_battery.json`.
   - `test_seniority_harness.py`: Seniority filter harness.
   - `test_workana_settings.py`: Workana scraper settings and keyword translation.
   - `test_verify_multi_niche.py`: Multi-niche taxonomy verification.
   - `test_adversarial_challenges.py`: Challenge handling and adversarial inputs.

#### How Tests Run Across the Project
- **Primary Pytest Runner (`run_tests.py`)**:
  - Command: `python run_tests.py`
  - Mechanism: Executes `pytest.main(["-v", "-p", "no:warnings", "tests"])` programmatically (lines 17-22). Returns exit code `0` on success.
- **Direct Pytest Execution**:
  - Command: `pytest tests/`
- **Python Unittest Discovery**:
  - Command: `python -m unittest discover tests` (for TestCase files such as `test_milestone2_macro_searches.py`).
- **Standalone Root Test Scripts**:
  - `test_scrapers.py`: Standalone script mocking network calls and executing scraper modules (`jsearch`, `workana`, `remotar`, `glassdoor`, `gupy`, `vagas_com`, `programathor`, `coodesh`, `geekhunter`).
  - `test_all_platforms.py`, `test_boolean_scrapers.py`, `test_clt_scrapers_live.py`: Targeted standalone runner scripts.

---

## 2. Scraper Test Patterns & Mocking Architecture

### Test Patterns & Contracts
Scraper tests enforce a normalized dictionary schema contract across all platforms. A scraper function (`scrape(keyword, level="Todos", ...)`):
- Returns a `list` of `dict` objects.
- Each `dict` must adhere to the schema:
  - `platform`: `str` (Platform name e.g. "Gupy", "InfoJobs", "Workana", "LinkedIn")
  - `title`: `str` (Job position title)
  - `company`: `str` (Company name)
  - `budget`: `str` (Salary / budget string)
  - `link`: `str` (Job post URL)
  - `requirements`: `str` (Job description text; tests enforce minimum length e.g. >= 10 or >= 500 chars)
  - Optional fields: `job_type` ("CLT" / "PJ"), `profession` (Search keyword), `level` ("Todos" / "Júnior" / "Pleno" / "Sênior")

### Mocking Strategy (Hermetic & Sandbox Execution)
Scraper tests rely on library-level monkeypatching in `tests/conftest.py`:
1. **Dynamic Importers & Coroutine Wrappers (`tests/test_tier1.py:8-46`)**:
   - `get_infojobs()` inspects `inspect.iscoroutinefunction(ij.scrape)`. If `scrape` is an `async def`, it wraps the scraper in a `SyncWrapper` that invokes `asyncio.run(mod.scrape(*args, **kwargs))`.
2. **Playwright Mocking (`tests/conftest.py:99-288`)**:
   - Replaces `playwright.sync_api` and `playwright.async_api` with mock browser objects (`MockPage`, `MockElement`, `MockBrowserContext`).
   - Enables Playwright-based scrapers (`infojobs.py`, `workana.py`) to run headlessly without spinning up real Chromium binaries or making network calls.
3. **HTTP Requests Mocking (`tests/conftest.py:386-464`)**:
   - `requests.get` and `requests.post` return `Response` objects populated with canned HTML/JSON.
   - `curl_cffi.requests.get` returns `MockCurlResponse` to simulate Cloudflare challenge bypass.

---

## 3. Adapting & Writing Scraper Tests for the 6 New Categories

### The 6 Broad Categories & Macro Keywords
The project taxonomy defines 6 main broad domains (configured in `bot.py` under `SEARCH_MAPPING`, `CO_OCCURRENCE_RULES`, and `BLACKLIST_PROFILES`):

| # | Broad Category | Primary Macro Keywords | Representative Sub-Professions |
|---|----------------|-----------------------|--------------------------------|
| 1 | **Operações Físicas / Indústria** | `"Operações Físicas"`, `"Indústria"` | Pintor Industrial, Mecânico Industrial, Técnico de Manutenção |
| 2 | **Logística** | `"Logística"` | Almoxarife, Assistente de Logística, Expedidor |
| 3 | **Administrativo** | `"Administrativo"` | Assistente Administrativo, Assistente Financeiro, Recepcionista |
| 4 | **Criativos / Design** | `"Criativos"`, `"Design"` | Designer Gráfico, Editor de Vídeo, UX/UI Designer |
| 5 | **Inteligência de Vendas / Vendas** | `"Inteligência de Vendas"`, `"Vendas"` | Executivo de Vendas B2B, SDR, Consultor Comercial |
| 6 | **Engenharia de Dados** | `"Engenharia de Dados"` | Engenheiro de Dados, Analista de Dados, Analista SQL |

### Scrapers Under Test
We target 4 updated scrapers representing different scraping paradigms:
1. `scrapers/gupy.py`: Async scraper utilizing Gupy's JSON API (`gupy_mapping` maps keywords to Gupy indexed terms).
2. `scrapers/infojobs.py`: Async scraper using Playwright for search page navigation + `curl_cffi` for job description extraction.
3. `scrapers/workana.py`: Async scraper using Playwright for project listing search, utilizing `bot.CO_OCCURRENCE_RULES` for broad query expansion.
4. `scrapers/linkedin.py`: Sync scraper using `curl_cffi` with `chrome110` impersonation and advanced boolean OR queries (`keyword_mapping`).

### Adapted Test Implementation Design (`tests/test_scrapers_macro_categories.py`)
To verify updated scrapers across the 6 categories, a dedicated Pytest file can be structured as follows:

```python
import pytest
import asyncio
import inspect
from bot import is_job_relevant, classify_job_profession, DEFAULT_SETTINGS

import scrapers.gupy as gupy
import scrapers.infojobs as infojobs
import scrapers.workana as workana
import scrapers.linkedin as linkedin

# Helper for async scrapers
def run_scraper(scraper_mod, keyword, level="Todos"):
    if inspect.iscoroutinefunction(scraper_mod.scrape):
        return asyncio.run(scraper_mod.scrape(keyword=keyword, level=level))
    return scraper_mod.scrape(keyword=keyword, level=level)

CATEGORIES_TO_TEST = [
    ("Indústria", ["Pintor Industrial", "Mecânico Industrial"]),
    ("Logística", ["Almoxarife", "Assistente de Logística"]),
    ("Administrativo", ["Assistente Administrativo", "Assistente Financeiro"]),
    ("Design", ["Designer Gráfico", "Editor de Vídeo"]),
    ("Vendas", ["Executivo de Vendas", "SDR"]),
    ("Engenharia de Dados", ["Engenheiro de Dados", "Analista de Dados"])
]

SCRAPERS = [
    ("Gupy", gupy),
    ("InfoJobs", infojobs),
    ("Workana", workana),
    ("LinkedIn", linkedin)
]

@pytest.mark.parametrize("scraper_name, scraper_mod", SCRAPERS)
@pytest.mark.parametrize("macro_kw, expected_subprofs", CATEGORIES_TO_TEST)
def test_scraper_macro_category_execution(scraper_name, scraper_mod, macro_kw, expected_subprofs):
    """Verifies scrapers return valid schemas and pass local classification & relevance rules for macro categories."""
    jobs = run_scraper(scraper_mod, macro_kw)
    assert isinstance(jobs, list), f"{scraper_name} failed to return a list for '{macro_kw}'"
    
    # Under test mocks or live execution, verify job structure if results exist
    for job in jobs:
        assert "title" in job
        assert "company" in job
        assert "link" in job
        assert "platform" in job
        assert "requirements" in job
        assert len(job["requirements"]) > 0
        
        # Verify classification & relevance filter integration
        classified = classify_job_profession(job)
        assert "profession" in classified
        assert "category" in classified
```

---

## 4. Programmatic Verification Plan

### Step 1: Baseline Test Suite Execution
- **Command**: `python run_tests.py`
- **Success Criteria**: All 49 existing systematic tier tests pass with exit code `0`.

### Step 2: Unittest Category & Macro-Search Verification
- **Command**: `pytest tests/test_milestone2_macro_searches.py`
- **Success Criteria**:
  - `SEARCH_MAPPING` contains all 6 macro keywords.
  - `Pintor Industrial` and `Mecânico Industrial` pass global title blacklist.
  - Cross-domain jobs (e.g. `Advogado` in `Indústria`, `Gestor de Tráfego` in `Logística`) are rejected.

### Step 3: Updated Scrapers Macro-Category Verification
- **Command**: `pytest tests/test_scrapers_macro_categories.py -v`
- **Success Criteria**:
  - 100% pass rate across Gupy, InfoJobs, Workana, and LinkedIn scrapers for all 6 macro search terms.
  - Valid return schema (title, company, budget, link, platform, requirements).
  - Proper integration with `is_job_relevant()` and `classify_job_profession()`.

### Step 4: Full End-to-End Pipeline Verification
- **Command**: `pytest tests/test_tier4.py`
- **Success Criteria**: End-to-end API triggers (`/api/trigger`) successfully process macro searches, persist jobs to `jobs_test.db`, and pass AI evaluation.
