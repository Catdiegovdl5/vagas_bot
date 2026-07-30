# Handoff Report: Milestone 2 — Scraper Configuration & Macro-Searches (Requirement R2)

## 1. Observation
Direct codebase investigation of `C:\Users\99196\OneDrive\Documentos\vagas_bot`:

- **`PROJECT.md` (lines 1-33)**: Defines data flow where frontend triggers `/api/search` or `/api/trigger` with macro keywords or category names; backend executes broad domain searches across scrapers (`scrapers/*.py`) and applies local classification & filtering via `CO_OCCURRENCE_RULES`, `blacklist`, and `is_job_relevant` in `bot.py`.
- **`bot.py`**:
  - `blacklist` (lines 1427-1511): Contains niche-specific blacklists indexed by normalized keyword keys.
  - `CO_OCCURRENCE_RULES` (lines 1522-1731): Dictionary mapping normalized search terms to list of required word groups. Each group must have at least 1 match in job title/requirements for the job to be deemed relevant.
  - `SEARCH_MAPPING` (lines 1879-1998): Maps user input / UI strings to canonical normalized keyword keys.
  - `is_job_relevant(job, keyword, settings)` (lines 2002-2218): Resolves `clean_kw = SEARCH_MAPPING.get(keyword, keyword)`, normalizes to `kw_norm`, applies `active_global_blacklist`, checks local `blacklist[kw_norm]`, and delegates co-occurrence checking to `check_co_occurrence(full_text, kw_norm, job)`.
- **`app.py`**:
  - Endpoint `@app.post("/api/trigger")` (lines 548-617): Receives `keyword`, `level`, `location`, `platforms`, runs scrapers asynchronously, filters results with `is_job_relevant`, and inserts valid jobs into `jobs.db`.
  - Endpoint `@app.api_route("/api/search", methods=["GET", "POST"])` (lines 619-666): Receives `keyword`, `level`, `location`, `platforms`, runs scrapers, filters results with `is_job_relevant`, inserts jobs, and returns matching jobs list.
  - `run_initial_seed_search()` (lines 684-700): Currently hardcodes `seed_keywords = ["Python", "Analytics Engineer", "IA-Ops", "Growth Engineer", "React"]`.
  - `background_periodic_hunt_loop()` (lines 701-718): Currently hardcodes `for kw in ["Python", "Analytics Engineer", "IA-Ops"]:` for periodic background hunting every 600 seconds.
- **`static/index.html` (lines 1026-1041 & 1421-1460)**:
  - M1 updated `PROFESSION_CATEGORIES` with 6 new broad categories: `operacoes_fisicas`, `logistica`, `administrativo`, `criativos`, `inteligencia_vendas`, `engenharia_dados` (and existing categories `growth_engineer`, `performance`, `ia_ops`, `sdr_tecnico`, `analytics_engineer`, `server_side_tracking`, `outros`).
- **`scrapers/`**: All 17 scraper modules (`gupy.py`, `catho.py`, `infojobs.py`, `workana.py`, `linkedin.py`, `indeed.py`, `vagas_com.py`, `remotar.py`, etc.) accept standard kwargs (`keyword`, `level`, `location`, `country`, `max_pages`) and return lists of raw job dictionaries.

---

## 2. Logic Chain
1. **Frontend to Scraper Data Flow**: When a user selects a broad category (e.g., "Operações Físicas", "Logística", "Administrativo", "Criativos", "Inteligência de Vendas", "Engenharia de Dados") or a specific sub-profession, `/api/trigger` or `/api/search` receives the keyword string.
2. **Macro Keyword Execution**: Scrapers query job portals using broad macro keywords ("Indústria", "Logística", "Administrativo", "Vendas", "Design", "Engenharia de Dados"). This maximizes recall by retrieving broad candidate job postings from external job boards.
3. **Local Domain Filtering & Classification (`is_job_relevant`)**:
   - `SEARCH_MAPPING` maps the macro search term (e.g. "Indústria" -> "operacoes fisicas", "Design" -> "criativos", "Vendas" -> "inteligencia de vendas", "Dados" -> "engenharia de dados", "Logística" -> "logistica", "Administrativo" -> "administrativo") and sub-profession names to canonical keys.
   - `CO_OCCURRENCE_RULES` enforces group co-occurrence requirements for each canonical key. For macro categories, Group 1 specifies domain context terms (e.g., logistics, physical operations, admin, design, sales, data engineering) and Group 2 specifies valid role titles/functions.
   - `blacklist` blocks cross-domain mismatches (e.g., software dev jobs appearing under physical operations, medical jobs under admin).
4. **Seed & Background Hunt Automated Coverage**: Updating `run_initial_seed_search()` and `background_periodic_hunt_loop()` in `app.py` guarantees that all 6 broad category macro-keywords are continuously scraped and populated in `jobs.db` on startup and during automatic 10-minute cycles.

---

## 3. Caveats
- No changes should be made to `static/index.html` as M1 is already complete (`DONE`).
- Macro-search keywords like "Indústria" or "Vendas" may return a large volume of raw results from external scrapers; local filtering in `is_job_relevant` must be strict enough to discard non-relevant jobs without dropping valid sub-professions.
- Short keywords (e.g., "rh", "dp", "ui", "ux") require exact word boundary matching (`(?<![a-z0-9])...(?![a-z0-9])`) in `bot.py` to prevent substring false positives (e.g., matching "ui" in "guia").

---

## 4. Conclusion
To complete Requirement R2 for Milestone 2, the Worker should execute the following 3 concrete implementation steps in `bot.py` and `app.py`:

### Implementation Plan for Worker

#### Step 1: Update `bot.py` Taxonomy & Filtering Rules
1. **Extend `SEARCH_MAPPING` in `bot.py`** (around line 1879):
   Add mappings for all 6 broad category macro-keywords and sub-professions:
   ```python
   # Broad Category Macro Mappings
   "Operações Físicas": "operacoes fisicas",
   "Operacoes Fisicas": "operacoes fisicas",
   "Indústria": "operacoes fisicas",
   "Industria": "operacoes fisicas",
   "Logística": "logistica",
   "Logistica": "logistica",
   "Administrativo": "administrativo",
   "Criativos": "criativos",
   "Design": "criativos",
   "Inteligência de Vendas": "inteligencia de vendas",
   "Inteligencia de Vendas": "inteligencia de vendas",
   "Vendas": "inteligencia de vendas",
   "Engenharia de Dados": "engenharia de dados",
   "Dados": "engenharia de dados",

   # Sub-Professions Mappings
   "Pintor Industrial": "pintor industrial",
   "Operador de Máquina": "operador de maquina",
   "Mecânico Industrial": "mecanico industrial",
   "Eletricista Industrial": "eletricista industrial",
   "Soldador": "soldador",
   "Torneiro Mecânico": "torneiro mecanico",
   "Técnico em Manutenção": "tecnico em manutencao",
   "Operador de Produção": "operador de producao",
   "Montador Industrial": "montador industrial",
   "Auxiliar de Produção": "auxiliar de producao",
   "Almoxarife": "almoxarife",
   "Assistente de Logística": "assistente de logistica",
   "Operador de Empilhadeira": "operador de empilhadeira",
   "Estoquista": "estoquista",
   "Conferente": "conferente",
   "Analista de Logística": "analista de logistica",
   "Inside Sales": "inside sales",
   "Account Executive": "account executive",
   ```

2. **Extend `CO_OCCURRENCE_RULES` in `bot.py`** (around line 1522):
   Add multi-group co-occurrence rules for broad macro categories and sub-professions:
   ```python
   "operacoes fisicas": [
       ["operacao", "operacoes", "producao", "industrial", "manutencao", "fabrica", "usinagem", "solda", "pintura", "mecanica", "eletrica", "montagem"],
       ["operador", "tecnico", "tecnica", "mecanico", "eletricista", "soldador", "pintor", "usinador", "montador", "auxiliar", "ajudante", "torneiro"]
   ],
   "logistica": [
       ["logistica", "estoque", "almoxarifado", "expedicao", "recebimento", "transporte", "frotas", "frete", "empilhadeira", "inventario", "supply chain", "armazem", "carga"],
       ["almoxarife", "estoquista", "assistente", "auxiliar", "analista", "operador", "conferente", "coordenador", "gerente", "motorista", "ajudante"]
   ],
   "administrativo": [
       ["administrativo", "administracao", "adm", "escritorio", "backoffice", "financeiro", "recursos humanos", "rh", "recepcao", "faturamento", "contabilidade", "fiscal", "secretaria", "departamento pessoal", "contas"],
       ["assistente", "auxiliar", "analista", "recepcionista", "secretaria", "secretario", "atendente", "coordenador", "gerente", "estagiario", "iniciante"]
   ],
   "criativos": [
       ["design", "designer", "video", "motion", "copywriter", "arte", "ui", "ux", "midia social", "social media", "audiovisual", "ilustracao", "redacao", "conteudo", "criativos"],
       ["designer", "editor", "editora", "copywriter", "redator", "redatora", "criativo", "criativa", "ilustrador", "ilustradora", "social media", "especialista", "analista"]
   ],
   "inteligencia de vendas": [
       ["vendas", "comercial", "sdr", "bdr", "inside sales", "prospeccao", "sales", "outbound", "inbound", "closer", "pre vendas", "contas", "account executive"],
       ["executivo", "executiva", "gerente", "consultor", "consultora", "vendedor", "vendedora", "sdr", "bdr", "representante", "assessor", "assessora", "especialista", "analista"]
   ],
   "engenharia de dados": [
       ["dados", "data", "pipeline", "pipelines", "etl", "elt", "spark", "pyspark", "databricks", "airflow", "kafka", "dbt", "sql", "data lake", "data warehouse", "bigquery", "snowflake", "power bi", "analytics"],
       ["engenheiro", "engenheira", "data engineer", "analista", "arquiteto", "arquiteta", "especialista", "dev", "cientista"]
   ],
   "pintor industrial": [
       ["pintor", "pintura"],
       ["industrial", "fabrica", "oficina", "estruturas", "pistola", "airless"]
   ],
   "almoxarife": [
       ["almoxarife", "almoxarifado"],
       ["estoque", "materiais", "recebimento", "expedicao", "inventario", "controle"]
   ],
   "operador de empilhadeira": [
       ["operador", "operadora", "empilhaderista"],
       ["empilhadeira", "retratil", "combustao", "armazem", "deposito"]
   ],
   "conferente": [
       ["conferente", "conferencia"],
       ["carga", "expedicao", "recebimento", "mercadorias", "estoque", "logistica"]
   ],
   ```

3. **Extend `blacklist` in `bot.py`** (around line 1427):
   Add negative keyword filters for macro category keys to eliminate false positives:
   ```python
   "operacoes fisicas": ["software", "programador", "desenvolvedor", "frontend", "backend", "fullstack", "medico", "enfermeiro", "advogado"],
   "logistica": ["programador", "desenvolvedor", "medico", "enfermeiro", "advogado", "professor"],
   "administrativo": ["producao", "limpeza", "carga", "descarga", "pesado", "operario", "servente", "cozinha", "estoque", "repositor"],
   "criativos": ["programador", "desenvolvedor", "dba", "suporte", "medico", "enfermeiro"],
   "inteligencia de vendas": ["loja", "balcao", "caixa", "repositor", "estoque", "limpeza", "panfleteiro"],
   "engenharia de dados": ["suporte", "infraestrutura", "redes", "helpdesk", "service desk", "dba", "entrada de dados", "digitador"],
   ```

#### Step 2: Configure Scrapers and Backend Routes in `app.py`
Verify that `/api/trigger` and `/api/search` pass requested broad macro keywords ("Indústria", "Logística", "Administrativo", "Vendas", "Design", "Engenharia de Dados") directly to scrapers, allowing scrapers to fetch broad job lists which are then filtered locally via `is_job_relevant`.

#### Step 3: Update `run_initial_seed_search()` and `background_periodic_hunt_loop()` in `app.py`
In `app.py`:
Define `MACRO_SEED_KEYWORDS`:
```python
MACRO_SEED_KEYWORDS = [
    "Indústria",
    "Logística",
    "Administrativo",
    "Criativos",
    "Inteligência de Vendas",
    "Engenharia de Dados",
    "Python",
    "Analytics Engineer",
    "IA-Ops",
    "Growth Engineer",
    "React"
]
```
1. In `run_initial_seed_search()` (line 684):
   Iterate over `MACRO_SEED_KEYWORDS` instead of the old 5 hardcoded keywords.
2. In `background_periodic_hunt_loop()` (line 701):
   Iterate over `MACRO_SEED_KEYWORDS` instead of the old 3 hardcoded keywords.

---

## 5. Verification Method
To verify implementation:
1. **Compilation Check**:
   ```bash
   python -m py_compile bot.py app.py
   ```
2. **Category & Classification Test Harness**:
   Create or run test scripts validating `is_job_relevant` for macro keywords and sub-professions:
   ```bash
   python -m pytest tests/test_category_taxonomy.py tests/test_category_taxonomy_stress.py
   ```
3. **Empirical Seed & Search Verification**:
   Execute a quick python test script to verify `is_job_relevant` returns `True` for valid job titles under each of the 6 broad categories and sub-professions, and `False` for blacklisted titles.
