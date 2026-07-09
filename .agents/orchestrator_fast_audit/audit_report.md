# Fast Audit Report

## High-Severity Issues Identified

### 1. BeautifulSoup Class Lambda AttributeError (High Severity)
- **Description**: In BeautifulSoup 4, the `class` attribute is parsed as a list of strings. Calling `.lower()` directly on `c` in a lambda function raises `AttributeError: 'list' object has no attribute 'lower'`. This causes the scrapers to abort or fail to extract job details, returning 0 jobs.
- **Locations**:
  - `scrapers/catho.py` (lines 54, 57, 59)
  - `scrapers/vagas_com.py` (lines 33, 37, 53, 56)
  - `scrapers/programathor.py` (lines 33, 51, 54)
  - `scrapers/coodesh.py` (lines 33, 39, 54)
  - `scrapers/geekhunter.py` (line 33)

### 2. Missing Core Dependency in requirements.txt (High Severity)
- **Description**: The 6 new scrapers fallback to `import requests` if `curl_cffi` fails to load. However, `requests` is not present in `requirements.txt`. If `curl_cffi` is missing, the fallback raises `ModuleNotFoundError: No module named 'requests'`, halting scraping execution.

### 3. Event Loop Blocking PDF Parsing in bot.py (High Severity)
- **Description**: CPU/IO intensive operations (synchronous PDF extraction using `PyPDF2.PdfReader` and writing to disk) are executed directly inside the main thread's async event loop. This blocks the loop and causes Telegram dashboard unresponsive lag/timeouts for all concurrent users.
- **Location**: `bot.py` (lines 839-850)

### 4. Uncaught Exceptions in asyncio.gather in bot.py (High Severity)
- **Description**: In `bot.py`, `asyncio.gather` executes proposal generation tasks concurrently without `return_exceptions=True` and without exception handling inside `generate_proposal_only()`. A single Groq API exception (rate-limit, timeout, credential error) will propagate and crash the entire hunting loop.
- **Location**: `bot.py` (line 696)
