# CLT Scrapers Evaluation and Integration Plan

## Executive Summary
This report presents a detailed evaluation of the CLT scrapers in the `vagas_bot` codebase (`gupy.py`, `catho.py`, `infojobs.py`, and `vagas_com.py`) and outlines a plan to refactor and integrate them natively as asynchronous modules under a standard async signature: `async def scrape(keyword, level="Todos", max_pages=...)`.

---

## 1. Scraper Integration & Architecture in `bot.py`

### 1.1 How Scrapers are Managed
In `bot.py`, scrapers are managed dynamically via a platform settings mapping. In `DEFAULT_SETTINGS["platforms"]` (lines 79-97), platforms are defined with boolean values indicating whether they are active:
- **Nacionais (CLT)**: `gupy`, `catho`, `infojobs`, `vagas_com` (grouped as Nacionais under configuration menu).
- **Globais (CLT/PJ)**: `linkedin`, `indeed`, `glassdoor`.
- **Foco em TI**: `coodesh`, `geekhunter`, `programathor`, `github_vagas`.
- **Remotos**: `remotar`, `jooble`, `jsearch`.
- **Freelance**: `workana` (and `gmail`, `novenove` which are toggled off by default).

### 1.2 Import, Configuration, and Execution Flow
Scraper execution occurs in the `_do_hunt(keyword, message, callback)` function in `bot.py` (lines 993-1411):
1. **Keyword Mapping**: Before searching, the user-selected job niche title (e.g., `"Especialista em IA"`) is translated into a search term (e.g., `"Especialista IA"`) using `search_mapping` (lines 1044-1164).
2. **Dynamic Importing**: The function `fetch_plat(plat)` imports the corresponding scraper module using `importlib.import_module(f"scrapers.{plat}")` (line 1178).
3. **Execution Routing**:
   - The bot inspects whether the scraper's `scrape` function is a coroutine:
     ```python
     if inspect.iscoroutinefunction(module.scrape):
         res = await module.scrape(keyword=plat_search_keyword, level="Todos")
     else:
         if plat in [...]:
             res = await asyncio.to_thread(module.scrape, keyword=plat_search_keyword, level="Todos", country=settings["location"])
         else:
             res = await asyncio.to_thread(module.scrape, keyword=plat_search_keyword, level="Todos")
     ```
   - *Issue*: Synchronous scrapers (all except `workana`) are executed in separate threads using `asyncio.to_thread`. InfoJobs, which uses synchronous Playwright internally, is also run within an executor thread, which is resource-intensive and prone to event-loop scheduling conflicts.

---

## 2. Job Relevance Filtering (`is_job_relevant`)

The relevance of gathered jobs is verified locally via `is_job_relevant(job, keyword, settings)` (lines 915-991) to filter out garbage and misclassified postings before alerting the user:
1. **Talent Pool Bypass**: Rejects jobs whose title contains `"banco de talentos"` or `"talent pool"`.
2. **Location Filtering**:
   - If user location is `"Brasil (Remoto)"`:
     - Freelance platforms are exempt.
     - Presential/hibrido jobs that do not explicitly mention `"remoto"` are discarded.
     - Non-remote jobs with a local city not containing `"brasil"` or `"brazil"` are discarded.
   - If user location is `"Londrina/PR"` or `"Assaí/PR"`:
     - Discards jobs not matching local city whitelist (e.g. Londrina, Assaí, Cambé, etc.) or lacking remote terms.
3. **Contract Filtering**:
   - If `clt` is selected, discards jobs mentioning `pj`, `freelancer`, or `pessoa juridica` unless they also mention `clt`.
   - If `pj` is selected, discards jobs mentioning `clt` or `carteira assinada` unless they also mention `pj`.
4. **Seniority Check**: Checks job title against level boundaries:
   - Junior: Discards if title contains senior/pleno terms.
   - Pleno: Discards if title contains junior/senior terms.
   - Senior: Discards if title contains junior/pleno terms.
5. **Blacklist Check**:
   - Compares job title with `global_title_blacklist` (e.g., professor, advogado, médico, etc.), ignoring words present in the query `keyword`.
   - Compares job title with niche-specific blacklists in `blacklist` mapping (e.g. for `especialista em ia`, blocks `vendas`, `marketing`, `trafego`, etc.).
6. **Co-Occurrence Verification**: Calls `check_co_occurrence(full_text, kw_norm, job)`:
   - If keyword matches keys in `CO_OCCURRENCE_RULES`, it enforces that at least one term from Group A and one term from Group B are present in the text (e.g., for `especialista em ia`, Group A contains AI terms and Group B contains professional/action terms).

---

## 3. Analysis of Existing Scrapers

### 3.1 `scrapers/gupy.py` (Employability API)
- **Mechanism**: Standard HTTP client using `curl_cffi` (impersonates Chrome 110) falling back to standard `requests` if `curl_cffi` is unavailable.
- **Data Source**: Fetches JSON from `https://employability-portal.gupy.io/api/v1/jobs?jobName={keyword}&limit=30`. Fallback parses HTML parsing of the `__NEXT_DATA__` script tag.
- **Status**: Synchronous.

### 3.2 `scrapers/catho.py` (HTML Scraping)
- **Mechanism**: Requests HTML via `curl_cffi` (Chrome 110) or standard `requests`. Parses cards using `BeautifulSoup`.
- **Data Source**: Scrapes `https://www.catho.com.br/vagas/{keyword}/?q={keyword}`.
- **Status**: Synchronous.

### 3.3 `scrapers/vagas_com.py` (HTML Scraping)
- **Mechanism**: Requests HTML via `curl_cffi` (Chrome 110) or standard `requests`. Parses list items using `BeautifulSoup`.
- **Data Source**: Scrapes `https://www.vagas.com.br/vagas-de-{keyword_hyphenated}`.
- **Status**: Synchronous.

### 3.4 `scrapers/infojobs.py` (Playwright / curl_cffi Hybrid)
- **Mechanism**: Uses `sync_playwright` (with `stealth_sync` protection bypass) to navigate to the search page. Once job cards are located:
  1. For each card (up to 15), it extracts basic metadata (title, company, link, salary).
  2. To retrieve job requirements, it attempts a fast HTTP GET request via `curl_cffi` targeting the job link.
  3. If blocked or timed out (indicated by Cloudflare pages or consecutive failures), it falls back to opening a new Playwright page (`context.new_page()`) to load and query the description.
- **Status**: Synchronous wrapper enclosing a synchronous Playwright session.

### 3.5 `scrapers/workana.py` (Reference Playwright Async)
- **Mechanism**: Native async function using `async_playwright` and `stealth_async`.
- **Structure**:
  - Implements `async def scrape(keyword="Python", level="Todos", max_pages=100)`.
  - Normalizes search keyword and maps it using `bot.CO_OCCURRENCE_RULES` dynamically to query broad terms first, avoiding over-filtering on the platform search.
  - Loops up to `max_pages` with random pauses (`asyncio.sleep(random.uniform(2.5, 5.0))`).
  - Fetches project cards via `page.query_selector_all(".project-item")` and closes browser cleanly.

---

## 4. Platform Viability & Refactoring Plan

### 4.1 Platform Viability Matrix

| Platform | Viability | Pros | Cons | Recommended Engine |
|---|---|---|---|---|
| **Gupy** | **Extremely High** | Public JSON API; fast; clean data; no Cloudflare blocks. | No major cons. | `curl_cffi` (Async) |
| **Catho** | **High** | Stable HTML structure; standard selectors. | Moderate Cloudflare block risk. | `curl_cffi` (Async) |
| **Vagas.com** | **High** | Stable HTML; easy to query. | Search keyword formatting needs hyphen replacement. | `curl_cffi` (Async) |
| **InfoJobs** | **Medium** | Large market share of CLT jobs in Brazil. | Heavy Cloudflare protection; slow; requires Playwright. | `playwright.async_api` |

### 4.2 Refactoring Blueprint to Async Signature

To integrate CLT scrapers smoothly with `workana.py` and prevent thread blocking, all CLT modules must be refactored to follow the signature:
`async def scrape(keyword, level="Todos", max_pages=1)`

#### A. Gupy Scraper Refactoring (`scrapers/gupy.py`)
- **Engine**: Replace synchronous `requests`/`curl_cffi` with `curl_cffi.requests.AsyncSession` or `aiohttp`.
- **Pagination**: Implement a loop up to `max_pages`. Pass the pagination parameters to Gupy's API:
  `api_url = f"https://employability-portal.gupy.io/api/v1/jobs?jobName={encoded_kw}&limit=30&offset={offset}"` where `offset = (page - 1) * 30`.
- **Code Sketch**:
  ```python
  from curl_cffi.requests import AsyncSession

  async def scrape(keyword, level="Todos", max_pages=1):
      jobs = []
      limit = 30
      async with AsyncSession() as session:
          for page in range(1, max_pages + 1):
              offset = (page - 1) * limit
              api_url = f"https://employability-portal.gupy.io/api/v1/jobs?jobName={urllib.parse.quote(keyword)}&limit={limit}&offset={offset}"
              response = await session.get(api_url, impersonate="chrome110", timeout=15)
              # parse JSON and append jobs...
      return jobs
  ```

#### B. Catho Scraper Refactoring (`scrapers/catho.py`)
- **Engine**: Replace with `curl_cffi.requests.AsyncSession`.
- **Pagination**: Catho paginates via `&page={page}`.
- **Code Sketch**:
  ```python
  async def scrape(keyword, level="Todos", max_pages=1):
      jobs = []
      async with AsyncSession() as session:
          for page in range(1, max_pages + 1):
              url = f"https://www.catho.com.br/vagas/{urllib.parse.quote(keyword)}/?q={urllib.parse.quote(keyword)}&page={page}"
              response = await session.get(url, impersonate="chrome110", timeout=15)
              # BeautifulSoup parse and append...
      return jobs
  ```

#### C. Vagas.com Scraper Refactoring (`scrapers/vagas_com.py`)
- **Engine**: Replace with `curl_cffi.requests.AsyncSession`.
- **Pagination**: Vagas.com paginates via `?pagina={page}`.
- **Code Sketch**:
  ```python
  async def scrape(keyword, level="Todos", max_pages=1):
      jobs = []
      formatted_kw = keyword.replace(' ', '-')
      async with AsyncSession() as session:
          for page in range(1, max_pages + 1):
              url = f"https://www.vagas.com.br/vagas-de-{urllib.parse.quote(formatted_kw)}?pagina={page}"
              response = await session.get(url, impersonate="chrome110", timeout=15)
              # BeautifulSoup parse and append...
      return jobs
  ```

#### D. InfoJobs Scraper Refactoring (`scrapers/infojobs.py`)
- **Engine**: Refactor completely from `playwright.sync_api` to `playwright.async_api`.
- **Architecture**:
  - Load search page via `async_playwright`.
  - Loop through `max_pages`. InfoJobs paginates via `&page={page}` on the search query.
  - Optimize details fetching:
    - Instead of launching separate `new_page()` instances per card (which causes context overhead), reuse a single secondary tab or, preferably, make async `curl_cffi` requests inside a `gather` pool to download description texts.
- **Code Sketch**:
  ```python
  from playwright.async_api import async_playwright
  from curl_cffi.requests import AsyncSession

  async def scrape(keyword, level="Todos", max_pages=1):
      jobs = []
      encoded_kw = urllib.parse.quote(keyword)
      async with async_playwright() as p:
          browser = await p.chromium.launch(headless=True)
          context = await browser.new_context(user_agent="...", locale="pt-BR")
          page = await context.new_page()
          
          for p_num in range(1, max_pages + 1):
              url = f"https://www.infojobs.com.br/vagas-de-emprego.aspx?palavra={encoded_kw}&page={p_num}"
              await page.goto(url, wait_until="domcontentloaded")
              cards = await page.query_selector_all('div.element-vaga')
              
              # Extract card info and async gather descriptions
              # ...
          await browser.close()
      return jobs
  ```

---

## 5. Integration Plan in `bot.py`

Once all scrapers expose an `async def scrape` function, the dynamic invocation routing inside `bot.py`'s `_do_hunt` (lines 1180-1200) can be simplified to:

```python
async def fetch_plat(plat):
    logger.info(f"🚀 Iniciando scraper: {plat.upper()}")
    try:
        # Determine query parameters
        plat_search_keyword = base_keyword
        if actual_level != "Todos" and plat not in ['workana', '99freelas', 'freelancer']:
            plat_search_keyword = f"{base_keyword} {actual_level}"
            
        module = importlib.import_module(f"scrapers.{plat}")
        
        # Max pages can default to 1 for standard runs or 3 for deep searches
        max_pages = 2 if plat in ['infojobs', 'catho', 'gupy'] else 1
        
        for tentativa in range(3):
            try:
                # All scrapers are now async coroutines
                res = await module.scrape(keyword=plat_search_keyword, level="Todos", max_pages=max_pages)
                
                if res:
                    for job in res:
                        job["level"] = actual_level
                plat_status[plat] = f"✅ {len(res)} vagas"
                logger.info(f"✅ Scraper {plat.upper()} finalizado. Vagas encontradas: {len(res)}")
                return res
            except Exception as inner_e:
                logger.warning(f"⚠️ Instabilidade no scraper {plat.upper()} (Tentativa {tentativa+1}/3): {inner_e}")
                plat_status[plat] = f"⚠️ Retry {tentativa+1}/3"
                if tentativa < 2:
                    await asyncio.sleep(2)
        plat_status[plat] = "❌ Falhou"
        return []
    except Exception as e:
        logger.exception(f"❌ Erro fatal ao carregar scraper {plat.upper()}: {e}")
    plat_status[plat] = "❌ Falhou"
    return []
```

This cleans up the blocking synchronous calls (`asyncio.to_thread`) and ensures the scrapers run fully inside the main asynchronous event loop, promoting scalability and resource-efficiency.
