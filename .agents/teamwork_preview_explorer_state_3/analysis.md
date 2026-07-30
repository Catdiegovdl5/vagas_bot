# Analysis Report: Location Filtering Test Suite & Test Harness Architecture

**Author**: Explorer 3 (retried)  
**Date**: 2026-07-21  
**Working Directory**: `C:/Users/99196/OneDrive/Documentos/vagas_bot/.agents/teamwork_preview_explorer_state_3`  
**Target Project**: `C:/Users/99196/OneDrive/Documentos/vagas_bot`

---

## Executive Summary

This report provides a comprehensive investigation of the existing unit/integration test suite, test harness architecture, and end-to-end location filtering mechanisms in `vagas_bot`. It establishes:
1. An exhaustive inventory of existing root-level test scripts (including `test_location_uf.py`) and `tests/` directory files.
2. An analysis of how location parameter propagation functions from `static/index.html` frontend triggers through `app.py` `/api/trigger` to backend `is_job_relevant` in `bot.py`.
3. An audit of Brazilian state (UF) mapping dictionaries across Python (`UF_MAP` in `bot.py`) and JavaScript/HTML (`#state-select` in `static/index.html`).
4. A complete, runnable test script specification (`test_location_state.py`) designed and validated to cover parameter passing, UF map completeness, remote job preservation, and state/city matching with word boundary regex protection.

---

## 1. Existing Test File Inventory & Test Harness Setup

### Root Level Test Scripts
The project root contains multiple standalone test and verification scripts:
- **`test_location_uf.py`**: (131 lines, 6,193 bytes) Validates `is_job_relevant` with real simulated jobs across SP, RJ, MG, PR, RS, SC, BA, DF, remote jobs, and word boundary anti-false-positive regex (e.g. checking that "Especialista" does not trigger "SP"). Executed successfully with 21/21 passing tests.
- **`test_all_platforms.py`**: Scraper availability and integration testing across 16+ platforms.
- **`test_boolean_scrapers.py`**: Boolean query string parser & scraper filter validation.
- **`test_bot.py`**: Telegram bot handler & menu navigation unit tests.
- **`test_carreiras.py`**: Career guide roadmap data & step progress tracking tests.
- **`test_clt_scrapers_live.py`**: Live network scraper execution tests for CLT platforms.
- **`test_experience.py`**: Experience level extraction & seniority filter checks.
- **`test_filter_validation.py`**: Parameter validation & edge case input sanitization.
- **`test_iniciantes.py`**: Special beginner mode ("Iniciantes Tudo") filter verification.
- **`test_keywords.py`**: Keyword search mapping (`SEARCH_MAPPING`) & co-occurrence rules verification.
- **`test_menu_expansion.py`**: UI button markup expansion tests.
- **`test_motor.py`**: Core matching engine tests (`is_job_relevant`, title normalization, blacklist).
- **`test_relevance_fixed.py`**: Regression testing for job relevance logic.
- **`test_saas.py`**: Web API endpoint availability test.
- **`test_scrapers.py`**: Mocked unit tests for individual scrapers (`scrapers/gupy.py`, `scrapers/catho.py`, etc.).
- **`test_seniority_filter.py`**: Seniority level (Júnior, Pleno, Sênior) boundary tests.

### `tests/` Subdirectory Architecture
The `tests/` directory hosts a structured test harness using Pytest:
- **`tests/conftest.py`**: Shared Pytest fixtures, mock DB initializers, and environment setups.
- **`tests/mock_auto_apply.py`**, **`tests/mock_glassdoor.py`**, **`tests/mock_infojobs.py`**: Mocking layers for external API/HTTP dependencies.
- **`tests/sanity_battery.json`**: Baseline json test dataset for deterministic validation.
- **`tests/test_tier1.py`** to **`tests/test_tier4.py`**: Tiered test execution pipeline.
- **`tests/test_seniority_harness.py`**, **`tests/test_relevance_stress.py`**, **`tests/test_adversarial_challenges.py`**: Stress and adversarial edge-case test suites.

---

## 2. Location Filtering Parameter Flow & End-to-End Testability

### Flow Architecture
```
[Frontend UI: static/index.html]
    │  - Dropdown #state-select (27 UFs: SP, RJ, MG...)
    │  - Input #loc-input / Modal #hunt-loc
    │  - Function submitSearch()
    ▼
[POST /api/trigger in app.py]
    │  - JSON Payload: {"keyword": "...", "location": "SP", "level": "...", "platforms": [...]}
    │  - Extracts: location = data.get("location", "Todos")
    │  - Background task: run_hunt_background()
    ▼
[Scraper Execution & Filtering in app.py]
    │  - Calls module.scrape(keyword=keyword, level=level, max_pages=10)
    │  - Constructs settings = {"level": level, "location": location, ...}
    │  - Calls is_job_relevant(job, keyword, settings) for each scraped job
    ▼
[Backend Engine in bot.py: is_job_relevant]
    │  - Parses user_location = settings.get('location')
    │  - Checks UF_MAP dictionary for expanded keywords (e.g. "sp" -> ["sao paulo"])
    │  - Applies word boundary regex loc_word_match(text, kw)
    │  - Preserves 100% remote / freelance jobs regardless of state filter
    ▼
[Database Insertion]
    │  - Only relevant jobs are persisted via insert_jobs(filtered_jobs)
```

### Programmatic Testing Methods
1. **Backend REST API Endpoint Testing**:
   Using `fastapi.testclient.TestClient`, we post a JSON payload with `"location": "SP"` to `/api/trigger`. We mock `bot.is_job_relevant` to record the `settings` argument and verify `settings['location'] == 'SP'`.
2. **Frontend Structural & Filter Testing**:
   We inspect `static/index.html` structure to verify `<select id="state-select">` options and test JavaScript `filterData()` logic which checks `normTitle`, `normReq`, `normCompany`, and `normLoc` against `locQuery`.
3. **Core Engine Unit Testing**:
   We pass synthetic job objects with diverse locations, descriptions, and platforms to `is_job_relevant` with specific `settings` to verify matching accuracy and remote preservation.

---

## 3. Brazilian UF Mapping Audit (Python & Frontend)

### Python `UF_MAP` in `bot.py`
The `UF_MAP` dictionary (defined around line 2018 of `bot.py`) contains all 27 Brazilian federative units (26 states + 1 federal district):
| UF | Primary Name / Keywords | Capital / Main Cities Included |
|----|-------------------------|--------------------------------|
| **SP** | `"sao paulo"` | São Paulo |
| **RJ** | `"rio de janeiro"` | Rio de Janeiro |
| **MG** | `"minas gerais"` | Belo Horizonte |
| **PR** | `"parana"` | Curitiba, Londrina |
| **RS** | `"rio grande do sul"` | Porto Alegre |
| **SC** | `"santa catarina"` | Florianópolis |
| **BA** | `"bahia"` | Salvador |
| **PE** | `"pernambuco"` | Recife |
| **CE** | `"ceara"` | Fortaleza |
| **DF** | `"distrito federal"` | Brasília |
| **ES** | `"espirito santo"` | Vitória |
| **GO** | `"goias"` | Goiânia |
| **MA** | `"maranhao"` | São Luís |
| **MT** | `"mato grosso"` | Cuiabá |
| **MS** | `"mato grosso do sul"` | Campo Grande |
| **PA** | `"para"` | Belém |
| **PB** | `"paraiba"` | João Pessoa |
| **AM** | `"amazonas"` | Manaus |
| **RN** | `"rio grande do norte"` | Natal |
| **AL** | `"alagoas"` | Maceió |
| **PI** | `"piaui"` | Teresina |
| **SE** | `"sergipe"` | Aracaju |
| **RO** | `"rondonia"` | Porto Velho |
| **TO** | `"tocantins"` | Palmas |
| **AC** | `"acre"` | Rio Branco |
| **AP** | `"amapa"` | Macapá |
| **RR** | `"roraima"` | Boa Vista |

### Frontend `#state-select` Dropdown in `static/index.html`
The HTML dropdown contains `<option value="UF">State Name (UF)</option>` for all 27 UFs plus an `Exterior` option.

---

## 4. Design & Execution of `test_location_state.py`

A dedicated, standalone test script `test_location_state.py` was created in `.agents/teamwork_preview_explorer_state_3/test_location_state.py`.

### Key Assertions Tested & Results:
1. **Endpoint Parameter Propagation**: Posted request to FastAPI `/api/trigger` with `"location": "SP"`. Confirmed status 200 and verified `settings["location"] == "SP"` was received by `is_job_relevant`. `[PASSOU]`
2. **UF Mapping Completeness Audit**:
   - `UF_MAP` in `bot.py` verified for all 27 Brazilian UFs (`AC`, `AL`, `AM`, `AP`, `BA`, `CE`, `DF`, `ES`, `GO`, `MA`, `MG`, `MS`, `MT`, `PA`, `PB`, `PE`, `PI`, `PR`, `RJ`, `RN`, `RO`, `RR`, `RS`, `SC`, `SE`, `SP`, `TO`). `[PASSOU]`
   - Dropdown `#state-select` in `static/index.html` verified for all 27 UFs. `[PASSOU]`
3. **Job Filtering & Remote Job Preservation**:
   - 100% Remote jobs (Gupy, Workana, Remotar) tested with filters `SP`, `AM`, `RS`, `CE` -> All returned `True`. `[PASSOU]`
   - Presencial jobs matched by UF abbreviation (`"São Paulo - SP"`), full state name (`"Minas Gerais"`), or capital/main city (`"Curitiba"`, `"Salvador"`) -> All returned `True`. `[PASSOU]`
   - Presencial jobs from state A (e.g. SP, PR) tested against state B (e.g. RJ, SC) -> Returned `False`. `[PASSOU]`
   - Word boundary substring anti-false-positive check (`"Especialista"` in RJ tested against filter `SP`) -> Returned `False`. `[PASSOU]`

---

## 5. Recommendations & Execution Commands

### Commands to Run Test Suite

To run the standalone location UF unit test:
```bash
python test_location_uf.py
```

To run the complete location state test suite created in this task:
```bash
python .agents/teamwork_preview_explorer_state_3/test_location_state.py
```

To run the entire test suite using Pytest:
```bash
python -m pytest tests/ -v
```

### Recommendation for Project Integration
Move or copy `.agents/teamwork_preview_explorer_state_3/test_location_state.py` into the root `test_location_state.py` or `tests/test_location_state.py` in the main codebase during implementation/testing phases.
