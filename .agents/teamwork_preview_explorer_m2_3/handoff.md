# HANDOFF REPORT — Explorer (Milestone 2: Scraper Configuration & Macro-Searches)

## 1. Observation
- **Project Structure**:
  - `PROJECT.md` defines Milestone 2 scope: Update `bot.py`, `app.py`, and scraper keyword mappings (`CO_OCCURRENCE_RULES`, macro-search terms, local filtering in `is_job_relevant`).
  - `static/index.html` (lines 1026-1041, 1421-1466) defines 14 category IDs, including the 6 broad categories: `operacoes_fisicas`, `logistica`, `administrativo`, `criativos`, `inteligencia_vendas`, and `engenharia_dados`.
  - `bot.py`:
    - `global_title_blacklist` (lines 1381-1396) currently includes `"pintor"`, `"mecanico"`, `"servicos gerais"`.
    - `blacklist` dict (lines 1427-1511) maps keyword normalized names to lists of negative terms.
    - `CO_OCCURRENCE_RULES` (lines 1522-1731) contains strict 2-group co-occurrence rules for specific technical professions, but lacks entries for the 6 broad macro-search categories (`operacoes fisicas`, `logistica`, `administrativo`, `criativos`, `inteligencia de vendas`, `engenharia de dados`) and their new sub-professions (`pintor industrial`, `almoxarife`, `assistente financeiro`, `inside sales`, `conferente`, etc.).
    - `SEARCH_MAPPING` (lines 1879-1998 & 2221-2260) maps display titles to normalized internal keys.
    - `is_job_relevant()` (lines 2002-2218) filters jobs using `SEARCH_MAPPING`, level, location, `global_title_blacklist`, `blacklist`, and `check_co_occurrence()`. In line 2204, `active_global_blacklist = [term for term in global_title_blacklist if term not in kw_norm ...]`.
  - `scrapers/*.py`: Scrapers such as `gupy.py` (lines 21-77), `infojobs.py` (lines 31-87), `linkedin.py` (lines 41-97) use keyword mapping dictionaries (`gupy_mapping`, `infojobs_mapping`, `keyword_mapping`) to translate incoming search keywords into platform-specific query strings.
  - `app.py`:
    - `run_initial_seed_search()` (lines 684-700) uses `seed_keywords = ["Python", "Analytics Engineer", "IA-Ops", "Growth Engineer", "React"]`.
    - `background_periodic_hunt_loop()` (lines 701-718) loops over `["Python", "Analytics Engineer", "IA-Ops"]`.

## 2. Logic Chain
1. **Observation**: Scrapers are invoked with macro keywords (e.g. "Indústria", "Logística", "Administrativo", "Vendas", "Design", "Engenharia de Dados") or standardized category keys (`operacoes_fisicas`, `logistica`, etc.).
2. **Step 1 (Scraper Mappings)**: In `scrapers/gupy.py`, `scrapers/infojobs.py`, `scrapers/linkedin.py`, etc., if the macro terms or category keys are missing from `gupy_mapping` / `infojobs_mapping` / `keyword_mapping`, scrapers pass raw unoptimized strings to APIs. Adding macro category terms and sub-professions to these dictionaries ensures scrapers fetch broad job pools for each domain.
3. **Step 2 (`bot.py` Keyword Normalization)**: `is_job_relevant` resolves incoming search keywords via `SEARCH_MAPPING`. Adding `"Operações Físicas"`, `"Indústria"`, `"Logística"`, `"Administrativo"`, `"Criativos"`, `"Design"`, `"Inteligência de Vendas"`, `"Vendas"`, `"Engenharia de Dados"`, `"Dados"` and new sub-professions to `SEARCH_MAPPING` guarantees clean normalization.
4. **Step 3 (Co-Occurrence & Filtering)**: When scrapers return broad job pools from macro searches, `is_job_relevant` filters jobs locally.
   - For macro category keys in `CO_OCCURRENCE_RULES`, Group 1 specifies domain terms (e.g. `["producao", "industrial", "fabrica", "manutencao"]`) and Group 2 specifies role terms (e.g. `["operador", "tecnico", "mecanico", "soldador", "pintor"]`).
   - For specific sub-professions in `CO_OCCURRENCE_RULES` (e.g. `"pintor industrial"`, `"almoxarife"`), rules specify specific skill and role combinations.
5. **Step 4 (Blacklist Exemption)**: `global_title_blacklist` contains `"pintor"` and `"mecanico"`. In `is_job_relevant`, when `kw_norm` is `"operacoes fisicas"`, `"industria"`, or a sub-profession like `"pintor industrial"`, terms like `"pintor"` and `"mecanico"` must be exempted from `active_global_blacklist`, preventing false positive rejections of legitimate industrial jobs.
6. **Step 5 (Seed Search & Auto-Hunt)**: Updating `run_initial_seed_search()` and `background_periodic_hunt_loop()` in `app.py` to include macro search keywords ensures the database is automatically seeded and periodically populated across all 6 broad categories.

## 3. Caveats
- **Scraper Rate Limits**: Running background hunt loops over 10+ macro keywords across 4+ scrapers increases API calls. Staggering execution or sleeping between queries inside `background_periodic_hunt_loop` prevents rate limiting by job platforms.
- **Location filtering**: Macro searches targeting "Remoto" vs "Presencial" rely on existing `is_job_relevant` location logic. No changes to location matching are required for M2.

## 4. Conclusion & Step-by-Step Implementation Plan for Worker

### Plan Overview
The Worker must make contiguous, precise updates to `bot.py`, `app.py`, and `scrapers/*.py`.

### Step 1: Update `bot.py`
1. **`SEARCH_MAPPING` & `search_mapping`**:
   Add mappings for all 6 broad categories and sub-professions:
   ```python
   "Operações Físicas": "operacoes fisicas",
   "Indústria": "operacoes fisicas",
   "Produção": "operacoes fisicas",
   "Logística": "logistica",
   "Administrativo": "administrativo",
   "Criativos": "criativos",
   "Design": "criativos",
   "Inteligência de Vendas": "inteligencia de vendas",
   "Vendas": "inteligencia de vendas",
   "Engenharia de Dados": "engenharia de dados",
   "Dados": "engenharia de dados",
   "Pintor Industrial": "pintor industrial",
   "Operador de Produção": "operador de producao",
   "Técnico de Manutenção": "tecnico de manutencao",
   "Mecânico Industrial": "mecanico industrial",
   "Eletricista Industrial": "eletricista industrial",
   "Soldador": "soldador",
   "Montador Industrial": "montador industrial",
   "Almoxarife": "almoxarife",
   "Operador de Empilhadeira": "operador de empilhadeira",
   "Conferente": "conferente",
   "Auxiliar de Expedição": "auxiliar de expedicao",
   "Estoquista": "estoquista",
   "Assistente Financeiro": "assistente financeiro",
   "Digitador": "digitador",
   "Arte Finalista": "arte finalista",
   "Ilustrador": "ilustrador",
   "Inside Sales": "inside sales",
   "Account Executive": "account executive",
   "Closer": "closer",
   ```
2. **`CO_OCCURRENCE_RULES`**:
   Add rule definitions for:
   - Macro categories: `"operacoes fisicas"`, `"logistica"`, `"administrativo"`, `"criativos"`, `"inteligencia de vendas"`, `"engenharia de dados"`.
   - Sub-professions: `"pintor industrial"`, `"operador de producao"`, `"tecnico de manutencao"`, `"mecanico industrial"`, `"eletricista industrial"`, `"soldador"`, `"almoxarife"`, `"operador de empilhadeira"`, `"conferente"`, `"auxiliar de expedicao"`, `"estoquista"`, `"digitador"`, `"arte finalista"`, `"ilustrador"`, `"inside sales"`, `"account executive"`, `"closer"`.
3. **`is_job_relevant` & `global_title_blacklist`**:
   In `is_job_relevant()` (around line 2204), exempt `"pintor"` and `"mecanico"` from `active_global_blacklist` when searching in the context of `"operacoes fisicas"` or industrial sub-professions.
   ```python
   is_ops_context = kw_norm in ["operacoes fisicas", "industria", "producao", "pintor industrial", "mecanico industrial", "soldador", "eletricista industrial"]
   active_global_blacklist = [
       term for term in global_title_blacklist 
       if term not in kw_norm 
       and not (user_level in ("ganhar experiencia", "iniciantes tudo", "iniciantes stuff") and term in ("voluntario", "voluntary"))
       and not (is_ops_context and term in ("pintor", "mecanico"))
   ]
   ```
4. **`blacklist` dict**:
   Add entries for macro categories and sub-professions to filter out unrelated fields (e.g., ensure `"gestor de trafego"` does not match road traffic, `"operacoes fisicas"` does not match software development).

### Step 2: Update Scrapers (`scrapers/gupy.py`, `scrapers/infojobs.py`, `scrapers/linkedin.py`, etc.)
In keyword mapping dictionaries:
- Add `"operacoes fisicas"`, `"industria"`, `"logistica"`, `"administrativo"`, `"criativos"`, `"design"`, `"inteligencia de vendas"`, `"vendas"`, `"engenharia de dados"` mapping to platform query strings (e.g. `"Indústria"`, `"Logística"`, `"Administrativo"`, `"Design"`, `"Vendas"`, `"Engenharia de Dados"`).
- Add new sub-professions.

### Step 3: Update `app.py`
1. **`run_initial_seed_search()`**:
   Set `seed_keywords = ["Indústria", "Logística", "Administrativo", "Design", "Vendas", "Engenharia de Dados", "Python", "Analytics Engineer", "IA-Ops", "Growth Engineer", "React"]`.
2. **`background_periodic_hunt_loop()`**:
   Set macro search keywords: `macro_hunt_keywords = ["Indústria", "Logística", "Administrativo", "Design", "Vendas", "Engenharia de Dados", "Python", "Analytics Engineer", "IA-Ops"]`.
3. **Routes `/api/trigger` & `/api/search`**:
   Ensure incoming category names are passed through `SEARCH_MAPPING` or macro-keyword resolution prior to local filtering.

## 5. Verification Method
- **Syntax Verification**:
  ```powershell
  python -m py_compile bot.py app.py scrapers/gupy.py scrapers/infojobs.py scrapers/linkedin.py
  ```
- **Automated Test Suite**:
  ```powershell
  python run_tests.py
  pytest tests/test_category_taxonomy.py tests/test_category_taxonomy_stress.py
  ```
- **Filter & Classification Verification**:
  Run unit test scripts or create a verification script checking `is_job_relevant` for macro categories and sub-professions (e.g. verifying "Pintor Industrial" passes for "operacoes fisicas", "Almoxarife" passes for "logistica", etc.).
