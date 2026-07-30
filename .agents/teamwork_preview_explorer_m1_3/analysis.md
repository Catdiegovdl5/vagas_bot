# Audit Report: Remote Job Retention & Test Infrastructure

**Explorer**: Explorer 3 (Integration & Test Explorer replacement)  
**Target Directory**: `C:/Users/99196/OneDrive/Documentos/vagas_bot`  
**Date**: 2026-07-21  

---

## 1. Executive Summary

A comprehensive audit of **Remote Job Retention** (frontend & backend location filtering) and **Test Infrastructure setup** in `vagas_bot` was conducted.

### Core Findings
1. **Frontend Discrepancy & Defect in `static/index.html`**:
   - While 100% remote jobs are correctly identified by `getJobWorkModel(j) === 'remoto'`, the current client-side `filterData()` function calculates location matching via simple string inclusion (`normLoc.includes(locQuery) || normTitle.includes(locQuery) ...`).
   - When any state/UF filter (e.g., SP, RJ, MG, PR, RS) is active in `#state-select`, `#loc-input` is populated with the 2-letter state acronym.
   - Jobs tagged as **100% Remote** (e.g. location text `"Brasil (Remoto)"`, `"Home Office"`) that do not explicitly contain the state acronym (e.g. `"SP"`) **are erroneously filtered out and hidden from the user interface**.
2. **Backend Remote Retention in `bot.py`**:
   - The backend `is_job_relevant(job, keyword, settings)` in `bot.py` **ALREADY implements Remote Job Retention**. Remote jobs (`is_remote_term`, `is_freelance_platform`, `is_remote_default_platform`) bypass state location checks and return `True` for any selected state.
3. **Backend Location Parameter Passing in `app.py`**:
   - `app.py` `/api/trigger` receives `location`, `keyword`, `level`, and `platforms`. It passes `location` to `is_job_relevant()` during background post-scraping filtration, but does not pass `location` to individual `module.scrape()` functions (except for country-capable scrapers).
4. **Test Infrastructure Status**:
   - Root test script `test_location_uf.py` contains 21 unit tests verifying backend UF filtering and Remote Job Retention in `bot.py` (All 21 tests PASS).
   - Comprehensive E2E test battery under `tests/` contains 69 tests covering scrapers, snippet bypass, AI ranking, auto-apply, and API endpoints.
   - **Gap**: There is currently no programmatic automated test verifying frontend JavaScript location filter retention (`static/index.html`) or end-to-end frontend/backend location state consistency.

---

## 2. Detailed Audit: Remote Job Retention in Frontend (`static/index.html`)

### 2.1 Remote Job Identification
In `static/index.html` (lines 689–708), 100% remote jobs are identified via `getJobWorkModel(job)`:
```javascript
function getJobWorkModel(job) {
    const title = (job.title || '').toLowerCase();
    const reqs = (job.requirements || '').toLowerCase();
    const loc = (job.location || '').toLowerCase();
    
    const norm = (title + ' ' + reqs + ' ' + loc).normalize('NFD').replace(/[\u0300-\u036f]/g, '');

    const hasHybrid = /\b(hibrid[oa]s?|hybrid)\b/.test(norm);
    const hasRemote = /\b(remot[oa]s?|home\s*office|remote|teletrabalho|wfh|work\s*from\s*home|anywhere)\b/.test(norm);
    
    const normPresential = norm.replace(/\b(nao|não)\s+(e\s+)?presencia[li]s?\b/g, '');
    const hasPresential = /\b(presencia[li]s?|onsite|on-site)\b/.test(normPresential);

    if (hasHybrid) return 'hibrido';
    if (hasRemote && !hasPresential) return 'remoto';
    if (hasPresential && !hasRemote) return 'presencial';
    if (hasRemote) return 'remoto';
    if (hasPresential) return 'presencial';
    return 'outros';
}
```
* **Observation**: `getJobWorkModel(job)` correctly classifies jobs as `'remoto'` when remote patterns (`remoto`, `home office`, `remote`, `teletrabalho`, `wfh`, `work from home`, `anywhere`) are detected without presential qualifiers.

### 2.2 Location Filtering Logic (`filterData()`)
In `static/index.html` (lines 1080–1128):
```javascript
function filterData() {
    const query = normStr(document.getElementById('search-input').value);
    const locQuery = normStr(document.getElementById('loc-input').value);
    ...
    viewData = allData.filter(j => {
        const normTitle = normStr(j.title);
        const normReq = normStr(j.requirements);
        const normCompany = normStr(j.company);
        const normLoc = normStr(j.location);
        ...
        let matchLoc = true;
        if (locQuery) {
            matchLoc = normTitle.includes(locQuery) || normReq.includes(locQuery) || normCompany.includes(locQuery) || normLoc.includes(locQuery);
        }
        ...
        return matchQuery && matchLoc && matchPlat && matchCat && matchWm && matchSen;
    });
}
```

### 2.3 Defect & Impact Analysis
- **Scenario**: User selects state **"SP"** (São Paulo) in `<select id="state-select">`.
- **Event Flow**:
  1. `onchange` fires `setLocFilter('SP')`.
  2. `setLocFilter('SP')` sets `#loc-input` value to `"SP"` and invokes `filterData()`.
  3. `locQuery` becomes `"sp"`.
  4. `matchLoc` checks if `"sp"` is contained in `normTitle`, `normReq`, `normCompany`, or `normLoc`.
  5. A job titled `"Desenvolvedor Backend Python"`, company `"TechCorp"`, location `"Brasil (Remoto)"`, requirements `"Vaga 100% remota com contrato CLT."` is processed:
     - `getJobWorkModel(job)` returns `'remoto'`.
     - None of title, requirements, company, or location contains the string `"sp"`.
     - `matchLoc` evaluates to **`false`**.
     - **Result**: The job is **FILTERED OUT** and hidden from the dashboard!
- **Conclusion**: The requirement **"Verify that when any state/UF filter (e.g. SP, RJ, MG) is active, jobs tagged as 100% Remote remain visible"** is **FAILED** in current `static/index.html`.

### 2.4 Proposed Frontend Fix
To ensure 100% remote jobs remain visible when any location/state filter is applied:
```javascript
let matchLoc = true;
if (locQuery) {
    const isRemote = (getJobWorkModel(j) === 'remoto');
    if (isRemote) {
        matchLoc = true; // 100% Remote jobs are retained for all state/UF filters
    } else {
        const locKeywords = getLocKeywords(locQuery); // Expanded state UF keywords
        matchLoc = locKeywords.some(kw => 
            normLoc.includes(kw) || normTitle.includes(kw) || normReq.includes(kw) || normCompany.includes(kw)
        );
    }
}
```

---

## 3. Detailed Audit: Backend Location Pipeline (`app.py` & `bot.py`)

### 3.1 Endpoint `/api/trigger` in `app.py`
In `app.py` (lines 181–232):
- Extracts request payload:
  `keyword = data.get("keyword", "Python")`
  `level = data.get("level", "Todos")`
  `location = data.get("location", "Todos")`
- Background task `run_hunt_background()` invokes scraper modules passing `keyword` and `level`.
- Post-scraping filtering applies `is_job_relevant(job, keyword, settings)` where `settings["location"] = location`.

### 3.2 Backend Remote Job Retention in `bot.py`
In `bot.py` (lines 1998–2014):
```python
if user_location and user_location not in ['todos', 'todas', 'qualquer', 'all']:
    if 'remoto' in user_location:
        if is_freelance_platform or is_remote_default_platform:
            pass
        elif is_remote_term:
            pass
        elif is_presential_term:
            return False
        elif len(job_loc) > 3 and 'brasil' not in job_loc and 'brazil' not in job_loc:
            return False
    else:
        # Vagas 100% remotas ou em plataformas freelance sempre atendem a qualquer cidade
        if is_freelance_platform or is_remote_term or is_remote_default_platform:
            pass
        else:
            ... # UF word boundary matching & state expansion
```
- **Backend Behavior**: When `user_location` is set to a state acronym (e.g. `'sp'`, `'rj'`, `'mg'`), any job classified as remote (`is_remote_term`, `is_freelance_platform`, `is_remote_default_platform`) hits `pass` and bypasses state checks, returning `True`.
- **Status**: Backend Remote Job Retention is **100% COMPLIANT**.

---

## 4. Audit of Test Infrastructure

### 4.1 Root Unit Test (`test_location_uf.py`)
- **Status**: Execution verified (21 tests run, 21 PASSED).
- **Coverage**:
  - Word boundary anti-false-positives (e.g. `especialista` does not match `SP`).
  - Correct state matching (`SP`, `RJ`, `MG`, `PR`, `RS`, `SC`, `BA`, `DF`).
  - Remote jobs retention (`Dev Remoto` passes for `SP`, `RJ`, `AM`; `Freelance Workana` passes for `SP`, `RR`).
  - State cross-rejection (`SP` job rejected under `RJ` filter).

### 4.2 Comprehensive E2E Test Suite (`tests/`)
- **Status**: Execution verified via `python run_tests.py` / `pytest tests/` (69 tests collected).
- **Structure**:
  - `test_tier1.py`: Feature coverage for scrapers, snippet bypass, AI ranking, auto-apply.
  - `test_tier2.py`: Boundary and corner cases.
  - `test_tier3.py`: Cross-feature integration combinations.
  - `test_tier4.py`: Real-world API endpoints (`/api/trigger`, `/api/jobs`, `/api/webhook/n8n`, `/api/logs`).

---

## 5. Programmatic Test Plan for Location Filtering & Remote Retention

To bridge the gap and ensure automated regression coverage for both frontend state filtering and backend parameter passing, the following test plan is proposed:

### 5.1 Test Suite Structure

```
tests/
├── test_frontend_remote_retention.py   # Unit/Integration tests for static/index.html filter logic
└── test_backend_location_pipeline.py  # Integration tests for app.py & bot.py location filtering
```

### 5.2 Test Specifications

#### Module A: `test_frontend_remote_retention.py`
* **Objective**: Validate that `filterData()` in `static/index.html` retains 100% remote jobs when state filters are selected.
* **Implementation Strategy**: Node.js/jsdom runner or Playwright headless browser / Python JS interpreter (`js2py` / `pyexecjs`) evaluating `static/index.html`.
* **Test Cases**:
  1. `test_remote_job_retained_on_state_sp_filter()`: Input synthetic dataset containing 100% Remote job (`location: "Brasil (Remoto)"`). Select `SP` in `#state-select`. Assert job appears in `viewData`.
  2. `test_remote_job_retained_on_state_rj_mg_filter()`: Input 100% Remote job (`location: "Home Office"`). Select `RJ` / `MG`. Assert job appears in `viewData`.
  3. `test_presential_job_filtered_out_on_wrong_state()`: Input presential job (`location: "Curitiba - PR"`). Select `SP`. Assert job is excluded from `viewData`.
  4. `test_presential_job_included_on_correct_state()`: Input presential job (`location: "São Paulo - SP"`). Select `SP`. Assert job appears in `viewData`.
  5. `test_uf_city_expansion()`: Input job located in `"Campinas"`. Select `SP`. Assert job appears in `viewData`.

#### Module B: `test_backend_location_pipeline.py`
* **Objective**: Verify end-to-end location parameter handling from `/api/trigger` to DB storage and `is_job_relevant`.
* **Test Cases**:
  1. `test_api_trigger_location_parameter_pass_through()`: Send POST to `/api/trigger` with `{"location": "SP", "keyword": "Python"}`. Verify `is_job_relevant` receives `settings["location"] == "SP"`.
  2. `test_backend_remote_retention_all_27_ufs()`: Loop over all 27 Brazilian UFs (`AC`, `AL`, `AP`, `AM`, `BA`, `CE`, `DF`, `ES`, `GO`, `MA`, `MT`, `MS`, `MG`, `PA`, `PB`, `PR`, `PE`, `PI`, `RJ`, `RN`, `RS`, `RO`, `RR`, `SC`, `SP`, `SE`, `TO`). Call `is_job_relevant(remote_job, "Python", {"location": uf})`. Assert returns `True` for 27/27 UFs.
  3. `test_backend_presential_cross_state_rejection()`: Call `is_job_relevant(presential_sp_job, "Python", {"location": "RJ"})`. Assert returns `False`.

---

## 6. Summary Matrix

| Audit Item | Current Status | Identified Defect | Remediation Action |
|---|---|---|---|
| **100% Remote Job Identification** | ✅ PASS | None (`getJobWorkModel` parses remote patterns) | Maintain current regex |
| **Frontend Remote Job Retention** | ❌ FAILED | `filterData()` in `index.html` excludes remote jobs when state filter is active | Update `filterData()` to add `isRemote` retention bypass |
| **Backend Remote Job Retention** | ✅ PASS | None (`bot.py` `is_job_relevant` bypasses state check for remote jobs) | Maintain current logic |
| **Backend Location Param Passing** | ✅ PASS | `app.py` passes `location` to `is_job_relevant` | Maintain current endpoint structure |
| **Test Infrastructure Setup** | ✅ PASS | Unit tests (21/21 pass) and E2E battery (69 tests collected) exist | Add proposed `test_frontend_remote_retention.py` script |

