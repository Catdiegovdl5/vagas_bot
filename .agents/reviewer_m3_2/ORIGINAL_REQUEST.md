## 2026-07-29T11:02:29Z
You are Reviewer M3_2 (teamwork_preview_reviewer) for Milestone 3 (Final Integration Gate) of the Vagas Sniper Bot project.
Your working directory is: C:\Users\99196\OneDrive\Documentos\vagas_bot\.agents\reviewer_m3_2
Parent Orchestrator: 142d139e-4e7b-46c4-95f0-eaa412b7aeef

Scope of Review:
1. Examine Python files: `bot.py`, `app.py`, and `scrapers/*.py`.
   - Verify `SEARCH_MAPPING` macro-keywords for broad queries ("Indústria", "Logística", "Administrativo", "Vendas", "Dados", "Design").
   - Verify `CO_OCCURRENCE_RULES` in `bot.py` for local sub-profession filtering and title co-occurrences.
   - Verify `global_title_blacklist` exemptions for blue collar / industrial roles (e.g., "Operador", "Pintor", "Ajudante", "Mecânico", "Motorista", "Almoxarife").
   - Verify `classify_job_profession()` helper function and category/sub-profession matching logic.
   - Check `app.py` seed search keywords and background periodic hunt loop integrations.
2. Confirm Python syntax by inspecting/compiling code (`python -m py_compile bot.py app.py scrapers/*.py`).
3. Write your detailed review report to `C:\Users\99196\OneDrive\Documentos\vagas_bot\.agents\reviewer_m3_2\handoff.md`.
4. Include explicit VETO/APPROVE decision.
5. Send a completion message with summary to parent 142d139e-4e7b-46c4-95f0-eaa412b7aeef.
