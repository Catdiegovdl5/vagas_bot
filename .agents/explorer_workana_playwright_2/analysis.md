# Workana Scraper Integration Analysis

This document provides a detailed technical analysis of the integration between the **Workana scraper** (`scrapers/workana.py`) and the main bot orchestration system (`bot.py`), including how keywords are mapped, expanded, and queried, and how candidate/applied statuses are handled.

---

## 1. Scraper Invocation & Execution Cycle

### Import and Dynamic Loading
The scrapers are imported dynamically during the search execution phase (`_do_hunt` inside `bot.py`). 
* **Dynamic Import**: 
  ```python
  module = importlib.import_module(f"scrapers.{plat}")
  ```
  Here, `plat` represents the platform string (e.g., `"workana"`).
* **Synchronous-to-Asynchronous Thread Execution**: Since scrapers in this codebase are synchronous (blocking I/O using libraries like `requests` or `curl_cffi`), `bot.py` wraps their invocation in `asyncio.to_thread` to prevent blocking the main asyncio event loop:
  ```python
  res = await asyncio.to_thread(module.scrape, keyword=plat_search_keyword, level="Todos")
  ```
  *Note:* Platforms in the set `['jsearch', 'jooble', 'github_vagas', 'novenove', 'freelancer', 'indeed', 'linkedin', 'gmail', 'glassdoor', 'infojobs', 'gupy', 'vagas_com', 'programathor', 'coodesh', 'geekhunter']` are called with an additional `country` parameter. `workana` is not in this list, falling to the fallback block shown above with `level="Todos"`.

### Hunting and Gathering Cycle
1. **Trigger**: The hunt cycle begins when a user clicks a technology/profession button under `nicho_<name>` (which triggers the callback handler `process_hunt` parsing `hunt_<keyword>`) or when they type a raw message handled by `handle_free_text`.
2. **Setup**: The bot queries `get_user_settings(chat_id)` to resolve active platforms.
3. **Execution**: The bot runs the `fetch_plat` helper coroutine concurrently for all active platforms using:
   ```python
   results = await asyncio.gather(*(fetch_plat(p) for p in active_plats))
   ```
4. **Post-processing**: The returned lists of jobs are consolidated, deduplicated (using the job link as a primary key, or title and company name as a fallback), and filtered locally using `is_job_relevant(job, keyword, settings)`.
5. **Storage and Messaging**: Jobs are saved to SQLite (`jobs.db`) and delivered sequentially via Telegram messages with inline keyboard action buttons.

---

## 2. Keyword Mapping & CO_OCCURRENCE_RULES

### CO_OCCURRENCE_RULES Definition
The `CO_OCCURRENCE_RULES` dictionary in `bot.py` (lines 611–1825) holds keyword mapping configurations for relevance verification. For each supported niche, it contains two lists of keywords:
* **Group A (Index 0)**: Tech-specific keywords and skills (e.g., `"python"`, `"django"`, `"fastapi"`).
* **Group B (Index 1)**: Role or seniority level designations (e.g., `"desenvolvedor"`, `"dev"`, `"engineer"`).

For instance, the entry for `"desenvolvedor python"` is defined as:
```python
"desenvolvedor python": [
    [
        "python", "django", "fastapi", "flask", "pandas", "scrapy", 
        "numpy", "celery", "poetry", "pipenv", "asyncio", "backend"
    ],
    [
        "desenvolvedor", "desenvolvedora", "programador", "programadora", 
        "engenheiro", "engenheira", "dev", "backend", "back-end", 
        "fullstack", "software engineer"
    ]
]
```

### Keyword Verification
The verification helper `check_co_occurrence(text_norm, kw_norm, job=None)` checks that a job contains:
1. At least one term from **Group A** (Index 0).
2. At least one term from **Group B** (Index 1).
If the keyword does not exist in `CO_OCCURRENCE_RULES`, it falls back to ensuring all significant non-stopwords of the query are present in the job details.

---

## 3. Keyword Expansion and Passing to Workana Scraper

### Keyword Expansion Pipeline
1. In `_do_hunt` (`bot.py`), the display keyword clicked by the user is mapped to a search term using `search_mapping`:
   ```python
   base_keyword = search_mapping.get(keyword, keyword)
   ```
2. The code checks if the platform is freelance:
   ```python
   is_freelance = plat in ['workana', '99freelas', 'freelancer']
   ```
3. Seniority level is appended for regular job boards, but **specifically omitted** for freelance boards to maximize search yield:
   ```python
   plat_search_keyword = base_keyword
   if actual_level != "Todos" and not is_freelance:
       plat_search_keyword = f"{base_keyword} {actual_level}"
   ```
4. Inside `scrapers/workana.py`, the incoming keyword is normalized and used to query `bot.CO_OCCURRENCE_RULES` for further expansion:
   ```python
   kw_norm = "".join(c for c in unicodedata.normalize('NFKD', keyword) if unicodedata.category(c) != 'Mn').lower()
   search_kw = keyword
   if kw_norm in bot.CO_OCCURRENCE_RULES:
       grupo_a = bot.CO_OCCURRENCE_RULES[kw_norm][0]
       termos = grupo_a[:2]
       search_kw = " ".join(termos)
   ```
   If a match is found, the scraper query is expanded to the **first two terms of Group A** joined by a space. E.g., `"Desenvolvedor Python"` expands to query `"python django"`.

### Crucial Integration Gap / Bug
There is a naming mismatch between `search_mapping` values and `CO_OCCURRENCE_RULES` keys in `bot.py`:
* `bot.py` first maps user inputs (e.g. `"Especialista em IA"`) using `search_mapping` to simplified scraper keywords (e.g., `"Especialista IA"`).
* In `workana.py`, it normalizes `"Especialista IA"` to `"especialista ia"` and checks if it exists in `bot.CO_OCCURRENCE_RULES`.
* Since the key defined in `CO_OCCURRENCE_RULES` is the unmapped menu text `"especialista em ia"`, the lookup `kw_norm in bot.CO_OCCURRENCE_RULES` fails.
* Consequently, **keyword expansion does not trigger** for multiple terms, including:
  * `"Especialista IA"` (mapped from `"Especialista em IA"`, misses `"especialista em ia"`)
  * `"Engenheiro IA"` (mapped from `"Engenheiro de IA"`, misses `"engenheiro de ia"`)
  * `"AI Developer"` (mapped from `"Desenvolvedor de Agentes IA"`, misses `"desenvolvedor de agentes ia"`)
  * `"Analista Power BI"` (mapped from `"Analista de Power BI"`, misses `"analista de power bi"`)
  * `"Analista Analytics"` (mapped from `"Analista de Analytics"`, misses `"analista de analytics"`)
  * `"Analista Marketing Digital"` (mapped from `"Analista de Marketing Digital"`, misses `"analista de marketing digital"`)
  * `"Especialista SEO"` (mapped from `"Especialista em SEO"`, misses `"especialista em seo"`)
  * `"Analista CRM"` (mapped from `"Analista de CRM"`, misses `"analista de crm"`)
  * `"Analista RH"` (mapped from `"Analista de RH"`, misses `"analista de rh"`)

For these terms, Workana is queried with the raw unexpanded `base_keyword` value instead of the Group A terms.

---

## 4. Candidate & Applied Status Handling

Status tracking is handled using SQLite (`jobs.db`) located in the project's root, using queries and actions defined in `database.py`.

### Database Schema
* **`applied_jobs` Table**: Tracks links that the user has already marked as applied or had an auto-apply completed for.
  ```sql
  CREATE TABLE IF NOT EXISTS applied_jobs (
      link TEXT PRIMARY KEY,
      applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  )
  ```

### Code Interaction Flow
1. **Checking Applied Status**: Before showing jobs to the user, `bot.py` checks if a job's link has already been recorded in `applied_jobs`:
   ```python
   already_applied = await asyncio.to_thread(is_applied, link)
   ```
2. **Visual Feedback on UI**:
   * If `already_applied` is **True**:
     * The bot skips executing `auto_apply`.
     * The bot renders the buttons: `✅ Já me Candidatei` (non-functional callback query `noop_applied`) and `🔗 Ver Vaga Novamente` (url linking to job).
   * If `already_applied` is **False**:
     * The bot attempts a silent automatic email application: `auto_apply.auto_apply(job, str(chat_id))`.
     * The bot renders buttons: `🎯 Aplicar para a Vaga` (opens the link) and `✋ Já me Candidatei` (callback data `mark_applied_btn`).
3. **Manual Status Transition**:
   * When a user manually clicks `✋ Já me Candidatei` on Telegram, it triggers the callback query `mark_applied_btn`.
   * The handler `handle_mark_applied` extracts the job link from the message's button URL and runs:
     ```python
     await asyncio.to_thread(mark_applied, link)
     ```
   * It then edits the Telegram inline markup, swapping the `✋ Já me Candidatei` button with the inactive `✅ Já me Candidatei` label so the user gets immediate visual feedback that the state has been updated.
