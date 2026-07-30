# Playwright Environment Analysis Findings

This report outlines the status of the Playwright installation, browsers availability, existing scraper test strategies, and steps for verification in headless mode on Windows.

---

## 1. Playwright Python Package Installation Status
- **Requirements Check**: The `requirements.txt` file does **not** contain the `playwright` or `playwright-stealth` packages.
- **Start Scripts Check**: The system start-up script `start_bot.bat` runs `pip install -q openai python-dotenv aiogram aiohttp httpx` but does not install `playwright`.
- **Implementation Imports**: Two S-Tier scrapers (`scrapers/glassdoor.py` and `scrapers/indeed.py`) import `playwright.sync_api.sync_playwright` and attempt to import `playwright_stealth`. If `playwright` is not installed globally or in the active virtual environment, these scrapers will throw an `ImportError` when run without mocks.

---

## 2. Playwright Browsers Availability Status
A directory check was performed on the default user profile location for Playwright browsers on Windows: `C:\Users\99196\AppData\Local\ms-playwright`.
- **Status**: **Installed and Available**.
- **Found Directories**:
  - `chromium-1208`
  - `chromium-1223`
  - `chromium_headless_shell-1208`
  - `chromium_headless_shell-1223`
  - `firefox-1509`
  - `webkit-2248`
  - `.links`, `ffmpeg-1011`, `winldd-1007`
  
*Note: Although the browser binaries are cached in the user profile, the Python bindings (`playwright` library) must still be installed in the environment to utilize them.*

---

## 3. Existing Test Suites & Scraper Verification
The workspace features three distinct test suites/scripts:

### A. Mock-Based Scraper Test (`test_scrapers.py`)
- **How it works**: Intercepts imports by registering `PlaywrightSyncApiMock` and `MockCurlCffi` in `sys.modules`.
- **Verification Method**: Simulates page loads and element query selectors using mock classes. Ensures the scraper logic parses cards correctly (e.g. Glassdoor mock HTML elements) and maps fields (`title`, `company`, `budget`, `link`, `requirements`) according to contract schemas.
- **Coverage**: Runs offline with zero network/browser dependencies.

### B. Search Engine Co-occurrence Test (`test_motor.py`)
- **How it works**: Uses a hardcoded catalog of 16 test cases containing simulated job titles/requirements and expected match results (True/False).
- **Verification Method**: Simulates the `check_co_occurrence` parser to filter true positives (e.g. "Dev Python Backend") and block false positives (e.g. "Enfermeira com python", "Motorista de Aplicativo Python"). Does not use scrapers or browsers.

### C. Live Scraper Verification Script (`scrapers/run_test.py`)
- **How it works**: Import and run real scraper modules directly (`linkedin`, `glassdoor`, `infojobs`, `indeed`, `jooble`).
- **Verification Method**: Executes `scrape` function using the real network and browsers. Validates schema compliance (essential keys present) and platforms-specific requirements (e.g. LinkedIn description length >= 500 chars).
- **Execution**: Can be run using `python scrapers/run_test.py`. Requires actual playwright installation.

### D. Pytest E2E Suite (`tests/` via `run_tests.py`)
- **How it works**: Implements systematic coverage (Tiers 1 to 4) over 49 tests.
- **Verification Method**: Fully mocks all network libraries (`requests`, `curl_cffi`, `playwright.sync_api`, `playwright.async_api`, `AsyncGroq`) in `tests/conftest.py` to achieve zero flakiness.

---

## 4. Headless Mode Installation & Verification Steps on Windows

To install and verify Playwright in headless mode on the user's Windows environment:

### Step 1: Install Python Packages
Execute in Powershell/CMD to install the required libraries:
```cmd
pip install playwright playwright-stealth
```

### Step 2: Install Playwright Chromium Browser
Install the Chromium browser version mapped to the installed python package version:
```cmd
playwright install chromium
```

### Step 3: Run Headless Verification Code
Run a dry run script to ensure headless mode is fully working:
```python
from playwright.sync_api import sync_playwright

def verify_headless():
    print("[+] Launching headless Chromium...")
    with sync_playwright() as p:
        # Launching with headless=True (default in scraper files)
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        # Navigate to a simple domain to test DNS and navigation
        page.goto("https://example.com")
        title = page.title()
        print(f"[+] Page loaded successfully. Title: {title}")
        
        assert "Example Domain" in title, "Failed to load page content correctly"
        browser.close()
    print("[+] Headless Playwright verified successfully!")

if __name__ == "__main__":
    verify_headless()
```
