## 2026-07-21T17:54:49-03:00
You are the Forensic Integrity Auditor. Perform a final, independent forensic audit of all modified files (`app.py`, `static/index.html`, `scrapers/*.py`, `test_location_state.py`, `test_location_uf.py`).

Your working directory is: `C:/Users/99196/OneDrive/Documentos/vagas_bot/.agents/teamwork_preview_auditor_state_final`

Audit Protocol:
1. Code Inspection: Verify that location parameter passing logic (`app.py`, `scrapers/*.py`) and 27 UF state mapping logic (`static/index.html`) are authentically implemented with genuine logic. Confirm NO hardcoded test results, dummy returns, or mock bypasses exist in production code.
2. Static Analysis: Verify `test_location_state.py` and `test_location_uf.py` genuinely test state location filtering and parameter repass.
3. Execution Validation: Execute `python test_location_state.py` and `python test_location_uf.py` using `run_command` in `C:/Users/99196/OneDrive/Documentos/vagas_bot` to confirm 100% real execution and 0 test failures.
4. Render Verdict: Issue explicit verdict `CLEAN` or `INTEGRITY VIOLATION`.

Write your full audit report to `C:/Users/99196/OneDrive/Documentos/vagas_bot/.agents/teamwork_preview_auditor_state_final/audit.md` and `handoff.md`.
Send a message with your audit verdict once complete.
