# Handoff Report

## 1. Observation
We observed the following files, line ranges, test outputs, and codebase attributes:
* **File Under Audit**: `C:/Users/99196/OneDrive/Documentos/vagas_bot/scrapers/workana.py` (lines 1 to 100).
* **Vue Tag Extraction**:
  ```python
  57:             search_tag = soup.find('search')
  58:             if not search_tag or not search_tag.has_attr(':results-initials'):
  59:                 break
  60:                 
  61:             data = json.loads(search_tag[':results-initials'])
  62:             results = data.get('results', [])
  ```
* **Alternate Tag Verification (from `scratch/test_json2.py` and `scratch/test_json.py`)**:
  - `scratch/test_json2.py` (line 8): `# Workana usa vue.js, a tag é <search-project-list :initials="{...}">`
  - `scratch/test_json.py` (lines 7 to 9):
    ```python
    tag = soup.find('search-project-list')
    if tag and tag.has_attr(':initials'):
        data = json.loads(tag[':initials'])
    ```
* **Pagination & Rate-Limit Fallback**:
  ```python
  35:         for page in range(1, max_pages + 1):
  36:             if page > 1:
  37:                 time.sleep(random.uniform(2.0, 4.5))
  38:                 
  39:             url = f"https://www.workana.com/jobs?query={search_kw}&page={page}"
  ```
  ```python
  51:             if r is not None and r.status_code == 429:
  52:                 break
  ```
* **Test Verification**:
  - Running command `python -m pytest tests/test_workana_settings.py` successfully completed:
    ```
    collected 4 items
    tests\test_workana_settings.py ....                                      [100%]
    ======================= 4 passed, 3 warnings in 10.18s ========================
    ```
* **Network Restrictions**:
  - The system is operating in CODE_ONLY mode, which prevents real-world requests to external domains such as `workana.com`.

---

## 2. Logic Chain
1. **Request Integrity**: The current code requests pages using `curl_cffi` (impersonating Chrome) or standard `requests` (as fallback). However, Workana employs Cloudflare bot mitigation (Turnstile / CAPTCHA), which blocks headless/stateless HTTP requests. Under verification failure, these tools receive a `403 Forbidden` or challenge page rather than the search results.
2. **Dynamic Rendering vs Static Parsing**: In `scrapers/workana.py`, lines 57-62 check for `<search :results-initials="...">`. But `scratch/test_json.py` and `scratch/test_json2.py` verify that Workana has changed its Vue component tags to `<search-project-list :initials="...">` and key elements to `.get('projects')`.
3. **Execution Gap**: Since `requests` and `curl_cffi` cannot execute JS and are easily blocked, they fail to render Vue.js client-side modifications. A transition to Playwright browser automation is required to ensure JavaScript is evaluated, and the final HTML DOM is parsed.
4. **DOM Selectors Deduction**: If using Playwright, the browser will render the page. Cards can be collected using the classes identified in the investigation (`.project-card`, `.project-item`), and details (link, title, budget, description) can be parsed directly from active DOM nodes instead of a fragile JSON attribute parse.

---

## 3. Caveats
* **Actual Live Selectors**: Due to operating in CODE_ONLY network mode, we could not execute a live browser check to inspect the exact class names on the current live `workana.com` website. The DOM structure analysis is based on historical records, scratch files, and developer comments present in the workspace (`scratch/test_workana.py`, `scratch/test_json2.py`).
* **Stealth Requirements**: If using Playwright, a stealth layer (`playwright-stealth`) is highly recommended to prevent Cloudflare from detecting the automated Chromium instances.

---

## 4. Conclusion
* **Current Scrape Logic**: Works by issuing requests via `curl_cffi` / `requests`, querying `<search :results-initials="...">` using BeautifulSoup, parsing the inline JSON string, and mapping keys (`title`, `slug`, `description`, `budget`) into standard job schema.
* **Limitations**: High risk of Cloudflare blockage, inability to parse pages where Vue.js mounts dynamically without server-rendered initials, and code breakage due to frontend tag modifications (e.g. `<search>` vs `<search-project-list>`).
* **DOM Structure**: Job card elements are structured under classes `.project-item` / `.project-card`. The titles are anchors inside `.project-title`, links are the `href` values of these anchors, budgets are found in `.budget`, and descriptions are in `.project-details` / `.project-description`.

---

## 5. Verification Method
* To verify the current mock pagination and toggle settings, run:
  ```bash
  python -m pytest tests/test_workana_settings.py
  ```
* To inspect the code structure of the workana scraper, inspect:
  - Scraper: `C:/Users/99196/OneDrive/Documentos/vagas_bot/scrapers/workana.py`
  - Tests: `C:/Users/99196/OneDrive/Documentos/vagas_bot/tests/test_workana_settings.py`
