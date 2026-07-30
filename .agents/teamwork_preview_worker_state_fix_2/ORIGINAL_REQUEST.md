## 2026-07-21T20:48:40Z
<USER_REQUEST>
You are a teamwork_preview_worker agent.
Your working directory is: C:/Users/99196/OneDrive/Documentos/vagas_bot/.agents/teamwork_preview_worker_state_fix_2
Project directory: C:/Users/99196/OneDrive/Documentos/vagas_bot

TASK:
Fix the 1 minor test mismatch in test_location_state.py line 125:
`test_location_state.py` expects `const UF_MAP` in JS, but `static/index.html` defines `const UF_MAPPING`.

Instructions:
1. View `static/index.html` and `test_location_state.py` to see the definitions around line 125.
2. Fix this by defining `const UF_MAP = UF_MAPPING;` (alias) in `static/index.html` (or updating `test_location_state.py` line 125 regex if appropriate) so `python test_location_state.py` passes with 0 failures!
3. Run `python test_location_state.py` and `python test_location_uf.py` using `run_command` in `C:/Users/99196/OneDrive/Documentos/vagas_bot`.
4. Verify 100% PASS with 0 failures or errors.

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A Forensic Auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Write a handoff report in your working directory C:/Users/99196/OneDrive/Documentos/vagas_bot/.agents/teamwork_preview_worker_state_fix_2/handoff.md and report back with exact test results.
</USER_REQUEST>
