# Scraper Investigation Analysis

This report documents the findings regarding the 9 scrapers under `scrapers/` for the `vagas_bot` project.

## Summary of Findings

| Scraper | Status | Core Issue | Proposed Fix Strategy |
| --- | --- | --- | --- |
| **JSearch** | Failed (0 results) | RapidAPI `/search` endpoint returned 404 Endpoint Not Found. Likely due to expired/suspended RapidAPI subscription or endpoint deprecation. | Check subscription status of `JSEARCH_API_KEY` on RapidAPI and verify the correct host and endpoint route in current JSearch docs. |
| **Workana** | Operational / Flaky | Works in standalone tests (returns 14 results), but occasionally returns 0 in the main bot execution. | Enhance logging in `bot.py` to separate scraper-level failures from post-scraping filter exclusions. |
| **Remotar** | Failed (0 results) | Selector structure changes. Website is now a client-rendered Next.js SPA. The BeautifulSoup selector for `div.job-list-item` is obsolete. | Rewrite scraper to call the backend API endpoint directly: `https://api.remotar.com.br/jobs` which returns JSON data. |
| **Glassdoor** | Failed (0 results) | Cloudflare bot protection blocks the headless Playwright instance. | Implement residential proxies, user-agent rotation, or use an API wrapper. |
| **Gupy** | Failed (0 results) | The API endpoint `https://portal.gupy.io/api/job-search` redirects to the HTML landing page instead of returning JSON. | Retrieve correct endpoint parameters and headers used by the frontend portal, or scrape the frontend pages. |
| **Vagas.com** | Partially working | Returns jobs (e.g., 7 jobs in logs) but can be flaky depending on search term and Cloudflare blocks. | Ensure proper User-Agent header rotation. |
| **Programathor** | Failed (0 results) | Captcha/Cloudflare block page or selector mismatch. | Verify current selectors and bypass Cloudflare blocks. |
| **Coodesh** | Failed (0 results) | Selector mismatch or API change. | Update CSS selectors. |
| **Geekhunter** | Failed (0 results) | Requires authentication or selectors are obsolete. | Update selectors or implement API request structure. |

---

## Detailed Findings

### 1. JSearch (`scrapers/jsearch.py`)
- **API Call**: `https://jsearch.p.rapidapi.com/search?query=...`
- **Error**: RapidAPI returned `404 {"message":"Endpoint '/search' does not exist"}`.
- **Cause**: Deprecated endpoint route or suspended subscription for the API Key.
- **Fix**: Verify JSearch API documentation on RapidAPI, update route if it changed, and renew API subscription.

### 2. Workana (`scrapers/workana.py`)
- **API Call**: Parses HTML from `https://www.workana.com/jobs?query=...` using Vue.js init payload inside the `<search>` tag's `:results-initials` attribute.
- **Status**: The scraper works. In standalone execution, it successfully parsed 14 jobs.
- **Cause of 0 results in bot**: The jobs retrieved were either filtered out by `bot.py` criteria (such as location/contract/level mismatches) or temporary bot detection occurred.
- **Fix**: Add pre-filter logs to `bot.py` to see the original number of jobs retrieved.

### 3. Remotar (`scrapers/remotar.py`)
- **Scraper logic**: Uses BeautifulSoup to search for `div.job-list-item` in static HTML.
- **Status**: Failed (0 results).
- **Cause**: Remotar converted to Next.js Client-Side SPA (`nextExport: true`). There are no jobs in the initial HTML or `__NEXT_DATA__`.
- **Fix**: Re-write scraper to query Axios GET to `https://api.remotar.com.br/jobs` (returns JSON of 50 jobs).

### 4. Glassdoor (`scrapers/glassdoor.py`)
- **Scraper logic**: Uses sync Playwright.
- **Status**: Failed (0 results).
- **Cause**: Headless browser blocked by Cloudflare.
- **Fix**: Use proxies or stealth library.

### 5. Gupy (`scrapers/gupy.py`)
- **API Call**: Queries `https://portal.gupy.io/api/job-search?term=...`
- **Status**: Failed (0 results).
- **Cause**: The endpoint redirects to HTML home page (200 status but HTML response), causing `r.json()` to fail.
- **Fix**: Locate and use the actual API endpoints or correct request headers.

### 6. Remaining Scrapers (Vagas.com, Programathor, Coodesh, Geekhunter)
- In line with parent instructions, detailed investigations were stopped after the parent synthesized findings from Explorer 1 and 2, which cover the complete picture for these scrapers.
