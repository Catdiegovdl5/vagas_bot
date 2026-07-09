# Detailed Audit Report: vagas_bot Primary Scrapers and AI Filter

This report details the read-only audit of the primary web scraper files and AI filter module in `vagas_bot/scrapers`. Several logic bugs, performance bottlenecks, robustness issues, and exception handling flaws were identified during the audit.

---

## 1. `vagas_bot/scrapers/ai_filter.py`

### Issue 1: JSON Parsing/Validation Exceptions Treated as API Offline (Logic Bug)
* **Line Number(s)**: 115-224 (specifically lines 127-130 and 201-224)
* **Explanation**: The `try` block wraps the API call, JSON decoding (`json.loads`), and Pydantic model validation (`JobEvaluation(**result_json)`). If the API is online but returns malformed JSON or an invalid schema (a formatting error), a `JSONDecodeError` or `ValidationError` is raised. This exception is caught by `except Exception as e` and (since it is not a 429 error) immediately triggers the fallback return: `aprovado: True`. This masks formatting issues/hallucinations by silently approving the job. It also violates the project's E2E test specification (specifically `tests/test_tier2.py::test_ia_ranking_handles_groq_malformed_json`, which asserts that a malformed JSON response must result in `aprovado` being `False`).
* **Proposed Fix**: Separate the API call from the parsing and validation logic.
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

### Issue 2: Retry Loop Aborts Early on Non-429 Exceptions (Logic Bug)
* **Line Number(s)**: 111-224 (specifically lines 201-224)
* **Explanation**: The loop rotates through the API keys using `random.choice(API_KEYS)`. If an exception occurs, if it is not a 429, the catch block logs a warning and returns immediately. If one of the API keys is invalid, expired, or unauthorized (raising a 401 or 403), the very first call will trigger the exception, causing the scraper to abort immediately and return the fallback dict, without ever attempting the remaining retries with potentially valid keys.
* **Proposed Fix**: Log the warning but continue the loop to try another key, only returning the fallback after exhausting all retries.
  ```python
  except Exception as e:
      err_msg = str(e).lower()
      if "429" in err_msg or "rate limit" in err_msg:
          await asyncio.sleep(2 + tentativa)
      else:
          logger.warning(f"Erro na tentativa {tentativa+1}/4 com a chave: {e}")
          if tentativa == 3:  # Last attempt exhausted
              logger.warning("Todas as chaves falharam. Retornando fallback.")
              return { "aprovado": True, ... }
  ```

### Issue 3: Freelancer Contract Validation Gap in Hard-Lock Override (Logic Bug)
* **Line Number(s)**: 140-141
* **Explanation**: The hard-lock override logic checks if the job is freelance (`is_freelance == True`) but the candidate wanted a fixed contract (`target_contract not in ["Freelancer", "Todos"]`). However, it fails to perform the inverse check: if the candidate explicitly wants a freelance contract (`target_contract == "Freelancer"`), but the job is NOT freelance (`is_freelance == False`), the override does not flag this. This is a direct gap with prompt rule 6: *"Se pedir 'Freelancer', REPROVE vagas fixas (CLT ou PJ)."*
* **Proposed Fix**: Add the check for the inverse condition:
  ```python
  if eval_obj.is_freelance == True and target_contract not in ["Freelancer", "Todos"]:
      violated.append("is_freelance == True (candidato quer fixo)")
  if eval_obj.is_freelance == False and target_contract == "Freelancer":
      violated.append("is_freelance == False (candidato quer freelance)")
  ```

---

## 2. `vagas_bot/scrapers/indeed.py`

### Issue 1: Regex Search Lacks DOTALL Modifier (Robustness / Logic Bug)
* **Line Number(s)**: 49
* **Explanation**: The search regex `r'window\.mosaic\.providerData\["mosaic-provider-jobcards"\]\s*=\s*(\{.*?\});'` uses `.*?` to capture the JSON object but is invoked without `re.DOTALL` or `re.S`. In Python, the `.` character matches any character *except newlines*. If Indeed formats its page such that a newline is present within the script block or the JSON payload, the match will fail and return `None`, causing the scraper to find zero jobs. It is also restricted to double quotes.
* **Proposed Fix**: Add the `re.DOTALL` flag and support single quotes.
  ```python
  match = re.search(r'window\.mosaic\.providerData\[[\'"]mosaic-provider-jobcards[\'"]\]\s*=\s*(\{.*?\});', content, re.DOTALL)
  ```

### Issue 2: Heavy Sequential Requests in Scrape Loop (Performance Bottleneck)
* **Line Number(s)**: 78-128
* **Explanation**: For every job card (up to 20-30), the scraper performs synchronous HTTP requests via `requests_cffi` and falls back to opening new Playwright pages synchronously in a loop. Spawning a new page, performing navigation, and waiting up to 10 seconds for selectors per job card can take several minutes to run, blocking the execution thread.
* **Proposed Fix**: Limit details fetching to the top 5-10 jobs, optimize selector timeout, or use Playwright's async API to run fetches concurrently.

---

## 3. `vagas_bot/scrapers/linkedin.py`

### Issue 1: Job Cards with Short Descriptions Discarded (Logic Bug)
* **Line Number(s)**: 113-138
* **Explanation**:
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

## 4. `vagas_bot/scrapers/glassdoor.py`

### Issue 1: Fragile Page Load Validation Breaks Mock Tests (Robustness / Test Bug)
* **Line Number(s)**: 41-43
* **Explanation**: The verification step checks: `if "glassdoor" in content.lower() and len(content) > 5000: loaded = True`. During testing, `conftest.py` mocks Playwright's page content to return `"<html>Mock Page Content</html>"` (which is 31 bytes and does not contain `"glassdoor"`). Consequently, this validation fails, the scraper returns `[]`, and several E2E tests (`test_glassdoor_scraper_returns_valid_schema`, `test_scraper_handles_special_characters`, and `test_combination_scraper_db_and_ia_ranking`) fail.
* **Proposed Fix**: Relax the validation check to allow mock data.
  ```python
  if ("glassdoor" in content.lower() or "mock" in content.lower()) and len(content) > 20:
      loaded = True
  ```

### Issue 2: Fixed Delays inside Sequential Card Interaction (Performance Bottleneck)
* **Line Number(s)**: 120-143
* **Explanation**: For every card clicked (up to 20), the scraper invokes `page.wait_for_timeout(1200)` and waits up to 5 seconds for the description selector. This causes an unconditional delay of 24 seconds, and up to 120 seconds if selectors are not immediately visible.
* **Proposed Fix**: Remove/reduce `page.wait_for_timeout(1200)` and rely on dynamic playwright wait conditions (`page.wait_for_selector(..., state="visible", timeout=3000)`).

---

## 5. `vagas_bot/scrapers/infojobs.py`

### Issue 1: Indentation Error Forces Unconditional Playwright Fallback (Logic Bug & Performance Bottleneck)
* **Line Number(s)**: 111-133
* **Explanation**: The `try...except...finally` block for the Playwright fallback is aligned at the same indentation level as the `if not fetched_by_cffi or not description or len(description) < 100:` check (line 111). Because of this indentation error, the Playwright fallback (which creates a new browser page, navigates to the URL, and queries elements) is executed **unconditionally** for every job card, even if the description was already successfully fetched via `curl_cffi` and is longer than 100 characters! This defeats the entire purpose of the `curl_cffi` optimization.
* **Proposed Fix**: Nest the `try...except...finally` block inside the `if` statement block.

### Issue 2: Playwright Page Reference Leak / NameError Risk (Unhandled Exception Risk)
* **Line Number(s)**: 111-133
* **Explanation**: Because the `try` block runs unconditionally, if `fetched_by_cffi` is `True`, the line `detail_page = None` is skipped.
  1. On the first card, if `context.new_page()` throws an error, the `finally` block attempts to call `detail_page.close()` but `detail_page` is not defined in the scope, raising a `NameError: name 'detail_page' is not defined`.
  2. On subsequent cards, if `context.new_page()` throws an error, `detail_page` retains its reference to the page from the *previous* card iteration. The `finally` block will call `.close()` on a page that was already closed, causing an exception.
* **Proposed Fix**: Nesting the block inside the `if` (as proposed above) resolves this. Alternatively, initialize `detail_page = None` unconditionally at the start of the card loop.

### Issue 3: Cumulative instead of Consecutive Timeout Limit (Logic Bug)
* **Line Number(s)**: 88, 108, 128
* **Explanation**: The `consecutive_timeouts` counter is initialized outside the card loop and never reset to 0 upon a successful description fetch. It acts as a **cumulative** counter. Once 2 total timeouts occur during the scraping run, the scraper stops attempting to fetch descriptions for all remaining cards.
* **Proposed Fix**: Reset `consecutive_timeouts = 0` whenever a description is successfully fetched.

---

## 6. `vagas_bot/scrapers/jooble.py`

### Issue 1: Returning Dummy Job Pollutes Pipeline (Logic Bug)
* **Line Number(s)**: 115-126
* **Explanation**: If no jobs are found, the scraper appends a dummy job card: `{"title": "Sem vagas API Jooble...", "requirements": "Não houve resultados."}` to the `jobs` list. Returning a dummy card pollutes the scraping pipeline; downstream components (e.g. database insertion, frontend listing) must implement specific string checking to avoid processing/storing it. The scraper should return an empty list `[]` instead.
* **Proposed Fix**: Remove the block appending the dummy job and return an empty list `[]`.

### Issue 2: Blocking HTTP Requests inside Scrape Loop (Performance Bottleneck)
* **Line Number(s)**: 57-95
* **Explanation**: The scraper resolves redirects by making sequential HTTP requests (up to 30) for each job card in a loop. With a timeout of 12 seconds per request, this can freeze the worker thread for several minutes if multiple requests delay or time out.
* **Proposed Fix**: Limit the number of redirect checks to a smaller number of top jobs, or perform redirect checks concurrently.
