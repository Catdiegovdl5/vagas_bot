# Technical Analysis Report: Backend Location Parameter Passing Audit (Requirement 1 - R1)

## Executive Summary
This report provides a comprehensive, read-only audit of location parameter flow across `app.py`, `bot.py`, and all scraper modules in `scrapers/*.py`. 

The primary finding is that **the `location` parameter is frequently dropped, ignored, misnamed, or excluded from scraper invocations and search request URLs across the entire backend**. While `app.py` extracts `location` from HTTP payloads and `bot.py` maintains user location in `user_settings_db`, neither caller consistently propagates `location` to scrapers. Furthermore, async scrapers in `bot.py` are completely bypassed for location argument injection, and multiple scrapers contain fragile string checks (e.g. `if "Brasil" not in country: return []`) that cause silent failures when city-specific locations (e.g. `Londrina/PR`) are selected.

---

## 1. Audit of Request Handlers & Dispatchers

### 1.1 `app.py`
* **Endpoint `/api/trigger` (`trigger_hunt`, lines 181–233)**:
  * **Observation**: Line 195 extracts `location = data.get("location", "Todos")`. However, lines 207–210 execute the scraper:
    ```python
    if inspect.iscoroutinefunction(module.scrape):
        jobs = await module.scrape(keyword=keyword, level=level)
    else:
        jobs = await asyncio.to_thread(module.scrape, keyword=keyword, level=level)
    ```
  * **Defect**: `location` is completely omitted from calls to `module.scrape()`. Scrapers execute with their default internal parameter values (usually `"Brasil"` or `None`).
* **Seed & Loop Background Tasks** (`run_initial_seed_search` lines 260–276, `background_periodic_hunt_loop` lines 277–294):
  * **Observation**: Lines 269, 271, 287, and 289 call `module.scrape(keyword=kw, level="Todos")` without passing any location parameter.

### 1.2 `bot.py`
* **Scraper Invocation in `fetch_plat` (`_do_hunt`, lines 2360–2405)**:
  * **Observation**: Lines 2376–2388 construct arguments and invoke scrapers:
    ```python
    kwargs = {
        "keyword": plat_search_keyword,
        "level": "Todos"
    }
    if "contract" in sig.parameters:
        kwargs["contract"] = contract_val
        
    if inspect.iscoroutinefunction(module.scrape):
        res = await module.scrape(**kwargs)
    else:
        if "country" in sig.parameters and plat in ['jsearch', 'jooble', 'github_vagas', 'novenove', 'freelancer', 'indeed', 'linkedin', 'gmail', 'glassdoor', 'infojobs', 'gupy', 'vagas_com', 'programathor', 'coodesh', 'geekhunter']:
            kwargs["country"] = settings["location"]
        res = await asyncio.to_thread(module.scrape, **kwargs)
    ```
  * **Defect 1 (Async Branch Bypass)**: Async coroutine scrapers (e.g. `gupy`, `infojobs`, `catho`, `vagas_com`, `workana`) enter `if inspect.iscoroutinefunction(...)`. `kwargs` at line 2376 contains **ONLY** `keyword`, `level`, and `contract`. The logic that sets `kwargs["country"] = settings["location"]` is inside the `else` block (sync branch). As a result, **no async scrapers ever receive location from `bot.py`**.
  * **Defect 2 (Parameter Naming Inconsistency)**: `bot.py` passes `settings["location"]` under the key `"country"`, assuming every scraper uses `country`. Scrapers that use `location` or do not include `"country"` in `sig.parameters` receive no location input.

---

## 2. Individual Scraper Audit (`scrapers/*.py`)

The table below lists all scraper modules, their current function signatures, parameter names used, and observed defects regarding location handling.

| File Path | Function Signature | Parameter Name | Current Location Handling & Defects |
|---|---|---|---|
| `scrapers/linkedin.py` | `def scrape(keyword, level="Todos", country="Brasil", contract="Todos")` | `country` | Checks `country` for `"Londrina"`, `"Assaí"`, `"remote"`/`"remoto"`. Correctly maps to `location` query param & `&f_WT=2`. Parameter named `country` instead of `location`. |
| `scrapers/glassdoor.py` | `def scrape(keyword, level="Todos", country="Brasil")` | `country` | **Ignored**. Accepts `country` in signature but never uses it. URL uses hardcoded `locT=N&locId=0` (location disabled). |
| `scrapers/infojobs.py` | `async def scrape(keyword, level="Todos", max_pages=1, **kwargs)` | `country` (via `kwargs.get`) | **Defective & Ignored**. Uses `country = kwargs.get("country", "Brasil")`. Executes `if "Brasil" not in country: return []`, causing instant failure if `country="Londrina/PR"`. URL `https://www.infojobs.com.br/vagas-de-emprego.aspx?palavra={kw}` omits location filter. |
| `scrapers/indeed.py` | `def scrape(keyword, level="Todos", country="Brasil")` | `country` | Only checks `"Londrina"` or `"Assaí"` in `country`. If `country="Brasil"`, `loc_param` is set to `""`. Parameter named `country`. |
| `scrapers/jooble.py` | `def scrape(keyword, level="Todos", country="Brasil")` | `country` | Fragile order of checks: `if "Brasil" in country` executes before `elif "Londrina" in country`. If `country="Londrina, Brasil"`, it matches `"Brasil"` and defaults `loc="Brazil"`. |
| `scrapers/gupy.py` | `async def scrape(keyword, level="Todos", max_pages=10, **kwargs)` | `country` (via `kwargs.get`) | **Defective & Ignored**. Executes `if "Brasil" not in country: return []` (fails on city names). API endpoint `employability-portal.gupy.io/api/v1/jobs` omits location parameters. |
| `scrapers/catho.py` | `async def scrape(keyword, level="Todos", max_pages=1, **kwargs)` | `country` (via `kwargs.get`) | **Defective & Ignored**. `if "Brasil" not in country: return []` breaks city locations. URL `https://www.catho.com.br/vagas/{kw}` does not include location. |
| `scrapers/coodesh.py` | `def scrape(keyword, level="Todos", country="Brasil")` | `country` | **Defective & Ignored**. `if "Brasil" not in country: return []` breaks city locations. API `api.coodesh.com/v2/jobs?search={kw}` omits location filter. |
| `scrapers/freelancer.py` | `def scrape(keyword, level="Todos", country="Brasil")` | `country` | **Ignored**. Parameter present in signature but unused in API call (natively remote). |
| `scrapers/geekhunter.py` | `def scrape(keyword, level="Todos", country="Brasil")` | `country` | **Defective & Ignored**. `if "Brasil" not in country: return []` breaks city locations. URL `geekhunter.com/pt/vagas?q={kw}` omits location. |
| `scrapers/github_vagas.py` | `def scrape(keyword, level="Todos", country="Brasil")` | `country` | **Ignored**. Checks `country == "USA"`, but GitHub issues search query omits location keywords. |
| `scrapers/gmail.py` | `def scrape(keyword, level="Todos", country="Brasil")` | `country` | **Ignored**. Parameter unused in Gmail message filtering. |
| `scrapers/jsearch.py` | `def scrape(keyword, level, country="Brasil")` | `country` | Checks `if "Brasil" in country`. If `country="Londrina/PR"`, `"Brasil"` is missing so it drops the `country=br` parameter from RapidAPI request. |
| `scrapers/meta_ads.py` | `def scrape(keyword, level="Todos", country="Brasil")` | `country` | **Defective**. `if "Brasil" not in country: return []` causes immediate failure for city-level inputs like `"Londrina/PR"`. |
| `scrapers/novenove.py` | `def scrape(keyword, level="Todos", country="Brasil")` | `country` | **Ignored**. Parameter present in signature but unused in search URL. |
| `scrapers/programathor.py` | `def scrape(keyword, level="Todos", country="Brasil")` | `country` | **Defective & Ignored**. `if "Brasil" not in country: return []` breaks city inputs. URL `programathor.com.br/jobs?text={kw}` omits location. |
| `scrapers/remotar.py` | `def scrape(keyword="Python", level="Todos", contract="Todos")` | None | **Missing**. Signature does not accept `location` or `country` parameter. |
| `scrapers/vagas_com.py` | `async def scrape(keyword, level="Todos", max_pages=1, **kwargs)` | `country` (via `kwargs.get`) | **Defective & Ignored**. `if "Brasil" not in country: return []` breaks city inputs. URL `vagas.com.br/vagas-de-{kw}` omits location. |
| `scrapers/workana.py` | `async def scrape(keyword="Python", level="Todos", max_pages=100)` | None | **Missing**. Signature does not accept `location` or `country` parameter. |

---

## 3. Core Problems Summary
1. **`app.py` Call Site Failure**: `/api/trigger` reads `location` from payload but drops it when calling `module.scrape()`.
2. **`bot.py` Call Site Failure**: `fetch_plat()` sets `kwargs["country"]` only for synchronous scrapers inside an `else` block. Async scrapers receive no location parameter.
3. **Destructive Guard Clause**: 7 scrapers (`infojobs`, `gupy`, `catho`, `coodesh`, `geekhunter`, `programathor`, `vagas_com`) use `if "Brasil" not in country: return []`, which causes all of them to return 0 results whenever a user selects a specific location such as `"Londrina/PR"` or `"Assaí/PR"`.
4. **Signature & Parameter Inconsistency**: Some scrapers expect `country`, others expect `**kwargs`, and others (`remotar`, `workana`) have no location parameter in signature.
5. **Search Query Omission**: Even when location is passed, scrapers for Glassdoor, InfoJobs, Catho, Coodesh, Gupy, GeekHunter, Programathor, Vagas.com, and 99Freelas fail to append location parameters to their outbound HTTP GET/POST requests.

---

## 4. Proposed Code Changes for R1 Implementation

### 4.1 Fix `app.py` (`c:/Users/99196/OneDrive/Documentos/vagas_bot/app.py`)
**Lines 207–210**: Pass `location=location` and `country=location` to `module.scrape`:
```python
# Before (Lines 207-210):
if inspect.iscoroutinefunction(module.scrape):
    jobs = await module.scrape(keyword=keyword, level=level)
else:
    jobs = await asyncio.to_thread(module.scrape, keyword=keyword, level=level)

# Proposed Change:
scrape_args = {"keyword": keyword, "level": level, "location": location, "country": location}
sig = inspect.signature(module.scrape)
valid_args = {k: v for k, v in scrape_args.items() if k in sig.parameters or any(p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values())}

if inspect.iscoroutinefunction(module.scrape):
    jobs = await module.scrape(**valid_args)
else:
    jobs = await asyncio.to_thread(module.scrape, **valid_args)
```

### 4.2 Fix `bot.py` (`c:/Users/99196/OneDrive/Documentos/vagas_bot/bot.py`)
**Lines 2376–2390**: Standardize argument preparation for both async and sync scrapers:
```python
# Before (Lines 2376-2388):
kwargs = {
    "keyword": plat_search_keyword,
    "level": "Todos"
}
if "contract" in sig.parameters:
    kwargs["contract"] = contract_val
    
if inspect.iscoroutinefunction(module.scrape):
    res = await module.scrape(**kwargs)
else:
    if "country" in sig.parameters and plat in [...]:
        kwargs["country"] = settings["location"]
    res = await asyncio.to_thread(module.scrape, **kwargs)

# Proposed Change:
location_val = settings.get("location", "Brasil (Remoto)")
kwargs = {
    "keyword": plat_search_keyword,
    "level": "Todos"
}
if "contract" in sig.parameters:
    kwargs["contract"] = contract_val
if "location" in sig.parameters:
    kwargs["location"] = location_val
if "country" in sig.parameters:
    kwargs["country"] = location_val
if any(p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values()):
    kwargs["location"] = location_val
    kwargs["country"] = location_val

if inspect.iscoroutinefunction(module.scrape):
    res = await module.scrape(**kwargs)
else:
    res = await asyncio.to_thread(module.scrape, **kwargs)
```

### 4.3 Standardize Scraper Signatures and Guard Clauses (`scrapers/*.py`)
1. **Standardize Signatures**: Add `location="Brasil"` (and accept `country=None` or `**kwargs`) to `scrape()` in all scrapers (`remotar.py`, `workana.py`, `gupy.py`, `infojobs.py`, `catho.py`, etc.).
2. **Replace Guard Clauses**: In `gupy.py`, `catho.py`, `coodesh.py`, `infojobs.py`, `vagas_com.py`, `programathor.py`, `geekhunter.py`, `meta_ads.py`:
   * Replace `if "Brasil" not in country: return jobs` with flexible normalization (e.g. accept any Brazil state/city string unless explicitly non-supported international location like "USA").
3. **URL Parameter Propagation**:
   * For scrapers supporting location query params, pass normalized location string to the request URL (e.g. `Glassdoor`, `InfoJobs`, `Catho`, `Vagas.com`, `Gupy`).
