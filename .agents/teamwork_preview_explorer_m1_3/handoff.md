# Handoff Report — Milestone 1: UI Taxonomy Update & Mega-Menu Drawers

## 1. Observation
- **Target Files**:
  - `C:\Users\99196\OneDrive\Documentos\vagas_bot\PROJECT.md` (lines 18–22): Defines Milestone 1 scope as updating `static/index.html` mega-menu drawers and JS profession mapping constants.
  - `C:\Users\99196\OneDrive\Documentos\vagas_bot\static\index.html`: Web UI dashboard containing profession category definitions, drawer rendering, and filter functions.
- **Current `PROFESSION_CATEGORIES` Constant (`static/index.html:1026-1035`)**:
  ```javascript
  const PROFESSION_CATEGORIES = [
      { id: "all", name: "Todas as Vagas", icon: "<i class='fa-solid fa-layer-group'></i>", label_pt: "Todas as Vagas", label_en: "All Jobs", kws: [] },
      { id: "growth_engineer", name: "Growth & Tráfego", icon: "<i class='fa-solid fa-bullhorn'></i>", label_pt: "Growth & Tráfego", label_en: "Growth & Traffic", kws: [...] },
      { id: "performance", name: "Performance & Mídia", icon: "<i class='fa-solid fa-chart-pie'></i>", label_pt: "Performance & Mídia", label_en: "Performance & Media", kws: [...] },
      { id: "ia_ops", name: "IA-Ops", icon: "<i class='fa-solid fa-robot'></i>", label_pt: "IA-Ops", label_en: "IA-Ops Specialist", kws: [...] },
      { id: "sdr_tecnico", name: "SDR Técnico", icon: "<i class='fa-solid fa-phone'></i>", label_pt: "SDR Técnico", label_en: "Technical SDR", kws: [...] },
      { id: "analytics_engineer", name: "Analytics Engineer", icon: "<i class='fa-solid fa-chart-line'></i>", label_pt: "Analytics Engineer", label_en: "Analytics Engineer", kws: [...] },
      { id: "server_side_tracking", name: "Server-Side Tracking", icon: "<i class='fa-solid fa-gear'></i>", label_pt: "Server-Side Tracking", label_en: "Server-Side Tracking", kws: [...] },
      { id: "outros", name: "Outros", icon: "<i class='fa-solid fa-folder'></i>", label_pt: "Outros", label_en: "Others", kws: [...] }
  ];
  ```
- **Current Drawer Accordion Rendering (`static/index.html:1404-1472`)**:
  `renderCategoryDrawers()` organizes categories into 3 basic groups:
  1. `🚀 Marketing & Growth` (`growth_engineer`, `sdr_tecnico`, `performance`)
  2. `🧠 Engenharia de IA & Dados` (`ia_ops`, `analytics_engineer`, `server_side_tracking`)
  3. `📁 Geral & Outros` (`outros`, `all`)
- **Current Dynamic Category Filtering & Exclusion (`static/index.html:1063-1094`)**:
  `matchesCategory(j, catObj)` tests title/profession keywords. For `outros`, it excludes any job matching non-`outros` categories defined in `PROFESSION_CATEGORIES`.
- **Current Modal Quick Pills (`static/index.html:1286-1295`)**:
  `renderHuntQuickPills()` iterates over `PROFESSION_CATEGORIES` to populate pill buttons in `modal-hunt`.
- **Backend Search Integration (`app.py:107-120`)**:
  `/api/jobs` filters by `profession` parameter using substring matching on `profession` or `title`.

---

## 2. Logic Chain
1. **User Requirement R1 Analysis**:
   - Merge 6 new categories:
     1. Operações Físicas
     2. Logística
     3. Administrativo
     4. Criativos
     5. Inteligência de Vendas
     6. Engenharia de Dados
   - Transform category system into a comprehensive mega-menu of professional drawers.
   - Maintain complete JS constant & keyword mapping consistency across all UI components.
2. **Category Definition Expansion**:
   Adding the 6 new categories expands `PROFESSION_CATEGORIES` from 8 to 14 entries. Each new entry must adhere to the exact JS schema object (`id`, `name`, `icon`, `label_pt`, `label_en`, `kws`):
   - `operacoes_fisicas`: `["operacao", "operador", "manutencao", "producao", "industrial", "fabrica", "mecanico", "eletricista", "tecnico", "obras", "servicos gerais", "pintor", "montador"]`
   - `logistica`: `["logistica", "almoxarife", "almoxarifado", "estoque", "expedicao", "estoquista", "frete", "transportes", "supply chain", "armazem", "recebimento", "compras"]`
   - `administrativo`: `["administrativo", "auxiliar administrativo", "assistente administrativo", "secretaria", "recepcionista", "backoffice", "financeiro", "contabilidade", "rh", "recursos humanos", "faturamento"]`
   - `criativos`: `["designer", "ui/ux", "copywriter", "redator", "edicao de video", "editor de video", "design grafico", "criador de conteudo", "social media", "motion designer", "illustrator", "figma"]`
   - `inteligencia_vendas`: `["inteligencia de vendas", "sales intelligence", "sales ops", "revops", "revenue ops", "crm analyst", "analista de crm", "salesforce", "hubspot", "operacoes de vendas"]`
   - `engenharia_dados`: `["engenheiro de dados", "data engineer", "etl", "pipeline de dados", "spark", "pyspark", "airflow", "snowflake", "bigquery", "data warehouse", "sql", "redshift"]`
3. **Mega-Menu Accordion Architecture**:
   With 14 total categories, `renderCategoryDrawers()` should organize them into 6 domain-focused accordion drawers:
   - **Group 1: 🚀 Marketing & Growth** (`growth_engineer`, `performance`, `criativos`)
   - **Group 2: 💼 Vendas & Comercial** (`sdr_tecnico`, `inteligencia_vendas`)
   - **Group 3: 🧠 Engenharia, IA & Dados** (`engenharia_dados`, `analytics_engineer`, `ia_ops`, `server_side_tracking`)
   - **Group 4: 🏭 Operações & Logística** (`operacoes_fisicas`, `logistica`)
   - **Group 5: 🏢 Gestão & Administrativo** (`administrativo`)
   - **Group 6: 📁 Outros & Visão Geral** (`outros`, `all`)
4. **Cascading Effects & Consistency Check**:
   - `matchesCategory()`: Because `catObj.id === 'outros'` filters out all other categories in `PROFESSION_CATEGORIES`, adding the 6 new categories automatically prevents physical ops, logistics, admin, creative, sales intelligence, and data engineering jobs from mistakenly sinking into `Outros`.
   - `renderHuntQuickPills()`: Automatically picks up all 13 active categories (excluding `all`), populating the "Nova Busca ao Vivo" modal.
   - `selectCategory()`: Properly passes `catObj.name` to `/api/jobs?profession=...` which matches against title/profession in `app.py`.

---

## 3. Recommended Step-by-Step Implementation Strategy for Worker

### Step 1: Update `PROFESSION_CATEGORIES` in `static/index.html` (Line ~1026)
Replace `PROFESSION_CATEGORIES` definition with the full 14-category array:
```javascript
const PROFESSION_CATEGORIES = [
    { id: "all", name: "Todas as Vagas", icon: "<i class='fa-solid fa-layer-group'></i>", label_pt: "Todas as Vagas", label_en: "All Jobs", kws: [] },
    { id: "growth_engineer", name: "Growth & Tráfego", icon: "<i class='fa-solid fa-bullhorn'></i>", label_pt: "Growth & Tráfego", label_en: "Growth & Traffic", kws: ["growth", "trafego", "ads", "gtm", "ga4", "pixel", "facebook", "google ads", "meta ads", "tiktok ads", "media buyer", "inbound", "seo", "crm"] },
    { id: "performance", name: "Performance & Mídia", icon: "<i class='fa-solid fa-chart-pie'></i>", label_pt: "Performance & Mídia", label_en: "Performance & Media", kws: ["performance", "midia paga", "paid media", "gestor de trafego", "tráfego pago"] },
    { id: "criativos", name: "Criativos", icon: "<i class='fa-solid fa-palette'></i>", label_pt: "Criativos", label_en: "Creative & Design", kws: ["designer", "ui/ux", "copywriter", "redator", "edicao de video", "editor de video", "design grafico", "criador de conteudo", "social media", "motion designer", "illustrator", "figma"] },
    { id: "sdr_tecnico", name: "SDR Técnico", icon: "<i class='fa-solid fa-phone'></i>", label_pt: "SDR Técnico", label_en: "Technical SDR", kws: ["sdr", "bdr", "inside sales", "prospeccao", "sales development", "vendas", "closer", "outbound"] },
    { id: "inteligencia_vendas", name: "Inteligência de Vendas", icon: "<i class='fa-solid fa-magnifying-glass-chart'></i>", label_pt: "Inteligência de Vendas", label_en: "Sales Intelligence & RevOps", kws: ["inteligencia de vendas", "sales intelligence", "sales ops", "revops", "revenue ops", "crm analyst", "analista de crm", "salesforce", "hubspot", "operacoes de vendas"] },
    { id: "engenharia_dados", name: "Engenharia de Dados", icon: "<i class='fa-solid fa-database'></i>", label_pt: "Engenharia de Dados", label_en: "Data Engineering", kws: ["engenheiro de dados", "data engineer", "etl", "pipeline de dados", "spark", "pyspark", "airflow", "snowflake", "bigquery", "data warehouse", "sql", "redshift"] },
    { id: "analytics_engineer", name: "Analytics Engineer", icon: "<i class='fa-solid fa-chart-line'></i>", label_pt: "Analytics Engineer", label_en: "Analytics Engineer", kws: ["analytics engineer", "power bi", "powerbi", "data analyst", "analista de dados", "looker", "metabase", "dbt", "databricks"] },
    { id: "ia_ops", name: "IA-Ops", icon: "<i class='fa-solid fa-robot'></i>", label_pt: "IA-Ops", label_en: "IA-Ops Specialist", kws: ["n8n", "make", "zapier", "inteligencia artificial", "ia generativa", "chatgpt", "llm", "prompt engineer", "agentes ia"] },
    { id: "server_side_tracking", name: "Server-Side Tracking", icon: "<i class='fa-solid fa-gear'></i>", label_pt: "Server-Side Tracking", label_en: "Server-Side Tracking", kws: ["server-side", "gtm server", "stape", "meta capi", "conversions api", "tracking server", "tag manager"] },
    { id: "operacoes_fisicas", name: "Operações Físicas", icon: "<i class='fa-solid fa-industry'></i>", label_pt: "Operações Físicas", label_en: "Physical Operations", kws: ["operacao", "operador", "manutencao", "producao", "industrial", "fabrica", "mecanico", "eletricista", "tecnico", "obras", "servicos gerais", "pintor", "montador"] },
    { id: "logistica", name: "Logística", icon: "<i class='fa-solid fa-truck-ramp-box'></i>", label_pt: "Logística", label_en: "Logistics & Supply", kws: ["logistica", "almoxarife", "almoxarifado", "estoque", "expedicao", "estoquista", "frete", "transportes", "supply chain", "armazem", "recebimento", "compras"] },
    { id: "administrativo", name: "Administrativo", icon: "<i class='fa-solid fa-briefcase'></i>", label_pt: "Administrativo", label_en: "Administrative", kws: ["administrativo", "auxiliar administrativo", "assistente administrativo", "secretaria", "recepcionista", "backoffice", "financeiro", "contabilidade", "rh", "recursos humanos", "faturamento"] },
    { id: "outros", name: "Outros", icon: "<i class='fa-solid fa-folder'></i>", label_pt: "Outros", label_en: "Others", kws: ["outros", "geral", "suporte", "design", "devops"] }
];
```

### Step 2: Refactor `renderCategoryDrawers()` Mega-Menu Groups (Line ~1404)
Update `renderCategoryDrawers()` to render 6 professional accordion groups:
```javascript
function renderCategoryDrawers() {
    const bar = document.getElementById('category-drawers');
    const lang = currentLang;

    const groups = [
        {
            title: "🚀 Marketing & Growth",
            open: true,
            items: [
                PROFESSION_CATEGORIES.find(c => c.id === 'growth_engineer'),
                PROFESSION_CATEGORIES.find(c => c.id === 'performance'),
                PROFESSION_CATEGORIES.find(c => c.id === 'criativos')
            ].filter(Boolean)
        },
        {
            title: "💼 Vendas & Comercial",
            open: false,
            items: [
                PROFESSION_CATEGORIES.find(c => c.id === 'sdr_tecnico'),
                PROFESSION_CATEGORIES.find(c => c.id === 'inteligencia_vendas')
            ].filter(Boolean)
        },
        {
            title: "🧠 Engenharia, IA & Dados",
            open: false,
            items: [
                PROFESSION_CATEGORIES.find(c => c.id === 'engenharia_dados'),
                PROFESSION_CATEGORIES.find(c => c.id === 'analytics_engineer'),
                PROFESSION_CATEGORIES.find(c => c.id === 'ia_ops'),
                PROFESSION_CATEGORIES.find(c => c.id === 'server_side_tracking')
            ].filter(Boolean)
        },
        {
            title: "🏭 Operações & Logística",
            open: false,
            items: [
                PROFESSION_CATEGORIES.find(c => c.id === 'operacoes_fisicas'),
                PROFESSION_CATEGORIES.find(c => c.id === 'logistica')
            ].filter(Boolean)
        },
        {
            title: "🏢 Gestão & Administrativo",
            open: false,
            items: [
                PROFESSION_CATEGORIES.find(c => c.id === 'administrativo')
            ].filter(Boolean)
        },
        {
            title: "📁 Outros & Visão Geral",
            open: false,
            items: [
                PROFESSION_CATEGORIES.find(c => c.id === 'outros'),
                PROFESSION_CATEGORIES.find(c => c.id === 'all')
            ].filter(Boolean)
        }
    ];

    let html = `<div style="display:flex; flex-direction:column; gap:4px; margin-bottom: 20px;">`;
    
    groups.forEach(g => {
        html += `
        <details class="group" ${g.open ? 'open' : ''}>
            <summary>
                <span>${g.title}</span>
                <svg class="accordion-arrow" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"></polyline></svg>
            </summary>
            <div class="drawer-content">
        `;

        g.items.forEach(cat => {
            let count = 0;
            if (cat.id === 'all') {
                count = allData.length;
            } else {
                count = allData.filter(j => matchesCategory(j, cat)).length;
            }
            const label = lang === 'pt' ? cat.label_pt : cat.label_en;
            const activeClass = cat.id === selectedCategory ? 'active' : '';

            html += `
                <div class="drawer-pill ${activeClass}" onclick="selectCategory('${cat.id}')">
                    <span>${cat.icon} ${esc(label)}</span>
                    <span class="pill-count">${count}</span>
                </div>
            `;
        });
        
        html += `</div></details>`;
    });
    
    html += `</div>`;
    bar.innerHTML = html;
}
```

---

## 4. Caveats
- **Read-Only Mode**: No source files (`static/index.html`, `app.py`, `bot.py`) were modified during this investigation.
- **Backend Alignment in Milestone 2**: Milestone 1 focuses on frontend taxonomy UI & JS constants (`static/index.html`). Milestone 2 will handle backend rules (`CO_OCCURRENCE_RULES`, scrapers, and filtering in `bot.py`).

---

## 5. Conclusion
Milestone 1 requirement R1 is fully mapped out. Integrating the 6 new categories into `PROFESSION_CATEGORIES` and grouping all 14 categories into 6 professional accordion drawers in `renderCategoryDrawers()` will complete the UI taxonomy update seamlessly without breaking existing functionality or keyword matching.

---

## 6. Verification Method
1. **HTML & Syntax Verification**:
   Inspect `static/index.html` structure to ensure all JS objects are valid and all 14 categories are properly rendered.
2. **Automated Test Suite**:
   Run:
   `py -m pytest`
   Ensure existing backend and filter test suites pass without regression.
3. **UI Functional Verification**:
   - Check that all 6 mega-menu accordion drawers expand and collapse smoothly.
   - Verify category pills display correct job count badges.
   - Verify quick pills in "Nova Busca ao Vivo" modal render all 13 non-`all` category options.
