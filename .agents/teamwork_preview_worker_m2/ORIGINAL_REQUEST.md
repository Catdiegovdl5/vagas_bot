## 2026-07-29T10:50:42Z
You are a Worker agent assigned to execute Milestone 2 (Scraper Configuration & Macro-Searches) for Vagas Sniper Bot.
Working directory: C:\Users\99196\OneDrive\Documentos\vagas_bot\.agents\teamwork_preview_worker_m2

Task Scope (Requirement R2):
Update scraping logic, keyword mapping configurations (`CO_OCCURRENCE_RULES`, `SEARCH_MAPPING`, `blacklist`), `is_job_relevant()`, `bot.py`, and `app.py` to support the new taxonomy.
Configure scrapers and backend search routes to execute macro-searches for broad categories (e.g., "Indústria", "Logística", "Administrativo", "Vendas", "Design", "Engenharia de Dados") and rely on local filtering in `bot.py` to classify specific sub-professions (like "Pintor Industrial" or "Almoxarife").

Detailed Implementation Steps:
1. Open `bot.py`:
   a. Update `SEARCH_MAPPING` to map broad macro keywords ("Operações Físicas", "Indústria", "Logística", "Administrativo", "Criativos", "Design", "Inteligência de Vendas", "Vendas", "Engenharia de Dados") and all sub-professions ("Pintor Industrial", "Almoxarife", "Assistente Financeiro", "Editor de Vídeo", "SDR", "Executivo de Vendas", etc.) to normalized strings.
   b. Modify `global_title_blacklist`: remove generic "pintor" and "mecanico" so legitimate industrial roles like "Pintor Industrial" and "Mecânico Industrial" pass `active_global_blacklist`.
   c. Add two-group `CO_OCCURRENCE_RULES` for broad macro search keywords and all sub-professions under the 6 new categories:
      - Group 0: domain/sector keywords (e.g. `["operacoes", "industrial", "industria", "producao", "manutencao", "fabrica", "usinagem"]`).
      - Group 1: role/title keywords (e.g. `["operador", "tecnico", "mecanico", "eletricista", "soldador", "pintor", "montador", "ajudante"]`).
   d. Add targeted `blacklist` rules for macro search keywords to prevent cross-domain false positives.
   e. Implement `classify_job_profession(job)` helper in `bot.py` to auto-tag `job['profession']` and `job['category']` based on title and requirements keywords, and integrate it into `is_job_relevant()` and/or job processing.

2. Open `app.py`:
   a. Update `run_initial_seed_search()` to search broad category macro keywords ("Indústria", "Logística", "Administrativo", "Design", "Vendas", "Engenharia de Dados", "Python", "Analytics Engineer", "IA-Ops", "Growth Engineer", "React") and run `classify_job_profession` before inserting jobs.
   b. Update `background_periodic_hunt_loop()` to cycle through macro keywords ("Indústria", "Logística", "Administrativo", "Design", "Vendas", "Engenharia de Dados", "Python", "IA-Ops") and run `classify_job_profession`.

3. Create unit test suite `tests/test_milestone2_macro_searches.py`:
   - Test macro keyword searches for all 6 broad categories.
   - Test sub-profession classification and relevance matching (e.g., "Pintor Industrial", "Almoxarife", "Assistente Financeiro", "Editor de Vídeo", "Executivo de Vendas", "Engenheiro de Dados").
   - Test that "Pintor Industrial" is NOT rejected by `global_title_blacklist`.
   - Test that invalid cross-domain jobs are correctly rejected by `blacklist`.

4. Run syntax & test checks:
   - Run `python -m py_compile bot.py app.py scrapers/*.py` to verify zero compilation syntax errors.
   - Run `python -m pytest tests/ -v` to ensure 100% pass rate.

Write your handoff report to `C:\Users\99196\OneDrive\Documentos\vagas_bot\.agents\teamwork_preview_worker_m2\handoff.md`.
Report back when finished.
