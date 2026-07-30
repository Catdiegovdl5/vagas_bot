# Code Review Report — R1 Location Parameter Implementation

**Reviewer**: Reviewer 1 (reviewer_critic)
**Date**: 2026-07-21
**Verdict**: **PASS / APPROVE**

---

## 1. Executive Summary

A comprehensive code review and adversarial analysis was conducted on the R1 changes in `app.py` and all scraper modules in `scrapers/*.py`. The implementation of the `location` parameter is robust, backward-compatible, and well-integrated across the application stack.

---

## 2. Review Checklist Verification

### Item 1: `app.py` `run_hunt_background` Location Extraction & Repass
- **Extraction**: `location = data.get("location", "Todos")` correctly extracts the parameter from incoming request payloads.
- **Dynamic Passing**: `candidate_kwargs` packs `location` and `country`. Uses `inspect.signature(module.scrape)` to verify if scrapers accept `**kwargs` (`Parameter.VAR_KEYWORD`) or specific parameters, filtering accordingly before invocation.
- **Async/Sync Support**: Correctly checks `inspect.iscoroutinefunction(module.scrape)` and invokes scrapers via `await module.scrape(**kwargs)` or offloads via `asyncio.to_thread(module.scrape, **kwargs)`.
- **Downstream Relevance**: `location` is passed in `settings` (`settings = {"level": level, "location": location, ...}`) to `bot.is_job_relevant()` for precise location/state filtering.
- **Status**: **VERIFIED - PASS**

### Item 2: `scrapers/*.py` Function Signatures & Location Query Usage
- **Signatures**: All scraper modules (`catho`, `coodesh`, `freelancer`, `geekhunter`, `github_vagas`, `glassdoor`, `gmail`, `gupy`, `indeed`, `infojobs`, `jooble`, `jsearch`, `linkedin`, `meta_ads`, `novenove`, `programathor`, `remotar`, `vagas_com`, `workana`) have updated signatures accepting `location=""`, `country=""`, and `**kwargs`.
- **URL / Query Construction**:
  - `catho.py`, `freelancer.py`, `github_vagas.py`, `jsearch.py`, `novenove.py`: Appends non-generic location strings (`f" {loc}"`) to search queries.
  - `indeed.py`, `linkedin.py`: Maps specific cities (e.g. Londrina, Assaí) and custom locations into platform-native location URL parameters (`&l=...`, `location=...`).
  - `jooble.py`: Passes target location to the Jooble API search payload.
  - National/Global platforms (`gupy`, `coodesh`, `geekhunter`, `workana`, `remotar`): Process queries and delegate state/city precision to `bot.is_job_relevant()`.
- **Country Filter**: Scrapers checking for Brazil restriction correctly validate `if loc and loc.upper() in ["USA", "US", "UNITED STATES"]`.
- **Status**: **VERIFIED - PASS**

### Item 3: Error Handling & Backward Compatibility
- **Defaults**: When `location` is omitted from API requests, `app.py` defaults `location` to `"Todos"`. In scrapers, default parameter is `location=""` or `country=""`.
- **Generic Handling**: Values such as `"Todos"`, `"Brasil"`, `"Brasil (Remoto)"`, and `"Remoto"` are recognized as default/global search targets and do not pollute keyword queries with literal `"Todos"`.
- **Exception Safety**: All scraper executions remain wrapped in `try...except` blocks to prevent single-scraper failures from crashing the background hunt process.
- **Status**: **VERIFIED - PASS**

### Item 4: Test Execution & Verification
- **Execution of `test_location_state.py`**:
  - Endpoint `/api/trigger` parameter repass test: **PASSED**
  - UF Map completeness (27 UFs): **PASSED**
  - Remote job preservation & location filtering: **PASSED**
- **Adversarial Check**: No hardcoded test results, facade implementations, or bypasses detected.
- **Status**: **VERIFIED - PASS**

---

## 3. Conclusion & Rationale

The R1 changes meet all architectural, functional, and quality requirements. The verdict is **PASS / APPROVE**.
