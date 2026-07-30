# Comprehensive Audit Report: Requirement R1 — Backend Location Parameter Passing

**Author**: Explorer 1 (Backend Specialist)  
**Date**: 2026-07-21  
**Project**: vagas_bot  
**Target Files**: `app.py`, `bot.py`, `scrapers/*.py`  
**Status**: Completed  

---

## 1. Executive Summary

An audit of Requirement R1 was conducted to evaluate how the `location` parameter is handled across backend API endpoints, background jobs, bot search dispatchers, and individual scrapers.

### Core Findings:
1. **`app.py` Endpoint Parameter Dropping**: `/api/trigger` accepts `location` in the JSON request body (`location = data.get("location", "Todos")`), but completely drops it when invoking scrapers (`module.scrape(keyword=keyword, level=level)`). Neither async nor sync scrapers receive `location` or `country`.
2. **`app.py` Background Routines**: `run_initial_seed_search()` and `background_periodic_hunt_loop()` invoke scrapers with only `keyword` and `level`, leaving `location` unassigned.
3. **`bot.py` Asymmetric Dispatch**: `bot.py` passes `country=settings["location"]` ONLY to synchronous scrapers that explicitly define `country` in `inspect.signature`. Async (coroutine) scrapers (`gupy`, `catho`, `infojobs`, `vagas_com`, `workana`) NEVER receive `location` or `country` parameters.
4. **Scraper Signature & Handling Discrepancies**:
   - `remotar.py` and `workana.py` do NOT accept `location`, `country`, or `**kwargs` in their function signature. Passing `location` or `country` raises a `TypeError`.
   - `indeed.py` and `linkedin.py` hardcode location checks specifically for `"Londrina"` and `"Assaí"`, reverting all other valid locations (e.g., `"São Paulo"`, `"Curitiba"`, `"Brasil (Remoto)"`) to default strings or empty parameters.
   - `freelancer.py`, `glassdoor.py`, `gmail.py`, and `novenove.py` accept a `country` parameter but completely ignore it in their execution.
   - Async scrapers (`catho`, `gupy`, `infojobs`, `vagas_com`) accept `**kwargs` and read `kwargs.get("country", "Brasil")`, but only check if `"Brasil"` is in `country` rather than building location-filtered search URLs.

---

## 2. Endpoint & Background Routine Audit (`app.py`)

### 2.1 `/api/trigger` (POST)
- **Lines 193–195**:
  ```python
  keyword = data.get("keyword", "Python")
  level = data.get("level", "Todos")
  location = data.get("location", "Todos")
  ```
- **Lines 207–210** (`run_hunt_background`):
  ```python
  if inspect.iscoroutinefunction(module.scrape):
      jobs = await module.scrape(keyword=keyword, level=level)
  else:
      jobs = await asyncio.to_thread(module.scrape, keyword=keyword, level=level)
  ```
- **Defect Observation**: `location` is extracted from the JSON body on line 195, but is **omitted** from both the async (`await module.scrape(...)`) and sync (`asyncio.to_thread(module.scrape, ...)`) calls on lines 208 and 210.
- **Impact**: Scrapers run without location awareness. While post-filtering occurs at line 225 (`is_job_relevant(job, keyword, settings)`), scrapers cannot use `location` in their initial HTTP query/API request to fetch location-specific job postings.

### 2.2 `run_initial_seed_search()` (Startup Event)
- **Lines 268–271**:
  ```python
  if inspect.iscoroutinefunction(module.scrape):
      jobs = await module.scrape(keyword=kw, level="Todos")
  else:
      jobs = await asyncio.to_thread(module.scrape, keyword=kw, level="Todos")
  ```
- **Defect Observation**: No `location` or `country` argument is supplied when seeding initial data.

### 2.3 `background_periodic_hunt_loop()` (Periodic 10-min Loop)
- **Lines 286–289**:
  ```python
  if inspect.iscoroutinefunction(module.scrape):
      jobs = await module.scrape(keyword=kw, level="Todos")
  else:
      jobs = await asyncio.to_thread(module.scrape, keyword=kw, level="Todos")
  ```
- **Defect Observation**: No `location` or `country` argument is passed during automated periodic background searches.

---

## 3. Bot Search Dispatcher Audit (`bot.py`)

### 3.1 `fetch_plat(plat)` Execution Flow (Lines 2360–2405)
- **Coroutine Scrapers Branch** (Lines 2383–2384):
  ```python
  kwargs = {"keyword": plat_search_keyword, "level": "Todos"}
  if "contract" in sig.parameters: kwargs["contract"] = contract_val

  if inspect.iscoroutinefunction(module.scrape):
      res = await module.scrape(**kwargs)
  ```
  - **Defect**: `kwargs` built for coroutine scrapers contains only `"keyword"` and `"level"`. Neither `location` nor `country` is included, even though async scrapers like `gupy`, `catho`, `infojobs`, and `vagas_com` support `**kwargs`.
- **Synchronous Scrapers Branch** (Lines 2385–2388):
  ```python
  else:
      if "country" in sig.parameters and plat in ['jsearch', 'jooble', 'github_vagas', 'novenove', 'freelancer', 'indeed', 'linkedin', 'gmail', 'glassdoor', 'infojobs', 'gupy', 'vagas_com', 'programathor', 'coodesh', 'geekhunter']:
          kwargs["country"] = settings["location"]
      res = await asyncio.to_thread(module.scrape, **kwargs)
  ```
  - **Defect**: `settings["location"]` is passed under key `"country"` instead of `"location"`. Scrapers expecting `location` or scrapers without `"country"` in their parameter signature fail to receive the setting.

---

## 4. Comprehensive Scrapers Audit (`scrapers/*.py`)

The table below summarizes the auditing of all 19 active scraper modules in `scrapers/`:

| Scraper File | Async / Sync | Signature | Accepts `location`? | Accepts `country`? | Location Parameter Handling | Identified Issue / Defect |
|---|---|---|---|---|---|---|
| `catho.py` | Async | `async def scrape(keyword, level="Todos", max_pages=1, **kwargs)` | Via `**kwargs` | Via `**kwargs` | Checks `if "Brasil" not in country: return []`. Does not use location in search URL (`https://www.catho.com.br/vagas/...`). | Never passed by `app.py` or `bot.py` (coroutine branch). URL ignores location. |
| `coodesh.py` | Sync | `def scrape(keyword, level="Todos", country="Brasil")` | No | Yes | Checks `if "Brasil" not in country: return []`. Coodesh API URL (`https://api.coodesh.com/v2/jobs?...`) omits location. | `app.py` drops parameter. API URL ignores city/state location. |
| `freelancer.py` | Sync | `def scrape(keyword, level="Todos", country="Brasil")` | No | Yes | Parameter `country` is declared in signature but never referenced in code. | `country` parameter completely unused and ignored. `app.py` drops parameter. |
| `geekhunter.py` | Sync | `def scrape(keyword, level="Todos", country="Brasil")` | No | Yes | Checks `if "Brasil" not in country: return []`. Search URL (`https://www.geekhunter.com/pt/vagas?q=...`) omits location. | `app.py` drops parameter. Query ignores location. |
| `github_vagas.py` | Sync | `def scrape(keyword, level="Todos", country="Brasil")` | No | Yes | Checks `if country == "USA": return []`. GitHub Search API query omits location filters. | `app.py` drops parameter. Location parameter ignored in search query. |
| `glassdoor.py` | Sync | `def scrape(keyword, level="Todos", country="Brasil")` | No | Yes | Parameter `country` is declared in signature but never referenced in code. Search URL uses hardcoded `locT=N&locId=0`. | `country` parameter completely unused. `app.py` drops parameter. |
| `gmail.py` | Sync | `def scrape(keyword, level="Todos", country="Brasil")` | No | Yes | Parameter `country` is declared in signature but never referenced in code. | `country` parameter completely unused. `app.py` drops parameter. |
| `gupy.py` | Async | `async def scrape(keyword, level="Todos", max_pages=1, **kwargs)` | Via `**kwargs` | Via `**kwargs` | Checks `if "Brasil" not in country: return []`. Gupy API URL (`https://employability-portal.gupy.io/api/v1/jobs?...`) omits location. | Never passed by `app.py` or `bot.py` (coroutine branch). API URL ignores location. |
| `indeed.py` | Sync | `def scrape(keyword, level="Todos", country="Brasil")` | No | Yes | Checks `if "Londrina" in country: loc_param = "&l=Londrina%2C+PR&radius=15"` / `elif "Assaí"...` else `loc_param = ""`. | Drops all non-Londrina/Assaí locations to empty string. `app.py` drops parameter. |
| `infojobs.py` | Async | `async def scrape(keyword, level="Todos", max_pages=1, **kwargs)` | Via `**kwargs` | Via `**kwargs` | Checks `if "Brasil" not in country: return []`. InfoJobs URL (`https://www.infojobs.com.br/vagas-de-emprego.aspx?...`) omits location. | Never passed by `app.py` or `bot.py` (coroutine branch). URL ignores location. |
| `jooble.py` | Sync | `def scrape(keyword, level="Todos", country="Brasil")` | No | Yes | Maps `"Brasil"`, `"USA"`, `"Londrina"`, `"Assaí"` to `payload["location"]`. | `app.py` drops parameter. Unrecognized city names do not pass through dynamically. |
| `jsearch.py` | Sync | `def scrape(keyword, level, country="Brasil")` | No | Yes | Maps `"Brasil"` to `country=br` and `"USA"` to `country=us`. | `app.py` drops parameter. City/state location cannot be passed. |
| `linkedin.py` | Sync | `def scrape(keyword, level="Todos", country="Brasil", contract="Todos")` | No | Yes | Checks `"Londrina"` or `"Assaí"`, else defaults `loc_param = "Brasil"`. Checks `remote` in country for `&f_WT=2`. | `app.py` drops parameter. Non-Londrina/Assaí cities revert to `"Brasil"`. |
| `meta_ads.py` | Sync | `def scrape(keyword, level="Todos", country="Brasil")` | No | Yes | Checks `if "Brasil" not in country: return []`. Uses `countryCode="BR"`. | `app.py` drops parameter. City/state location ignored. |
| `novenove.py` | Sync | `def scrape(keyword, level="Todos", country="Brasil")` | No | Yes | Parameter `country` is declared in signature but never referenced in code. | `country` parameter completely unused. `app.py` drops parameter. |
| `programathor.py` | Sync | `def scrape(keyword, level="Todos", country="Brasil")` | No | Yes | Checks `if "Brasil" not in country: return []`. URL (`https://programathor.com.br/jobs?text=...`) omits location. | `app.py` drops parameter. URL ignores location. |
| `remotar.py` | Sync | `def scrape(keyword="Python", level="Todos", contract="Todos")` | **NO** | **NO** | Signature lacks `location`, `country`, and `**kwargs`. | Calling with `location` or `country` throws `TypeError`. |
| `vagas_com.py` | Async | `async def scrape(keyword, level="Todos", max_pages=1, **kwargs)` | Via `**kwargs` | Via `**kwargs` | Checks `if "Brasil" not in country: return []`. URL (`https://www.vagas.com.br/vagas-de-...`) omits location. | Never passed by `app.py` or `bot.py` (coroutine branch). URL ignores location. |
| `workana.py` | Async | `async def scrape(keyword="Python", level="Todos", max_pages=100)` | **NO** | **NO** | Signature lacks `location`, `country`, and `**kwargs`. | Calling with `location` or `country` throws `TypeError`. |

---

## 5. Risk Assessment & Architectural Impact

1. **Information Loss at Retrieval Stage**: Because scrapers execute broad searches without location queries, scrapers returning page-budgeted results (e.g. 15 to 30 items) miss location-specific postings in target regions (e.g. Londrina, Curitiba, São Paulo).
2. **API Incompatibility Risks**: Attempting a naive global refactor passing `location=location` to all scrapers will crash `remotar.py` and `workana.py` with `TypeError: unexpected keyword argument`.
3. **Inconsistent Naming Convention**: `app.py` sends `location`, `bot.py` passes `country=settings["location"]`, while individual scrapers expect either `location`, `country`, or `**kwargs`.

---

## 6. Recommendations for Implementation Phase

To fulfill Requirement R1 cleanly without breaking existing scrapers:

1. **Standardize Scraper Signatures**:
   - Update `remotar.py` and `workana.py` signatures to accept `location="Todos", country="Brasil", **kwargs`.
   - Ensure all scrapers accept `location="Todos"` and `country="Brasil"` (or `**kwargs`).
2. **Patch `app.py` Dispatcher**:
   - In `run_hunt_background()`, inspect scraper signature (`sig = inspect.signature(module.scrape)`).
   - Pass `location=location` or `country=location` (or both via `kwargs`) to both async and sync scrapers.
   - Update `run_initial_seed_search()` and `background_periodic_hunt_loop()` accordingly.
3. **Patch `bot.py` Dispatcher**:
   - Ensure `fetch_plat()` passes `location` / `country` into `kwargs` for BOTH coroutine (async) scrapers and synchronous scrapers.
4. **Enhance In-Scraper Location Filtering**:
   - Update scrapers with native location search capability (`indeed.py`, `linkedin.py`, `jooble.py`, `catho.py`, etc.) to process dynamic location strings rather than hardcoded checks for Londrina/Assaí.
