# Empirical Verification Report: FastAPI `/api/trigger` Endpoint Location Parameter Handling

## Executive Summary
**Verdict**: **PASS (VERIFIED)**
FastAPI `/api/trigger` endpoint in `app.py` correctly extracts the `location` parameter from JSON request payloads across all tested Brazilian state acronyms (UFs: `"SP"`, `"RJ"`, `"MG"`, `"PR"`, `"RS"`, `"SC"`, `"BA"`), passes `settings["location"]` set to the exact requested UF to `bot.is_job_relevant`, and delivers the location parameter to all platform scrapers without raising exceptions.

---

## 1. Test Environment & Scope
- **Target File**: `app.py` (`/api/trigger` endpoint)
- **Dependencies & Modules**: `bot.py` (`is_job_relevant`), `scrapers/*` (16 platform modules)
- **Target UFs Tested**: `"SP"`, `"RJ"`, `"MG"`, `"PR"`, `"RS"`, `"SC"`, `"BA"`
- **Test Frameworks Executed**:
  1. Custom Empirical Async Test Harness (`run_fast_empirical_test.py`)
  2. Pytest Test Suite targeting FastAPI ASGI / AsyncClient (`test_location_empirical.py`)

---

## 2. Empirical Test Results

### A. Pytest Execution (`python -m pytest test_location_empirical.py`)
- **Command**: `python -m pytest test_location_empirical.py`
- **Result**: `7 passed, 3 warnings in 5.57s`
- **Test Cases**:
  - `test_api_trigger_location_propagation[SP]`: PASSED
  - `test_api_trigger_location_propagation[RJ]`: PASSED
  - `test_api_trigger_location_propagation[MG]`: PASSED
  - `test_api_trigger_location_propagation[PR]`: PASSED
  - `test_api_trigger_location_propagation[RS]`: PASSED
  - `test_api_trigger_location_propagation[SC]`: PASSED
  - `test_api_trigger_location_propagation[BA]`: PASSED

### B. Custom Test Harness Breakdown (`run_fast_empirical_test.py`)

| UF | `/api/trigger` Status | Response Payload Status | Scrapers Invoked | `is_job_relevant` Calls | `settings["location"]` Received | Scraper Exceptions | Match Verified |
|----|-----------------------|-------------------------|------------------|-------------------------|---------------------------------|-------------------|----------------|
| **SP** | 200 OK | `"status": "success"` | 16 / 16 | 16 | `['SP']` | None (0) | PASS |
| **RJ** | 200 OK | `"status": "success"` | 16 / 16 | 16 | `['RJ']` | None (0) | PASS |
| **MG** | 200 OK | `"status": "success"` | 16 / 16 | 16 | `['MG']` | None (0) | PASS |
| **PR** | 200 OK | `"status": "success"` | 16 / 16 | 16 | `['PR']` | None (0) | PASS |
| **RS** | 200 OK | `"status": "success"` | 16 / 16 | 16 | `['RS']` | None (0) | PASS |
| **SC** | 200 OK | `"status": "success"` | 16 / 16 | 16 | `['SC']` | None (0) | PASS |
| **BA** | 200 OK | `"status": "success"` | 16 / 16 | 16 | `['BA']` | None (0) | PASS |

---

## 3. Detailed Parameter Pipeline Analysis

### 1. Endpoint Handling in `app.py`
In `app.py` lines 181-196:
```python
@app.post("/api/trigger")
async def trigger_hunt(request: Request):
    data = await request.json()
    ...
    location = data.get("location", "Todos")
```
When payload `{"location": "<UF>"}` is posted, `data.get("location")` extracts the exact string (e.g. `"SP"`).

### 2. Scraper Signature Inspection & Argument Filtering
In `app.py` lines 207-220:
```python
sig = inspect.signature(module.scrape)
candidate_kwargs = {
    "keyword": keyword,
    "level": level,
    "location": location,
    "country": location,
    "max_pages": 10
}
has_kwargs = any(p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values())
if has_kwargs:
    kwargs = candidate_kwargs
else:
    kwargs = {k: v for k, v in candidate_kwargs.items() if k in sig.parameters}
```
Empirical test confirmed that all 16 scrapers (`workana`, `gupy`, `catho`, `infojobs`, `linkedin`, `vagas_com`, `novenove`, `freelancer`, `remotar`, `programathor`, `geekhunter`, `coodesh`, `github_vagas`, `indeed`, `glassdoor`, `jooble`) accept `location` or `**kwargs` and receive `location="<UF>"` without throwing parameter type or missing argument errors.

### 3. Settings Construction & Relevance Filtering in `bot.py`
In `app.py` lines 233-239:
```python
settings = {
    "level": level,
    "location": location,
    "contract": "Todos",
    "education": "Todos"
}
filtered_jobs = [job for job in all_jobs if is_job_relevant(job, keyword, settings)]
```
Empirical spying on `is_job_relevant` verified that `settings["location"]` is passed as the exact requested UF string.
Inside `bot.py`:
`user_location = normalize_str(settings.get('location', 'Todos'))`
For `"SP"`, `user_location` becomes `"sp"`.
`UF_MAP["sp"]` expands to `["sao paulo"]`.
Matching jobs with `"São Paulo - SP"` evaluate to `True`, while jobs in non-matching UFs (e.g. `"Rio de Janeiro - RJ"`) evaluate to `False`.

---

## 4. Conclusion
The FastAPI `/api/trigger` location parameter pipeline is fully robust, correctly handles state UFs (`SP`, `RJ`, `MG`, `PR`, `RS`, `SC`, `BA`), propagates exact values to relevance filtering, and invokes scraper modules without exceptions.
