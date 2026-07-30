# Handoff Report: Requirement 1 (R1) - Backend Location Parameter Passing Audit

## 1. Observation
Direct evidence gathered during investigation:

* **`app.py` (lines 195, 207-210)**:
  Line 195: `location = data.get("location", "Todos")`.
  Lines 207-210:
  ```python
  if inspect.iscoroutinefunction(module.scrape):
      jobs = await module.scrape(keyword=keyword, level=level)
  else:
      jobs = await asyncio.to_thread(module.scrape, keyword=keyword, level=level)
  ```
  `location` is read from request JSON but never passed to `module.scrape()`.

* **`app.py` (lines 269, 271, 287, 289)**:
  `module.scrape(keyword=kw, level="Todos")` calls scrapers in initial seed and periodic hunt loop without location parameter.

* **`bot.py` (lines 2376-2388)**:
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
      if "country" in sig.parameters and plat in [...]:
          kwargs["country"] = settings["location"]
      res = await asyncio.to_thread(module.scrape, **kwargs)
  ```
  Async coroutine scrapers entering `if inspect.iscoroutinefunction(...)` never receive `kwargs["country"]` or `kwargs["location"]`. Location injection is strictly inside the `else` (sync) block.

* **`scrapers/*.py`**:
  * Scraper function signatures predominantly use `country="Brasil"` instead of `location` or `**kwargs`.
  * Scrapers `scrapers/remotar.py` and `scrapers/workana.py` do not accept `location` or `country` parameters in `scrape()`.
  * 7 scrapers (`infojobs.py`, `gupy.py`, `catho.py`, `coodesh.py`, `geekhunter.py`, `programathor.py`, `vagas_com.py`) contain `if "Brasil" not in country: return jobs`. When `country` is `"Londrina/PR"` or `"Assaí/PR"`, `"Brasil"` is not in the string, causing these scrapers to return 0 jobs (`[]`).
  * Scraper `glassdoor.py` accepts `country="Brasil"` but ignores it in request URLs (`locId=0`).
  * Scraper `jooble.py` evaluates `if "Brasil" in country:` before `elif "Londrina" in country:`. If `country="Londrina, Brasil"`, `"Brasil"` matches first and overrides city-level search.

---

## 2. Logic Chain
1. **Request Entry Point (`app.py` & `bot.py`)**: Users configure location via API payload or Telegram settings.
2. **Dispatch Bottleneck**: When `app.py` or `bot.py` invokes scrapers, the `location` variable is dropped (in `app.py` for all scrapers; in `bot.py` for all async scrapers, and for sync scrapers that don't match exact parameter name `"country"`).
3. **Scraper Execution Defect**: Even when `country` is passed by `bot.py` to sync scrapers, 7 scrapers abort execution if `country` does not contain `"Brasil"` literally. Furthermore, Glassdoor, InfoJobs, Catho, Coodesh, Gupy, GeekHunter, Programathor, and Vagas.com do not append location parameters to outbound HTTP requests.
4. **Result**: Location filtering fails across the application, defaulting to nationwide/unfiltered queries or returning empty results for specific municipal inputs.

---

## 3. Caveats
- Scrapers relying on third-party public APIs (e.g. `remotar`, `workana`, `freelancer`, `github_vagas`) may have limited native support for municipal location filtering at the HTTP request level; post-scraping filtering (via `is_job_relevant` in `bot.py` or `ai_filter.py`) remains necessary for those platforms.
- Live scraping responses were not executed over HTTP during this investigation turn to comply with read-only guidelines.

---

## 4. Conclusion
Requirement 1 (R1) requires immediate remediation in `app.py`, `bot.py`, and `scrapers/*.py`:
1. Standardize scraper signature signatures to accept `location` (with alias support for `country` / `**kwargs`).
2. Update `app.py` line 207-210 to pass `location=location` to all scraper calls.
3. Update `bot.py` line 2376-2388 to inject `location` for BOTH async and sync scrapers.
4. Remove the `if "Brasil" not in country:` guard clauses in scrapers to prevent false zero-result returns when city names are provided.
5. Update scrapers to append location parameters to their respective HTTP search requests where supported.

---

## 5. Verification Method
1. Inspect `analysis.md` and `handoff.md` in `C:/Users/99196/OneDrive/Documentos/vagas_bot/.agents/teamwork_preview_explorer_state_1/`.
2. Run pytest on existing test files (e.g. `pytest test_filter_validation.py` or `pytest test_bot.py`) once implementer applies the proposed changes.
3. Invalidate current state if `app.py` or `bot.py` continue to call `module.scrape` without location arguments.
