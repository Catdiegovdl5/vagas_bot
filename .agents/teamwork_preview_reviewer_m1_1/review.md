## Review Summary

**Verdict**: REQUEST_CHANGES (FAIL)

## Findings

### [Critical] Finding 1: Unhandled AttributeError in scrapers/linkedin.py when country is None

- **What**: `linkedin.scrape()` raises `AttributeError: 'NoneType' object has no attribute 'lower'` when `country=None` is passed, and fails to apply remote filter when `location` contains "remoto".
- **Where**: `scrapers/linkedin.py`, line 129: `if "remote" in country.lower() or "remoto" in country.lower():`
- **Why**: `country` is evaluated via `.lower()` directly without checking if `country` is `None` or string. If a caller invokes `scrape(keyword="Python", location="Brasil (Remoto)", country=None)`, `country` is `None` causing an unhandled crash. Moreover, when `location="Brasil (Remoto)"` is passed with default `country=""`, `country.lower()` is empty, ignoring `location` for remote filter calculation (`&f_WT=2`).
- **Suggestion**: Use `loc = (country or location or "").lower()` and check `if "remote" in loc or "remoto" in loc:`.

### [Major] Finding 2: Location parameter is ignored in target API/URL queries in multiple scrapers

- **What**: Multiple scrapers define `loc = location or country...`, but do not pass `loc` to target search APIs or query URLs for valid non-US locations (e.g. "São Paulo", "Rio de Janeiro", "Curitiba").
- **Where**:
  - `scrapers/remotar.py` (L12): `loc` is assigned but never used anywhere in the file.
  - `scrapers/workana.py` (L14): `loc` is assigned but never used anywhere in the file.
  - `scrapers/gupy.py` (L13): `loc` is only checked for `"USA"`/`"US"`, but never passed to `portal.api.gupy.io/api/v1/jobs`.
  - `scrapers/infojobs.py` (L24): `loc` is only checked for `"USA"`/`"US"`, but never included in InfoJobs search request URL.
  - `scrapers/coodesh.py` (L10), `scrapers/geekhunter.py` (L11), `scrapers/programathor.py` (L11), `scrapers/vagas_com.py` (L12), `scrapers/meta_ads.py` (L8): `loc` is checked for USA/US exclusion but otherwise ignored when building search queries/URLs.
  - `scrapers/glassdoor.py` (L11), `scrapers/gmail.py` (L14): `loc` is assigned but never used in target requests.
- **Why**: Requirement R1 item 3 requires scrapers to query target APIs/URLs using location when supplied. Storing `loc` in a local variable without appending it to the API query string or URL query parameters leaves location filtering ineffective at the scraper level.
- **Suggestion**: Update these scrapers to append `loc` to search terms (e.g., `search_kw += f" {loc}"`) or include location query parameters in target API calls when `loc` is provided.

## Verified Claims

- **app.py entry points** → verified via source inspection of `/api/trigger`, `/api/search`, `run_hunt_background`, `run_initial_seed_search`, `background_periodic_hunt_loop` → PASS (All pass `location=location` or `country=location` to `module.scrape(...)`).
- **bot.py dispatcher** → verified via source inspection of `fetch_plat` → PASS (Extracts location settings, checks signature/kwargs, passes `location` and `country` to sync and async scrapers).
- **Scraper signature compliance** → verified via python signature inspection across 19 scrapers → PASS (All accept `location`, `country`, and `**kwargs`).
- **Active location propagation in select scrapers** → verified in `indeed.py`, `jooble.py`, `jsearch.py`, `catho.py`, `github_vagas.py`, `novenove.py`, `freelancer.py` → PASS (These scrapers format `loc` into URLs, request bodies, or search terms).
- **linkedin.py country=None execution** → verified via python execution → FAIL (Crashes with `AttributeError`).

## Coverage Gaps

- None. Evaluated `app.py`, `bot.py`, and all 19 scraper modules in `scrapers/`.

## Unverified Items

- Live network API responses for external job boards (blocked by network environment or anti-bot protections in dry run, though parameter propagation logic was fully verified via AST/code inspection and local execution).
