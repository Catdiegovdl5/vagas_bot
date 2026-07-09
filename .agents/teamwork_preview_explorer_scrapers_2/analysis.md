# Scraper Investigation Report (9 Platforms)

This document contains detailed findings on why the 9 job scrapers return 0 results or fail under `scrapers/`, along with programmatic strategies to resolve each issue.

---

## Executive Summary

Our investigation reveals that the 9 scrapers fail primarily due to five distinct systemic issues:
1. **Cloudflare/Bot Detection Blocks**: 5 platforms (Workana, Glassdoor, Gupy, Programathor, Geekhunter) block simple requests or headless automation out-of-the-box.
2. **Incorrect URL Search Formats (SEO Landing Page Trap)**: 2 platforms (Vagas.com, Programathor) construct URLs pointing to tag landing pages rather than dynamic query endpoints, returning 404s for any custom search terms.
3. **Client-Side Rendering (SPA container empty HTML)**: 1 platform (Coodesh) renders its vacancy list dynamically via client-side javascript, meaning static DOM parsing catches nothing.
4. **Outdated Selectors & URL Routes**: 1 platform (Remotar) points to a deactivated search route and uses obsolete CSS class selectors.
5. **Credential/API Decommissioning**: JSearch uses an expired/exhausted default RapidAPI key and fails silently without logging error statuses, while Geekhunter redirects anonymous requests to a registration/auth page.

---

## Detailed Scraper Diagnosis & Fix Strategies

### 1. Jsearch (`scrapers/jsearch.py`)
*   **Root Cause**:
    *   **Expired Fallback API Key**: The default RapidAPI key defined on line 21 (`"7af3cebf37mshb1adb579644f3d1p1f605fjsn26d9e7a63fe0"`) is expired or has exceeded its monthly free quota limit. The `.env` file does not define `JSEARCH_API_KEY`.
    *   **Silent Fail**: The code performs `data = response.json()` and checks `if data.get("data")`. If JSearch returns a 401 Unauthorized or 429 Rate Limit error, the JSON response contains error details rather than a `"data"` key. The scraper exits silently, returning `[]` without triggering an exception or logging the API failure.
*   **Proposed Fix Strategy**:
    1. Update the HTTP response validation to raise an error if `response.status_code != 200` or if `"message"` (typical of RapidAPI errors) is present.
    2. Add `JSEARCH_API_KEY` to the `.env.example` file and document how users can obtain a free key.
    3. Log a clear warning or error using `logger` when the key is rejected.

### 2. Workana (`scrapers/workana.py`)
*   **Root Cause**:
    *   **Cloudflare Protection**: Workana is protected by Cloudflare. Requests sent using standard Python `requests` are often blocked (HTTP 403 Forbidden).
    *   **Vue.js Initialization Selector**: The parser targets the `<search>` tag with the attribute `:results-initials` (lines 28–32). If Workana alters this tag name, updates Vue.js configurations, or shifts to client-side hydration fetching, `soup.find('search')` returns `None` and the loop silently continues, yielding 0 results.
*   **Proposed Fix Strategy**:
    1. **Client Upgrade**: Replace standard `requests` with `curl_cffi` (using `impersonate="chrome110"`) or Playwright to bypass Cloudflare bot challenges.
    2. **Resilient Initial State Extraction**: Write a fallback regex parser targeting `<script>` blocks that contain initial hydration data (like `window.__INITIAL_STATE__` or similar JSON blobs) in case the tag `:results-initials` is renamed.
    3. **Warning Logs**: Add log messages if the search tag is missing or the response status code is not 200.

### 3. Remotar (`scrapers/remotar.py`)
*   **Root Cause**:
    *   **Decommissioned URL Route**: The scraper targets `https://remotar.com.br/search/jobs?q={search_kw}` (line 9). Remotar has updated its routing structure, and this path returns a 404. The correct search route is `https://remotar.com.br/search?q={search_kw}`.
    *   **Outdated DOM Selectors**: The code tries to extract elements using `soup.find_all('div', class_='job-list-item')` (line 20). Following a site redesign, Remotar no longer utilizes these CSS classes.
*   **Proposed Fix Strategy**:
    1. Update the query URL to `https://remotar.com.br/search?q={search_kw}`.
    2. Inspect current DOM elements on remotar.com.br/search and map new Tailwind CSS classes / component hierarchies (e.g. searching for link elements pointing to `/vaga/` or updated card wrappers).
    3. Set a modern User-Agent and headers.

### 4. Glassdoor (`scrapers/glassdoor.py`)
*   **Root Cause**:
    *   **Aggressive Cloudflare Turnstile Blocks**: Glassdoor uses severe bot mitigation. Headless browser automation (Playwright Chromium) gets flagged and stuck on the Cloudflare challenge page immediately, timing out after 45 seconds.
    *   **Obsolete SEO URL Formats**: The URL `https://www.glassdoor.com.br/Vagas/{keyword}-vagas-SRCH_KO0...` only works for very specific pre-built paths. When complex multi-word keywords are sent, the URL structure breaks.
*   **Proposed Fix Strategy**:
    1. **Headless Bypass**: Launch Playwright with Undetected Chromium options (e.g. disabling the automation flag, configuring specific chrome user data profiles, or running in headful mode with realistic delay parameters).
    2. **Query Search URL**: Standardize searches onto `https://www.glassdoor.com.br/Job/jobs.htm?sc.keyword={encoded_kw}`.
    3. **Hierarchy-Based Parsing**: Instead of compilation-dependent classes (like `JobsList_jobListItem`), query DOM nodes hierarchically (e.g. list items inside the primary search result container).

### 5. Gupy (`scrapers/gupy.py`)
*   **Root Cause**:
    *   **Cloudflare Block on API**: The API endpoint `https://portal.gupy.io/api/job-search` (line 21) is protected. Direct requests from scripts trigger Cloudflare, returning 403 Forbidden.
    *   **Next.js Hydration Fallback Fail**: The fallback script parses `__NEXT_DATA__` from the page HTML (line 46). Since the original request is blocked by Cloudflare, the HTML returned is the challenge page, which does not contain the `__NEXT_DATA__` script tag, causing the fallback to fail and return an empty list.
*   **Proposed Fix Strategy**:
    1. **Impersonate Requests**: Implement `curl_cffi` using the `chrome110` impersonation template, combined with realistic headers (`Sec-Ch-Ua`, `Sec-Fetch-Mode`, etc.).
    2. **Alternative Host Extraction**: Query the Gupy jobs via their alternative API endpoints or extract the data using a session cookie obtained by loading the portal once via Playwright.

### 6. Vagas Com (`scrapers/vagas_com.py`)
*   **Root Cause**:
    *   **SEO Landing Page Fallacy**: The scraper targets `https://www.vagas.com.br/vagas-de-{encoded_kw}` (line 19) where spaces are replaced by hyphens. This format works only for standard, pre-built SEO tag pages (like `vagas-de-python`). For any custom/complex keyword (like `Especialista-em-IA-Generativa`), the page does not exist and returns a 404, leading to 0 results.
*   **Proposed Fix Strategy**:
    1. Change the search endpoint to Vagas.com's dynamic query endpoint: `https://www.vagas.com.br/vagas/?q={encoded_kw}` where `encoded_kw` is URL encoded (e.g. spaces encoded as `+` or `%20`). This query endpoint supports all keywords.
    2. Map the updated DOM container and CSS selectors on the dynamic search page.

### 7. Programathor (`scrapers/programathor.py`)
*   **Root Cause**:
    *   **SEO Landing Page Fallacy**: The scraper queries `https://programathor.com.br/jobs-{encoded_kw}` (line 19). Just like Vagas.com, this URL is an SEO-friendly path created only for popular tags. Custom keyword searches result in a 404 page.
    *   **Cloudflare Blocking**: Standard HTTP libraries are challenged by Programathor's Cloudflare security layer.
*   **Proposed Fix Strategy**:
    1. Change the search URL to Programathor's dynamic search endpoint: `https://programathor.com.br/jobs?text={encoded_kw}`.
    2. Employ `curl_cffi` with browser fingerprints to bypass Cloudflare.

### 8. Coodesh (`scrapers/coodesh.py`)
*   **Root Cause**:
    *   **SPA Client-Side Rendering**: Coodesh is a Single Page Application (Next.js/React). The initial page HTML is a blank container, and the jobs are loaded via frontend API calls. The `requests` library only fetches the initial blank HTML containing no job cards, so BeautifulSoup finds 0 results.
*   **Proposed Fix Strategy**:
    1. **Direct API Scraping**: Reverse-engineer Coodesh's public backend API endpoint (e.g., querying `https://api.coodesh.com/public/jobs?...`) instead of loading the HTML search page.
    2. **Browser Execution**: Alternatively, use Playwright to load `https://coodesh.com/vagas?search={encoded_kw}` and wait for the job list elements to be rendered in the DOM before parsing.

### 9. Geekhunter (`scrapers/geekhunter.py`)
*   **Root Cause**:
    *   **Mandatory Authentication Barrier**: Geekhunter requires candidates to log in to search or view jobs. Anonymous requests to `https://geekhunter.com.br/vagas` redirect to a signup/login screen or display an empty search shell.
    *   **Cloudflare Shield**: Geekhunter blocks bots using Cloudflare.
*   **Proposed Fix Strategy**:
    1. **Session Authentication**: Require credentials (`GEEKHUNTER_EMAIL`, `GEEKHUNTER_PASSWORD`) in `.env` and programmatically perform a login request, storing cookies for subsequent searches.
    2. **Playwright Login**: Automate the login sequence using Playwright and export session data/cookies to the scraper requests session.

---

## Systemic Logic Gaps in `bot.py`

During our investigation, we identified a critical integration gap in `bot.py` (lines 637-640):
```python
if plat in ['jsearch', 'jooble', 'github_vagas', 'novenove', 'freelancer', 'indeed', 'linkedin', 'gmail', 'glassdoor', 'infojobs']:
    res = await asyncio.to_thread(module.scrape, keyword=search_keyword, level="Todos", country=settings["location"])
else:
    res = await asyncio.to_thread(module.scrape, keyword=search_keyword, level="Todos")
```
### Observation
*   The scrapers `gupy`, `vagas_com`, `programathor`, `coodesh`, and `geekhunter` are NOT listed in the `if` block, so they are executed in the `else` clause **without the `country` parameter**.
*   However, these 5 scrapers have the signature: `def scrape(keyword, level="Todos", country="Brasil"):` and check:
    ```python
    if "Brasil" not in country:
        return jobs
    ```
### Impact
*   Since `bot.py` calls them without `country`, it defaults to `"Brasil"`. This works fine if the user is searching for remote jobs.
*   However, if the user configures local search for a specific city like `"Londrina/PR"` or `"Assaí/PR"` (via `/settings` command):
    *   The platforms in the `if` block receive `country="Londrina/PR"`.
    *   The 5 unlisted platforms (`gupy`, `vagas_com`, `programathor`, `coodesh`, `geekhunter`) still receive the default `country="Brasil"` and run nationwide, bypassing the user's localized setting and polluting local search results with national listings!
    *   If they were to receive the city (e.g. `country="Londrina/PR"`), they would return `[]` immediately due to the check `if "Brasil" not in country`. Thus, this logic gap results in unnecessary processing overhead and irrelevant results for regional caçadas.
