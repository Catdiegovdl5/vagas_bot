## 2026-07-29T10:46:57Z
You are an Explorer agent assigned to investigate Milestone 2 (Scraper Configuration & Macro-Searches) for Vagas Sniper Bot.
Working directory: C:\Users\99196\OneDrive\Documentos\vagas_bot\.agents\teamwork_preview_explorer_m2_2

Task:
Read PROJECT.md at C:\Users\99196\OneDrive\Documentos\vagas_bot\PROJECT.md, bot.py, app.py, and scrapers in C:\Users\99196\OneDrive\Documentos\vagas_bot.
Analyze how to satisfy Requirement R2:
1. Update `CO_OCCURRENCE_RULES`, `blacklist`, and `is_job_relevant` in `bot.py` to support all sub-professions under the 6 new broad categories (Operações Físicas, Logística, Administrativo, Criativos, Inteligência de Vendas, Engenharia de Dados).
2. Configure scrapers and backend search routes (`app.py`, `bot.py`) to execute macro-searches for broad category keywords (e.g. "Indústria", "Logística", "Administrativo", "Vendas", "Design", "Engenharia de Dados") and rely on local filtering in `is_job_relevant` to classify specific sub-professions (e.g. "Pintor Industrial", "Almoxarife", "Assistente Financeiro", etc.).
3. Update `run_initial_seed_search()` and `background_periodic_hunt_loop()` in `app.py` to include macro-search categories.

Provide a detailed analysis and step-by-step implementation plan for the Worker in your handoff report at C:\Users\99196\OneDrive\Documentos\vagas_bot\.agents\teamwork_preview_explorer_m2_2\handoff.md.
Do NOT modify source files directly (read-only exploration). Report back when done.
