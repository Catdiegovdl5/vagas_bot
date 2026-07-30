## 2026-07-17T14:51:20Z

You are teamwork_preview_worker.
Your working directory is: C:/Users/99196/OneDrive/Documentos/vagas_bot/.agents/worker_workana_playwright
Your mission is to refactor the Workana scraper in the Vagas Sniper Bot to use Playwright (headless Chromium) instead of requests/curl_cffi, resolve the integration gaps and await it properly in bot.py, and update the unit tests to pass.

Please perform the following steps:
1. Package installation:
   Add 'playwright' and 'playwright-stealth' to C:/Users/99196/OneDrive/Documentos/vagas_bot/requirements.txt.
   Run the package installation using `pip install playwright playwright-stealth` in the virtual environment. Also run `playwright install chromium` if necessary.

2. Refactor scrapers/workana.py:
   - Change 'scrape' to be an asynchronous function: `async def scrape(keyword="Python", level="Todos", max_pages=10)`.
   - Use `playwright.async_api.async_playwright` to launch headless Chromium.
   - Use `playwright-stealth`'s `stealth_async(page)` if available to bypass Cloudflare challenges.
   - For each page from 1 to max_pages, navigate to `https://www.workana.com/jobs?query={search_kw}&page={page}` with a timeout of 30 seconds and `wait_until="domcontentloaded"`.
   - Wait for job card elements to load. The selectors to check and wait for: '.job-item' as primary, but also support '.project-item' or '.project-card' as fallbacks. If no items are found after waiting, handle the timeout exception gracefully and break or return.
   - Add an asynchronous delay using `await asyncio.sleep(random.uniform(2.0, 4.5))` or `await page.wait_for_timeout(...)` between page loads.
   - Extract title, budget, link, and description/requirements from the DOM card elements into the existing dictionary schema:
     * title: card.query_selector('.project-title a') or similar
     * link: get_attribute('href') from the title anchor (joined to https://www.workana.com if relative)
     * description/requirements: card.query_selector('.project-details') or '.project-description' or the card's text
     * budget: card.query_selector('.budget') or '.project-budget'
     * platform: "Workana"
     * company: "Cliente Workana"
     * job_type: "PJ"
     * profession: keyword
     * level: level
   - Fix the search scope expansion: normalise the keyword (remove accents, lowercase). Define `MAPPED_KEYS` to map mapped terms to the original `CO_OCCURRENCE_RULES` keys in bot.py (e.g. "especialista ia" -> "especialista em ia", "engenheiro ia" -> "engenheiro de ia", "ai developer" -> "desenvolvedor de agentes ia", etc.). Check if the mapped key is in `bot.CO_OCCURRENCE_RULES`, and if so, join the top two Group A terms to form the search query.

3. Update bot.py:
   - In bot.py (around lines 2200-2210), import `inspect`.
   - Check if `module.scrape` is a coroutine function: `if inspect.iscoroutinefunction(module.scrape):`
   - If it is, await it directly: `res = await module.scrape(keyword=plat_search_keyword, level="Todos")`.
   - Otherwise, keep the fallback `asyncio.to_thread` calls for the synchronous scrapers.

4. Update tests/test_workana_settings.py:
   - Refactor `test_workana_scraper_pagination_delays_and_termination` to be an `async def` and use `@pytest.mark.asyncio`.
   - Await the `workana.scrape` call.
   - Mock the Playwright async methods (`async_playwright` context manager, browser, browser context, page, cards) using unittest.mock to simulate the pagination, return the expected mock data, and test the 429 status code or early exit behavior, matching the test's assertions.

5. Verify:
   - Run the pytest suite: `pytest tests/test_workana_settings.py` and verify all tests pass.
   - Write your handoff report to C:/Users/99196/OneDrive/Documentos/vagas_bot/.agents/worker_workana_playwright/handoff.md.

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A Forensic Auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.
