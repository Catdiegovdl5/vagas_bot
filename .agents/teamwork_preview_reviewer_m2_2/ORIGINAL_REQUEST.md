## 2026-07-29T10:57:33Z
You are a Reviewer agent assigned to evaluate Milestone 2 (Scraper Configuration & Macro-Searches) for Vagas Sniper Bot.
Working directory: C:\Users\99196\OneDrive\Documentos\vagas_bot\.agents\teamwork_preview_reviewer_m2_2

Task:
1. Examine bot.py, app.py, scrapers/*.py, and tests/test_milestone2_macro_searches.py.
2. Verify that Requirement R2 is satisfied:
   - Broad category macro keywords ("Indústria", "Logística", "Administrativo", "Design", "Vendas", "Engenharia de Dados") are correctly defined in SEARCH_MAPPING, CO_OCCURRENCE_RULES, and blacklist.
   - Generic terms "pintor" and "mecanico" were removed from global_title_blacklist to allow legitimate industrial roles like "Pintor Industrial" and "Mecânico Industrial".
   - Helper classify_job_profession(job) is implemented and integrated.
   - Seed search and periodic background hunt loops in app.py use macro category search keywords.
3. Run python -m py_compile bot.py app.py scrapers/*.py and python -m pytest tests/test_milestone2_macro_searches.py -v.
4. Write your review verdict and findings in your report at C:\Users\99196\OneDrive\Documentos\vagas_bot\.agents\teamwork_preview_reviewer_m2_2\handoff.md. Report back when done.
