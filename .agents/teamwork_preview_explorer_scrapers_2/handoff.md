# Handoff Report — Backend Job Models & Scraper Payload Compatibility

**Agent**: `teamwork_preview_explorer_scrapers_2`  
**Working Directory**: `C:\Users\99196\OneDrive\Documentos\vagas_bot\.agents\teamwork_preview_explorer_scrapers_2`  
**Date**: 2026-07-29  

---

## 1. Observation

Direct observations from inspecting codebase files:

1. **`database.py` (lines 51–76 & lines 126–154)**:
   - Table `jobs` schema:
     ```sql
     CREATE TABLE IF NOT EXISTS jobs (
         id TEXT PRIMARY KEY,
         title TEXT,
         company TEXT,
         budget TEXT,
         link TEXT,
         platform TEXT,
         added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
         job_type TEXT,
         profession TEXT,
         level TEXT,
         requirements TEXT,
         location TEXT,
         lat REAL,
         lon REAL,
         lang TEXT
     )
     ```
   - Validation in `insert_jobs(jobs)` (lines 137–141):
     ```python
     link = job.get('link') or ''
     title = job.get('title') or ''
     platform = job.get('platform') or ''
     if not link or not title or not platform or link == '#':
         continue
     ```
   - Normalization call in `insert_jobs(jobs)` (lines 142–144):
     ```python
     raw_prof = job.get('profession') or ''
     from scrapers.ai_filter import classify_profession_fallback
     clean_profession = classify_profession_fallback(title, raw_prof)
     ```

2. **`scrapers/ai_filter.py` (lines 36–63)**:
   - Allowed professions list:
     ```python
     ALLOWED_PROFESSIONS = [
         "Growth & Tráfego",
         "IA-Ops",
         "SDR Técnico",
         "Analytics Engineer",
         "Server-Side Tracking",
         "Outros"
     ]
     ```
   - Deterministic classification fallback logic:
     ```python
     def classify_profession_fallback(title: str, current_profession: str = "") -> str:
         if current_profession and current_profession.strip() in ALLOWED_PROFESSIONS:
             return current_profession.strip()
         ...
     ```

3. **`bot.py` (lines 2017–2072 & lines 2195–2336)**:
   - `SEARCH_MAPPING` maps friendly names to taxonomy keys.
   - `classify_job_profession(job)` sets `job['category'] = cat` and `job['profession'] = prof` in-memory.

4. **`scrapers/linkedin.py`, `scrapers/gupy.py`, `scrapers/workana.py`**:
   - Return format across scrapers is `List[Dict[str, Any]]` containing keys: `"platform"`, `"title"`, `"company"`, `"budget"`, `"link"`, `"job_type"`, `"profession"`, `"level"`, `"requirements"`.

---

## 2. Logic Chain

1. **Observation 1** demonstrates that `insert_jobs()` in `database.py` validates `link`, `title`, and `platform`. If any of these are empty, missing, or equal to `'#'`, the job record is skipped.
2. **Observation 1 & 2** show that when inserting into `jobs.db`, `raw_prof` is passed to `classify_profession_fallback(title, raw_prof)`. If `raw_prof` is not present in `ALLOWED_PROFESSIONS`, regex rules map `title` to one of the 6 allowed professions or default to `"Outros"`.
3. **Observation 1** shows that the SQLite database table `jobs` includes a `profession` TEXT column, but does NOT include a `category` column. `category` is used as an in-memory attribute by `bot.py` during classification and filtering.
4. **Observation 3** shows that `bot.py` maintains `SEARCH_MAPPING` and `CO_OCCURRENCE_RULES` for term expansion and relevance checking for all categories (including the 6 new categories).
5. **Observation 4** confirms that all existing scrapers conform to returning dictionaries with `platform`, `title`, `company`, `budget`, `link`, `job_type`, `profession`, `level`, and `requirements`.

---

## 3. Caveats

- **PostgreSQL / SaaS Multi-Tenancy**: `database.py` contains `PostgresRLSTenantContext` abstractions for future RLS PostgreSQL migrations, but currently runs SQLite `jobs.db`.
- **Read-Only Scope**: This report is produced under read-only exploration rules. No modifications were made to project source files.

---

## 4. Conclusion

1. **Required Scraper Fields**: `link` (valid URL, non-empty, `!= '#'`), `title` (non-empty string), and `platform` (non-empty string).
2. **Database & Category Validation**: SQLite `jobs` table persists `profession` (fallback classified via `ALLOWED_PROFESSIONS`). `category` is an in-memory filter property created by `classify_job_profession()`.
3. **Category Normalization**: Scraper payload professions are normalized by `classify_profession_fallback()` in `ai_filter.py` and `classify_job_profession()` in `bot.py`.
4. **100% Payload Compatibility Requirement**: Scrapers must return `List[Dict[str, Any]]` containing `platform`, `title`, `link`, `company`, `budget`, `job_type`, `profession`, `level`, `requirements`, and `location`.

---

## 5. Verification Method

To independently verify these findings:

1. **Inspect Schema & Code**:
   - Check `database.py` lines 50–76 for table definition.
   - Check `database.py` lines 126–154 for `insert_jobs` filter logic.
   - Check `scrapers/ai_filter.py` lines 36–64 for `ALLOWED_PROFESSIONS`.
   - Check `bot.py` lines 2195–2336 for `classify_job_profession`.

2. **Run Pytest / Empirical Test Command**:
   - Command: `python run_tests.py` or `pytest`
   - Test `insert_jobs()` behavior with dictionary payloads omitting `link`, `title`, or `platform` to verify skipping behavior.
