# Handoff Report: Scrapers & Category Architecture Exploration

## 1. Observation

Direct observations made during codebase inspection:

1. **Active Scrapers & Invocation Structure**:
   - `bot.py` lines 85–103 define `DEFAULT_SETTINGS["platforms"]` containing 17 scrapers: `jsearch`, `jooble`, `workana`, `remotar`, `novenove`, `github_vagas`, `indeed`, `linkedin`, `glassdoor`, `infojobs`, `gupy`, `catho`, `vagas_com`, `programathor`, `coodesh`, `geekhunter`, `gmail`.
   - `bot.py` lines 270–310 in `_do_hunt()` dynamically import modules (`importlib.import_module(f"scrapers.{plat}")`) and call `module.scrape(keyword=plat_search_keyword, level="Todos", location=loc_val, country=loc_val, contract=contract_val)`.

2. **Category & Keyword Dispatch Flow**:
   - `bot.py` lines 182–195 (`process_mega_category`) define legacy `MAGIC_CATEGORIES`:
     ```python
     MAGIC_CATEGORIES = {
         "ti": ["Suporte N1", "Suporte Técnico", "Help Desk Júnior", "Técnico de Apoio ao Usuário de Informática", "Analista de Suporte Júnior"],
         "sdr": ["SDR Júnior", "SDR", "Inside Sales Júnior", "Assistente de Pré-Vendas", "Assistente de Growth"],
         "adm": ["Assistente Administrativo", "Auxiliar Administrativo", "Digitador", "Data Entry"],
         "dev": ["Desenvolvedor Júnior", "Programador Trainee", "Programador Júnior", "Desenvolvedor Node.JS Júnior"],
         "log": ["Auxiliar de Almoxarifado", "Auxiliar de Expedição", "Auxiliar de Estoque", "Assistente de Logística"]
     }
     ```
   - `_do_hunt()` receives the keyword string, resolves it through `SEARCH_MAPPING`, appends `level` (if `level != "Todos"` and platform is not freelance), and passes `keyword` to `module.scrape(**kwargs)`.

3. **Scraper Specialization & URL Mapping Quirks**:
   - **`scrapers/vagas_com.py`** (lines 22–75): Uses a hardcoded URL slug dictionary `vagas_com_mapping`. For example:
     ```python
     "especialista em ia": "inteligencia-artificial",
     "gestor de trafego": "gestor-de-trafego-pago",
     "assistente de logistica": "assistente-logistica"
     ```
     Fallback (line 82): `search_kw = vagas_com_mapping.get(kw_clean, kw_str.replace(' ', '-'))`.
   - **`scrapers/workana.py`** (lines 28–45): Uses `bot.CO_OCCURRENCE_RULES` to extract only the 1st term of `Grupo A`:
     ```python
     grupo_a = bot.CO_OCCURRENCE_RULES[mapped_key][0]
     search_kw = grupo_a[0]
     ```
     Rationale: Workana treats multi-word search strings as strict `AND`, resulting in 0 matches if long phrases are passed.
   - **`scrapers/github_vagas.py`** (lines 16–18): Hardcoded queries targeting software developer issue repositories:
     ```python
     repos = "repo:frontendbr/vagas repo:backend-br/vagas repo:react-brasil/vagas repo:qa-brasil/vagas"
     ```
   - **Tech-only platforms** (`scrapers/programathor.py`, `scrapers/geekhunter.py`, `scrapers/coodesh.py`): Query tech-only portals.

---

## 2. Logic Chain

1. **Premise**: Generic bulk category searches (e.g. searching `"Operações Físicas"` or `"Inteligência de Vendas"`) fail on native platform search APIs because job boards index specific job titles (e.g., `"Conferente"`, `"SDR"`), not abstract category names.
2. **Observation**: `bot.py` dispatches category searches by expanding a category key into a list of specific search terms (via `MAGIC_CATEGORIES`) and invoking `_do_hunt()` for each term.
3. **Observation**: `_do_hunt()` passes `keyword` to `module.scrape(**kwargs)`. Each scraper converts `keyword` into an HTTP query string, API parameter, or URL slug.
4. **Deduction**: Supporting the 6 new canonical categories requires:
   a. Replacing `MAGIC_CATEGORIES` in `bot.py` with term lists for the 6 new categories:
      - `operacoes_fisicas` (e.g. `"Operador de Produção"`, `"Auxiliar de Operações"`, `"Conferente"`, `"Operador de Empilhadeira"`, `"Auxiliar de Serviços Gerais"`, `"Mecanico de Manutenção"`, `"Operador de Maquinas"`)
      - `logistica` (e.g. `"Assistente de Logística"`, `"Auxiliar de Logística"`, `"Auxiliar de Almoxarifado"`, `"Auxiliar de Expedição"`, `"Analista de Logística"`, `"Controlador de Estoque"`, `"Operador Logístico"`)
      - `administrativo` (e.g. `"Assistente Administrativo"`, `"Auxiliar Administrativo"`, `"Assistente Financeiro"`, `"Assistente de Faturamento"`, `"Recepcionista"`, `"Analista Administrativo"`, `"Auxiliar de Escritório"`, `"Data Entry"`)
      - `criativos_performance` (e.g. `"Editor de Vídeo"`, `"Motion Designer"`, `"Designer Gráfico"`, `"Copywriter"`, `"Video Maker"`, `"Gestor de Tráfego"`, `"Criador de Conteúdo"`, `"Social Media"`)
      - `inteligencia_vendas` (e.g. `"SDR"`, `"BDR"`, `"Inside Sales"`, `"Analista de Sales Ops"`, `"Analista de CRM"`, `"Executivo de Vendas"`, `"Analista de Inteligência de Mercado"`, `"Growth Hacker"`)
      - `engenharia_ia_dados` (e.g. `"Engenheiro de IA"`, `"Engenheiro de Dados"`, `"Cientista de Dados"`, `"Analista de Dados"`, `"Analista de Power BI"`, `"Desenvolvedor de Agentes IA"`, `"Prompt Engineer"`, `"Machine Learning Engineer"`, `"Desenvolvedor Python"`)
   b. Updating `SEARCH_MAPPING`, `CO_OCCURRENCE_RULES`, and `BLACKLIST_PROFILES` in `bot.py` to recognize all terms across the 6 categories.
   c. Updating `vagas_com.py` slug dictionary (`vagas_com_mapping`) to include URL slugs for all newly introduced terms.
   d. Updating `workana.py` `MAPPED_KEYS` / `CO_OCCURRENCE_RULES` extraction so non-tech and tech keywords map to single-word root terms for Workana.
   e. Adding early returns in tech-only scrapers (`github_vagas.py`, `programathor.py`, `geekhunter.py`, `coodesh.py`) when non-tech categories are requested to avoid unnecessary network overhead and zero-result queries.

---

## 3. Caveats

- **No live code modification performed**: This investigation is strictly read-only. Source code files outside `.agents/` were not modified.
- **External API Rate Limits**: Scraping speed and status depend on external network stability (e.g., Apify API token for Meta Ads, RapidAPI key for JSearch, Cloudflare stealth for Infojobs).
- **No caveats** regarding codebase structure clarity — all scraper mechanisms were fully inspected and traced.

---

## 4. Conclusion

The existing scraper infrastructure in `scrapers/` and `bot.py` can be refactored to support the 6 new categories natively by:
1. Updating `bot.py`'s `MAGIC_CATEGORIES`, `SEARCH_MAPPING`, and `CO_OCCURRENCE_RULES` to dispatch concrete job title term sets for each of the 6 categories.
2. Updating `scrapers/vagas_com.py` with URL slug mappings for all new terms.
3. Updating `scrapers/workana.py` to extract single-word root terms for new category keywords.
4. Adding category guards in tech-only scrapers (`github_vagas.py`, `programathor.py`, `geekhunter.py`, `coodesh.py`) to bypass non-tech search terms.

---

## 5. Verification Method

1. **Verify Report Files**:
   - Confirm `analysis.md` and `handoff.md` exist in `C:\Users\99196\OneDrive\Documentos\vagas_bot\.agents\teamwork_preview_explorer_scrapers_1\`.
2. **Test Suite Execution**:
   - Run `python run_tests.py` or `pytest test_scrapers.py` to verify scraper parameter validation and test execution.
   - Run `python test_menu_expansion.py` and `python test_boolean_scrapers.py` to verify category button expansion logic.
