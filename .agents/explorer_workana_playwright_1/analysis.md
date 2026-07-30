# Workana Scraper Analysis Report

This report analyzes the current Workana scraper implementation (`vagas_bot/scrapers/workana.py`), identifies the limitations of the current request-based approach, and details the DOM structure required for a robust browser-based Playwright scraper.

---

## 1. Current Scraper Logic

The current scraper logic is implemented in the `scrape(keyword, level, max_pages)` function in `scrapers/workana.py` and works as follows:

### A. HTTP Requests & Fallback Mechanism
* **Keyword Normalization & Preprocessing**: The keyword is normalized (accent removal via NFKD normalization) and compared against co-occurrence rules defined in the bot config (`bot.CO_OCCURRENCE_RULES`). If a match is found, the search query is expanded using the top co-occurring terms. The search level (if not "Todos") is appended to the keyword, and the query is URL-encoded.
* **Request Execution**:
  - The script prioritizes `curl_cffi` (with browser impersonation configured for `chrome110` and custom headers like User-Agent, Accept-Language, Accept) to bypass basic bot-detection mechanisms.
  - If `curl_cffi` is not installed or raises an exception, the scraper falls back to standard Python `requests.get` with standard headers and a 15-second timeout.
  
### B. Pagination Flow
* **Loop Structure**: The scraper iterates over pages from `1` to `max_pages`.
* **Delays**: To simulate human browsing behavior, a random delay of `2.0` to `4.5` seconds (`time.sleep`) is added between requests for all pages beyond the first page.
* **Termination Conditions**: The pagination loop breaks early if:
  1. The response status code is `429` (Too Many Requests).
  2. The expected Vue.js entry point element (`<search>`) or its attributes are missing from the parsed HTML.
  3. The results list extracted from the page payload is empty.

### C. Parsing & Job Extraction
* **BeautifulSoup Parsing**: The response HTML is parsed using BeautifulSoup (`html.parser`).
* **Vue.js Payload Extraction**: Workana's page bootstrapping embeds the search results in the Vue.js component attributes. The script extracts the element `<search>` and reads the `:results-initials` attribute, decoding it as a JSON object via `json.loads`.
* **Fields Extraction**:
  - **Title**: Extracted from the `title` attribute of the result items. BeautifulSoup is used to strip any HTML tags (e.g. bold highlights) from the title text.
  - **Link**: Formed as `https://www.workana.com/job/{slug}` based on the `slug` attribute of the item. Falls back to the search page URL if `slug` is empty.
  - **Requirements (Description)**: Extracted from the `description` attribute and stripped of HTML formatting tags via BeautifulSoup.
  - **Budget**: Extracted from the `budget` attribute (defaults to `"A Combinar"`).
  - **Standard Metadata**: Fills platform as `"Workana"`, company as `"Cliente Workana"` (since specific client company names are not exposed on freelance postings), job type as `"PJ"`, profession as the queried `keyword`, level as the queried `level`.

---

## 2. Dynamic Loading Issues & Limitations

The current request-based scraper (`curl_cffi` and `requests`) suffers from critical limitations when scraping the live Workana platform:

### A. Cloudflare Protection & Bot Detection
Workana utilizes Cloudflare to protect its website. A stateless GET request via `requests` or even `curl_cffi` can trigger Cloudflare's Turnstile, CAPTCHA, or JS challenges. 
* **The Symptom**: When challenged, the request returns a `403 Forbidden`, `503 Service Unavailable`, or a Cloudflare landing page.
* **Scraper Impact**: Since the challenge page does not contain the Vue.js `<search>` tag, the scraper returns `None` for the tag search and halts immediately with 0 jobs.

### B. Client-Side Rendering (CSR)
Workana is an SPA-like application built with Vue.js. 
* **The Symptom**: Instead of server-side rendering the search results directly as HTML tags, the page relies on mounting a Vue component. If Workana moves its initial bootstrap data out of the HTML static payload (e.g. fetching it via dynamic asynchronous AJAX/Fetch calls to an internal API like `/api/jobs` after mounting), stateless scrapers will only see a skeleton HTML template.
* **Scraper Impact**: Since raw HTTP libraries cannot execute Javascript, the Vue application never mounts and the job items are never fetched or rendered, leading to 0 scraped vacancies.

### C. Template Tag & Attribute Changes
In modern frontend builds, Vue component tag names and properties are frequently changed or minified. 
* **The Symptom**: In different versions of the Workana application, developers might change the tag name from `<search>` to `<search-project-list>`, rename the attribute from `:results-initials` to `:initials`, or restructure the JSON structure (e.g. using `projects` instead of `results` in the payload).
* **Scraper Impact**: Because the parsing logic is hardcoded to specific tags (`soup.find('search')`) and JSON keys (`data.get('results')`), any update in the frontend deployment immediately breaks the scraper.

---

## 3. DOM Structure of Workana Job Items

To implement a robust browser-based scraper using Playwright, we must target the DOM elements rendered by the browser after JavaScript execution. The following selectors define the structure of the Workana jobs list page:

### A. Core Elements & Classes
* **Job Card Container**:
  - Class: `.project-item`, `.project-card`, or `.project-card-item` (or matching attribute tags like `div[class*="project-item"]`).
  - *Playwright selector*: `div.project-item` or `div.project-card`
* **Job Title**:
  - Class: `.project-title`, `.project-card-title`, or `h2.project-title`.
  - *Playwright selector*: `.project-title a` or `h2.project-title a`
* **Job Link**:
  - Extracted from the `href` attribute of the title anchor (`<a>`) tag.
  - *Playwright selector*: `.project-title a[href]`
* **Job Budget / Salary**:
  - Class: `.project-budget`, `.budget`, `.budget-amount`, `.price`, or `.project-card-budget`.
  - *Playwright selector*: `.budget span` or `span.budget`
* **Job Description / Requirements**:
  - Class: `.project-details`, `.project-description`, `.description`, `.project-card-description`, or `.project-body`.
  - *Playwright selector*: `.project-details` or `.project-description`
* **Client / Company**:
  - Workana does not display corporate company names. The client details are often shown in `.client-name` or `.project-card-client`. A generic fallback of `"Cliente Workana"` is used if unavailable.

### B. Suggested Playwright Implementation Strategy
To transition the Workana scraper to Playwright:
1. Launch Chromium with `headless=True` (or `headless=False` for local debugging/bypass checks).
2. Configure a stealth layer (`playwright-stealth`) to bypass Cloudflare detection.
3. Navigate to `https://www.workana.com/jobs?query={search_kw}&page={page}` and wait until the DOM is loaded (`wait_until="domcontentloaded"`).
4. Locate the list of cards using `page.query_selector_all('div.project-item')` or fallback card selectors.
5. Loop through cards and extract titles, links, budgets, and descriptions dynamically from the DOM text contents.
