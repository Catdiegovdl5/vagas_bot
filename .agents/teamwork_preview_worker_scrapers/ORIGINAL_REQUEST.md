## 2026-07-29T11:29:54Z

<USER_REQUEST>
You are teamwork_preview_worker_scrapers.
Your working directory is `C:\Users\99196\OneDrive\Documentos\vagas_bot\.agents\teamwork_preview_worker_scrapers`.
Please create your working directory if it does not exist, initialize `progress.md`, and execute the implementation tasks.

Objective:
Refactor scrapers in `scrapers/` and category dispatch in `bot.py` to natively support the 6 new profession categories:
1. Operações Físicas (e.g., Operador CNC, Pintor Industrial, Mecânico Industrial, Soldador, Eletricista, Operador de Produção, Auxiliar de Operações, Conferente)
2. Logística (e.g., Assistente de Logística, Auxiliar de Logística, Auxiliar de Almoxarifado, Operador de Empilhadeira, Auxiliar de Expedição, Motorista, Almoxarife)
3. Administrativo (e.g., Assistente Administrativo, Auxiliar Administrativo, Recepcionista, Auxiliar de Escritório, Data Entry, Digitador, Assistente Financeiro)
4. Criativos de Performance (e.g., Designer Conversional, Copywriter, Criador de Anúncios, Motion Designer, Editor de Vídeo, Gestor de Tráfego, Designer Gráfico)
5. Inteligência de Vendas (e.g., SDR, BDR, Inside Sales, Analista de Sales Ops, Executivo de Vendas, CRM, Analista de Vendas)
6. Engenharia de IA/Dados (e.g., Engenheiro de Dados, Engenheiro de IA, Machine Learning, Data Engineer, Cientista de Dados, Analista de Dados)

Tasks:
1. Refactor relevant scrapers in `scrapers/` (e.g., `gupy.py`, `infojobs.py`, `workana.py`, `linkedin.py`, `vagas_com.py`, `catho.py`, etc.) and `bot.py` (`MAGIC_CATEGORIES`, `SEARCH_MAPPING`, `CO_OCCURRENCE_RULES`, `BLACKLIST_PROFILES`, `vagas_com_mapping`, etc.) so that search queries natively inject key terms into native search/API queries for all 6 new categories, preventing generic bulk scraping.
2. Ensure downstream payload compatibility: Returned job dictionaries must have `profession` and `category` fields accurately populated and formatted to match downstream database insertion flows (`database.py`).
3. Adapt or create programmatic tests under `tests/` (e.g., creating `tests/test_scrapers_macro_categories.py` or adapting `tests/test_tier1.py` / `tests/test_milestone2_macro_searches.py`) verifying at least 3-4 updated scrapers using queries from the 6 new categories.
4. Execute `python run_tests.py` and verify all tests pass with 0 errors.

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A Forensic Auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Write your summary of changes to `changes.md` and `handoff.md` in `C:\Users\99196\OneDrive\Documentos\vagas_bot\.agents\teamwork_preview_worker_scrapers\`. Include full build and test execution results. Send a message to parent when done.
</USER_REQUEST>
