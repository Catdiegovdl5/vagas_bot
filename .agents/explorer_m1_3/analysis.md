# Analysis Report: vagas_bot Codebase Investigation

## Executive Summary
This report analyzes the startup and runtime exceptions within the `vagas_bot` codebase, documents how job keywords and filters are processed, and proposes a high-precision filtering solution crossing exact keyword matching with strict title allowlists and blocklists.

---

## 1. Startup & Runtime Exceptions Identification

The following startup and runtime exceptions have been identified in the codebase:

### A. Telegram Bot Crash on Startup (bot.py)
* **Location**: `bot.py:991` (inside `main()` function)
* **Code snippet**:
  ```python
  async def main():
      print("Bot Nativo Ligado e Aguardando Comandos!")
      await bot.set_chat_menu_button()
      
      while True:
          try:
              await dp.start_polling(bot)
          except Exception as e:
              ...
  ```
* **Description**: `await bot.set_chat_menu_button()` is called outside the `try/except` block. If the Telegram token is invalid, missing, or if the host machine has no internet connection, this call will raise an exception (such as `TelegramAPIError` or connection exceptions), causing the bot to crash and exit immediately on startup before ever entering the polling loop.

### B. Decommissioned Groq LLM Model (llama3-70b-8192)
* **Location**: `scrapers/ai_filter.py` (prior versions) / `erros_robo.log`
* **Evidence (erros_robo.log)**:
  ```log
  2026-07-04 13:21:17 | ERROR | Erro ao extrair JSON: Error code: 400 - {'error': {'message': 'The model `llama3-70b-8192` has been decommissioned and is no longer supported. Please refer to https://console.groq.com/docs/deprecations for a recommendation on which model to use instead.', 'type': 'invalid_request_error', 'code': 'model_decommissioned'}}
  ```
* **Description**: Groq decommissioned the `llama3-70b-8192` model. Any API requests targeting this model return a `400 Bad Request` exception. The current `scrapers/ai_filter.py` has been temporarily simplified to bypass LLM logic, causing several test cases that rely on Groq interactions and structured JSON responses (`test_ia_ranking_handles_groq_malformed_json`, `test_ia_ranking_handles_groq_rate_limits`) to fail.

### C. SSL Certificate Verification Failure
* **Location**: `bot.py` connection to `api.telegram.org` / `erros_robo.log`
* **Evidence (erros_robo.log)**:
  ```log
  ssl.SSLCertVerificationError: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: self-signed certificate in certificate chain (_ssl.c:1081)
  ...
  aiogram.exceptions.TelegramNetworkError: HTTP Client says - ClientConnectorCertificateError: Cannot connect to host api.telegram.org:443 ssl:True
  ```
* **Description**: Occurs during runtime when Python's SSL module cannot verify the SSL certificate of `api.telegram.org`. This usually happens when running behind corporate proxies, firewalls, or local antivirus SSL inspection without proper root certificate installation.

### D. Missing Import Constant causing Test Failure (test_ia_ranking_groq_client_no_api_keys)
* **Location**: `tests/test_tier2.py:230` importing from `scrapers/ai_filter.py`
* **Evidence**:
  ```
  FAILED tests/test_tier2.py::test_ia_ranking_groq_client_no_api_keys - ImportError: cannot import name 'API_KEYS' from 'scrapers.ai_filter'
  ```
* **Description**: The test case tries to import `API_KEYS` from `scrapers.ai_filter`, but this list is not defined in `scrapers/ai_filter.py`, raising an `ImportError`.

### E. Telegram Markdown Syntax Parsing Exceptions
* **Location**: `bot.py:884-885`
* **Code snippet**:
  ```python
  sent_msg = await send_with_retry(lambda: message.answer(text, reply_markup=markup, parse_mode="Markdown"))
  ```
* **Description**: If a job title, company name, or requirements snippet contains unescaped special characters (e.g. single underscores `_` or asterisks `*`), the Telegram API raises a `TelegramBadRequest` exception for malformed Markdown. Although `bot.py` has a `safe_md` sanitizer and a plain-text fallback, parsing failures still occur at runtime when unexpected characters slip through.

### F. SQLite Database Locks & Concurrency OperationalErrors
* **Location**: `database.py` and `auto_apply.py:200` (`run_auto_apply`)
* **Description**: `auto_apply.py` locks rows using `BEGIN IMMEDIATE TRANSACTION` to prevent race conditions during parallel processing. Under high load or when multiple processes access `jobs.db` concurrently, this raises a `sqlite3.OperationalError: database is locked`.

---

## 2. Keyword & Filter Processing Analysis

Currently, job keyword and filter processing is split between local Python logic and the scraped content:

### A. Scraper Search Stage
1. When a user starts a search (e.g. "/hunt Python"), the bot maps the user's selected niche keyword to a search term via `search_mapping` in `bot.py`.
2. It appends the target seniority level to the search term (e.g. `"Python Sênior"`), unless searching on freelance platforms (like Workana), and passes it to the scrapers.

### B. Local Filter Stage (`is_job_relevant` in `bot.py`)
Once raw jobs are fetched, they are filtered locally:
1. **Normalization**: Accents are stripped, and strings are converted to lowercase.
2. **Talent Pool Check**: Excludes "banco de talentos" and "talent pool".
3. **Location Filter**: If "remoto" is selected, the job must explicitly contain remote-related terms and must not contain "fake remote" phrases (e.g. "não é remoto"). If Londrina/Assaí are chosen, the location must match regional city lists.
4. **Contract Filter**: Strict enforcement of "clt" vs. "pj" terms.
5. **Seniority level Filter**: Checks the job title and requirements for terms that mismatch the user's level (e.g. a Junior user rejects jobs containing "Sênior", "Pleno", "Lead", etc.).
6. **Blocklists**:
   - **Global Blocklist**: Removes titles matching irrelevant professions (e.g. professor, legal, medical, manual labor).
   - **Niche-Specific Blocklist**: E.g., for "Especialista em IA Generativa", blocks titles containing developers, MLOps, DevOps, etc.
7. **Keyword Match**:
   - **Current `bot.py`**: Performs a simple literal check (`kw_norm in title_norm`) and falls back to a word-boundary regex match in the description text.
   - **Divergence with `bot.py.mine`**: `bot.py.mine` contains a complex dictionary `rules` that defines **co-occurrence groups** (e.g. checking that an AI job title contains both an AI term like "Midjourney" AND a creative term like "Design").
   - **Why `test_especialista_ia_generativa_keywords` failed**: Because the co-occurrence rules dictionary is missing from the active `bot.py` file. The active `bot.py` relies on a simple exact match of `"especialista em ia generativa"`, causing creative AI titles like `"Copywriter ChatGPT"` to be incorrectly rejected.

---

## 3. High-Precision Filtering Design Recommendation

To achieve high-precision filtering, we must cross **Exact Keyword Matching** with **Strict Title Allowlists and Blocklists**. The design below resolves the gaps in both `bot.py` and `scrapers/ai_filter.py`.

### A. Structural Architecture of the Filter
We propose replacing the simple keyword checks with a structured, three-tiered validation matrix:

```
[Raw Scraped Job]
       │
       ▼
┌─────────────────────────────┐
│ 1. Blocklist Verification   │ ──► [Fail] ──► Reject
└─────────────────────────────┘
       │ (Passes Global & Niche blocklists)
       ▼
┌─────────────────────────────┐
│ 2. Allowlist Verification   │ ──► [Fail] ──► Reject
└─────────────────────────────┘
       │ (Matches required title criteria)
       ▼
┌─────────────────────────────┐
│ 3. Exact Keyword Matching   │ ──► [Fail] ──► Reject
└─────────────────────────────┘
       │ (Confirmed word boundaries in title/description)
       ▼
[Approved Job]
```

### B. Data Structure Schema
A configuration dictionary will govern the filtering rules:

```python
FILTER_RULES = {
    "especialista em ia generativa": {
        "title_allowlist_groups": [
            # Group A (AI/Prompt tools/concepts)
            ["chatgpt", "gpt", "claude", "gemini", "midjourney", "stable diffusion", "ia", "ai", "prompt", "generativa"],
            # Group B (Creative / Marketing / Performance role context)
            ["copywriter", "redator", "designer", "design", "editor", "video", "trafego", "ads", "growth", "performance", "criativo"]
        ],
        "title_blocklist": [
            "mlops", "machine learning engineer", "redes neurais", "data scientist", "engenheiro de dados",
            "rpa", "backend", "desenvolvedor", "dev", "programador", "software engineer", "devops", "helpdesk"
        ],
        "required_description_keywords": ["ia", "ai", "inteligencia artificial", "artificial intelligence", "chatgpt", "generativa", "prompt"]
    },
    "backend python": {
        "title_allowlist_groups": [
            ["python"],
            ["backend", "back-end", "desenvolvedor", "dev", "engineer", "engenheiro", "software", "programador"]
        ],
        "title_blocklist": ["frontend", "front-end", "designer", "copywriter", "professor", "vendas"],
        "required_description_keywords": ["python"]
    }
}
```

### C. Implementation Algorithm (Pseudo-code)

```python
import re
import unicodedata

def normalize(text: str) -> str:
    if not text:
        return ""
    # Strip accents and lowercase
    text = unicodedata.normalize('NFD', text)
    return text.encode('ascii', 'ignore').decode('utf-8').lower()

def is_word_present(pattern_word: str, text: str) -> bool:
    """Matches words with wildcard support, e.g. 'consultor*' matches 'consultoria'"""
    if pattern_word.endswith('*'):
        regex_pattern = rf'\b{re.escape(pattern_word[:-1])}\w*'
    else:
        regex_pattern = rf'\b{re.escape(pattern_word)}\b'
    return bool(re.search(regex_pattern, text))

def evaluate_high_precision(job: dict, search_keyword: str) -> bool:
    title = normalize(job.get('title', ''))
    description = normalize(job.get('requirements', ''))
    full_text = f"{title} {description}"
    
    kw_key = normalize(search_keyword)
    
    # 1. Global Blocklist Check
    for term in GLOBAL_TITLE_BLACKLIST:
        if term not in kw_key and is_word_present(term, title):
            return False
            
    # If no specific rules exist for this keyword, fallback to basic keyword checks
    if kw_key not in FILTER_RULES:
        # Fallback exact word boundary check
        return is_word_present(kw_key, full_text)
        
    rules = FILTER_RULES[kw_key]
    
    # 2. Strict Title Blocklist Check
    for blocked in rules.get("title_blocklist", []):
        if is_word_present(blocked, title):
            return False
            
    # 3. Strict Title Allowlist (Group co-occurrence crossing)
    allowlist_groups = rules.get("title_allowlist_groups", [])
    if allowlist_groups:
        # Every group must have at least one matching word in the title
        matched_groups = []
        for group in allowlist_groups:
            matched = any(is_word_present(word, title) for word in group)
            matched_groups.append(matched)
        if not all(matched_groups):
            return False
            
    # 4. Exact Keyword Matching in Description/Full Text
    req_keywords = rules.get("required_description_keywords", [])
    if req_keywords:
        # Must contain at least one of the required description keywords with proper word boundaries
        if not any(is_word_present(kw, full_text) for kw in req_keywords):
            return False
            
    return True
```

### D. Key Design Advancements
1. **Co-occurrence Groups (AND of ORs)**: Solves the false positive issue by requiring a tool keyword *AND* a functional role keyword to coexist in the title (e.g. `Designer` AND `Midjourney`).
2. **Wildcard Boundaries**: Using `consultor*` pattern matching via regex solves matching inflected Portuguese words (`consultor`, `consultoria`, `consultora`).
3. **Double-layer Protection**: Excludes general blocklist items first, then matches specific positive clusters.
4. **Consistency across entry points**: Ensure this helper function is imported and run by both the Telegram bot (`bot.py`) and the FastAPI dashboard scraping endpoint (`app.py`), resolving the current bug where Dashboard jobs completely bypass local keyword filtering.
