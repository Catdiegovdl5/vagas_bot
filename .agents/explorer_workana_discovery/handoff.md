# Handoff Report: vagas_bot Discovery (Settings, Workana Scraper, and Candidate Checks)

## 1. Observation
The following file structures and behaviors were directly observed via read-only inspection of the codebase:
- **Settings Store**: Located in `bot.py` where a global dictionary `user_settings_db = {}` is defined (line 101). Default settings are cloned using `copy.deepcopy` from `DEFAULT_SETTINGS` (line 74-99). The inline keyboard is constructed in `get_settings_markup(chat_id)` (lines 155-173).
- **Language Detection Filter**: Implemented in `bot.py` inside the function `process_hunt` (lines 1127-1134). It imports `detect` from `langdetect` and uses:
  ```python
  def is_brazilian_job(text):
      try:
          if len(text) < 20: return True
          return detect(text) == 'pt'
      except:
          return True
  ```
  Jobs are filtered out if they are not from freelance platforms AND `is_brazilian_job` returns `False` (lines 1137-1144).
- **Workana Scraper**: Implemented in `scrapers/workana.py`. The scraper function is defined as `def scrape(keyword="Python", level="Todos")` (line 10). It loops over pages with `for page in [1, 2]:` (line 23), requests URLs using `curl_cffi` (line 32) or standard `requests` (line 37), parses the Vue.js payload in `:results-initials` via `json.loads` (line 46), and caps the list length at 30 (`if len(jobs) >= 30: break`, line 50).
- **Candidate Database Checks**: Defined in `database.py`. The schema contains the table `applied_jobs` (lines 35-40):
  ```sql
  CREATE TABLE IF NOT EXISTS applied_jobs (
      link TEXT PRIMARY KEY,
      applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  )
  ```
  Status check is performed via `is_applied(link)` (lines 99-107) and marked via `mark_applied(link)` (lines 109-117). In `bot.py` (lines 1196-1208), the inline keyboard is rendered depending on `already_applied = await asyncio.to_thread(is_applied, link)`. Clicking the mark button triggers callback `mark_applied_{link}`, handled at `bot.py:397-419`, which calls `mark_applied` and rewrites the markup.

---

## 2. Logic Chain
- **Settings Menu**: Since user settings are retrieved and updated in-memory via `get_user_settings(chat_id)` in `bot.py`, adding the PT-BR language shield state requires modifying `DEFAULT_SETTINGS` to include `"escudo_ptbr": True`. A toggle button with callback data `"toggle_escudo_ptbr"` can then query and display this state. The callback handler toggles the boolean value, allowing changes to propagate instantly.
- **Bypassing Language Shield**: In the `process_hunt` function, reading `settings.get("escudo_ptbr", True)` lets the bot determine if it should execute the `langdetect` clean-up loop or bypass it entirely (i.e. assigning `vagas_br = all_jobs`).
- **Pagination & Delays**: To pagination-enable `scrapers/workana.py`, the hardcoded loop `for page in [1, 2]` must be replaced by a dynamic range `for page in range(1, max_pages + 1)`. A break condition is added if `results` is empty. To avoid rate-limiting (HTTP 429), `time.sleep(random.uniform(2.0, 4.5))` can be inserted in this loop. Because the scraper is executed in a thread via `asyncio.to_thread`, synchronous sleep is thread-safe and non-blocking to the main loop.
- **Candidate Status Checks**: Checking if the job URL exists in the `applied_jobs` table using `is_applied` and setting the inline markup accordingly guarantees that already applied jobs show `"✅ Já me Candidatei"`. Marking jobs as applied updates the DB dynamically and replaces the `"✋ Já me Candidatei"` button to avoid multiple clicks.

---

## 3. Caveats
- **Settings Persistence**: Currently, settings are only stored in-memory in the dictionary `user_settings_db`. If the Telegram bot restarts, user configurations (including the state of `"escudo_ptbr"`) will reset to defaults. If persistent state is desired in the future, these settings should be serialized to a DB table or JSON file.
- **Scraper Cloudflare / Vue.js Changes**: Workana uses Cloudflare protection and a Vue.js hybrid rendering model. While using `curl_cffi` impersonating Chrome bypasses standard anti-bot protection, changes to Workana's Vue payload structure (specifically the tag `search` and property `:results-initials`) will break parsing.

---

## 4. Conclusion
The implementation of the requested features is highly feasible without complex architectural changes:
1. The settings menu can be modified locally in `bot.py` to add the `"escudo_ptbr"` toggle key, toggle button, and query callback handler.
2. The language detection loop in `bot.py` can be wrapped in a conditional check based on the `"escudo_ptbr"` configuration state.
3. `scrapers/workana.py` can support customizable pagination parameters (`max_pages`, `max_jobs`) and delays via random intervals of `time.sleep` in between page requests.
4. The database queries and buttons for candidate status check already exist and function correctly, validating the usage of the SQLite `applied_jobs` table.

---

## 5. Verification Method
To verify these behaviors independently, inspect the following files and functions:
1. **Settings configuration**: Check `bot.py` lines 74-99 and 155-173.
2. **Language filtering**: Check `bot.py` lines 1127-1144.
3. **Scraper logic**: Check `scrapers/workana.py` lines 10-85.
4. **Database structure**: Check `database.py` lines 35-40 and functions `is_applied`/`mark_applied`.
5. Run E2E test suites when accessible using:
   `python run_tests.py` or `pytest tests/`
