## 2026-07-21T20:31:54Z
You are Worker 1 (State Search Implementation & Verification Worker).
Your working directory is: `C:/Users/99196/OneDrive/Documentos/vagas_bot/.agents/teamwork_preview_worker_state_fix`

Task Summary:
Implement Requirement 1 (R1) and Requirement 2 (R2) for Job Search by State (UF mapping & location parameter passing) in `vagas_bot`.

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A Forensic Auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Detailed Instructions:

1. **R1: Backend Location Parameter Passing (`app.py`)**:
   - Edit `app.py` in function `run_hunt_background` (around line 207):
     Extract `location = data.get("location", "Todos")`.
     Inspect `module.scrape` parameters via `inspect.signature(module.scrape)` or construct `kwargs = {"keyword": keyword, "level": level, "max_pages": 10}`.
     If `"location"` is in `sig.parameters` or `sig.parameters` has `**kwargs`, pass `kwargs["location"] = location`.
     Invoke `module.scrape(**kwargs)` (async or via `asyncio.to_thread`).
   - Check scrapers in `scrapers/*.py` (e.g. `gupy.py`, `linkedin.py`, `infojobs.py`, `glassdoor.py`, `indeed.py`, `catho.py`, `workana.py`, `remotar.py`, etc.) and ensure `scrape` function accepts `location: str = "Todos"` or `**kwargs` and passes location to the search queries where applicable.

2. **R2: Frontend UF Mapping & 100% Remote Preservation (`static/index.html`)**:
   - In `static/index.html`:
     - Verify and update `<select id="state-select">` to contain all 27 Brazilian State UF options (`AC`, `AL`, `AP`, `AM`, `BA`, `CE`, `DF`, `ES`, `GO`, `MA`, `MT`, `MS`, `MG`, `PA`, `PB`, `PR`, `PE`, `PI`, `RJ`, `RN`, `RS`, `RO`, `RR`, `SC`, `SP`, `SE`, `TO`) plus `Exterior` and `Todos`.
     - Add `UF_MAP` dictionary in JavaScript mapping all 27 UFs to full state names (e.g., `SP` -> `São Paulo`, `RJ` -> `Rio de Janeiro`, `MG` -> `Minas Gerais`, `PR` -> `Paraná`, `RS` -> `Rio Grande do Sul`, `SC` -> `Santa Catarina`, `BA` -> `Bahia`, etc.) and main cities.
     - Implement state matching helper `isJobInState(job, ufCode)` with word boundary regex `\b${uf}\b` for UF codes to prevent false positive matches on words like `especialista` or `responsavel`.
     - In `filterData()`, update `matchLoc` logic:
       If job is 100% remote (`isRemote`), `matchLoc = true;` unconditionally (100% remote jobs MUST remain visible for any selected state).
       Otherwise, if a state/UF is selected, `matchLoc = isJobInState(job, locQuery)`.
     - Ensure `#state-select` dropdown change event sets `#loc-input` value and triggers `filterData()`.

3. **Test Suite Implementation & Verification (`test_location_state.py`)**:
   - Create `test_location_state.py` at project root `C:/Users/99196/OneDrive/Documentos/vagas_bot/test_location_state.py` (using the test suite structure designed by Explorer 3).
   - Run the test suite using `python test_location_state.py` via `run_command`.
   - Verify that 100% of the tests pass with exit code 0.

4. Document all file changes, build/test execution output, and test pass confirmation in `C:/Users/99196/OneDrive/Documentos/vagas_bot/.agents/teamwork_preview_worker_state_fix/handoff.md`.
Send a completion message to parent once done.
