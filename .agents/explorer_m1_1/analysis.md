# Vagas Bot Codebase Analysis: Exceptions, Filter Processing, and High-Precision Design

## 1. Startup & Runtime Exceptions (and Test Failures)

During our investigation of the `vagas_bot` codebase, we analyzed the source files and executed the test runner (`run_tests.py`). We identified several critical exceptions and test failures.

### A. Missing `API_KEYS` and Groq Logic in `scrapers/ai_filter.py` (ImportError)
* **Location**: `scrapers/ai_filter.py`
* **Symptom**: The test `test_ia_ranking_groq_client_no_api_keys` fails with the following traceback:
  ```python
  def test_ia_ranking_groq_client_no_api_keys():
  >       from scrapers.ai_filter import API_KEYS
  E       ImportError: cannot import name 'API_KEYS' from 'scrapers.ai_filter'
  ```
* **Investigation**: The file `scrapers/ai_filter.py` in the working directory has been modified. The entire Groq API logic, Pydantic model (`JobEvaluation`), and the constant `API_KEYS` were removed, leaving only a basic regex-based mock filter. This causes immediate import errors during tests and bot runs that expect the AI components.
* **Impact**: Blocks execution of all tests verifying Groq API interactions and ranking limits.

### B. SQLite Database Locks in Test Suite (`sqlite3.OperationalError: database is locked`)
* **Location**: `tests/test_tier1.py` and `tests/conftest.py`
* **Symptom**: Multiple tests (e.g. `test_auto_apply_skips_low_score_jobs`, `test_auto_apply_fails_gracefully_on_network_error`, `test_bot_centralized_seniority_level_filtering`) fail with:
  ```python
  E       sqlite3.OperationalError: database is locked
  ```
* **Investigation**: In `tests/test_tier1.py`, functions like `test_auto_apply_updates_database_applied` open manual database connections using `conn = sqlite3.connect(database.DB_PATH)`. If an exception occurs (e.g. a `UNIQUE constraint failed: jobs.id` due to leftover DB data), the test terminates before reaching `conn.close()`. The SQLite connection remains open, keeping a write lock on `jobs_test.db`. This locks subsequent tests and prevents `setup_test_db` in `conftest.py` from deleting or resetting the database file.
* **Impact**: Cascade failure of all database-touching tests.

### C. Missing Hard-Locks for Foreign Currency & English in AI Filter
* **Location**: `scrapers/ai_filter.py` (Classic/mock implementation on disk)
* **Symptom**: Tests `test_sanity_battery_zero_approval` and `test_foreign_currency_and_english_leakage` fail.
* **Investigation**: The current `score_job_match` function on disk does not implement the Python-level hard-locks for foreign currency (USD/Euro) and fluent English requirements for Junior positions. Therefore, when these jobs are passed to the filter, it returns `aprovado: True`, violating the E2E expectations.
* **Impact**: Fails the adversarial challenge sanity tests.

---

## 2. Job Keywords & Filters Processing

The matching and filtering pipeline in `vagas_bot` works in two distinct stages: Local Heuristics and AI Filtering.

### Stage 1: Local Heuristics (`bot.py` -> `is_job_relevant`)
When a search is triggered, the bot maps the user-selected category to a scraper query (e.g., `"Design e Social Media"` -> `"Social Media"`). Scrapers scrape raw jobs and feed them to `is_job_relevant(job, keyword, settings)`:
1. **Normalization**: Accents are stripped and strings are converted to lowercase.
2. **Talent Pool Exclusion**: Automatically discards jobs with titles containing "banco de talentos" or "talent pool".
3. **Location Check**: If the user's location is set to "Remoto", it rejects jobs containing presential/hybrid terms unless they also explicitly mention remote. If local (e.g., Londrina), it permits matches against a list of neighboring cities. Freelance platforms are exempt.
4. **Contract Check**: If CLT is selected, PJ/Freelance jobs are rejected (and vice-versa).
5. **Seniority Check**: If the candidate is Junior, titles containing Pleno/Sênior terms are blocked.
6. **Blacklists**:
   - **Global Blacklist**: Discards jobs containing words like `professor`, `médico`, `enfermeiro`, etc., in their title.
   - **Niche Blacklist**: Excludes specific words based on the search keyword (e.g., for `gestor de tráfego`, it blocks `aéreo`, `carga`, `logística`).
7. **Keyword Matching**:
   - The git repository version utilized a `rules` dictionary (list-of-lists of required words) to check queries.
   - The working directory version checks if `kw_norm` is a literal substring of `title_norm`, or performs a regex search `\bkw_norm\b` on the full text.

### Limitations of the Current Keyword Matching:
* **Phrase Dependency**: A search for `"Backend Python"` checks for that exact substring. If a job is titled `"Python Developer (Backend)"`, it will fail to match because of word ordering.
* **Substring Leaks**: Without strict boundary checks, matching `"Java"` will falsely approve `"Javascript"` jobs.
* **Missing Rules**: Since the local `rules` dictionary was deleted, complex searches fail to match their broad scraper outputs.

### Stage 2: AI Filtering (`scrapers/ai_filter.py` -> `score_job_match`)
Jobs that pass the local heuristics are written to the database. If `ai_filter` is enabled, the bot queries the Groq API (using `llama-3.3-70b-versatile`) to evaluate candidate-to-job compatibility.
* The LLM evaluates the job based on specific rules (e.g., Rule of Gold for AI jobs).
* Post-override Python hard-locks check if the LLM hallucinated, forcing `aprovado = False` if basic conditions (level, freelance, location) are violated.

---

## 3. Recommended Design for High-Precision Filtering

To solve the phrase-dependency and leakage issues, we design a **High-Precision Filter** combining exact keyword matching with strict title allowlists and blocklists.

### A. Core Architecture
Instead of broad checks, the filter decomposes the search keyword into structured rules:
1. **Title Allowlist Groups**: For a keyword like `"Backend Python"`, the allowlist is represented as `[["python", "django", "fastapi"], ["backend", "dev", "desenvolvedor", "engineer"]]`. The title must match **at least one** term from **each** group. This handles word order variations (e.g. `"Python Backend"` vs `"Backend Python Dev"`).
2. **Exact Word Matching**: Substring matches are replaced with strict word boundary checks (`\bkeyword\b`) to prevent partial word leaks.
3. **Niche Blocklists**: Eliminates irrelevant titles containing blocked terms.

### B. Python Implementation Sketch
Here is the proposed design for the high-precision gatekeeper function:

```python
import re
import unicodedata

def normalize_str(s: str) -> str:
    if not s:
        return ""
    s = unicodedata.normalize('NFD', str(s))
    return s.encode('ascii', 'ignore').decode('utf-8').lower()

class HighPrecisionFilter:
    def __init__(self):
        # Allowlist groups: at least one word from each inner list must be present in the title
        self.allowlists = {
            "backend python": [
                ["python", "django", "fastapi", "flask"],
                ["backend", "back-end", "developer", "dev", "programador", "engineer", "engenheiro"]
            ],
            "estagiario de ti / programacao": [
                ["estagio", "estagiario", "intern", "trainee"],
                ["ti", "programacao", "desenvolvimento", "computacao", "sistemas", "dev", "python", "software"]
            ],
            "gestor de trafego / performance": [
                ["trafego", "performance", "ads", "media", "midia", "marketing"],
                ["gestor", "analista", "especialista", "coordenador", "growth", "paid"]
            ]
        }
        
        # Blocklists of words that must NOT appear in the title (checked as exact words)
        self.blocklists = {
            "global": [
                "professor", "professora", "tutor", "docente", "aulas", "advogado", "direito",
                "medico", "enfermeiro", "dentista", "faxineiro", "limpeza", "copa", "servente"
            ],
            "gestor de trafego / performance": [
                "aereo", "logistica", "transporte", "rodoviario", "carga", "frota", "veiculos", "patio"
            ]
        }

    def exact_word_in_text(self, word: str, text: str) -> bool:
        """Checks if a normalized word exists in a normalized text with exact boundaries."""
        pattern = rf"\b{re.escape(word)}\b"
        return bool(re.search(pattern, text))

    def evaluate_job(self, title: str, requirements: str, keyword: str) -> bool:
        """
        Executes high-precision gatekeeping on a scraped job.
        Returns True if the job matches exact filters, False otherwise.
        """
        title_norm = normalize_str(title)
        reqs_norm = normalize_str(requirements)
        full_text = f"{title_norm} {reqs_norm}"
        kw_norm = normalize_str(keyword)

        # 1. Check Global Blocklist
        for blocked_word in self.blocklists.get("global", []):
            if blocked_word not in kw_norm:  # Avoid blocking the search keyword itself
                if self.exact_word_in_text(blocked_word, title_norm):
                    return False

        # 2. Check Niche-Specific Blocklist
        niche_blocklist = self.blocklists.get(kw_norm, [])
        for blocked_word in niche_blocklist:
            if self.exact_word_in_text(blocked_word, title_norm):
                return False

        # 3. Check Allowlist Groups (if defined for the keyword)
        if kw_norm in self.allowlists:
            allow_groups = self.allowlists[kw_norm]
            # Verify that the title contains at least one word from each group
            for group in allow_groups:
                group_matched = any(self.exact_word_in_text(allowed_word, title_norm) for allowed_word in group)
                if not group_matched:
                    return False
            return True

        # 4. Fallback: Exact word boundary match of the keyword in title or body
        # Splitting keywords (e.g. "python backend" -> must match both "python" and "backend" exactly)
        kw_words = [w for w in re.split(r'\W+', kw_norm) if len(w) > 2]
        if kw_words:
            # All individual words of the keyword query must exist as exact words in the job
            return all(self.exact_word_in_text(w, full_text) for w in kw_words)

        return False
```

### Advantages of this Design:
1. **Accurate matching order-independence**: Title `"Python Backend Dev"` matches `"Backend Python"` query because each group (`["python"...]` and `["backend"...]`) is satisfied.
2. **Zero false positives from partial words**: Checking `exact_word_in_text("java", ...)` won't match `"javascript"`.
3. **Decoupled rules**: Can be easily maintained and updated without interfering with AI prompt formatting.
