# Handoff Report — Milestone 2: Scraper Configuration & Macro-Searches

## 1. Observation

### Code Base Artifacts Examined
- `PROJECT.md` at `C:\Users\99196\OneDrive\Documentos\vagas_bot\PROJECT.md` (lines 1–33): Defines Milestone 2 scope: updating `bot.py`, `app.py`, and scraper keyword mappings (`CO_OCCURRENCE_RULES`, macro-search terms, local filtering) to support new profession categories.
- `static/index.html` (lines 1026–1041 & 1421–1466): Defines the 6 broad categories and their UI drawer mappings:
  1. **Operações Físicas** (`operacoes_fisicas` / macro term: `"Indústria"`, `"Operações Físicas"`)
  2. **Logística** (`logistica` / macro term: `"Logística"`)
  3. **Administrativo** (`administrativo` / macro term: `"Administrativo"`)
  4. **Criativos** (`criativos` / macro term: `"Design"`, `"Criativos"`)
  5. **Inteligência de Vendas** (`inteligencia_vendas` / macro term: `"Vendas"`, `"Inteligência de Vendas"`)
  6. **Engenharia de Dados** (`engenharia_dados` / macro term: `"Engenharia de Dados"`, `"Dados"`)
- `bot.py`:
  - `global_title_blacklist` (lines 1381–1396): Contains generic manual terms including `"mecanico"` and `"pintor"` (lines 1392–1393). In `is_job_relevant()` (lines 2204–2206), any job title matching terms in `active_global_blacklist` is immediately rejected. This causes valid sub-professions like `"Pintor Industrial"` and `"Mecânico Industrial"` to be incorrectly rejected.
  - `blacklist` (lines 1427–1511): Lacks entries for macro-category search keywords (`"operacoes fisicas"`, `"industria"`, `"logistica"`, `"administrativo"`, `"criativos"`, `"design"`, `"inteligencia de vendas"`, `"vendas"`, `"engenharia de dados"`) and their associated sub-professions.
  - `CO_OCCURRENCE_RULES` (lines 1522–1731): Currently lacks rules for macro-category search terms (`"operacoes fisicas"`, `"industria"`, `"logistica"`, `"administrativo"`, `"criativos"`, `"design"`, `"inteligencia de vendas"`, `"vendas"`, `"engenharia de dados"`) and sub-professions under these categories (`"pintor industrial"`, `"almoxarife"`, `"conferente de estoque"`, `"operador de empilhadeira"`, `"assistente financeiro"`, `"auxiliar de contabilidade"`, `"executivo de vendas"`, `"arquiteto de dados"`, `"salesops"`, etc.).
  - `SEARCH_MAPPING` (lines 1879–1998): Maps user inputs to normalized strings; missing mappings for macro terms and new sub-professions.
  - `is_job_relevant()` (lines 2002–2218): Evaluates job relevance using `check_co_occurrence()`. When a macro keyword is not in `CO_OCCURRENCE_RULES`, it falls back to strict word matching against the search string (lines 1848–1877), causing jobs captured by broad macro-searches to fail filtering if they lack the exact string (e.g. searching for `"Operações Físicas"` rejects `"Pintor Industrial"` because the word `"fisicas"` is absent).
- `app.py`:
  - `run_initial_seed_search()` (lines 684–699): `seed_keywords` currently set to `["Python", "Analytics Engineer", "IA-Ops", "Growth Engineer", "React"]`. Does not seed macro search categories.
  - `background_periodic_hunt_loop()` (lines 701–717): Periodic loop currently searches `["Python", "Analytics Engineer", "IA-Ops"]`. Does not include broad category macro keywords.
  - Search routes `/api/trigger` (lines 548–617) and `/api/search` (lines 619–665): Dispatch scrapers with `keyword` parameter and apply `is_job_relevant()`.

---

## 2. Logic Chain

1. **Macro Search Execution Flow**:
   - Scrapers (`scrapers/*.py`) receive a `keyword` parameter from backend search routes (`/api/trigger`, `/api/search`, seed search, background hunt loop).
   - When configured with macro category search terms (e.g., `"Indústria"`, `"Logística"`, `"Administrativo"`, `"Vendas"`, `"Design"`, `"Engenharia de Dados"`), scrapers query external job platforms and return raw lists of job postings matching those broad domains.

2. **Local Relevance & Classification Requirement**:
   - Upon capture, raw jobs are passed to `is_job_relevant(job, keyword, settings)`.
   - `is_job_relevant()` normalizes `keyword` via `SEARCH_MAPPING` to obtain `kw_norm`.
   - If `kw_norm` is a macro-category search term (e.g., `"operacoes fisicas"`, `"industria"`, `"logistica"`, `"administrativo"`, `"criativos"`, `"design"`, `"inteligencia de vendas"`, `"vendas"`, `"engenharia de dados"`), `is_job_relevant()` passes the job to `check_co_occurrence(text_norm, kw_norm, job)`.

3. **Co-Occurrence Failure Without Macro Rules**:
   - In `check_co_occurrence()`, if `kw_norm` is NOT present in `CO_OCCURRENCE_RULES`, the function falls back to checking whether every significant word in `kw_norm` appears in the job text.
   - For example, searching `"Operações Físicas"` evaluates `significant_words = ["operacoes", "fisicas"]`. A job titled `"Pintor Industrial"` or `"Operador de Produção"` does NOT contain `"fisicas"`, resulting in immediate rejection.
   - **Solution**: Add explicit two-group `CO_OCCURRENCE_RULES` for macro search keywords:
     - **Group 0 (Domain/Sector)**: Terms representing the broad domain (e.g., `["operacoes", "industrial", "industria", "producao", "manutencao", "fabrica", "usinagem"]`).
     - **Group 1 (Role/Title)**: Terms representing valid sub-profession roles (e.g., `["operador", "tecnico", "mecanico", "eletricista", "soldador", "pintor", "montador", "ajudante"]`).
     - A job passes the macro co-occurrence rule if it contains AT LEAST ONE domain term from Group 0 AND AT LEAST ONE role term from Group 1.

4. **Global Blacklist Conflicts**:
   - `global_title_blacklist` in `bot.py` currently contains `"pintor"` and `"mecanico"`.
   - When evaluating any job, `active_global_blacklist` rejects titles containing blacklisted words unless the search keyword itself contains that word.
   - For a macro search like `"Indústria"`, `kw_norm` ("industria") does NOT contain `"pintor"`. Therefore, a job titled `"Pintor Industrial"` would be rejected by `global_title_blacklist`.
   - **Solution**: Remove generic `"pintor"` and `"mecanico"` from `global_title_blacklist` (or refine them to `"pintor residencial"`, `"pintor de paredes"`, `"mecanico automotivo"`), relying on targeted niche blacklists for domain-specific filtering.

5. **Sub-Profession Classification**:
   - Requirement R2 requires local filtering in `is_job_relevant()` to classify specific sub-professions (e.g., `"Pintor Industrial"`, `"Almoxarife"`, `"Assistente Financeiro"`).
   - Each sub-profession requires:
     a) Entry in `SEARCH_MAPPING` mapping display name to normalized string.
     b) Entry in `CO_OCCURRENCE_RULES` validating title + requirements co-occurrence.
     c) Entry in `blacklist` rejecting cross-domain false positives (e.g. rejecting "professor de contabilidade" when evaluating "auxiliar de contabilidade").
     d) Classification logic in `is_job_relevant()` or a helper function `classify_sub_profession(job)` that sets `job['profession']` and `job['category']` based on title/requirement keyword matching.

6. **Seed Search & Periodic Background Loop**:
   - In `app.py`, `run_initial_seed_search()` and `background_periodic_hunt_loop()` must be updated to include macro category search keywords (`"Indústria"`, `"Logística"`, `"Administrativo"`, `"Design"`, `"Vendas"`, `"Engenharia de Dados"`).
   - This ensures the background engine populates database tables across all 6 broad categories upon application startup and maintains fresh postings during periodic hunt loops.

---

## 3. Caveats

- **External Platform Scraping**: Scrapers rely on third-party job site APIs/HTML. Offline tests and mock responses are used during unit testing; live network scraping depends on platform connectivity.
- **Backward Compatibility**: Existing IT and AI profession rules (e.g. `desenvolvedor python`, `ia_ops`, `server_side_tracking`, `analytics_engineer`) in `CO_OCCURRENCE_RULES` and `blacklist` must remain intact without regressions.
- **Sub-profession Disambiguation**: Vague titles like `"Assistente"` or `"Analista"` require checking description text (`job['requirements']`) to accurately assign `job['profession']` and `job['category']`.

---

## 4. Conclusion & Detailed Implementation Plan for Worker

To fulfill Requirement R2, the Worker should execute the following 4 step-by-step modifications:

### Step 1: Update `bot.py` (`SEARCH_MAPPING`, `global_title_blacklist`, `blacklist`, `CO_OCCURRENCE_RULES`)

1. **`SEARCH_MAPPING` Update**:
   Add macro category search keywords and all sub-professions to `SEARCH_MAPPING`:
   ```python
   # --- Broad Category Macro Keywords ---
   "Operações Físicas": "operacoes fisicas",
   "Indústria": "industria",
   "Logística": "logistica",
   "Administrativo": "administrativo",
   "Criativos": "criativos",
   "Design": "design",
   "Inteligência de Vendas": "inteligencia de vendas",
   "Vendas": "vendas",
   "Engenharia de Dados": "engenharia de dados",

   # --- Operações Físicas Sub-Professions ---
   "Operador de Produção": "operador de producao",
   "Auxiliar de Produção": "auxiliar de producao",
   "Mecânico Industrial": "mecanico industrial",
   "Técnico de Manutenção": "tecnico de manutencao",
   "Eletricista Industrial": "eletricista industrial",
   "Soldador": "soldador",
   "Caldeireiro": "caldeireiro",
   "Pintor Industrial": "pintor industrial",
   "Usinagem": "usinagem",
   "Montador Industrial": "montador industrial",

   # --- Logística Sub-Professions ---
   "Almoxarife": "almoxarife",
   "Auxiliar de Almoxarifado": "auxiliar de almoxarifado",
   "Conferente de Estoque": "conferente de estoque",
   "Operador de Empilhadeira": "operador de empilhadeira",
   "Assistente de Logística": "assistente de logistica",
   "Analista de Logística": "analista de logistica",
   "Assistente de Expedição": "assistente de expedicao",

   # --- Administrativo Sub-Professions ---
   "Assistente Administrativo": "assistente administrativo",
   "Auxiliar Administrativo": "auxiliar administrativo",
   "Assistente Financeiro": "assistente financeiro",
   "Analista Financeiro": "analista financeiro",
   "Auxiliar de Contabilidade": "auxiliar de contabilidade",
   "Assistente de Faturamento": "assistente de faturamento",
   "Analista de RH": "analista de rh",
   "Recepcionista": "recepcionista",
   "Assistente de Compras": "assistente de compras",

   # --- Criativos Sub-Professions ---
   "Designer Gráfico": "designer grafico",
   "Editor de Vídeo": "editor de video",
   "Motion Designer": "motion designer",
   "UX Designer": "ux designer",
   "Copywriter": "copywriter",
   "Social Media": "social media",
   "Ilustrador": "ilustrador",

   # --- Inteligência de Vendas Sub-Professions ---
   "SDR": "sdr",
   "BDR": "bdr",
   "Executivo de Vendas": "executivo de vendas",
   "Inside Sales": "inside sales",
   "Analista de Inteligência de Vendas": "analista de inteligencia de vendas",
   "Gerente de Contas": "gerente de contas",
   "Sales Operations": "salesops",

   # --- Engenharia de Dados Sub-Professions ---
   "Engenheiro de Dados": "engenheiro de dados",
   "Analytics Engineer": "analytics engineer",
   "Arquiteto de Dados": "arquiteto de dados",
   "Analista de Banco de Dados": "analista de banco de dados",
   "DBA": "dba",
   ```

2. **`global_title_blacklist` Adjustment**:
   Remove `"pintor"` and `"mecanico"` from `global_title_blacklist` (lines 1392–1393) so that industrial roles (`"Pintor Industrial"`, `"Mecânico Industrial"`) are not blocked during macro searches. Replace with specific manual non-industrial terms if desired (e.g. `"pintor residencial"`, `"pintor de parede"`).

3. **`CO_OCCURRENCE_RULES` Expansion**:
   Add rules for macro keywords and all sub-professions:
   ```python
   # --- Macro Category Rules ---
   "operacoes fisicas": [
       ["operacoes", "operacao", "industrial", "industria", "producao", "manutencao", "fabrica", "usinagem", "solda", "caldeiraria", "mecanica", "eletrica", "linha de producao"],
       ["operador", "operadora", "tecnico", "tecnica", "mecanico", "eletricista", "soldador", "caldeireiro", "pintor", "montador", "ajudante", "auxiliar", "inspetor", "lider", "encarregado"]
   ],
   "industria": [
       ["industrial", "industria", "producao", "manutencao", "fabrica", "usinagem", "solda", "caldeiraria", "mecanica", "eletrica"],
       ["operador", "operadora", "tecnico", "tecnica", "mecanico", "eletricista", "soldador", "caldeireiro", "pintor", "montador", "ajudante", "auxiliar", "inspetor"]
   ],
   "logistica": [
       ["logistica", "estoque", "almoxarifado", "expedicao", "recebimento", "armazem", "transporte", "supply chain", "frete", "frotas"],
       ["assistente", "auxiliar", "analista", "almoxarife", "conferente", "operador", "coordenador", "gerente", "especialista"]
   ],
   "administrativo": [
       ["administrativo", "administracao", "adm", "financeiro", "contabilidade", "faturamento", "fiscal", "recursos humanos", "rh", "recepcao", "compras", "secretaria"],
       ["assistente", "auxiliar", "analista", "recepcionista", "secretaria", "tecnico", "coordenador", "gerente"]
   ],
   "criativos": [
       ["design", "designer", "criativo", "criativos", "arte", "video", "motion", "copywriting", "social media", "ilustracao", "audiovisual", "ui", "ux"],
       ["designer", "editor", "copywriter", "redator", "ilustrador", "criador", "produtor", "assistente", "analista", "especialista"]
   ],
   "design": [
       ["design", "designer", "graphic", "grafico", "figma", "photoshop", "illustrator", "ui", "ux", "arte", "branding"],
       ["designer", "criativo", "criativa", "assistente", "analista", "especialista"]
   ],
   "inteligencia de vendas": [
       ["vendas", "comercial", "sdr", "bdr", "inside sales", "sales", "prospeccao", "contas", "outbound", "closer"],
       ["executivo", "representante", "analista", "consultor", "gerente", "sdr", "bdr", "vendedor", "vendedora", "especialista"]
   ],
   "vendas": [
       ["vendas", "comercial", "sales", "sdr", "bdr", "inside sales", "prospeccao", "contas", "negociacao"],
       ["executivo", "representante", "analista", "consultor", "gerente", "sdr", "bdr", "vendedor", "vendedora"]
   ],
   "engenharia de dados": [
       ["dados", "data", "pipeline", "etl", "spark", "airflow", "sql", "snowflake", "bigquery", "databricks", "data warehouse", "lakehouse"],
       ["engenheiro", "engenheira", "data engineer", "analytics engineer", "arquiteto", "arquiteta", "desenvolvedor", "analista", "dba"]
   ],

   # --- Sub-Profession Rules ---
   "pintor industrial": [
       ["pintura", "pintor", "tinta", "superficie", "estrutura metalica", "industrial", "jateamento"],
       ["pintor", "auxiliar", "tecnico", "operador", "industrial"]
   ],
   "almoxarife": [
       ["almoxarifado", "estoque", "materiais", "recebimento", "inventario", "pecas"],
       ["almoxarife", "auxiliar", "assistente", "conferente", "operador"]
   ],
   "conferente de estoque": [
       ["estoque", "conferencia", "inventario", "recebimento", "expedicao", "mercadorias"],
       ["conferente", "auxiliar", "assistente", "operador"]
   ],
   "operador de empilhadeira": [
       ["empilhadeira", "movimentacao", "carga", "descarte", "palete", "armazem"],
       ["operador", "operadora", "motorista"]
   ],
   "assistente financeiro": [
       ["financeiro", "contas a pagar", "contas a receber", "conciliacao", "fluxo de caixa", "tesouraria", "faturamento"],
       ["assistente", "auxiliar", "analista", "tecnico"]
   ],
   "auxiliar de contabilidade": [
       ["contabil", "contabilidade", "balancete", "lancamentos", "fiscal", "impostos"],
       ["auxiliar", "assistente", "analista", "tecnico"]
   ],
   "executivo de vendas": [
       ["vendas", "comercial", "b2b", "contas", "negociacao", "fechamento", "proposta", "inside sales"],
       ["executivo", "gerente", "consultor", "representante", "account executive"]
   ],
   "arquiteto de dados": [
       ["dados", "data", "arquitetura", "modelagem", "data warehouse", "data lake", "governance"],
       ["arquiteto", "arquiteta", "lead", "specialist", "especialista"]
   ],
   "salesops": [
       ["salesops", "sales operations", "crm", "salesforce", "hubspot", "funil de vendas", "metricas comerciais"],
       ["analista", "especialista", "coordenador", "gerente"]
   ]
   ```

4. **`blacklist` Additions**:
   Add targeted niche blacklist entries for macro search keywords and sub-professions to prevent domain cross-contamination:
   ```python
   "operacoes fisicas": ["professor", "medico", "advogado", "vendedor de loja", "corretor", "telemarketing"],
   "industria": ["professor", "medico", "advogado", "vendedor de loja", "corretor"],
   "logistica": ["programador frontend", "pedreiro", "faxineiro", "professor", "medico"],
   "administrativo": ["servente", "pedreiro", "cozinheiro", "motorista de caminhao", "faxineiro"],
   "criativos": ["pedreiro", "motorista", "faxineiro", "mecanico", "eletricista"],
   "design": ["pedreiro", "motorista", "faxineiro", "mecanico", "eletricista"],
   "inteligencia de vendas": ["repositor de supermercado", "caixa de loja", "panfleteiro", "limpeza", "pedreiro"],
   "vendas": ["repositor de supermercado", "caixa de loja", "panfleteiro", "limpeza"],
   "engenharia de dados": ["suporte n1", "digitador", "entrada de dados", "atendimento ao cliente", "vendedor de balcao"]
   ```

---

### Step 2: Implement Sub-Profession Classification Helper in `bot.py` / `app.py`

Create a classification helper function `classify_job_profession(job)`:
```python
def classify_job_profession(job: dict) -> dict:
    """
    Classifica automaticamente a vaga em uma sub-profissão e categoria com base no título e requisitos.
    """
    title = normalize_str(job.get('title', ''))
    reqs = normalize_str(job.get('requirements', ''))
    full = title + " " + reqs

    # 1. Operações Físicas
    if any(k in title for k in ['pintor industrial', 'jateador']):
        job['profession'] = 'Pintor Industrial'
        job['category'] = 'operacoes_fisicas'
    elif any(k in title for k in ['mecanico industrial', 'mecanico de manutencao']):
        job['profession'] = 'Mecânico Industrial'
        job['category'] = 'operacoes_fisicas'
    elif any(k in title for k in ['eletricista industrial', 'eletrotecnico']):
        job['profession'] = 'Eletricista Industrial'
        job['category'] = 'operacoes_fisicas'
    elif any(k in title for k in ['soldador', 'caldeireiro']):
        job['profession'] = 'Soldador'
        job['category'] = 'operacoes_fisicas'
    elif any(k in title for k in ['operador de producao', 'auxiliar de producao']):
        job['profession'] = 'Operador de Produção'
        job['category'] = 'operacoes_fisicas'
    elif any(k in title for k in ['usinagem', 'torneiro mecanico']):
        job['profession'] = 'Usinagem'
        job['category'] = 'operacoes_fisicas'

    # 2. Logística
    elif any(k in title for k in ['almoxarife', 'auxiliar de almoxarifado']):
        job['profession'] = 'Almoxarife'
        job['category'] = 'logistica'
    elif any(k in title for k in ['conferente', 'conferente de estoque']):
        job['profession'] = 'Conferente de Estoque'
        job['category'] = 'logistica'
    elif any(k in title for k in ['operador de empilhadeira']):
        job['profession'] = 'Operador de Empilhadeira'
        job['category'] = 'logistica'
    elif any(k in title for k in ['assistente de logistica', 'analista de logistica']):
        job['profession'] = 'Assistente de Logística'
        job['category'] = 'logistica'

    # 3. Administrativo
    elif any(k in title for k in ['assistente financeiro', 'analista financeiro']):
        job['profession'] = 'Assistente Financeiro'
        job['category'] = 'administrativo'
    elif any(k in title for k in ['auxiliar de contabilidade', 'assistente contabil']):
        job['profession'] = 'Auxiliar de Contabilidade'
        job['category'] = 'administrativo'
    elif any(k in title for k in ['assistente de faturamento']):
        job['profession'] = 'Assistente de Faturamento'
        job['category'] = 'administrativo'
    elif any(k in title for k in ['assistente administrativo', 'auxiliar administrativo']):
        job['profession'] = 'Assistente Administrativo'
        job['category'] = 'administrativo'

    # 4. Criativos
    elif any(k in title for k in ['designer grafico', 'arte finalista']):
        job['profession'] = 'Designer Gráfico'
        job['category'] = 'criativos'
    elif any(k in title for k in ['editor de video', 'motion designer', 'videomaker']):
        job['profession'] = 'Editor de Vídeo'
        job['category'] = 'criativos'
    elif any(k in title for k in ['ux designer', 'ui designer', 'product designer']):
        job['profession'] = 'UX Designer'
        job['category'] = 'criativos'
    elif any(k in title for k in ['copywriter', 'redator']):
        job['profession'] = 'Copywriter'
        job['category'] = 'criativos'

    # 5. Inteligência de Vendas
    elif any(k in title for k in ['sdr', 'bdr', 'inside sales']):
        job['profession'] = 'SDR'
        job['category'] = 'inteligencia_vendas'
    elif any(k in title for k in ['executivo de vendas', 'account executive', 'closer']):
        job['profession'] = 'Executivo de Vendas'
        job['category'] = 'inteligencia_vendas'
    elif any(k in title for k in ['salesops', 'sales operations']):
        job['profession'] = 'Sales Operations'
        job['category'] = 'inteligencia_vendas'

    # 6. Engenharia de Dados
    elif any(k in title for k in ['engenheiro de dados', 'data engineer']):
        job['profession'] = 'Engenheiro de Dados'
        job['category'] = 'engenharia_dados'
    elif any(k in title for k in ['analytics engineer']):
        job['profession'] = 'Analytics Engineer'
        job['category'] = 'engenharia_dados'
    elif any(k in title for k in ['arquiteto de dados', 'data architect']):
        job['profession'] = 'Arquiteto de Dados'
        job['category'] = 'engenharia_dados'

    return job
```
Integrate `classify_job_profession(job)` into `is_job_relevant()` or the scraper job ingestion flow in `app.py` (`run_hunt_background` and `api_search`).

---

### Step 3: Update `app.py` Seed Search & Background Hunt Loop

1. **`run_initial_seed_search()`** in `app.py` (lines 684–699):
   Update `seed_keywords` to include broad category macro keywords:
   ```python
   async def run_initial_seed_search():
       """Executa buscas iniciais para popular todas as categorias de vagas."""
       seed_keywords = [
           "Indústria",
           "Logística",
           "Administrativo",
           "Design",
           "Vendas",
           "Engenharia de Dados",
           "Python",
           "Analytics Engineer",
           "IA-Ops",
           "Growth Engineer",
           "React"
       ]
       platforms = ["workana", "gupy", "catho", "infojobs"]
       for kw in seed_keywords:
           for plat in platforms:
               try:
                   module = importlib.import_module(f"scrapers.{plat}")
                   if inspect.iscoroutinefunction(module.scrape):
                       jobs = await module.scrape(keyword=kw, level="Todos", location="Todos", country="Todos")
                   else:
                       jobs = await asyncio.to_thread(module.scrape, keyword=kw, level="Todos", location="Todos", country="Todos")
                   if isinstance(jobs, list) and jobs:
                       from bot import classify_job_profession
                       classified = [classify_job_profession(j) for j in jobs]
                       await asyncio.to_thread(insert_jobs, classified)
               except Exception as e:
                   logger.error(f"Seed search error [{plat} - {kw}]: {e}")
   ```

2. **`background_periodic_hunt_loop()`** in `app.py` (lines 701–717):
   Update keywords list to cycle through broad categories:
   ```python
   async def background_periodic_hunt_loop():
       """Loop contínuo que busca novas vagas a cada 10 minutos (600 segundos)."""
       macro_keywords = [
           "Indústria",
           "Logística",
           "Administrativo",
           "Design",
           "Vendas",
           "Engenharia de Dados",
           "Python",
           "IA-Ops"
       ]
       while True:
           await asyncio.sleep(600)
           logger.info("[BACKGROUND AUTO-HUNT] Executando busca automatizada periódica...")
           try:
               for kw in macro_keywords:
                   for plat in ["workana", "gupy", "catho", "infojobs"]:
                       module = importlib.import_module(f"scrapers.{plat}")
                       if inspect.iscoroutinefunction(module.scrape):
                           jobs = await module.scrape(keyword=kw, level="Todos", location="Todos", country="Todos")
                       else:
                           jobs = await asyncio.to_thread(module.scrape, keyword=kw, level="Todos", location="Todos", country="Todos")
                       if isinstance(jobs, list) and jobs:
                           from bot import classify_job_profession
                           classified = [classify_job_profession(j) for j in jobs]
                           await asyncio.to_thread(insert_jobs, classified)
           except Exception as e:
               logger.error(f"Erro no loop de busca periódica: {e}")
   ```

---

## 5. Verification Method

To verify the implementation independently:

1. **Syntax Verification**:
   ```powershell
   python -m py_compile bot.py app.py scrapers/*.py
   ```
   *Expected outcome*: Zero compilation syntax errors.

2. **Unit Test Suite**:
   ```powershell
   python -m pytest tests/ -v
   ```
   *Expected outcome*: All test suites pass without regression.

3. **Macro-Search & Classification Integration Test**:
   Create `tests/test_milestone2_macro_searches.py` with test cases:
   - Test macro keyword matching for all 6 broad categories: `"Indústria"`, `"Logística"`, `"Administrativo"`, `"Design"`, `"Vendas"`, `"Engenharia de Dados"`.
   - Test sub-profession relevance and classification for `"Pintor Industrial"`, `"Almoxarife"`, `"Assistente Financeiro"`, `"Editor de Vídeo"`, `"SDR"`, `"Engenheiro de Dados"`.
   - Test that `"Pintor Industrial"` is NOT rejected by `global_title_blacklist`.
   - Test that invalid cross-domain jobs (e.g. "Professor de Contabilidade") are rejected by `blacklist`.
   - Run:
     ```powershell
     python -m pytest tests/test_milestone2_macro_searches.py -v
     ```

### Invalidation Conditions
- Any existing IT/AI test in `tests/` failing due to keyword or blacklist changes.
- Macro searches for `"Indústria"` or `"Logística"` returning 0 matches when given valid mock jobs like `"Pintor Industrial"` or `"Almoxarife"`.
- `py_compile` throwing syntax or import errors.
