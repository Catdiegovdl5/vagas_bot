## 2026-07-21T20:53:47Z
You are Worker 2 (Remediation Specialist).
Working directory: C:/Users/99196/OneDrive/Documentos/vagas_bot/.agents/teamwork_preview_worker_m2_1
Project directory: C:/Users/99196/OneDrive/Documentos/vagas_bot

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A Forensic Auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Task — Remediate issues identified in Audit & Code Review:

1. Fix scrapers/linkedin.py:
   - Line 129: Prevent `AttributeError: 'NoneType' object has no attribute 'lower'` when `country` or `location` is None.
   - Use safe string handling: `c_str = (country or "").lower()` and `l_str = (location or "").lower()`.
   - Ensure `loc = location or country or ""` is passed and formatted into LinkedIn location parameter (`&f_WT=2` for remote, or `location` query string).

2. Fix scrapers/*.py:
   - Review all scrapers (`gupy.py`, `catho.py`, `remotar.py`, `workana.py`, `infojobs.py`, `coodesh.py`, `vagas_com.py`, `glassdoor.py`, `meta_ads.py`, `geekhunter.py`, `programathor.py`, `gmail.py`, etc.).
   - Ensure all scrapers accept `location: str = ""` and `country: str = ""` without raising `TypeError` or `AttributeError` if passed `None`.
   - Ensure `loc = location or country or ""` is safely extracted and incorporated into search query parameters or API calls where applicable.

3. Fix test_location_state.py and static/index.html:
   - In static/index.html: Define `const UF_MAP = { ... };` directly and assign `const UF_MAPPING = UF_MAP;` so both variable names reference the 27 UF dictionary object.
   - In test_location_state.py: Ensure regex `re.search(r'const (?:UF_MAP|UF_MAPPING)\s*=\s*\{([^}]+)\}', html_content, re.DOTALL)` matches the JS dictionary cleanly.

4. Execute Tests:
   - Run `python test_location_state.py` and verify 100% of tests pass with exit code 0.
   - Run `python test_location_uf.py` and verify all 21 tests pass with exit code 0.
   - Run `python run_tests.py` or `pytest` and verify exit code 0 across the entire test suite.

5. Deliverables:
   - Write your implementation report to C:/Users/99196/OneDrive/Documentos/vagas_bot/.agents/teamwork_preview_worker_m2_1/changes.md.
   - Write your handoff report to C:/Users/99196/OneDrive/Documentos/vagas_bot/.agents/teamwork_preview_worker_m2_1/handoff.md with exact test execution outputs.
   - Send a message to parent (ID: cdc1f171-557a-4aaf-88f1-3ed20d724ae9) summarizing your fixes and test results.
