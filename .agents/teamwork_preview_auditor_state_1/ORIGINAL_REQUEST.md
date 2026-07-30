## 2026-07-21T17:50:05-03:00
You are the Forensic Auditor (retried). Perform an independent integrity audit of all modified files (`app.py`, `static/index.html`, `scrapers/*.py`, `test_location_state.py`).

Your working directory is: `C:/Users/99196/OneDrive/Documentos/vagas_bot/.agents/teamwork_preview_auditor_state_1`

Audit Protocol:
1. Code Inspection: Verify that all location parameter passing logic and UF state mapping logic are genuinely implemented. Confirm there are NO hardcoded test responses, dummy returns, facade functions, or mock bypasses in production code (`app.py`, `bot.py`, `static/index.html`, `scrapers/*.py`).
2. Static Analysis: Inspect `test_location_state.py` and `test_location_uf.py` to confirm tests genuinely execute code paths and check return values.
3. Execution Validation: Execute `python test_location_state.py` and `python test_location_uf.py` directly to confirm real execution and zero failures.
4. Render Verdict: Issue explicit verdict `CLEAN` or `INTEGRITY VIOLATION`.

Write your full audit report to `C:/Users/99196/OneDrive/Documentos/vagas_bot/.agents/teamwork_preview_auditor_state_1/audit.md` and `handoff.md`.
Send a message with your audit verdict once complete.
