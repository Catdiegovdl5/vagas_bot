# Handoff Report — Milestone 1: UI Taxonomy Update (Requirement R1)

## 1. Observation

### Key Codebase Locations in `static/index.html`
- **File Path**: `C:\Users\99196\OneDrive\Documentos\vagas_bot\static\index.html`
- **Lines 1026–1035**: `PROFESSION_CATEGORIES` JavaScript array currently defines 8 category objects:
  ```javascript
  const PROFESSION_CATEGORIES = [
      { id: "all", name: "Todas as Vagas", icon: "<i class='fa-solid fa-layer-group'></i>", label_pt: "Todas as Vagas", label_en: "All Jobs", kws: [] },
      { id: "growth_engineer", name: "Growth & Tráfego", icon: "<i class='fa-solid fa-bullhorn'></i>", label_pt: "Growth & Tráfego", label_en: "Growth & Traffic", kws: ["growth", "trafego", "ads", "gtm", "ga4", "pixel", "facebook", "google ads", "meta ads", "tiktok ads", "media buyer", "inbound", "seo", "crm"] },
      { id: "performance", name: "Performance & Mídia", icon: "<i class='fa-solid fa-chart-pie'></i>", label_pt: "Performance & Mídia", label_en: "Performance & Media", kws: ["performance", "midia paga", "paid media", "gestor de trafego", "tráfego pago"] },
      { id: "ia_ops", name: "IA-Ops", icon: "<i class='fa-solid fa-robot'></i>", label_pt: "IA-Ops", label_en: "IA-Ops Specialist", kws: ["n8n", "make", "zapier", "inteligencia artificial", "ia generativa", "chatgpt", "llm", "prompt engineer", "agentes ia"] },
      { id: "sdr_tecnico", name: "SDR Técnico", icon: "<i class='fa-solid fa-phone'></i>", label_pt: "SDR Técnico", label_en: "Technical SDR", kws: ["sdr", "bdr", "inside sales", "prospeccao", "sales development", "vendas", "closer", "outbound"] },
      { id: "analytics_engineer", name: "Analytics Engineer", icon: "<i class='fa-solid fa-chart-line'></i>", label_pt: "Analytics Engineer", label_en: "Analytics Engineer", kws: ["analytics engineer", "power bi", "powerbi", "data analyst", "analista de dados", "looker", "metabase", "dbt", "databricks"] },
      { id: "server_side_tracking", name: "Server-Side Tracking", icon: "<i class='fa-solid fa-gear'></i>", label_pt: "Server-Side Tracking", label_en: "Server-Side Tracking", kws: ["server-side", "gtm server", "stape", "meta capi", "conversions api", "tracking server", "tag manager"] },
      { id: "outros", name: "Outros", icon: "<i class='fa-solid fa-folder'></i>", label_pt: "Outros", label_en: "Others", kws: ["outros", "geral", "suporte", "design", "devops"] }
  ];
  ```

- **Lines 1060–1094**: `matchesCategory(j, catObj)` handles string normalization (`normStr`) and keyword matching across job title (`j.title`) and profession (`j.profession`). For `id === 'outros'`, it dynamically checks all categories in `PROFESSION_CATEGORIES` except `all` and `outros`.
- **Lines 1404–1472**: `renderCategoryDrawers()` renders the category accordions in `#category-drawers`. Currently hardcodes 3 accordion groups (`🚀 Marketing & Growth`, `🧠 Engenharia de IA & Dados`, `📁 Geral & Outros`).
- **Lines 1286–1295**: `renderHuntQuickPills()` generates quick selection pills in the Hunt Modal (`#hunt-quick-pills`) by iterating dynamically over `PROFESSION_CATEGORIES`.
- **Lines 1766, 1797–1800**: `filterData()` filters job postings dynamically using `PROFESSION_CATEGORIES.find(c => c.id === selectedCategory)`.

---

## 2. Logic Chain

1. **Category Expansion (Requirement R1.1)**:
   - The prompt specifies 6 new categories:
     1. Operações Físicas (`operacoes_fisicas`)
     2. Logística (`logistica`)
     3. Administrativo (`administrativo`)
     4. Criativos (`criativos`)
     5. Inteligência de Vendas (`inteligencia_vendas`)
     6. Engenharia de Dados (`engenharia_dados`)
   - Merging these 6 new categories into `PROFESSION_CATEGORIES` along with existing ones yields a total of 14 categories (including `all` and `outros`).

2. **Mega-Menu Drawer Accordion Organization (Requirement R1.2)**:
   - The UI category system displays drawers inside `<details class="group">` collapsible accordions inside `#category-drawers`.
   - To transform the drawer system into a comprehensive mega-menu, the 14 categories should be organized into 4 logical, professional drawer groups in `renderCategoryDrawers()`:
     - **Drawer Group 1: `🚀 Marketing, Growth & Vendas`**
       - `growth_engineer` (Growth & Tráfego)
       - `performance` (Performance & Mídia)
       - `sdr_tecnico` (SDR Técnico)
       - `inteligencia_vendas` (Inteligência de Vendas)
       - `criativos` (Criativos & Design)
     - **Drawer Group 2: `🧠 Engenharia, IA & Dados`**
       - `ia_ops` (IA-Ops Specialist)
       - `engenharia_dados` (Engenharia de Dados)
       - `analytics_engineer` (Analytics Engineer)
       - `server_side_tracking` (Server-Side Tracking)
     - **Drawer Group 3: `🏭 Operações, Logística & Administrativo`**
       - `operacoes_fisicas` (Operações Físicas)
       - `logistica` (Logística)
       - `administrativo` (Administrativo)
     - **Drawer Group 4: `📁 Geral & Visão Global`**
       - `all` (Todas as Vagas)
       - `outros` (Outros)

3. **JS Constant & Mapping Consistency (Requirement R1.3)**:
   - Keywords (`kws`) for each of the 6 new categories must be accent-free, lowercase, normalized strings compatible with `normStr()` in `matchesCategory()`:
     - `operacoes_fisicas`: `["operacao", "operacoes", "industrial", "manutencao", "tecnico", "operador", "producao", "fabrica", "mecanico", "eletricista", "soldador", "usinagem", "montador", "qualidade"]`
     - `logistica`: `["logistica", "almoxarife", "estoque", "expedicao", "deposito", "transporte", "inventario", "motorista", "conferente", "supply chain", "cadeia de suprimentos", "faturamento"]`
     - `administrativo`: `["administrativo", "auxiliar administrativo", "assistente administrativo", "recepcionista", "secretaria", "financeiro", "faturamento", "recursos humanos", "rh", "departamento pessoal", "dp", "atendimento", "backoffice"]`
     - `criativos`: `["criativo", "criativos", "designer", "editor de video", "copywriter", "social media", "motion", "artes", "audiovisual", "design", "conteudo", "redator"]`
     - `inteligencia_vendas`: `["inteligencia de vendas", "sales ops", "commercial", "comercial", "crm", "sales intelligence", "prospeccao", "inside sales", "bdr", "sdr", "closer"]`
     - `engenharia_dados`: `["engenharia de dados", "data engineer", "engenheiro de dados", "etl", "pipeline", "sql", "big data", "spark", "airflow", "snowflake", "databricks", "data warehouse", "dw"]`
   - FontAwesome icons should be assigned to each new category:
     - `operacoes_fisicas`: `<i class='fa-solid fa-industry'></i>`
     - `logistica`: `<i class='fa-solid fa-truck-ramp-box'></i>`
     - `administrativo`: `<i class='fa-solid fa-briefcase'></i>`
     - `criativos`: `<i class='fa-solid fa-palette'></i>`
     - `inteligencia_vendas`: `<i class='fa-solid fa-chart-user'></i>`
     - `engenharia_dados`: `<i class='fa-solid fa-database'></i>`
   - Portuguese and English labels (`label_pt`, `label_en`) should be provided for i18n support.

---

## 3. Caveats

- **Scope Boundary**: As an Explorer agent, no direct modifications were made to source files (`static/index.html`). All changes must be executed by the Worker agent.
- **Backend Classification Alignment (M2 Dependency)**: Milestone 1 strictly targets frontend taxonomy in `static/index.html`. Updating backend rules (`bot.py` `CO_OCCURRENCE_RULES`) is planned for Milestone 2. However, frontend keyword matching in `matchesCategory()` acts as a fallback on job titles, ensuring immediate UI filtering functionality even before backend scrapers are updated.

---

## 4. Conclusion & Recommended Worker Implementation Plan

### Recommended Implementation Steps for Worker:

1. **Update `PROFESSION_CATEGORIES` array in `static/index.html` (lines 1026–1035)**:
   Replace/Expand `PROFESSION_CATEGORIES` with the complete 14-item list:
   ```javascript
   const PROFESSION_CATEGORIES = [
       { id: "all", name: "Todas as Vagas", icon: "<i class='fa-solid fa-layer-group'></i>", label_pt: "Todas as Vagas", label_en: "All Jobs", kws: [] },
       { id: "growth_engineer", name: "Growth & Tráfego", icon: "<i class='fa-solid fa-bullhorn'></i>", label_pt: "Growth & Tráfego", label_en: "Growth & Traffic", kws: ["growth", "trafego", "ads", "gtm", "ga4", "pixel", "facebook", "google ads", "meta ads", "tiktok ads", "media buyer", "inbound", "seo", "crm"] },
       { id: "performance", name: "Performance & Mídia", icon: "<i class='fa-solid fa-chart-pie'></i>", label_pt: "Performance & Mídia", label_en: "Performance & Media", kws: ["performance", "midia paga", "paid media", "gestor de trafego", "tráfego pago"] },
       { id: "ia_ops", name: "IA-Ops", icon: "<i class='fa-solid fa-robot'></i>", label_pt: "IA-Ops", label_en: "IA-Ops Specialist", kws: ["n8n", "make", "zapier", "inteligencia artificial", "ia generativa", "chatgpt", "llm", "prompt engineer", "agentes ia"] },
       { id: "sdr_tecnico", name: "SDR Técnico", icon: "<i class='fa-solid fa-phone'></i>", label_pt: "SDR Técnico", label_en: "Technical SDR", kws: ["sdr", "bdr", "inside sales", "prospeccao", "sales development", "vendas", "closer", "outbound"] },
       { id: "inteligencia_vendas", name: "Inteligência de Vendas", icon: "<i class='fa-solid fa-chart-user'></i>", label_pt: "Inteligência de Vendas", label_en: "Sales Intelligence", kws: ["inteligencia de vendas", "sales ops", "commercial", "comercial", "crm", "sales intelligence", "prospeccao", "inside sales", "bdr", "sdr", "closer"] },
       { id: "criativos", name: "Criativos & Design", icon: "<i class='fa-solid fa-palette'></i>", label_pt: "Criativos & Design", label_en: "Creatives & Design", kws: ["criativo", "criativos", "designer", "editor de video", "copywriter", "social media", "motion", "artes", "audiovisual", "design", "conteudo", "redator"] },
       { id: "analytics_engineer", name: "Analytics Engineer", icon: "<i class='fa-solid fa-chart-line'></i>", label_pt: "Analytics Engineer", label_en: "Analytics Engineer", kws: ["analytics engineer", "power bi", "powerbi", "data analyst", "analista de dados", "looker", "metabase", "dbt", "databricks"] },
       { id: "engenharia_dados", name: "Engenharia de Dados", icon: "<i class='fa-solid fa-database'></i>", label_pt: "Engenharia de Dados", label_en: "Data Engineering", kws: ["engenharia de dados", "data engineer", "engenheiro de dados", "etl", "pipeline", "sql", "big data", "spark", "airflow", "snowflake", "databricks", "data warehouse", "dw"] },
       { id: "server_side_tracking", name: "Server-Side Tracking", icon: "<i class='fa-solid fa-gear'></i>", label_pt: "Server-Side Tracking", label_en: "Server-Side Tracking", kws: ["server-side", "gtm server", "stape", "meta capi", "conversions api", "tracking server", "tag manager"] },
       { id: "operacoes_fisicas", name: "Operações Físicas", icon: "<i class='fa-solid fa-industry'></i>", label_pt: "Operações Físicas", label_en: "Physical Operations", kws: ["operacao", "operacoes", "industrial", "manutencao", "tecnico", "operador", "producao", "fabrica", "mecanico", "eletricista", "soldador", "usinagem", "montador", "qualidade"] },
       { id: "logistica", name: "Logística", icon: "<i class='fa-solid fa-truck-ramp-box'></i>", label_pt: "Logística", label_en: "Logistics & Supply Chain", kws: ["logistica", "almoxarife", "estoque", "expedicao", "deposito", "transporte", "inventario", "motorista", "conferente", "supply chain", "cadeia de suprimentos", "faturamento"] },
       { id: "administrativo", name: "Administrativo", icon: "<i class='fa-solid fa-briefcase'></i>", label_pt: "Administrativo", label_en: "Administrative & Support", kws: ["administrativo", "auxiliar administrativo", "assistente administrativo", "recepcionista", "secretaria", "financeiro", "faturamento", "recursos humanos", "rh", "departamento pessoal", "dp", "atendimento", "backoffice"] },
       { id: "outros", name: "Outros", icon: "<i class='fa-solid fa-folder'></i>", label_pt: "Outros", label_en: "Others", kws: ["outros", "geral", "suporte", "devops"] }
   ];
   ```

2. **Update `renderCategoryDrawers()` in `static/index.html` (lines 1408–1436)**:
   Restructure `groups` array:
   ```javascript
   const groups = [
       {
           title: "🚀 Marketing, Growth & Vendas",
           open: true,
           items: [
               PROFESSION_CATEGORIES.find(c => c.id === 'growth_engineer'),
               PROFESSION_CATEGORIES.find(c => c.id === 'performance'),
               PROFESSION_CATEGORIES.find(c => c.id === 'sdr_tecnico'),
               PROFESSION_CATEGORIES.find(c => c.id === 'inteligencia_vendas'),
               PROFESSION_CATEGORIES.find(c => c.id === 'criativos')
           ].filter(Boolean)
       },
       {
           title: "🧠 Engenharia, IA & Dados",
           open: false,
           items: [
               PROFESSION_CATEGORIES.find(c => c.id === 'ia_ops'),
               PROFESSION_CATEGORIES.find(c => c.id === 'engenharia_dados'),
               PROFESSION_CATEGORIES.find(c => c.id === 'analytics_engineer'),
               PROFESSION_CATEGORIES.find(c => c.id === 'server_side_tracking')
           ].filter(Boolean)
       },
       {
           title: "🏭 Operações, Logística & Administrativo",
           open: false,
           items: [
               PROFESSION_CATEGORIES.find(c => c.id === 'operacoes_fisicas'),
               PROFESSION_CATEGORIES.find(c => c.id === 'logistica'),
               PROFESSION_CATEGORIES.find(c => c.id === 'administrativo')
           ].filter(Boolean)
       },
       {
           title: "📁 Geral & Visão Global",
           open: false,
           items: [
               PROFESSION_CATEGORIES.find(c => c.id === 'all'),
               PROFESSION_CATEGORIES.find(c => c.id === 'outros')
           ].filter(Boolean)
       }
   ];
   ```

---

## 5. Verification Method

1. **Static Syntax Verification**:
   - Parse `static/index.html` via Python `html.parser` or JavaScript syntax check to verify zero syntax/tag balance errors.
   ```bash
   python -c "import html.parser; html.parser.HTMLParser().feed(open('static/index.html', encoding='utf-8').read())"
   ```

2. **DOM & Category Mapping Verification**:
   - Verify that all 14 categories in `PROFESSION_CATEGORIES` exist and are correctly linked inside the 4 drawer groups.
   - Test `renderHuntQuickPills()` to ensure pills for all non-all categories appear in the Hunt modal.

3. **Empirical UI Verification**:
   - Launch application server: `python app.py`
   - Access `http://localhost:8000/` and verify that:
     - 4 collapsible accordion drawers render in the top navigation area.
     - Clicking each category drawer pill filters the job list appropriately and updates pill counters.
