# Plan: Refactoring CLT Scrapers to Native Async

## Objective
Refactor Gupy, Catho, Vagas.com.br, and InfoJobs scrapers to match the `async def scrape(keyword, level="Todos", max_pages=1)` signature and use async clients (Playwright async_api or curl_cffi AsyncSession).

## Tasks
1. Refactor `scrapers/gupy.py` to:
   - Use `curl_cffi.requests.AsyncSession` (or `aiohttp` / standard `requests` wrapped if needed, but `curl_cffi` async is preferred).
   - Use `async def scrape(keyword, level="Todos", max_pages=1)`.
   - Support pagination by looping `page` from 1 to `max_pages`, computing `offset = (page - 1) * 30` and calling the Gupy employability JSON API.
2. Refactor `scrapers/catho.py` to:
   - Use `curl_cffi.requests.AsyncSession`.
   - Use `async def scrape(keyword, level="Todos", max_pages=1)`.
   - Support pagination by adding `&page={page}` to the URL query.
3. Refactor `scrapers/vagas_com.py` to:
   - Use `curl_cffi.requests.AsyncSession`.
   - Use `async def scrape(keyword, level="Todos", max_pages=1)`.
   - Support pagination by adding `?pagina={page}` to the URL query.
4. Refactor `scrapers/infojobs.py` to:
   - Use `playwright.async_api`.
   - Use `async def scrape(keyword, level="Todos", max_pages=1)`.
   - Paginate through the search pages using `&page={page}`.
   - Fetch detail description text for each job card using `curl_cffi.requests.AsyncSession` or a fallback `new_page()` (async).
5. Ensure each scraper returns a list of dictionaries matching the standard layout:
   ```python
   {
       "platform": str,      # "Gupy", "Catho", "Vagas.com", "Infojobs"
       "title": str,
       "company": str,
       "budget": str,        # "A Combinar" or salary
       "link": str,
       "job_type": "CLT",
       "profession": keyword,
       "level": level,
       "requirements": str   # Full description text
   }
   ```
6. Verify syntax of the modified python files using `py_compile` or similar.
