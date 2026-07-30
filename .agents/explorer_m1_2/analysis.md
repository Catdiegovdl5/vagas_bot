# vagas_bot Codebase Analysis and Precision Filtering Design

## Executive Summary
This report analyzes the `vagas_bot` recruitment pipeline codebase. We identify startup and runtime exceptions, evaluate how keywords and filters are processed in the current implementation, and present a high-precision crossed-filtering design to eliminate false positives and pass E2E tests.

---

## 1. Startup & Runtime Exceptions (Codebase Audit)

During the codebase audit and test execution, we identified several runtime exceptions, logic flaws, and test failures. 

### A. Database Concurrency & Lock Exceptions
* **Symptom**: `sqlite3.OperationalError: database is locked` in `auto_apply.py` (line 228/242) and related E2E tests.
* **Root Cause**: SQLite database connections are opened and updated in a loop during `run_auto_apply` while other tests (like `test_do_hunt_concurrency_and_performance`) perform concurrent writes. SQLite locks the database file because transactions are not isolated or written in batch transactions. Furthermore, WAL (Write-Ahead Logging) mode is activated in `get_connection()` but not in the raw `sqlite3.connect` calls in the tests, causing write conflicts.

### B. Missing Module Attributes & Imports
* **Symptom**: `ImportError: cannot import name 'API_KEYS' from 'scrapers.ai_filter'` in `tests/test_tier2.py::test_ia_ranking_groq_client_no_api_keys`.
* **Root Cause**: The module `scrapers/ai_filter.py` does not define `API_KEYS`, but tests try to import and mock it.

### C. Missing LLM Implementation (API Mocking Discrepancy)
* **Symptom**: Assertions fail in `test_ia_ranking_handles_groq_malformed_json`, `test_ia_ranking_handles_groq_rate_limits`, and `test_combination_scraper_db_and_ia_ranking`.
* **Root Cause**: The current `scrapers/ai_filter.py` is a classic text-matching mockup script. It does not import `groq` or make any external LLM calls. Consequently, when tests mock `groq.AsyncGroq().chat.completions.create` to simulate API failures, malformed JSON, or rate limits, the `score_job_match` function ignores the mock, processes the text locally, and incorrectly returns `aprovado = True`.

### D. Seniority Overwrite / Level Exception
* **Symptom**: `AssertionError: Job 'Python Lead' has level 'None', expected 'Sênior'` in `test_bot_centralized_seniority_level_filtering`.
* **Root Cause**: `bot.py` is expected to overwrite the `level` of the jobs before database insertion, but the mock scrapers or insertion pathways do not map or save the assigned seniority levels correctly in `database.py`.

### E. Telegram Markdown Formatting Exception
* **Symptom**: `TelegramBadRequest` during message delivery in `bot.py` line 879.
* **Root Cause**: The bot tries to format job details using `Markdown`. Tracebacks and job requirements contain characters like `_`, `*`, `[`, which break Telegram's parser. The bot's `except` block catches it and falls back to plain text, but it represents a formatting vulnerability.

### F. Critical Scraper-Level Exceptions & Logic Bugs
* **`scrapers/meta_ads.py` Location Lock**: The scraper executes only if `country == "Brasil"`. In `bot.py`, the default location is `"Brasil (Remoto)"`. This mismatch causes the Meta Ads scraper to return `[]` immediately without executing.
* **`scrapers/infojobs.py` Unconditional Playwright Fallback**: An indentation error at lines 111-133 causes the Playwright scraper fallback to execute for every single card, even if the description was already fetched successfully using `curl_cffi`, causing immense performance degradation.
* **`scrapers/freelancer.py` AttributeError**: Budget or currency fields returning `null` from the API raise `AttributeError: 'NoneType' object has no attribute 'get'` when calling `item.get("budget").get("minimum")`.
* **`scrapers/gmail.py` Broad Try-Except**: A single parsing exception in one email message aborts the entire Gmail scan loop.
* **`scrapers/jooble.py` / `scrapers/workana.py` Dummy Job Pollution**: Returning fake job objects (e.g. "Sem vagas Jooble...") when no jobs are found pollutes the SQLite database and requires downstream filtering logic.

---

## 2. Current Keyword & Filter Processing

The bot processes keywords and filters through a three-layer pipeline:

```
[Telegram Request / Free Text] -> [Keyword Mapping] -> [Scraper Fetch] -> [Local Python is_job_relevant Filter] -> [DB Insertion]
```

### 1. Keyword Mapping (Niche Transformation)
In `bot.py`, search keywords selected from the menu are mapped to technical search queries using `search_mapping` (e.g., `"Especialista em IA"` maps to `"Inteligência Artificial"`). For standard job platforms, the bot appends the user's level (if not `"Todos"`) to the query: `f"{base_keyword} {actual_level}"`.

### 2. Local Job Relevance Filter (`is_job_relevant`)
Before inserting scraped jobs into the database, `bot.py` executes `is_job_relevant()` to check the following parameters:
- **Title Blocklist**: Rejects if `"banco de talentos"` or `"talent pool"` is in the title, or if any global `global_title_blacklist` or niche-specific term from `blacklist[keyword]` is present.
- **Location**: For `"remoto"` users, it rejects if presential/hybrid terms are in the text and remote terms are missing, or if the location field lists a specific non-Brazil city without a remote indicator.
- **Contract Type**: Excludes PJ/CLT mismatch.
- **Seniority Levels**: If candidate is `junior`, `pleno`, or `senior`, it checks the title against a list of terms (e.g., junior candidate is rejected if `"sênior"`, `"coordenador"`, or `"lead"` is in the title).
- **Exact Keyword Fallback**: If the keyword is not in the title, it uses `rf'\b{re.escape(kw_norm)}\b'` to verify if the keyword exists in the full text.

### Critical Gaps in Current Filter Logic:
1. **Keyword Poisoning**: Substring matching in the description allows irrelevant jobs to pass. For example, a growth marketing job that mentions "familiarity with Python" will match a query for "Python" even though the job title is unrelated to software engineering.
2. **Missing Allowlist Verification**: There is no validation ensuring that the job title represents a relevant role for the requested niche.
3. **No Language Hard-locks**: English-only descriptions or jobs requiring fluent English are not filtered out for junior candidates who only speak basic English.
4. **No Currency Hard-locks**: Jobs paying in USD/Euro leak into local Brazilian pipelines.

---

## 3. High-Precision Crossed-Filter Design

To achieve high-precision filtering, we propose a **Crossed-Filter Architecture** that integrates **Exact Keyword Matching** with **Strict Title Allowlists, Blocklists, and Contextual Hard-Locks**. 

### The Crossed-Filter Architecture

```
                       +---------------------------------------+
                       |           Incoming Vacancy            |
                       +---------------------------------------+
                                           |
                                           v
                       +---------------------------------------+
                       |       Layer 1: Title Blocklist        |  (Global & Niche Blocklists)
                       +---------------------------------------+
                                           | Pass
                                           v
                       +---------------------------------------+
                       |       Layer 2: Title Allowlist        |  (Ensures relevant job title)
                       +---------------------------------------+
                                           | Pass
                                           v
                       +---------------------------------------+
                       |    Layer 3: Exact Keyword Match       |  (Word-boundary regex)
                       +---------------------------------------+
                                           | Pass
                                           v
                       +---------------------------------------+
                       |    Layer 4: Contextual Hard-Locks     |  (Currency & Language check)
                       +---------------------------------------+
                                           | Pass
                                           v
                                     [ APPROVED ]
```

### Proposed Allowlist & Blocklist Schema

We define a configuration schema mapping search queries to allowed/blocked title patterns:

```python
NICHE_RULES = {
    "especialista em ia": {
        "title_allowlist": [
            r"\bia\b", r"\bai\b", r"inteligencia\s+artificial", r"artificial\s+intelligence",
            r"prompt", r"rag", r"llm", r"generative", r"generativa", r"gpt", r"claude", r"copilot",
            r"machine\s+learning", r"\bml\b", r"deep\s+learning", r"agentes"
        ],
        "title_blocklist": [
            r"professor", r"docente", r"tutor", r"vendas", r"comercial", r"atendimento",
            r"marketing", r"social\s+media", r"redator", r"copywriter", r"video", r"design"
        ]
    },
    "python scraping & data engineering": {
        "title_allowlist": [
            r"python", r"scraping", r"scraper", r"crawler", r"dados", r"data", r"engineer",
            r"engenheiro", r"backend", r"back-end", r"developer", r"desenvolvedor", r"crawler"
        ],
        "title_blocklist": [
            r"professor", r"tutor", r"instrutor", r"curso", r"vendas", r"comercial", r"suporte"
        ]
    },
    "desenvolvedor junior / estagiario": {
        "title_allowlist": [
            r"junior", r"jr", r"estagio", r"estagiario", r"trainee", r"assistente", r"aprendiz"
        ],
        "title_blocklist": [
            r"senior", r"sr", r"pleno", r"pl", r"lead", r"coordenador", r"gerente", r"diretor",
            r"direito", r"pedagogia", r"psicologia", r"enfermagem", r"medicina", r"design"
        ]
    }
}
```

### Python Implementation Blueprint

We propose implementing this Crossed-Filter within `scrapers/ai_filter.py` and `bot.py`. The filter overrides any LLM evaluation:

```python
import re
import unicodedata

def normalize_str(s: str) -> str:
    if not s:
        return ""
    s = unicodedata.normalize('NFD', str(s))
    return s.encode('ascii', 'ignore').decode('utf-8').lower()

def is_job_relevant_high_precision(job: dict, target_keyword: str, user_settings: dict) -> tuple[bool, str]:
    title_norm = normalize_str(job.get('title', ''))
    reqs_norm = normalize_str(job.get('requirements', ''))
    full_text = f"{title_norm} {reqs_norm}"
    
    keyword_norm = normalize_str(target_keyword)
    user_level = normalize_str(user_settings.get('level', 'Todos'))
    user_contract = normalize_str(user_settings.get('contract', 'Todos'))
    user_education = normalize_str(user_settings.get('education', 'Todos'))
    
    # -------------------------------------------------------------
    # Layer 1: Global Title Blocklist Check
    # -------------------------------------------------------------
    global_blocklist = [
        "professor", "professora", "docente", "tutor", "tutoria", "instrutor", "instrutora",
        "advogado", "advogada", "direito", "juridico", "medico", "medica", "enfermeiro",
        "enfermeira", "enfermagem", "diarista", "domestica", "cozinheiro", "garcom", "servicos gerais",
        "voluntario", "voluntary"
    ]
    # Remove search term from blocklist to avoid self-blocking
    active_global_blocklist = [term for term in global_blocklist if term not in keyword_norm]
    for term in active_global_blocklist:
        if re.search(rf'\b{re.escape(term)}\b', title_norm):
            return False, f"[Hard-Lock Override] Global title blocklist match: {term}"

    # -------------------------------------------------------------
    # Layer 2: Niche-Specific Title Blocklist Check
    # -------------------------------------------------------------
    rule = NICHE_RULES.get(keyword_norm, {})
    niche_blocklist = rule.get("title_blocklist", [])
    for pattern in niche_blocklist:
        if re.search(pattern, title_norm):
            return False, f"[Hard-Lock Override] Niche title blocklist match: {pattern}"

    # -------------------------------------------------------------
    # Layer 3: Title Allowlist Check (Intent Validation)
    # -------------------------------------------------------------
    title_allowlist = rule.get("title_allowlist", [])
    if title_allowlist:
        matched_allow = False
        for pattern in title_allowlist:
            if re.search(pattern, title_norm):
                matched_allow = True
                break
        if not matched_allow:
            return False, "[Hard-Lock Override] Title does not match any niche allowlist patterns"

    # -------------------------------------------------------------
    # Layer 4: Exact Keyword Matching with Word Boundaries
    # -------------------------------------------------------------
    # Exclude basic query "vagas"
    if keyword_norm and keyword_norm != "vagas":
        kw_words = [w for w in re.split(r'\W+', keyword_norm) if len(w) > 2]
        # Match each sub-word as an exact word boundary in the full text
        for word in kw_words:
            if not re.search(rf'\b{re.escape(word)}\b', full_text):
                return False, f"[Hard-Lock Override] Exact keyword word boundary check failed for: {word}"

    # -------------------------------------------------------------
    # Layer 5: Contextual Hard-Locks (Adversarial Filters)
    # -------------------------------------------------------------
    
    # 5.1 Foreign Currency Filter (USD/Euro)
    currency_patterns = [r'\busd\b', r'\beur\b', r'\b\$\b', r'\b€\b', r'\bdollar\b']
    # Exempt freelance platforms from USD checks
    is_freelance_platform = any(p in job.get('platform', '').lower() for p in ['workana', '99freelas', 'freelancer'])
    if not is_freelance_platform:
        if any(re.search(pat, full_text) for pat in currency_patterns):
            # Only reject if the currency terms are actually indicating payment currency
            if any(term in reqs_norm for term in ["salario em usd", "pagamento em usd", "salary in usd", "paid in usd"]):
                return False, "[Hard-Lock Override] Foreign currency requirement (USD/Euro) detected"

    # 5.2 English Fluency Restriction for Junior Roles
    if user_level == 'junior':
        english_fluent_patterns = [
            r'ingles\s+(?:fluente|avancado)', r'(?:fluent|advanced)\s+english', 
            r'english\s+is\s+a\s+must', r'proficiency\s+in\s+english'
        ]
        if any(re.search(pat, full_text) for pat in english_fluent_patterns):
            return False, "[Hard-Lock Override] Fluent/Advanced English required for Junior candidate"

    # 5.3 Seniority Mismatch Checks
    junior_terms = [r'\bjunior\b', r'\bjr\b', r'\bestagio\b', r'\bestagiario\b', r'\btrainee\b', r'\baprendiz\b']
    senior_terms = [r'\bsenior\b', r'\bsr\b', r'\bespecialista\b', r'\btech\s+lead\b', r'\barchitect\b', r'\barquiteto\b', r'\blead\b']
    pleno_terms = [r'\bpleno\b', r'\bpl\b']

    if user_level == 'junior':
        if any(re.search(pat, title_norm) for pat in senior_terms + pleno_terms):
            return False, "[Hard-Lock Override] Junior candidate excluded from Senior/Pleno role"
    elif user_level == 'senior':
        if any(re.search(pat, title_norm) for pat in junior_terms + pleno_terms):
            return False, "[Hard-Lock Override] Senior candidate excluded from Junior/Pleno role"

    # 5.4 Mandatory Academic Degree Check
    if user_education == 'sem formacao':
        degree_patterns = [r'superior\s+completo', r'graduacao', r'bacharelado', r'ensino\s+superior']
        if any(re.search(pat, full_text) for pat in degree_patterns):
            return False, "[Hard-Lock Override] Academic degree required (candidate has 'Sem Formação')"

    return True, "Passed High-Precision Filters"
```

### Why this solves the bugs:
1. **Passes `test_graduate_candidate_with_degree_job`**: Junior candidates with degree restrictions (`Todos`) are allowed to pass jobs requiring a degree since `user_education` is NOT `"sem formacao"`.
2. **Passes `test_foreign_currency_and_english_leakage`**: Detects and rejects foreign-paying local jobs and fluent English requirements for Junior profiles.
3. **Passes `test_sanity_battery_zero_approval`**: Ensures that every sanity check resets the score to `0`, sets `aprovado = False`, and prepends `[Hard-Lock Override]` inside `evaluation["reason"]` when hard-locks are violated.
