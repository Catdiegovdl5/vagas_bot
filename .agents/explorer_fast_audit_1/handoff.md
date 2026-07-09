# Fast Audit Handoff Report

## 1. Observation
Direct observations of issues in the audited files:

### A. BeautifulSoup Class Lambda Multi-Valued Attribute Errors
In BeautifulSoup 4, the `class` attribute is treated as a multi-valued attribute and parsed as a list of strings (`list`). The following lines in the scrapers attempt to call `.lower()` directly on the class attribute `c`, which raises `AttributeError: 'list' object has no attribute 'lower'`:
*   **`scrapers/catho.py`**:
    *   Line 54: `salary_el = card.find('div', class_=lambda c: c and 'salary' in c.lower())`
    *   Line 57: `desc_el = card.find('span', class_=lambda c: c and 'description' in c.lower())`
    *   Line 59: `desc_el = card.find('div', class_=lambda c: c and 'description' in c.lower())`
*   **`scrapers/vagas_com.py`**:
    *   Line 33: `job_cards = soup.find_all('li', class_=lambda c: c and 'vaga' in c.lower())`
    *   Line 37: `title_el = card.find('h2') or card.find('a', class_=lambda c: c and 'link-detalhes-vaga' in c.lower())`
    *   Line 53: `comp_el = card.find('span', class_=lambda c: c and 'empresa' in c.lower())`
    *   Line 56: `desc_el = card.find('div', class_=lambda c: c and 'detalhes' in c.lower())`
*   **`scrapers/programathor.py`**:
    *   Line 33: `job_cards = soup.find_all('div', class_=lambda c: c and 'cell-list' in c.lower())`
    *   Line 51: `comp_el = card.find('div', class_=lambda c: c and 'logo' in c.lower())`
    *   Line 54: `tags = card.find_all('span', class_=lambda c: c and 'tag' in c.lower())`
*   **`scrapers/coodesh.py`**:
    *   Line 33: `job_cards = soup.find_all('div', class_=lambda c: c and 'job-card' in c.lower())`
    *   Line 39: `title_el = card.find('h3') or card.find('h2') or card.find('div', class_=lambda c: c and 'title' in c.lower())`
    *   Line 54: `comp_el = card.find('div', class_=lambda c: c and 'company' in c.lower())`
*   **`scrapers/geekhunter.py`**:
    *   Line 33: `job_cards = soup.find_all('div', class_=lambda c: c and 'job' in c.lower())`

### B. Missing Fallback Package Dependency in `requirements.txt`
All 6 new scrapers fallback dynamically to the standard `requests` module if `curl_cffi` fails to import:
*   **`scrapers/catho.py`** (line 25-27):
    ```python
    if not requests_cffi:
        import requests
        r = requests.get(url, headers=headers, timeout=15)
    ```
*   Observation of `requirements.txt`: The file does not include either `requests` or `curl_cffi`. If the environment does not have `curl_cffi` installed, it attempts `import requests`, which raises a `ModuleNotFoundError` because it is not installed/listed as a dependency.

### C. Event Loop Blocking Call in `bot.py`
In `bot.py`, the document handler for PDF resumes runs synchronous PDF reading and file writing operations:
*   **`bot.py`** (lines 839-850):
    ```python
    try:
        text = ""
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() or ""
                text += "\n"
                
        curriculo_txt_path = f"curriculo_{user_id}.txt"
        with open(curriculo_txt_path, "w", encoding="utf-8") as f:
            f.write(text)
    ```
This runs directly on the main event loop inside `async def handle_document`.

### D. Uncaught Exception Risk in Async Gather inside `bot.py`
In `bot.py`, proposal generation tasks for freelance jobs are gathered concurrently:
*   **`bot.py`** (line 696):
    ```python
    premium_jobs = await asyncio.gather(*(generate_proposal_only(j) for j in premium_jobs))
    ```
*   `generate_proposal_only` (lines 677-694) has no try-except block wrapping the Groq API call, and `asyncio.gather` does not use `return_exceptions=True`.

---

## 2. Logic Chain
1. **BS4 Class Attribute List-Type**: BeautifulSoup 4 represents multi-valued HTML attributes (such as `class`) as a python `list` of strings. Because `catho.py`, `vagas_com.py`, `programathor.py`, `coodesh.py`, and `geekhunter.py` pass a lambda function to `class_` which calls `c.lower()` directly, Python raises an `AttributeError` whenever evaluating tags that have a class attribute (Observation A).
2. **Scraper Failure / Empty Results**: 
   * In `geekhunter.py`, `vagas_com.py`, `programathor.py`, and `coodesh.py`, this error is raised outside the parser loops on the main `soup.find_all(...)` call. This error propagates to the main try-except block, causing the scraper to abort immediately and return 0 results.
   * In `catho.py`, the error occurs inside the card parser loop. Since almost all job cards have multiple classes, this error is raised for every single card, causing the loop to skip them all via `continue` and return 0 parsed jobs.
3. **ModuleNotFoundError**: Since neither `requests` nor `curl_cffi` is defined in `requirements.txt` (Observation B), a python environment generated from this file will raise `ModuleNotFoundError: No module named 'requests'` when `curl_cffi` is missing and fallback is triggered. Although caught by the scraper-level try-except block, this prevents the scraper from executing and results in 0 jobs found.
4. **Event Loop Starvation**: In `bot.py`, the PDF reader and file write actions run synchronously within the main thread's async event loop (Observation C). Reading and parsing a PDF is CPU-heavy and disk-I/O bound, which will halt/block the single thread's async event loop. During this execution, any other users interacting with the bot will experience timeouts or delayed messages.
5. **Hunt Failure from Groq Exception**: If any Groq request throws an error (e.g. Rate Limit, API key issue, or decommissioning) during the asynchronous gather (Observation D), the exception will propagate up and abort `asyncio.gather`, causing the entire `_do_hunt` routine to crash and prevent the user from receiving any job listings.

---

## 3. Caveats
* The audit was read-only and did not involve running code because terminal permission execution timed out.
* The Groq model `"llama-3.3-70b-versatile"` is currently specified in `scrapers/ai_filter.py` which appears to be a valid model, although earlier logs showed decommissioned model errors (`llama3-70b-8192`) indicating some legacy/test files or configurations might have used it.

---

## 4. Conclusion
The new scrapers contain a severe systematic parsing bug with BeautifulSoup `class_` lambdas that raises `AttributeError` on list attributes, resulting in 0 jobs scraped for Catho, Vagas.com, Programathor, Coodesh, and GeekHunter. Additionally, dependency issues in `requirements.txt` block the request fallbacks, synchronous CPU/IO operations block the bot's event loop during PDF resume uploads, and Groq API call failures inside the parallel gather block can abort the entire search workflow.

### Proposed Fixes:
1.  **BeautifulSoup Class Lambda Fix**:
    Replace lambdas checking `c.lower()` with case-insensitive regular expressions or functions that handle lists:
    *   *Before*:
        `job_cards = soup.find_all('div', class_=lambda c: c and 'job' in c.lower())`
    *   *After*:
        ```python
        import re
        job_cards = soup.find_all('div', class_=re.compile('job', re.I))
        ```
        Or checking list values:
        ```python
        job_cards = soup.find_all('div', class_=lambda c: c and any('job' in cls.lower() for cls in (c if isinstance(c, list) else [c])))
        ```
2.  **Dependency Fix**:
    Add `requests` and `curl_cffi` (if applicable) to `requirements.txt`.
3.  **Event Loop Blocking Fix**:
    Offload PDF reading and text saving to `asyncio.to_thread` in `bot.py`:
    ```python
    def parse_pdf(path):
        text = ""
        with open(path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() or ""
                text += "\n"
        return text

    text = await asyncio.to_thread(parse_pdf, file_path)
    ```
4.  **Async Gather Exception Handling**:
    Enable exception return or add a try-except block inside `generate_proposal_only`:
    ```python
    # Option A: In bot.py, capture exceptions in gather
    premium_jobs = await asyncio.gather(*(generate_proposal_only(j) for j in premium_jobs), return_exceptions=True)
    premium_jobs = [j for j in premium_jobs if isinstance(j, dict)]
    ```

---

## 5. Verification Method
1.  **BS4 Lambda Reproducer**:
    Run a python shell and execute:
    ```python
    from bs4 import BeautifulSoup
    soup = BeautifulSoup('<div class="job card">Test</div>', 'html.parser')
    # This raises AttributeError:
    soup.find_all('div', class_=lambda c: c and 'job' in c.lower())
    ```
2.  **Verify PDF Parsing event blocking**:
    Upload a large multi-page PDF to the bot and monitor if it freezes other concurrent tasks.
3.  **Run E2E Tests**:
    After applying fixes, run `python run_tests.py` to verify the entire system passes.
