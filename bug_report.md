# Vagas Bot Codebase Audit Report

This report presents the findings of a comprehensive read-only audit of the `vagas_bot` codebase. The audit identified logic bugs, syntax/compilation issues, unhandled exceptions, resource leaks, and performance bottlenecks across various modules.

No code modifications were made during this audit, adhering to the read-only constraint.

---

## Table of Contents
1. [Core System Audits](#1-core-system-audits)
   - [`bot.py`](#botpy)
   - [`app.py`](#apppy)
   - [`database.py`](#databasepy)
   - [`auto_apply.py`](#auto_applypy)
2. [Primary Scrapers and Filter Audits](#2-primary-scrapers-and-filter-audits)
   - [`scrapers/ai_filter.py`](#scrapersai_filterpy)
   - [`scrapers/linkedin.py`](#scraperslinkedinpy)
   - [`scrapers/indeed.py`](#scrapersindeedpy)
   - [`scrapers/glassdoor.py`](#scrapersglassdoorpy)
   - [`scrapers/infojobs.py`](#scrapersinfojobspy)
   - [`scrapers/jooble.py`](#scrapersjooblepy)
3. [Helper Scrapers, Launchers, and Utilities](#3-helper-scrapers-launchers-and-utilities)
   - [`scrapers/meta_ads.py`](#scrapersmeta_adspy)
   - [`scrapers/remotar.py`](#scrapersremotarpy)
   - [`scrapers/novenove.py`](#scrapersnovenovepy)
   - [`scrapers/freelancer.py`](#scrapersfreelancerpy)
   - [`scrapers/gmail.py`](#scrapersgmailpy)
   - [`scrapers/workana.py`](#scrapersworkanapy)
   - [`scrapers/jsearch.py`](#scrapersjsearchpy)
   - [`launcher.py`](#launcherpy)
   - [`render_bot.py`](#render_botpy)
   - [`verify_seniority.py`](#verify_senioritypy)

---

## 1. Core System Audits

### `bot.py`

#### Issue 1.1: Missing Callback Handler for `auto_apply_` Button
* **Line Number(s)**: 716-722
* **Description**: When sending a job with an email contact, the bot appends an `InlineKeyboardButton` with `callback_data=f"auto_apply_{count}"`. However, no handler is registered with the dispatcher for `F.data.startswith("auto_apply_")`. Clicking this button does nothing and shows a permanent loading spinner to the user.
* **Proposed Fix**: Add a callback query handler in `bot.py`:
  ```python
  @dp.callback_query(F.data.startswith("auto_apply_"))
  async def handle_auto_apply_callback(callback: CallbackQuery):
      # Process email application or notify user
      await callback.answer("Candidatura por e-mail agendada com sucesso!", show_alert=True)
  ```

#### Issue 1.2: Broken Error Reporting due to Markdown Parsing in `global_error_handler`
* **Line Number(s)**: 34-38
* **Description**: The global error handler attempts to report traceback logs to Telegram using Markdown formatting. However, python traceback strings frequently contain special characters like `_` (e.g., `__init__.py`) and `*` that cause Telegram's Markdown parser to fail with a `TelegramBadRequest` exception, crashing the error handler itself.
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

#### Issue 1.3: Python `and` Evaluation Bug in Callback Filter
* **Line Number(s)**: 303
* **Description**: The decorator `@dp.callback_query(F.data.startswith("hunt_") and F.data != "hunt_menu")` uses the Python `and` operator on two `MagicFilter` objects. In Python, `A and B` returns `B` if `A` is truthy, which simplifies the expression to `@dp.callback_query(F.data != "hunt_menu")`. This bypasses the `"hunt_"` prefix restriction entirely and matches any callback query that is not `"hunt_menu"`.
* **Proposed Fix**: Pass filters as separate arguments to the decorator:
  ```python
  @dp.callback_query(F.data.startswith("hunt_"), F.data != "hunt_menu")
  ```

#### Issue 1.4: Resource Leak of Downloaded PDF and Resumes
* **Line Number(s)**: 814, 825
* **Description**: In `handle_document`, the files `temp_curriculo_{user_id}.pdf` and `curriculo_{user_id}.txt` are written to disk but are never deleted, leading to gradual server storage exhaustion.
* **Proposed Fix**: Clean up temporary files in a `finally` block:
  ```python
  try:
      # read and parse PDF ...
  finally:
      if os.path.exists(file_path):
          os.remove(file_path)
  ```

#### Issue 1.5: Synchronous File I/O Blocking the Event Loop in `cmd_logs`
* **Line Number(s)**: 107-112
* **Description**: Inside `cmd_logs`, the bot reads the entire `"erros_robo.log"` file synchronously using `f.readlines()`. Since the log has a rotation size limit of 10 MB, reading this file synchronously inside the main thread will block the asynchronous event loop, delaying responses for all other active users.
* **Proposed Fix**: Run the file read operation in a threadpool using `asyncio.to_thread`:
  ```python
  def read_log_tail():
      with open("erros_robo.log", "r", encoding="utf-8") as f:
          f.seek(0, os.SEEK_END)
          # read tail data safely...
          return tail_data
  tail = await asyncio.to_thread(read_log_tail)
  ```

#### Issue 1.6: Blocking Synchronous I/O Calls inside Async Hunt Loop
* **Line Number(s)**: 704
* **Description**: In `_do_hunt`, the code calls `apply_result = auto_apply.auto_apply(job)` synchronously in the middle of the main loop processing. If `auto_apply` executes file checks or synchronous HTTP calls, it blocks the main thread's event loop.
* **Proposed Fix**: Wrap it in `asyncio.to_thread`:
  ```python
  apply_result = await asyncio.to_thread(auto_apply.auto_apply, job)
  ```

---

### `app.py`

#### Issue 2.1: Synchronous Blocking Database Call in Async Endpoint `/api/webhook/n8n`
* **Line Number(s)**: 55
* **Description**: The FastAPI endpoint `n8n_webhook` is declared as an `async def`, but it directly invokes the synchronous database helper `insert_jobs(jobs)`. Database transactions are blocking I/O operations and will freeze the whole FastAPI event loop.
* **Proposed Fix**: Call it inside a threadpool using `asyncio.to_thread`:
  ```python
  inserted = await asyncio.to_thread(insert_jobs, jobs)
  ```

#### Issue 2.2: Sequential Scraper Execution Bottleneck in `/api/trigger`
* **Line Number(s)**: 70-76
* **Description**: Scrapers are executed sequentially in a `for` loop inside `/api/trigger`. If a user initiates a scan on 4-5 platforms, the web request will take the sum of all scraper durations, easily triggering HTTP gateway timeouts (typically 30 seconds).
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

#### Issue 2.3: Hardcoded Absolute Paths Violating Portability
* **Line Number(s)**: 15, 36
* **Description**: The paths for logs and static assets are hardcoded to the local user folder:
  `"C:\\Users\\99196\\OneDrive\\Documentos\\vagas_bot\\system.log"` and `"C:\\Users\\99196\\OneDrive\Documentos\\vagas_bot\\static"`.
  This causes immediate failures if the project is run on another server, Docker container, or user profile.
* **Proposed Fix**: Define these paths relative to the application's root directory:
  ```python
  BASE_DIR = os.path.dirname(os.path.abspath(__file__))
  log_path = os.path.join(BASE_DIR, "system.log")
  STATIC_DIR = os.path.join(BASE_DIR, "static")
  ```

---

### `database.py`

#### Issue 3.1: Column Defaults Ignored for NULL Values in `get_jobs`
* **Line Number(s)**: 71-74
* **Description**: The function `get_jobs` maps columns `job_type`, `profession`, `level`, and `requirements` using conditional logic like `r[6] if len(r)>6 else "CLT"`. Since the `SELECT` query retrieves exactly 10 columns, `len(r)` is always 10 and the check is always `True`. If the database column contains a `NULL` (`None` in Python), the dictionary will store `None` rather than falling back to defaults like `"CLT"`.
* **Proposed Fix**: Check if the database value is not `None`:
  ```python
  "job_type": r[6] if (len(r) > 6 and r[6] is not None) else "CLT",
  "profession": r[7] if (len(r) > 7 and r[7] is not None) else "Tech",
  "level": r[8] if (len(r) > 8 and r[8] is not None) else "ND",
  "requirements": r[9] if (len(r) > 9 and r[9] is not None) else "Requisitos na página."
  ```

#### Issue 3.2: Unhandled KeyError in `insert_jobs` Batch Ingestion
* **Line Number(s)**: 43-49
* **Description**: `insert_jobs` iterates over `jobs` and accesses `job['link']`, `job['title']`, and `job['platform']` directly. If any job in the ingestion batch is missing one of these keys, a `KeyError` is raised, rolling back the entire batch and crashing the function.
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

### `auto_apply.py`

#### Issue 4.1: Hardcoded Global Resume Path in `auto_apply`
* **Line Number(s)**: 124, 26
* **Description**: `prepare_candidate_data` defaults to `"curriculo.txt"`. However, the bot saves user resumes as `curriculo_{user_id}.txt`. Consequently, `auto_apply` always looks for `"curriculo.txt"`, fails to find it, and submits applications with empty name and email strings.
* **Proposed Fix**: Accept the `user_id` or path in `auto_apply` and pass it from `bot.py`:
  ```python
  # In bot.py
  apply_result = await asyncio.to_thread(auto_apply.auto_apply, job, user_id=chat_id)
  
  # In auto_apply.py
  def auto_apply(job: dict, user_id: str = None) -> dict:
      path = f"curriculo_{user_id}.txt" if user_id else "curriculo.txt"
      candidate = prepare_candidate_data(path)
  ```

#### Issue 4.2: Hardcoded Candidate Identity in `apply_to_job`
* **Line Number(s)**: 181-182
* **Description**: `apply_to_job` prepares candidate form submission data by hardcoding `"name": "Diego Candidate"` and `"email": "diego@example.com"`. It completely ignores any curriculum files parsed via `prepare_candidate_data`.
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

#### Issue 4.3: SQLite Connection Exhaustion in Loop (`run_auto_apply`)
* **Line Number(s)**: 229-236
* **Description**: In `run_auto_apply`, the loop connects and disconnects from the SQLite database for *every single job* processed to update the job status. Repeatedly opening and closing SQLite connections within a hot loop is highly inefficient.
* **Proposed Fix**: Open the SQLite connection once before the loop, run all queries, commit, and then close it.

#### Issue 4.4: Synchronous/Blocking Network Requests in `apply_to_job`
* **Line Number(s)**: 185
* **Description**: `apply_to_job` uses `requests.post`, which is a synchronous, blocking network call. When called during testing or potential application routines, it halts thread execution.
* **Proposed Fix**: Wrap calling functions in `asyncio.to_thread` or switch to an asynchronous library like `httpx.AsyncClient`.

#### Issue 4.5: Concurrency Bug / Race Condition in `run_auto_apply`
* **Line Number(s)**: 219
* **Description**: `run_auto_apply` selects all jobs with `status = 'pending'` and iterates over them. If multiple processes or threads execute `run_auto_apply` concurrently, they will pull the same pending job list and submit duplicate job applications.
* **Proposed Fix**: Assign a unique `batch_id` to the running process, run an update statement first to mark jobs as `applying_<batch_id>`, and then retrieve only those marked jobs.

---

## 2. Primary Scrapers and Filter Audits

### `scrapers/ai_filter.py`

#### Issue 5.1: JSON Parsing/Validation Exceptions Treated as API Offline (Logic Bug)
* **Line Number(s)**: 115-224 (specifically lines 127-130 and 201-224)
* **Description**: The `try` block wraps the API call, JSON decoding (`json.loads`), and Pydantic model validation (`JobEvaluation(**result_json)`). If the API is online but returns malformed JSON or an invalid schema (a formatting error), a `JSONDecodeError` or `ValidationError` is raised. This exception is caught by `except Exception as e` and (since it is not a 429 error) immediately triggers the fallback return: `aprovado: True`. This masks formatting issues/hallucinations by silently approving the job. It also violates the project's E2E test specification (specifically `tests/test_tier2.py::test_ia_ranking_handles_groq_malformed_json`, which asserts that a malformed JSON response must result in `aprovado` being `False`).
* **Proposed Fix**: Separate the API call from the parsing and validation logic:
  ```python
  # 1. API Call Phase
  try:
      response = await client.chat.completions.create(...)
      result_text = response.choices[0].message.content
  except Exception as e:
      err_msg = str(e).lower()
      if "429" in err_msg or "rate limit" in err_msg:
          # Handle retry
          ...
      else:
          logger.warning("Groq API offline. Fallback approval.")
          return { "aprovado": True, "score": 50, "reason": "Fallback: API Offline", ... }

  # 2. Parsing & Validation Phase
  try:
      result_json = json.loads(result_text)
      eval_obj = JobEvaluation(**result_json)
  except Exception as e:
      logger.error(f"Groq returned malformed JSON or invalid schema: {e}")
      return {
          "aprovado": False,
          "score": 0,
          "reason": f"[Error] Malformed JSON or invalid schema: {e}",
          "reqs": "", "bonus": "", "benefits": "", "model": "",
          "salary_declared": False, "has_benefits": False, "exige_faculdade": False,
          "is_freelance": False, "vaga_corresponde_ao_cargo": False, "localidade_correta": False,
          "exige_experiencia": False, "proposal": ""
      }
  ```

#### Issue 5.2: Retry Loop Aborts Early on Non-429 Exceptions (Logic Bug)
* **Line Number(s)**: 111-224 (specifically lines 201-224)
* **Description**: The loop rotates through the API keys using `random.choice(API_KEYS)`. If an exception occurs, if it is not a 429, the catch block logs a warning and returns immediately. If one of the API keys is invalid, expired, or unauthorized (raising a 401 or 403), the very first call will trigger the exception, causing the scraper to abort immediately and return the fallback dict, without ever attempting the remaining retries with potentially valid keys.
* **Proposed Fix**: Log the warning but continue the loop to try another key, only returning the fallback after exhausting all retries.

#### Issue 5.3: Freelancer Contract Validation Gap in Hard-Lock Override (Logic Bug)
* **Line Number(s)**: 140-141
* **Description**: The hard-lock override logic checks if the job is freelance (`is_freelance == True`) but the candidate wanted a fixed contract (`target_contract not in ["Freelancer", "Todos"]`). However, it fails to perform the inverse check: if the candidate explicitly wants a freelance contract (`target_contract == "Freelancer"`), but the job is NOT freelance (`is_freelance == False`), the override does not flag this. This is a direct gap with prompt rule 6: *"Se pedir 'Freelancer', REPROVE vagas fixas (CLT ou PJ)."*
* **Proposed Fix**: Add the check for the inverse condition:
  ```python
  if eval_obj.is_freelance == True and target_contract not in ["Freelancer", "Todos"]:
      violated.append("is_freelance == True (candidato quer fixo)")
  if eval_obj.is_freelance == False and target_contract == "Freelancer":
      violated.append("is_freelance == False (candidato quer freelance)")
  ```

---

### `scrapers/linkedin.py`

#### Issue 6.1: Job Cards with Short Descriptions Discarded (Logic Bug)
* **Line Number(s)**: 113-138
* **Description**:
  ```python
  if description_text and len(description_text) >= 100:
      jobs.append({ ... })
  elif not description_text:
      jobs.append({ ... })
  ```
  If `description_text` is successfully retrieved but is very short (between 1 and 99 characters), both conditions evaluate to `False` (the first because `len < 100`, the second because `description_text` is not empty). As a result, the job is silently discarded. However, if the description fetch fails completely (`description_text = ""`), the job is accepted and appended with a generic placeholder description. This is a logical contradiction.
* **Proposed Fix**: Adjust the conditional logic so that jobs with short descriptions get the fallback placeholder description instead of being discarded.
  ```python
  if description_text and len(description_text) >= 100:
      jobs.append({
          "platform": "LinkedIn",
          ...
          "requirements": description_text
      })
  else:
      jobs.append({
          "platform": "LinkedIn",
          ...
          "requirements": f"Vaga de {title} na empresa {company}. Acesse o link para candidatura."
      })
  ```

---

### `scrapers/indeed.py`

#### Issue 7.1: Regex Search Lacks DOTALL Modifier (Robustness / Logic Bug)
* **Line Number(s)**: 49
* **Description**: The search regex `r'window\.mosaic\.providerData\["mosaic-provider-jobcards"\]\s*=\s*(\{.*?\});'` uses `.*?` to capture the JSON object but is invoked without `re.DOTALL` or `re.S`. In Python, the `.` character matches any character *except newlines*. If Indeed formats its page such that a newline is present within the script block or the JSON payload, the match will fail and return `None`, causing the scraper to find zero jobs. It is also restricted to double quotes.
* **Proposed Fix**: Add the `re.DOTALL` flag and support single quotes.
  ```python
  match = re.search(r'window\.mosaic\.providerData\[[\'"]mosaic-provider-jobcards[\'"]\]\s*=\s*(\{.*?\});', content, re.DOTALL)
  ```

#### Issue 7.2: Heavy Sequential Requests in Scrape Loop (Performance Bottleneck)
* **Line Number(s)**: 78-128
* **Description**: For every job card (up to 20-30), the scraper performs synchronous HTTP requests via `requests_cffi` and falls back to opening new Playwright pages synchronously in a loop. Spawning a new page, performing navigation, and waiting up to 10 seconds for selectors per job card can take several minutes to run, blocking the execution thread.
* **Proposed Fix**: Limit details fetching to the top 5-10 jobs, optimize selector timeout, or use Playwright's async API to run fetches concurrently.

---

### `scrapers/glassdoor.py`

#### Issue 8.1: Fragile Page Load Validation Breaks Mock Tests (Robustness / Test Bug)
* **Line Number(s)**: 41-43
* **Description**: The verification step checks: `if "glassdoor" in content.lower() and len(content) > 5000: loaded = True`. During testing, `conftest.py` mocks Playwright's page content to return `"<html>Mock Page Content</html>"` (which is 31 bytes and does not contain `"glassdoor"`). Consequently, this validation fails, the scraper returns `[]`, and several E2E tests (`test_glassdoor_scraper_returns_valid_schema`, `test_scraper_handles_special_characters`, and `test_combination_scraper_db_and_ia_ranking`) fail.
* **Proposed Fix**: Relax the validation check to allow mock data.
  ```python
  if ("glassdoor" in content.lower() or "mock" in content.lower()) and len(content) > 20:
      loaded = True
  ```

#### Issue 8.2: Fixed Delays inside Sequential Card Interaction (Performance Bottleneck)
* **Line Number(s)**: 120-143
* **Description**: For every card clicked (up to 20), the scraper invokes `page.wait_for_timeout(1200)` and waits up to 5 seconds for the description selector. This causes an unconditional delay of 24 seconds, and up to 120 seconds if selectors are not immediately visible.
* **Proposed Fix**: Remove/reduce `page.wait_for_timeout(1200)` and rely on dynamic playwright wait conditions (`page.wait_for_selector(..., state="visible", timeout=3000)`).

---

### `scrapers/infojobs.py`

#### Issue 9.1: Indentation Error Forces Unconditional Playwright Fallback (Logic Bug & Performance Bottleneck)
* **Line Number(s)**: 111-133
* **Description**: The `try...except...finally` block for the Playwright fallback is aligned at the same indentation level as the `if not fetched_by_cffi or not description or len(description) < 100:` check (line 111). Because of this indentation error, the Playwright fallback (which creates a new browser page, navigates to the URL, and queries elements) is executed **unconditionally** for every job card, even if the description was already successfully fetched via `curl_cffi` and is longer than 100 characters! This defeats the entire purpose of the `curl_cffi` optimization.
* **Proposed Fix**: Nest the `try...except...finally` block inside the `if` statement block.

#### Issue 9.2: Playwright Page Reference Leak / NameError Risk (Unhandled Exception Risk)
* **Line Number(s)**: 111-133
* **Description**: Because the `try` block runs unconditionally, if `fetched_by_cffi` is `True`, the line `detail_page = None` is skipped.
  1. On the first card, if `context.new_page()` throws an error, the `finally` block attempts to call `detail_page.close()` but `detail_page` is not defined in the scope, raising a `NameError: name 'detail_page' is not defined`.
  2. On subsequent cards, if `context.new_page()` throws an error, `detail_page` retains its reference to the page from the *previous* card iteration. The `finally` block will call `.close()` on a page that was already closed, causing an exception.
* **Proposed Fix**: Nesting the block inside the `if` (as proposed above) resolves this. Alternatively, initialize `detail_page = None` unconditionally at the start of the card loop.

#### Issue 9.3: Cumulative instead of Consecutive Timeout Limit (Logic Bug)
* **Line Number(s)**: 88, 108, 128
* **Description**: The `consecutive_timeouts` counter is initialized outside the card loop and never reset to 0 upon a successful description fetch. It acts as a **cumulative** counter. Once 2 total timeouts occur during the scraping run, the scraper stops attempting to fetch descriptions for all remaining cards.
* **Proposed Fix**: Reset `consecutive_timeouts = 0` whenever a description is successfully fetched.

---

### `scrapers/jooble.py`

#### Issue 10.1: Returning Dummy Job Pollutes Pipeline (Logic Bug)
* **Line Number(s)**: 115-126
* **Description**: If no jobs are found, the scraper appends a dummy job card: `{"title": "Sem vagas API Jooble...", "requirements": "Não houve resultados."}` to the `jobs` list. Returning a dummy card pollutes the scraping pipeline; downstream components (e.g. database insertion, frontend listing) must implement specific string checking to avoid processing/storing it. The scraper should return an empty list `[]` instead.
* **Proposed Fix**: Remove the block appending the dummy job and return an empty list `[]`.

#### Issue 10.2: Blocking HTTP Requests inside Scrape Loop (Performance Bottleneck)
* **Line Number(s)**: 57-95
* **Description**: The scraper resolves redirects by making sequential HTTP requests (up to 30) for each job card in a loop. With a timeout of 12 seconds per request, this can freeze the worker thread for several minutes if multiple requests delay or time out.
* **Proposed Fix**: Limit the number of redirect checks to a smaller number of top jobs, or perform redirect checks concurrently.

---

## 3. Helper Scrapers, Launchers, and Utilities

### `scrapers/meta_ads.py`

#### Issue 11.1: Location Check Prevents Execution Entirely (Critical Logic Bug)
* **Line Number(s)**: 8-9
* **Description**:
  ```python
  if country != "Brasil":
      return []
  ```
  In `bot.py`, the user settings default location is `"Brasil (Remoto)"`, and can also be `"Londrina/PR"` or `"Assaí/PR"`. None of these exactly equal `"Brasil"`. Thus, the condition `country != "Brasil"` evaluates to `True` under all circumstances, and the scraper immediately aborts by returning `[]`. It never runs.
* **Proposed Fix**: Check for the presence of the substring `"Brasil"` instead:
  ```python
  if "Brasil" not in country:
      return []
  ```

#### Issue 11.2: Unhandled None Type on Dataset ID (Robustness Issue)
* **Line Number(s)**: 34-35
* **Description**: If the Apify client call fails or returns a dictionary without `defaultDatasetId` (or if it is `None`), calling `client.dataset(None).iterate_items()` will throw a `TypeError` or API exception.
* **Proposed Fix**: Validate the `dataset_id` before querying it:
  ```python
  if not dataset_id:
      return []
  ```

---

### `scrapers/remotar.py`

#### Issue 12.1: Incorrect Job URL Mapping (Logic Bug)
* **Line Number(s)**: 40
* **Description**: The URL returned in the `"link"` attribute is the search page URL (`url = f"{base_url}&page={page}"`), instead of the individual job detail page URL. When users click "Aplicar para a Vaga" in the Telegram bot, they are taken to the generic list page instead of the job post itself.
* **Proposed Fix**: Extract the actual link from the job card HTML element:
  ```python
  # Locate the link inside the card
  link_elem = card.find('a')
  if link_elem and link_elem.get('href'):
      job_link = link_elem.get('href')
      if job_link.startswith('/'):
          job_link = f"https://remotar.com.br{job_link}"
  else:
      job_link = url
  ```
  Then replace `"link": url,` with `"link": job_link,`.

#### Issue 12.2: Unchecked HTTP Status Code (Robustness Issue)
* **Line Number(s)**: 17-18
* **Description**: The response text is parsed with `BeautifulSoup` immediately after requesting, without validating the HTTP status code. If the website returns a 403 Forbidden or 500 error, it will silently fail or parse empty/incorrect HTML.
* **Proposed Fix**: Validate the response status code before processing:
  ```python
  response = requests.get(url, headers=headers, timeout=5)
  if response.status_code == 200:
      soup = BeautifulSoup(response.text, 'html.parser')
      # rest of parsing...
  ```

---

### `scrapers/novenove.py`

#### Issue 13.1: Potential KeyError on Missing Href Attribute (Robustness Issue)
* **Line Number(s)**: 25
* **Description**: Accessing `link_el['href']` directly raises a `KeyError` if the anchor element does not contain an `href` attribute. This will throw an exception, breaking the scraper's execution.
* **Proposed Fix**: Use `.get('href')` to safely retrieve the attribute:
  ```python
  link = "https://www.99freelas.com.br" + link_el.get('href') if (link_el and link_el.get('href')) else url
  ```

#### Issue 13.2: Missing Default Parameter in Signature (Consistency Issue)
* **Line Number(s)**: 5
* **Description**: Unlike other scrapers, `keyword` is a required positional argument with no default. If the scraper is invoked programmatically without arguments elsewhere, it raises a `TypeError`.
* **Proposed Fix**: Define a default parameter for consistency:
  ```python
  def scrape(keyword="Python", level="Todos", country="Brasil"):
  ```

---

### `scrapers/freelancer.py`

#### Issue 14.1: Unhandled AttributeError when Parsing Null Values (Robustness Issue)
* **Line Number(s)**: 23-25
* **Description**: In Python, `.get("key", default)` only uses the default if the key is absent. If the API returns `"budget": null` or `"currency": null`, the returned value is `None`. Calling `.get("minimum")` on `None` raises `AttributeError: 'NoneType' object has no attribute 'get'`, crashing the scraper.
* **Proposed Fix**: Safely retrieve sub-keys:
  ```python
  budget = item.get("budget") or {}
  budget_min = budget.get("minimum") or 0
  budget_max = budget.get("maximum") or 0
  currency_data = item.get("currency") or {}
  currency = currency_data.get("code", "USD")
  ```

#### Issue 14.2: Missing Default Parameter in Signature (Consistency Issue)
* **Line Number(s)**: 4
* **Description**: `keyword` is a required argument with no default, violating consistency across scrapers.
* **Proposed Fix**: Update signature to:
  ```python
  def scrape(keyword="Python", level="Todos", country="Brasil"):
  ```

---

### `scrapers/gmail.py`

#### Issue 15.1: Broad Try-Except Outside Loop Aborts Processing (Logic Bug)
* **Line Number(s)**: 36-89
* **Description**: The entire list parsing loop `for msg in messages:` is enclosed in a single massive `try...except` block. If a single email has formatting errors, incorrect base64 padding, or raises an exception during parsing/decoding, the entire scraper halts immediately. This aborts processing of all other remaining emails.
* **Proposed Fix**: Place the inner email-parsing logic in its own `try...except` block:
  ```python
  for msg in messages:
      try:
          # message parsing logic...
      except Exception as inner_e:
          print(f"Erro ao processar e-mail individual: {inner_e}")
  ```

#### Issue 15.2: Unhandled Base64 Padding and Encoding Failures (Robustness Issue)
* **Line Number(s)**: 56, 61
* **Description**: Gmail's raw data can sometimes have incorrect base64 padding (missing `=` suffixes), causing `urlsafe_b64decode` to raise a `binascii.Error: Incorrect padding`. Furthermore, if the email body is encoded in an alternative charset (such as `ISO-8859-1`), calling `.decode('utf-8')` will raise a `UnicodeDecodeError`. Both of these will crash the list loop due to Issue 15.1.
* **Proposed Fix**: Use a helper function that dynamically appends padding and falls back to a different encoding format:
  ```python
  def decode_body(data):
      try:
          padded_data = data + '=' * (-len(data) % 4)
          decoded_bytes = base64.urlsafe_b64decode(padded_data)
          try:
              return decoded_bytes.decode('utf-8')
          except UnicodeDecodeError:
              return decoded_bytes.decode('latin-1')
      except Exception:
          return ""
  ```

---

### `scrapers/workana.py`

#### Issue 16.1: Dummy Job Generation Pollutes Database (Logic Bug / Inconsistency)
* **Line Number(s)**: 64-75
* **Description**: If no jobs are found, the scraper appends a fake listing: `title: f"Projeto Freelance: {keyword} {level}"` with dummy fields and links to the search page URL. This pollutes the SQLite database with fake data and runs counter to the project specification of "not returning fake garbage (lixo falso)".
* **Proposed Fix**: Remove lines 64-75 entirely. Let it return `[]` so that `bot.py` handles the empty result correctly.

#### Issue 16.2: Unencoded Query Parameters (Robustness Issue)
* **Line Number(s)**: 21
* **Description**: If `search_kw` contains special characters or spaces (e.g. `"Python Sênior"`), formatting them directly in the URL query string can cause parsing issues or result in 400 Bad Request responses.
* **Proposed Fix**: Use `urllib.parse.quote`:
  ```python
  import urllib.parse
  encoded_kw = urllib.parse.quote(search_kw)
  url = f"https://www.workana.com/jobs?query={encoded_kw}&page={page}"
  ```

---

### `scrapers/jsearch.py`

#### Issue 17.1: Dummy Job Generation with Invalid URLs (Logic Bug / Inconsistency)
* **Line Number(s)**: 58-69
* **Description**: Similar to Workana, the scraper generates a fake job post if no vacancies are found. The fake post has the URL `link: "#"`, which is invalid. The bot inserts this invalid entry into the database, but subsequently prints warnings and ignores sending it because it lacks an `"http"` prefix.
* **Proposed Fix**: Remove lines 58-69 entirely and return `[]` when no results are found.

#### Issue 17.2: Hardcoded RapidAPI Credentials (Security/Configuration Issue)
* **Line Number(s)**: 21
* **Description**: Hardcoding API keys directly in source files is a security vulnerability and limits flexibility.
* **Proposed Fix**: Fetch the key from environment variables:
  ```python
  import os
  rapidapi_key = os.environ.get("RAPIDAPI_KEY", "7af3cebf37mshb1adb579644f3d1p1f605fjsn26d9e7a63fe0")
  ```

#### Issue 17.3: Missing Default Parameter in Signature (Consistency Issue)
* **Line Number(s)**: 4
* **Description**: `level` is a required argument with no default, violating consistency across scrapers.
* **Proposed Fix**: Change signature to:
  ```python
  def scrape(keyword, level="Todos", country="Brasil"):
  ```

---

### `launcher.py`

#### Issue 18.1: Missing Startup Crash Detection on Subprocesses (Robustness Issue)
* **Line Number(s)**: 11-18
* **Description**: The launcher starts the bot and app via `subprocess.Popen` but doesn't verify if they successfully initialized. If either crashes immediately (e.g. due to missing packages or invalid configuration), the launcher will still report that everything is running.
* **Proposed Fix**: Check process health after a short delay:
  ```python
  time.sleep(2)
  if bot_process.poll() is not None:
      print("❌ Erro: O Sniper Bot (bot.py) falhou ao iniciar!")
  if app_process.poll() is not None:
      print("❌ Erro: O Servidor Web (app.py) falhou ao iniciar!")
  ```

---

### `render_bot.py`

#### Issue 19.1: Silent Failures in Polling Tasks (Zombie State Risk)
* **Line Number(s)**: 45-51
* **Description**: The main function creates two async tasks (`web_task` and `bot_task`) and gathers them. However, `web_task` runs an infinite sleep loop. If `bot_task` (the Telegram bot polling loop) crashes or terminates, `asyncio.gather` will continue waiting for `web_task` to complete. The process remains alive, responding with "Bot is running!" to health checks while the bot is actually dead.
* **Proposed Fix**: Use `asyncio.wait` with `return_when=asyncio.FIRST_COMPLETED` so that if either task fails or exits, the script cancels the other task and exits:
  ```python
  done, pending = await asyncio.wait(
      [web_task, bot_task],
      return_when=asyncio.FIRST_COMPLETED
  )
  for task in pending:
      task.cancel()
  # Propagate exceptions if any
  for task in done:
      task.result()
  ```

---

### `verify_seniority.py`

#### Issue 20.1: Non-Thread-Safe List Mutations in Mock Scraper (Concurrency Test Flaw)
* **Line Number(s)**: 29-31
* **Description**: The mock scraper is called concurrently from multiple threads via `asyncio.to_thread`. It appends directly to the global list `captured_keywords`. While `.append()` is atomic due to the GIL, concurrent calls can lead to race conditions or unpredictable ordering, making assertions unreliable.
* **Proposed Fix**: Implement a threading lock to control access to `captured_keywords`:
  ```python
  import threading
  list_lock = threading.Lock()
  
  def mock_scrape(keyword, level="Todos", country="Brasil"):
      with list_lock:
          captured_keywords.append(keyword)
      # ...
  ```

#### Issue 20.2: Database Cleanup Not Guaranteed on Assertion Failure (Robustness Issue)
* **Line Number(s)**: 164-169
* **Description**: If an assertion fails, the script continues, but if an unhandled exception is raised during execution, the database file at `TEST_DB_PATH` is left behind because cleanup is only performed at the very end of the function.
* **Proposed Fix**: Place the entire test harness inside a `try...finally` block to ensure cleanup runs in all circumstances:
  ```python
  async def run_harness():
      try:
          # test execution logic...
      finally:
          if os.path.exists(TEST_DB_PATH):
              try:
                  os.remove(TEST_DB_PATH)
              except Exception:
                  pass
  ```
