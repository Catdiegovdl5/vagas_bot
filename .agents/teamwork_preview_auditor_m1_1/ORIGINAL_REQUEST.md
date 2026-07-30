## 2026-07-21T20:50:32Z
Task: Perform forensic integrity verification on R1 (app.py location parameter passing) and R2 (static/index.html UF mapping & remote job retention).
1. Inspect app.py, bot.py, scrapers/, static/index.html, and test_location_state.py.
2. Check for integrity violations:
   - Hardcoded test returns, fake/dummy scraper implementations, or cheated test results.
   - Bypasses or hardcoded conditionals in location matching logic.
   - Misleading verification logs or fabricated test outputs.
3. Confirm that the implementation is 100% genuine and compliant with R1 and R2.
4. Write your audit report to C:/Users/99196/OneDrive/Documentos/vagas_bot/.agents/teamwork_preview_auditor_m1_1/audit_report.md and handoff to C:/Users/99196/OneDrive/Documentos/vagas_bot/.agents/teamwork_preview_auditor_m1_1/handoff.md.
5. Send a message to parent (ID: cdc1f171-557a-4aaf-88f1-3ed20d724ae9) stating your verdict: CLEAN or INTEGRITY VIOLATION.
