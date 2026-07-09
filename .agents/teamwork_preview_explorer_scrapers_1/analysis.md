# Scrapers Investigation Report - Explorer 1

This report details the investigation of the 9 job scrapers under `scrapers/` to verify why they return 0 results or fail. Detailed root causes and step-by-step fix strategies are provided for each scraper.

---

## Executive Summary

- **Working Scrapers (2/9)**: 
  - **Workana**: Fully operational. Returns raw Vue.js preloaded payloads.
  - **Vagas.com**: Fully operational. BS4 selectors successfully extract job listings.
- **Failing Scrapers (7/9)**:
  - **Jsearch**: Deactivated/Expired RapidAPI key (Status 404).
  - **Remotar**: Client-Side Rendering (CSR) template is empty on raw requests.
  - **Glassdoor**: Fooled by Cloudflare challenge pages due to weak success verification logic.
  - **Gupy**: Legacy search API endpoint decommissioned; needs redirection to the new employability API.
  - **Programathor**: Case-sensitivity bug in URL path (requests capital `Python` instead of lowercase `python`, returning 404/redirect).
  - **Coodesh**: Client-Side Rendering shell; needs API query with custom key `x-csh-key: coodesh-experts`.
  - **Geekhunter**: Domain changed and CSR skeletons block BS4 queries; needs updated path and selector parsing.

---

## Detailed Findings and Protests for Each Scraper

### 1. Jsearch (`scrapers/jsearch.py`)
- **Status**: Returns 0 results.
- **Direct Observation (Evidence)**:
  Direct HTTP query to `https://jsearch.p.rapidapi.com/search` using the hardcoded API key `7af3cebf37mshb1adb579644f3d1p1f605fjsn26d9e7a63fe0` returned:
  `Status: 404`
  `Response JSON: {'message': "Endpoint '/search' does not exist"}`
- **Reason for Failure**:
  RapidAPI routes requests to a 404 fallback when a subscription is deactivated, expired, or blocked. The hardcoded key is invalid or exhausted.
- **Proposed Fix Strategy**:
  Ensure the client provides a valid RapidAPI JSearch key in their `.env` file under `JSEARCH_API_KEY`. The python code already reads `os.environ.get("JSEARCH_API_KEY")`, so updating the environment variables will fix this scraper without code modifications.

### 2. Workana (`scrapers/workana.py`)
- **Status**: SUCCESS (returns 14+ jobs).
- **Direct Observation (Evidence)**:
  Running the custom test returned:
  `TESTING SCRAPER: Workana`
  `STATUS: SUCCESS`
  `RESULTS RETURNED: 14`
- **Reason for Success**:
  The scraper correctly retrieves the raw Vue.js preload payload inside the `<search>` tag's `:results-initials` attribute and deserializes it directly from JSON, which is highly robust.
- **Proposed Fix Strategy**: No action needed.

### 3. Remotar (`scrapers/remotar.py`)
- **Status**: Returns 0 results.
- **Direct Observation (Evidence)**:
  Evaluating raw HTML returned from `https://remotar.com.br/search/jobs?q=Python` showed:
  - `job-list-item` class divs found: 0
  - Next.js initial JSON data `__NEXT_DATA__` has empty `pageProps`.
- **Reason for Failure**:
  Remotar has migrated to a fully client-side rendered (CSR) Next.js structure. The raw HTML response contains only loading wrappers, meaning the BeautifulSoup scraper cannot locate `job-list-item` divs.
- **Proposed Fix Strategy**:
  Rewrite `remotar.py` to use `playwright` (already available in the environment) to load the page dynamically and wait for elements to render.
  - **Playwright Navigation**: Navigate to search URL and wait for `a.job-title` to render.
  - **Card Selector**: Locate parent elements or simply query all `a.job-title` tags.
  - **Data Parsing**:
    - **Title**: `a.job-title` text.
    - **Link**: Sibling `href` inside `a.job-title` (prefixed with `https://remotar.com.br`).
    - **Company**: Sibling `a.company` text.

### 4. Glassdoor (`scrapers/glassdoor.py`)
- **Status**: Returns 0 results.
- **Direct Observation (Evidence)**:
  Tracing the scraper execution showed that navigating to the first URL `https://www.glassdoor.com.br/Vagas/...` triggered a Cloudflare challenge page.
  The validation logic in `glassdoor.py`:
  `if ("glassdoor" in content.lower() or "mock" in content.lower()) and len(content) > 20`
  matched `True` on the Cloudflare challenge page because it contains the brand name "Glassdoor". This caused the scraper to cease trying the second (working) URL, and attempt to parse the challenge page, finding 0 cards.
- **Proposed Fix Strategy**:
  - **Enhance Validation**: Detect Cloudflare/CAPTCHA challenge pages explicitly by checking for texts like `"security check"`, `"captcha"`, `"checking your browser"`, or `"cloudflare"` in `content.lower()` and treating them as page load failures.
  - **Reorder URLs**: Put the query-parameter search URL `https://www.glassdoor.com.br/Job/jobs.htm?sc.keyword=...` first, as it has a higher bypass rate.
  - **Selectors**: Ensure card selectors match `li[data-test="jobListing"]` and link selectors capture `a[href*="/job-listing/"]` or `a[href*="/partner/jobListing.htm"]`.

### 5. Gupy (`scrapers/gupy.py`)
- **Status**: Returns 0 results.
- **Direct Observation (Evidence)**:
  Direct HTTP query to the scraper's target endpoint `https://portal.gupy.io/api/job-search?term=Python` returned:
  - `Status: 200`
  - `Content-Type: text/html` (re-routes to the SPA landing page shell instead of returning JSON).
- **Reason for Failure**:
  The legacy `/api/job-search` endpoint has been decommissioned.
- **Proposed Fix Strategy**:
  Change the API target endpoint to Gupy's new employability portal search API.
  - **New URL**: `https://employability-portal.gupy.io/api/v1/jobs?jobName={encoded_kw}&limit=30`
  - **No Schema Changes**: The JSON keys returned by this new endpoint (`name`, `careerPageName`, `jobUrl`, `type`, `city`, `state`, `description`) are identical to those expected by the scraper. Simply updating the URL restores the scraper.

### 6. Vagas.com (`scrapers/vagas_com.py`)
- **Status**: SUCCESS (returns 30 jobs).
- **Direct Observation (Evidence)**:
  Running the custom test returned:
  `TESTING SCRAPER: Vagas.com`
  `STATUS: SUCCESS`
  `RESULTS RETURNED: 30`
- **Reason for Success**:
  The scraper uses BeautifulSoup on raw HTML and the card class search `li vaga` successfully captures the pre-rendered cards.
- **Proposed Fix Strategy**: No action needed.

### 7. Programathor (`scrapers/programathor.py`)
- **Status**: Returns 0 results.
- **Direct Observation (Evidence)**:
  Quoting a query containing uppercase letters (e.g. `Python`) requests `https://programathor.com.br/jobs-Python`. This returns a 404 or redirects to the homepage because Programathor slugs are strictly lowercase. Lowercase queries to `jobs-python` return 47+ results successfully.
- **Reason for Failure**:
  The URL generator does not force the keyword to lowercase before replacing spaces with hyphens.
- **Proposed Fix Strategy**:
  In `scrapers/programathor.py`, change:
  `encoded_kw = urllib.parse.quote(search_kw.replace(' ', '-'))`
  to:
  `encoded_kw = urllib.parse.quote(search_kw.replace(' ', '-').lower())`

### 8. Coodesh (`scrapers/coodesh.py`)
- **Status**: Returns 0 results.
- **Direct Observation (Evidence)**:
  - Raw HTML contains only 16 divs and 1 link (empty Chakra UI container shell).
  - Querying Coodesh's public API `https://api.coodesh.com/v2/jobs` directly returned `401 Unauthorized` with body `{"message":"Faça a requisição utilizando o token de sessão"}`.
  - Browser network trace shows the browser authorizes API requests using the custom header `x-csh-key: coodesh-experts`.
- **Reason for Failure**:
  Coodesh is client-side rendered (meaning the BS4 scraper on raw HTML finds nothing). Direct API calls fail without the authorization header.
- **Proposed Fix Strategy**:
  Bypass HTML scraping entirely and consume Coodesh's public API by sending the authorization headers.
  - **Headers**:
    ```python
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'referer': 'https://coodesh.com/',
        'x-csh-key': 'coodesh-experts',
        'x-language': 'pt'
    }
    ```
  - **API Request**: `https://api.coodesh.com/v2/jobs?search={encoded_kw}&pageSize=30`
  - **JSON Parser**:
    - List of jobs: `data['docs']`
    - Title: `item.get('title')`
    - Company Name: `item.get('company', {}).get('company_name')`
    - Link: `https://coodesh.com/vagas/` + `item.get('slug')`
    - Requirements: `", ".join([s['name'] for s in item.get('skills', [])])`

### 9. Geekhunter (`scrapers/geekhunter.py`)
- **Status**: Returns 0 results.
- **Direct Observation (Evidence)**:
  - Geekhunter has migrated domain from `geekhunter.com.br` to `geekhunter.com/pt`.
  - The page uses Chakra UI loading skeletons, which are empty on raw HTML requests.
  - Class name `'job'` is no longer used in job card wrappers.
- **Reason for Failure**:
  Domain has changed, the elements are rendered dynamically, and the scraper searches for obsolete card classes on an empty skeleton template.
- **Proposed Fix Strategy**:
  - **Update Domain**: Navigate/request `https://www.geekhunter.com/pt/vagas?q={encoded_kw}`.
  - **BS4 Link Parsing**: The raw HTML response *does* contain server-pre-rendered job links within `a` tags containing `/jobs/` in their href attributes. We can extract these links directly:
    - Target: `soup.find_all('a', href=lambda h: h and '/jobs/' in h)`
    - Title: Sibling/child element text, e.g. `<p class="chakra-text css-q4uo1b">` or first `<p>` tag text.
    - Company: Extracted from the URL path: splitting the href `/pt/<company-name>/jobs/...` by `/` and grabbing the 4th element.
    - Requirements: Joining the list of skill divs (class `css-dqhvn`).
