# Handoff Report: CLT Scrapers Evaluation and Integration

## 1. Observation
- **Dynamic Scraper Executer**: In `bot.py` (lines 1178-1188), the bot dynamically imports and routes execution based on whether a scraper is a coroutine function (`async def`) or a standard synchronous function (`def`). Synchronous functions (all except `workana.py`) are deferred to `asyncio.to_thread`.
- **Existing CLT Scrapers**:
  - `scrapers/gupy.py` (lines 10-81): Uses `curl_cffi` requests (Chrome 110 impersonation) falling back to `requests` to fetch Gupy's public JSON API. It runs synchronously.
  - `scrapers/catho.py` (lines 9-78): Uses `curl_cffi`/`requests` to download job pages and `BeautifulSoup` to parse HTML. It runs synchronously.
  - `scrapers/vagas_com.py` (lines 9-75): Uses `curl_cffi`/`requests` and `BeautifulSoup` to parse HTML listings. It runs synchronously.
  - `scrapers/infojobs.py` (lines 17-162): Uses `playwright.sync_api` to bypass Cloudflare and search jobs, and then uses a hybrid method (`curl_cffi` requests or fallback Playwright detail page queries) to grab descriptions. It runs synchronously.
- **Reference Async Scraper**:
  - `scrapers/workana.py` (lines 12-151): Uses `playwright.async_api` natively under `async def scrape(keyword, level="Todos", max_pages=100)`. It handles multi-page crawls cleanly with `asyncio.sleep` delays.
- **Eligibility Checks**:
  - `bot.py` (lines 915-991) defines `is_job_relevant` which enforces strict exclusions based on:
    - Keywords (excluding talent pools).
    - User location settings (local match lists or remote-only rules).
    - Contract type boundaries (CLT vs. PJ).
    - Seniority keyword matching (Junior, Pleno, Sênior).
    - Global title and niche-specific blacklists.
    - Word groupings under `CO_OCCURRENCE_RULES` checked via `check_co_occurrence`.

---

## 2. Logic Chain
- **Observation 1**: `bot.py` has to run synchronous scrapers inside `asyncio.to_thread` executor threads to prevent blocking the main asyncio event loop.
- **Observation 2**: `scrapers/infojobs.py` runs synchronous Playwright (`playwright.sync_api`) inside `asyncio.to_thread`.
- **Inference 1**: Running synchronous Playwright inside executor threads is resource-intensive, risks thread-lock issues, and is a potential source of crash logs or high memory usage in production.
- **Observation 3**: `scrapers/workana.py` successfully uses async Playwright (`playwright.async_api`) in an `async def scrape` signature without blocking or thread execution overhead.
- **Inference 2**: Refactoring InfoJobs to use `playwright.async_api` and the other scrapers (`gupy`, `catho`, `vagas_com`) to use async HTTP requests (`curl_cffi.requests.AsyncSession`) will allow us to run all scrapers natively inside the main event loop via `asyncio.gather`, improving execution speed and resource efficiency.
- **Conclusion**: We should unify the signatures of the CLT scrapers to `async def scrape(keyword, level="Todos", max_pages=...)` and simplify `bot.py`'s dynamic invocation logic by removing the `asyncio.to_thread` executor branch for active scrapers.

---

## 3. Caveats
- **Platform Selectors Stability**: HTML selectors for Catho, Vagas.com, and InfoJobs are prone to breaking if platforms update their layouts. This investigation assumes the current selectors are operational.
- **IP Blocking and Rate Limits**: Increasing pagination (`max_pages > 1`) on Catho and InfoJobs increases the frequency of requests, raising the risk of IP blocks, which might necessitate the use of residential proxies or rotating user-agents.
- **Mocking Scrapers in Tests**: Test files (e.g., `test_scrapers.py`) mock `requests`, `curl_cffi`, and Playwright. After refactoring scrapers to native async, these tests and mock frameworks will require updates to handle async calls.

---

## 4. Conclusion
Integrating CLT platforms as native async scrapers is highly viable.
- **Gupy** remains the most viable platform to scrape due to its fast and clean public JSON API.
- **Catho** and **Vagas.com** are highly viable using `curl_cffi.requests.AsyncSession` for parsing HTML.
- **InfoJobs** is moderately viable but must be refactored to `playwright.async_api` to ensure event loop stability.
- **Actionable Next Steps**:
  1. Refactor `scrapers/gupy.py`, `scrapers/catho.py`, and `scrapers/vagas_com.py` to `async def` using `curl_cffi.requests.AsyncSession`.
  2. Refactor `scrapers/infojobs.py` to `async def` using `playwright.async_api` and optimize card detail gathering.
  3. Modify the scraper dispatch logic in `bot.py` (`_do_hunt` -> `fetch_plat`) to remove the synchronous `asyncio.to_thread` logic.
  4. Update `test_scrapers.py` mock framework to support async execution of the newly refactored scrapers.

---

## 5. Verification Method
- **Test Command**: Run `python test_scrapers.py` to verify standard scraper contract output formats under the mocked environment.
- **Production Dry-run**: Run the scraper tests in the actual live environment to confirm that `curl_cffi` and `playwright.async_api` bypass anti-bot screens.
- **Invalidation Condition**: If `test_scrapers.py` crashes due to async/coroutine execution errors (e.g. `TypeError: coroutine object is not subscriptable` or `RuntimeError: Timeout waiting for selector`), the verification fails.
