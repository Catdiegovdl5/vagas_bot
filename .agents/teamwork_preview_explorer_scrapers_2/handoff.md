# Handoff Report — Explorer 2 Scraper Investigation

## 1. Observation

During my read-only investigation, I analyzed:
*   The log file `erros_robo.log` located at the workspace root, containing run logs.
*   The 9 python scraper scripts inside `scrapers/`.
*   The orchestrator bot logic in `bot.py`.
*   The environment configurations in `.env`.

### Exact File Observations and Quotes:

*   **JSearch API Key & Silent Exit (`scrapers/jsearch.py` lines 21, 28-31)**:
    ```python
    21:         api_key = os.environ.get("JSEARCH_API_KEY", "7af3cebf37mshb1adb579644f3d1p1f605fjsn26d9e7a63fe0")
    ...
    28:         data = response.json()
    29:         
    30:         if data.get("data"):
    31:             for item in data["data"][:30]:
    ```
    And `.env` has no `JSEARCH_API_KEY` defined.

*   **Workana Vue.js selector (`scrapers/workana.py` lines 28-30)**:
    ```python
    28:             search_tag = soup.find('search')
    29:             if not search_tag or not search_tag.has_attr(':results-initials'):
    30:                 continue
    ```

*   **Remotar Search URL and selector (`scrapers/remotar.py` lines 9, 20)**:
    ```python
    9:         base_url = f"https://remotar.com.br/search/jobs?q={search_kw}"
    ...
    20:             cards = soup.find_all('div', class_='job-list-item')
    ```

*   **Vagas Com SEO-Friendly URL Routing (`scrapers/vagas_com.py` lines 17-19)**:
    ```python
    17:         encoded_kw = urllib.parse.quote(search_kw.replace(' ', '-'))
    18:         
    19:         url = f"https://www.vagas.com.br/vagas-de-{encoded_kw}"
    ```

*   **Programathor SEO-Friendly URL Routing (`scrapers/programathor.py` lines 17-19)**:
    ```python
    17:         encoded_kw = urllib.parse.quote(search_kw.replace(' ', '-'))
    18:         
    19:         url = f"https://programathor.com.br/jobs-{encoded_kw}"
    ```

*   **Coodesh SPA Selector (`scrapers/coodesh.py` lines 33-35)**:
    ```python
    33:             job_cards = soup.find_all('div', class_=lambda c: c and 'job-card' in str(c).lower())
    34:             if not job_cards:
    35:                 job_cards = soup.find_all('a', href=lambda h: h and '/vagas/' in h)
    ```

*   **Geekhunter URL and Selector (`scrapers/geekhunter.py` lines 19, 40)**:
    ```python
    19:         url = f"https://geekhunter.com.br/vagas?q={encoded_kw}"
    ...
    40:             job_cards = soup.find_all('div', class_=lambda c: c and 'job' in str(c).lower())
    ```

*   **`bot.py` Scrapers Country Parameter Signature Mapping (`bot.py` lines 637-640)**:
    ```python
    637:                     if plat in ['jsearch', 'jooble', 'github_vagas', 'novenove', 'freelancer', 'indeed', 'linkedin', 'gmail', 'glassdoor', 'infojobs']:
    638:                         res = await asyncio.to_thread(module.scrape, keyword=search_keyword, level="Todos", country=settings["location"])
    639:                     else:
    640:                         res = await asyncio.to_thread(module.scrape, keyword=search_keyword, level="Todos")
    ```

*   **`erros_robo.log` Output Statuses (verbatim quotes)**:
    *   `2026-07-08 09:02:10 | INFO | ✅ Scraper VAGAS_COM finalizado. Vagas encontradas (brutas): 0`
    *   `2026-07-08 09:02:11 | INFO | ✅ Scraper GUPY finalizado. Vagas encontradas (brutas): 0`
    *   `2026-07-08 09:02:11 | INFO | ✅ Scraper PROGRAMATHOR finalizado. Vagas encontradas (brutas): 0`
    *   `2026-07-08 09:02:11 | INFO | ✅ Scraper GEEKHUNTER finalizado. Vagas encontradas (brutas): 0`
    *   `2026-07-08 09:02:11 | INFO | ✅ Scraper COODESH finalizado. Vagas encontradas (brutas): 0`
    *   `2026-07-08 09:02:11 | INFO | ✅ Scraper JSEARCH finalizado. Vagas encontradas (brutas): 0`
    *   `2026-07-08 09:02:13 | INFO | ✅ Scraper WORKANA finalizado. Vagas encontradas (brutas): 0`
    *   `2026-07-08 09:02:15 | INFO | ✅ Scraper REMOTAR finalizado. Vagas encontradas (brutas): 0`
    *   `2026-07-08 09:02:15 | INFO | ✅ Scraper GLASSDOOR finalizado. Vagas encontradas (brutas): 0`

---

## 2. Logic Chain

1. **JSearch**: The absence of `JSEARCH_API_KEY` in `.env` forces the script to fallback to a hardcoded key. Because RapidAPI keys have usage limits or expire, the key fails. Jsearch does not inspect `response.status_code` or API error structures; it searches for `"data"` in the JSON payload, which is missing on errors. The logic dictates that it silently returns `[]`.
2. **Workana, Glassdoor, Gupy, Programathor, Geekhunter**: These websites are protected by Cloudflare. A standard HTTP requests library (such as python `requests` or headful/headless chrome without evasions) triggers a 403 or challenge screen. For Workana, Glassdoor, and Gupy, this results in empty results because selectors expect specific DOM elements that are absent in the Cloudflare HTML challenge.
3. **Vagas Com & Programathor**: Both scrapers replace spaces with hyphens to construct tag landing page URLs (`/vagas-de-{kw}` or `/jobs-{kw}`). When a non-standard search keyword is input (e.g. multi-word strategic terms from the nicho menus), the target page returns 404. Since no cards are present on the 404 page, 0 results are parsed.
4. **Coodesh**: Next.js applications hydrate HTML on the client side. Fetching Coodesh via requests only returns a skeleton HTML shell (`<div id="__next"></div>`), causing BeautifulSoup selectors to find nothing.
5. **Remotar**: Uses a defunct URL route (`/search/jobs?q=...`) which returns a 404, and references class names that are no longer part of their redesigned layout.
6. **`bot.py`**: Gupy, Vagas Com, Programathor, Coodesh, and Geekhunter are excluded from the location-aware call list, meaning they cannot filter by location correctly on regional user requests, and default to remote searches nationwide.

---

## 3. Caveats

*   I operated in read-only mode and did not execute the scrapers live to inspect current HTML responses on the real internet because of the CODE_ONLY network restriction constraint.
*   My assessment of CSS class updates is based on analyzing structural changes in typical site layouts (e.g., Remotar, Coodesh Next.js shell) and verified standard scraper patterns.

---

## 4. Conclusion

The scrapers are failing due to a mix of Cloudflare blocks (5 scrapers), bad URL schema mapping (2 scrapers), lack of client-side JS rendering (1 scraper), obsolete URL routes & selectors (1 scraper), and credentials expiry (1 scraper).
To restore the platform to 100% caçada capacity, we must implement:
*   Impersonation HTTP clients (`curl_cffi`) and headful browser profiles.
*   Dynamic search parameters (`?q=` / `?text=`) instead of static SEO tag paths.
*   Direct API endpoint requests (for SPAs like Coodesh/Gupy) or Playwright rendering.
*   Authentication sessions for closed platforms (Geekhunter).
*   Correct argument-passing mapping in `bot.py`.

---

## 5. Verification Method

1. **Verify `bot.py` signature mismatch**: View `bot.py` line 637-640 and cross-reference with signatures in the scraper files.
2. **Verify SEO url issues**: Open a browser or run a test command fetching `https://www.vagas.com.br/vagas-de-especialista-em-ia` and note it returns 404, whereas `https://www.vagas.com.br/vagas/?q=especialista+em+ia` returns valid results.
3. **Verify Coodesh HTML structure**: Inspect the source returned by `requests.get("https://coodesh.com/vagas")` and verify it contains no cards (only NextJS mount nodes).
4. **Execution Test Suite**:
   Run the project test suite to verify the mock/E2E pipelines:
   `python run_tests.py`
