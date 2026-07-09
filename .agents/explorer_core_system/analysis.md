# Codebase Audit & Security Report

**Date**: 2026-07-07T19:22:30Z  
**Scope**: Read-only audit of `database.py`, `bot.py`, `auto_apply.py`, and `app.py`.  
**Overall Status**: 15 distinct logic bugs, syntax/compilation pitfalls, unhandled exceptions, resource leaks, and performance bottlenecks identified.

---

## 1. File: `database.py`

### Issue 1.1: Column Defaults Ignored for NULL Values in `get_jobs`
* **Filename**: `C:\Users\99196\OneDrive\Documentos\vagas_bot\database.py`
* **Line Number(s)**: 71-74
* **Description**:
  The function `get_jobs` maps columns `job_type`, `profession`, `level`, and `requirements` using conditional logic like:
  ```python
  "job_type": r[6] if len(r)>6 else "CLT"
  ```
  Since the `SELECT` query retrieves exactly 10 columns, `len(r)` is always 10. Thus, `len(r)>6` is always `True`. If the database column contains a `NULL` (`None` in Python), the dictionary will store `None` rather than falling back to `"CLT"`.
* **Proposed Fix**: Check if the database value is not `None`:
  ```python
  "job_type": r[6] if (len(r) > 6 and r[6] is not None) else "CLT",
  "profession": r[7] if (len(r) > 7 and r[7] is not None) else "Tech",
  "level": r[8] if (len(r) > 8 and r[8] is not None) else "ND",
  "requirements": r[9] if (len(r) > 9 and r[9] is not None) else "Requisitos na página."
  ```

### Issue 1.2: Unhandled KeyError in `insert_jobs` Batch Ingestion
* **Filename**: `C:\Users\99196\OneDrive\Documentos\vagas_bot\database.py`
* **Line Number(s)**: 43-49
* **Description**:
  `insert_jobs` iterates over `jobs` and accesses `job['link']`, `job['title']`, and `job['platform']` directly. If any job in the ingestion batch is missing one of these required keys, a `KeyError` is raised. Since `conn.commit()` is called after the loop, this KeyError rolls back the entire batch and crashes the function.
* **Proposed Fix**: Extract keys safely and skip malformed jobs:
  ```python
  for job in jobs:
      try:
          link = job.get('link')
          title = job.get('title')
          platform = job.get('platform')
          if not link or not title or not platform:
              logger.warning(f"Skipping job insertion due to missing required fields: {job}")
              continue
          c.execute('INSERT INTO jobs ...', (...))
          inserted += 1
      except sqlite3.IntegrityError:
          pass
  ```

---

## 2. File: `bot.py`

### Issue 2.1: Missing Callback Handler for `auto_apply_` Button
* **Filename**: `C:\Users\99196\OneDrive\Documentos\vagas_bot\bot.py`
* **Line Number(s)**: 716-722
* **Description**:
  When sending a job with an email contact, the bot adds an `InlineKeyboardButton` with `callback_data=f"auto_apply_{count}"`. However, no handler is registered with the dispatcher for `F.data.startswith("auto_apply_")`. Clicking this button does nothing and shows a permanent loading spinner to the user.
* **Proposed Fix**: Add a callback query handler in `bot.py`:
  ```python
  @dp.callback_query(F.data.startswith("auto_apply_"))
  async def handle_auto_apply_callback(callback: CallbackQuery):
      # Process email application or notify user
      await callback.answer("Candidatura por e-mail agendada com sucesso!", show_alert=True)
  ```

### Issue 2.2: Broken Error Reporting due to Markdown Parsing in `global_error_handler`
* **Filename**: `C:\Users\99196\OneDrive\Documentos\vagas_bot\bot.py`
* **Line Number(s)**: 34-38
* **Description**:
  The global error handler tries to report tracebacks to Telegram using Markdown formatting. However, python traceback strings frequently contain special characters like `_` (e.g. `__init__.py`) and `*`. Telegram's Markdown parser will fail with a `TelegramBadRequest` error, causing the error handler itself to crash without notifying the user.
* **Proposed Fix**: Use HTML parse mode and escape the traceback string:
  ```python
  import html
  escaped_error = html.escape(erro_completo[:3800])
  msg = f"🚨 <b>CRITICAL BUG DETECTED:</b>\n<pre><code class=\"language-python\">{escaped_error}</code></pre>"
  if event.update.callback_query:
      await event.update.callback_query.message.answer(msg, parse_mode="HTML")
  elif event.update.message:
      await event.update.message.answer(msg, parse_mode="HTML")
  ```

### Issue 2.3: Python `and` Evaluation Bug in Callback Filter
* **Filename**: `C:\Users\99196\OneDrive\Documentos\vagas_bot\bot.py`
* **Line Number(s)**: 303
* **Description**:
  The decorator `@dp.callback_query(F.data.startswith("hunt_") and F.data != "hunt_menu")` uses the Python `and` operator on two truthy MagicFilter objects. In Python, `A and B` returns `B` if `A` is truthy, which simplifies to `@dp.callback_query(F.data != "hunt_menu")`. This bypasses the prefix restriction entirely and matches any callback query that is not `"hunt_menu"`, potentially stealing events meant for settings or modes.
* **Proposed Fix**: Pass filters as separate arguments to the decorator:
  ```python
  @dp.callback_query(F.data.startswith("hunt_"), F.data != "hunt_menu")
  ```

### Issue 2.4: Resource Leak of Downloaded PDF and Resumes
* **Filename**: `C:\Users\99196\OneDrive\Documentos\vagas_bot\bot.py`
* **Line Number(s)**: 814, 825
* **Description**:
  In `handle_document`, the files `temp_curriculo_{user_id}.pdf` and `curriculo_{user_id}.txt` are written to disk. They are never deleted, which will lead to persistent storage exhaustion on the server over time.
* **Proposed Fix**: Clean up temporary files in a `finally` block:
  ```python
  try:
      # read and parse PDF ...
  finally:
      if os.path.exists(file_path):
          os.remove(file_path)
  ```

### Issue 2.5: Synchronous File I/O Blocking the Event Loop in `cmd_logs`
* **Filename**: `C:\Users\99196\OneDrive\Documentos\vagas_bot\bot.py`
* **Line Number(s)**: 107-112
* **Description**:
  Inside `cmd_logs`, the bot opens and reads the entire `"erros_robo.log"` file synchronously using `f.readlines()`. Since the log has a rotation size limit of 10 MB, reading a 10 MB file synchronously inside the main thread will block the async event loop, delaying responses for all other active bot users.
* **Proposed Fix**: Read the tail end of the file asynchronously, or run the read operation in a threadpool:
  ```python
  def read_log_tail():
      with open("erros_robo.log", "r", encoding="utf-8") as f:
          # Seek to end and grab last lines
          f.seek(0, os.SEEK_END)
          # ... read tail
          return tail_data
  tail = await asyncio.to_thread(read_log_tail)
  ```

### Issue 2.6: Blocking Synchronous I/O Calls inside Async Hunt Loop
* **Filename**: `C:\Users\99196\OneDrive\Documentos\vagas_bot\bot.py`
* **Line Number(s)**: 704
* **Description**:
  In `_do_hunt`, the code calls `apply_result = auto_apply.auto_apply(job)` synchronously in the middle of the main loop processing. If `auto_apply` executes file checks or synchronous HTTP calls, it blocks the main thread's event loop.
* **Proposed Fix**: Wrap it in `asyncio.to_thread`:
  ```python
  apply_result = await asyncio.to_thread(auto_apply.auto_apply, job)
  ```

---

## 3. File: `auto_apply.py`

### Issue 3.1: Hardcoded Global Resume Path in `auto_apply`
* **Filename**: `C:\Users\99196\OneDrive\Documentos\vagas_bot\auto_apply.py`
* **Line Number(s)**: 124, 26
* **Description**:
  `prepare_candidate_data` defaults to `"curriculo.txt"`. When `bot.py` calls `auto_apply.auto_apply(job)` at line 704, it passes no arguments for the path or user identification. However, the bot saves user resumes as `curriculo_{user_id}.txt`. Consequently, `auto_apply` always looks for `"curriculo.txt"`, fails to find it, and submits applications with empty name and email strings.
* **Proposed Fix**: Accept the `user_id` or path in `auto_apply` and pass it from `bot.py`:
  ```python
  # In bot.py
  apply_result = await asyncio.to_thread(auto_apply.auto_apply, job, user_id=chat_id)
  
  # In auto_apply.py
  def auto_apply(job: dict, user_id: str = None) -> dict:
      path = f"curriculo_{user_id}.txt" if user_id else "curriculo.txt"
      candidate = prepare_candidate_data(path)
  ```

### Issue 3.2: Hardcoded Candidate Identity in `apply_to_job`
* **Filename**: `C:\Users\99196\OneDrive\Documentos\vagas_bot\auto_apply.py`
* **Line Number(s)**: 181-182
* **Description**:
  `apply_to_job` prepares candidate form submission data by hardcoding `"name": "Diego Candidate"` and `"email": "diego@example.com"`. It completely ignores any curriculum files parsed via `prepare_candidate_data`, meaning all auto-apply forms are filled with mock candidate details.
* **Proposed Fix**: Pass the `candidate` dictionary to `apply_to_job`:
  ```python
  def apply_to_job(job_link: str, resume_path: str, candidate: dict, mock_ats_url: str = None) -> bool:
      # ...
      data = {
          "job_link": job_link,
          "name": candidate.get("name", "Diego Candidate"),
          "email": candidate.get("email", "diego@example.com")
      }
  ```

### Issue 3.3: SQLite Connection Exhaustion in Loop (`run_auto_apply`)
* **Filename**: `C:\Users\99196\OneDrive\Documentos\vagas_bot\auto_apply.py`
* **Line Number(s)**: 229-236
* **Description**:
  In `run_auto_apply`, the loop connects and disconnects from the SQLite database for *every single job* processed to update the job status. Repeatedly opening and closing SQLite connections within a hot loop is highly inefficient.
* **Proposed Fix**: Open the SQLite connection once before the loop, run all queries, commit, and then close it:
  ```python
  upd_conn = sqlite3.connect(db_path, timeout=10)
  upd_conn.execute('PRAGMA journal_mode=WAL')
  try:
      upd_c = upd_conn.cursor()
      for (link,) in jobs:
          success = apply_to_job(link, resume_path, mock_ats_url)
          new_status = "applied" if success else "failed"
          upd_c.execute("UPDATE jobs SET status = ? WHERE link = ?", (new_status, link))
      upd_conn.commit()
  finally:
      upd_conn.close()
  ```

### Issue 3.4: Synchronous/Blocking Network Requests in `apply_to_job`
* **Filename**: `C:\Users\99196\OneDrive\Documentos\vagas_bot\auto_apply.py`
* **Line Number(s)**: 185
* **Description**:
  `apply_to_job` uses `requests.post`, which is a synchronous, blocking network call. When called during testing or potential application routines, it halts thread execution.
* **Proposed Fix**: Wrap calling functions in `asyncio.to_thread` or switch to an asynchronous library like `httpx.AsyncClient`.

### Issue 3.5: Race Condition / Concurrency Bug in `run_auto_apply`
* **Filename**: `C:\Users\99196\OneDrive\Documentos\vagas_bot\auto_apply.py`
* **Line Number(s)**: 219
* **Description**:
  `run_auto_apply` selects all jobs with `status = 'pending'` and iterates over them. If multiple processes or threads execute `run_auto_apply` concurrently, they will pull the same pending job list and submit duplicate job applications.
* **Proposed Fix**: Assign a unique `batch_id` to the running process, run an update statement first to mark jobs as `applying_<batch_id>`, and then retrieve only those marked jobs.

---

## 4. File: `app.py`

### Issue 4.1: Synchronous Blocking Database Call in Async Web Controller `/api/webhook/n8n`
* **Filename**: `C:\Users\99196\OneDrive\Documentos\vagas_bot\app.py`
* **Line Number(s)**: 55
* **Description**:
  The FastAPI endpoint `n8n_webhook` is declared as an `async def`, but it directly invokes the synchronous database helper `insert_jobs(jobs)`. Database transactions are blocking I/O operations and will freeze the whole FastAPI event loop.
* **Proposed Fix**: Call it inside a threadpool using `asyncio.to_thread`:
  ```python
  inserted = await asyncio.to_thread(insert_jobs, jobs)
  ```

### Issue 4.2: Sequential Scraper Execution Bottleneck in `/api/trigger`
* **Filename**: `C:\Users\99196\OneDrive\Documentos\vagas_bot\app.py`
* **Line Number(s)**: 70-76
* **Description**:
  Scrapers are executed sequentially in a `for` loop inside `/api/trigger`. If a user initiates a scan on 4-5 platforms, the web request will take the sum of all scraper durations, easily triggering HTTP gateway timeouts (typically 30 seconds).
* **Proposed Fix**: Execute the scraping tasks concurrently with `asyncio.gather`:
  ```python
  async def run_scraper(plat):
      module = importlib.import_module(f"scrapers.{plat}")
      return await asyncio.to_thread(module.scrape, keyword=keyword, level=level)
      
  results = await asyncio.gather(*(run_scraper(p) for p in platforms), return_exceptions=True)
  for jobs in results:
      if isinstance(jobs, list):
          all_jobs.extend(jobs)
  ```

### Issue 4.3: Hardcoded Absolute Paths Violating Portability
* **Filename**: `C:\Users\99196\OneDrive\Documentos\vagas_bot\app.py`
* **Line Number(s)**: 15, 36
* **Description**:
  The paths for logs and static assets are hardcoded to the local user folder:
  `"C:\\Users\\99196\\OneDrive\\Documentos\\vagas_bot\\system.log"` and `"C:\\Users\\99196\\OneDrive\\Documentos\\vagas_bot\\static"`.
  This causes immediate failures if the project is run on another server, Docker container, or user profile.
* **Proposed Fix**: Define these paths relative to the application's root directory:
  ```python
  BASE_DIR = os.path.dirname(os.path.abspath(__file__))
  log_path = os.path.join(BASE_DIR, "system.log")
  STATIC_DIR = os.path.join(BASE_DIR, "static")
  ```

---

## 5. Additional Test Failure Discrepancies (Out of Audited Files Scope)

### Issue 5.1: Contract Mismatch in `ai_filter.py` causing `test_ia_ranking_handles_groq_malformed_json` Failure
* **File & Test**: `tests/test_tier2.py:135 (test_ia_ranking_handles_groq_malformed_json)`
* **Explanation**: The E2E test asserts that when Groq returns malformed JSON, the function `score_job_match` should fail with `aprovado = False` and `score = 0`. However, the implementation in `scrapers/ai_filter.py` catches all exceptions and automatically approves the job by default (`aprovado = True`, `score = 50`) as a "safe fallback" to prevent missing job listings. This creates a contract conflict that causes the test to fail.
* **Proposed Fix**: Align the test assertions with the intended "safe fallback" behavior of the filter, or modify `ai_filter.py` to only fallback to approval for transient network errors (like HTTP 5xx/429) while rejecting invalid parsing outputs.

### Issue 5.2: Incomplete Playwright Mock causing Glassdoor Scraper Test Failures
* **File & Tests**: `tests/test_tier1.py:65 (test_glassdoor_scraper_returns_valid_schema)`, `tests/test_tier2.py:58 (test_scraper_handles_special_characters)`
* **Explanation**: The real Glassdoor scraper `scrape` function (in `scrapers/glassdoor.py`) performs a validation: `if "glassdoor" in content.lower() and len(content) > 5000:`. However, the global mock Playwright Page defined in `tests/conftest.py` returns `"<html>Mock Page Content</html>"`. Since this mocked page content is of length 30 and does not contain `"glassdoor"`, the Glassdoor scraper rejects it as not loaded, returning `[]` and failing the tests.
* **Proposed Fix**: Update the `MockPage` in `tests/conftest.py` to dynamically return page content containing `"glassdoor"` and of sufficient length when the navigated URL matches a Glassdoor endpoint.
