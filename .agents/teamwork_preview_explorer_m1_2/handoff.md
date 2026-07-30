# Handoff Report — Milestone 1 (UI Taxonomy Update)

## 1. Observation

Direct observations from examining `C:\Users\99196\OneDrive\Documentos\vagas_bot\PROJECT.md`, `C:\Users\99196\OneDrive\Documentos\vagas_bot\static\index.html`, and `C:\Users\99196\OneDrive\Documentos\vagas_bot\app.py`:

- **Current `PROFESSION_CATEGORIES` Constant** (`static/index.html:1026-1035`):
  Contains 8 entries: `all`, `growth_engineer`, `performance`, `ia_ops`, `sdr_tecnico`, `analytics_engineer`, `server_side_tracking`, and `outros`.
- **Current Category Drawer Rendering** (`static/index.html:1404-1472`):
  `renderCategoryDrawers()` builds 3 accordion drawers (`🚀 Marketing & Growth`, `🧠 Engenharia de IA & Dados`, `📁 Geral & Outros`).
- **Category Matching Logic** (`static/index.html:1063-1094`):
  `matchesCategory(j, catObj)` tests `title` and `profession` fields against `catObj.label_pt` and `catObj.kws`. For `id === 'outros'`, it dynamically filters out any job matching any keyword of other defined categories.
- **Quick Pills Generator** (`static/index.html:1286-1295`):
  `renderHuntQuickPills()` dynamically iterates `PROFESSION_CATEGORIES` to build quick search pills for the "Nova Busca ao Vivo" modal.
- **Backend Category Filter Interface** (`app.py:107-117`):
  `api_get_jobs(profession=...)` filters jobs where `profession.lower()` is contained in `job.profession` or `job.title`.
- **Icon Standards**:
  Several existing drawer headers in `static/index.html` use raw unicode emojis (`🚀`, `🧠`, `📁`). Modernized FontAwesome vector icons (`<i class="fa-solid fa-..."></i>`) are used elsewhere throughout the UI.

---

## 2. Logic Chain

1. **Category Taxonomy Merging**:
   - The user specified 6 new broad professional categories: `Operações Físicas`, `Logística`, `Administrativo`, `Criativos`, `Inteligência de Vendas`, and `Engenharia de Dados`.
   - Merging these 6 new categories with the 6 existing niche categories (`growth_engineer`, `performance`, `ia_ops`, `sdr_tecnico`, `analytics_engineer`, `server_side_tracking`) plus `all` and `outros` creates a complete 14-category taxonomy.
   - Each new category requires a unique `id`, human-readable `name` (sent to `/api/jobs`), FontAwesome `icon`, Portuguese `label_pt`, English `label_en`, and a comprehensive list of normalized keywords (`kws`).

2. **Mega-Menu Drawer Architecture**:
   - Rather than an unstructured list of pills, category drawers should be grouped into 5 professional domain drawers inside `renderCategoryDrawers()`:
     1. **🏭 Operações & Logística** (`operacoes_fisicas`, `logistica`)
     2. **🏢 Gestão & Administrativo** (`administrativo`, `inteligencia_vendas`, `sdr_tecnico`)
     3. **🎨 Criativos & Marketing** (`criativos`, `growth_engineer`, `performance`)
     4. **🧠 IA, Dados & Tech** (`engenharia_dados`, `ia_ops`, `analytics_engineer`, `server_side_tracking`)
     5. **🌐 Visão Geral & Outros** (`all`, `outros`)
   - Replacing unicode emojis with FontAwesome vector icons in drawer summary headers (`<i class="fa-solid fa-industry"></i>`, `<i class="fa-solid fa-building"></i>`, etc.) standardizes the UI and ensures compliance with project icon guidelines.

3. **JS Mappings & Constants Consistency**:
   - Updating `PROFESSION_CATEGORIES` automatically updates `renderHuntQuickPills()`.
   - Updating `matchesCategory(j, catObj)` to check both `catObj.label_pt` and `catObj.name` guarantees that backend-assigned `profession` strings match correctly.
   - The `outros` category automatically excludes all 12 specific categories because it filters against `PROFESSION_CATEGORIES`.

---

## 3. Caveats

- **Read-Only Scope**: This analysis was conducted strictly read-only. No source files were modified.
- **Scraper / Backend Alignment (Milestone 2 Dependency)**: M1 updates the UI frontend taxonomy (`static/index.html`). Backend macro-searches and `CO_OCCURRENCE_RULES` alignment in `bot.py` and `app.py` will be performed in Milestone 2. However, M1 UI components handle current or missing backend data gracefully via fallback keyword searching in `matchesCategory()`.

---

## 4. Conclusion

Requirement R1 can be satisfied with high precision by implementing a targeted update to `static/index.html`:

1. **Update `PROFESSION_CATEGORIES` Constant**: Add 6 new category objects (`operacoes_fisicas`, `logistica`, `administrativo`, `criativos`, `inteligencia_vendas`, `engenharia_dados`) with proper icons, labels, and keywords.
2. **Re-architect `renderCategoryDrawers()` Mega-Menu**: Restructure categories into 5 professional accordion drawers using FontAwesome icons.
3. **Enhance `matchesCategory()`**: Guarantee fallback matching against `catObj.name` as well as `catObj.label_pt` and `catObj.kws`.

### Detailed Step-by-Step Implementation Strategy for Worker:

#### Step 1: Update `PROFESSION_CATEGORIES` in `static/index.html` (around line 1026)
Replace `PROFESSION_CATEGORIES` with:
```javascript
const PROFESSION_CATEGORIES = [
    { id: "all", name: "Todas as Vagas", icon: "<i class='fa-solid fa-layer-group'></i>", label_pt: "Todas as Vagas", label_en: "All Jobs", kws: [] },
    { id: "operacoes_fisicas", name: "Operações Físicas", icon: "<i class='fa-solid fa-industry'></i>", label_pt: "Operações Físicas", label_en: "Physical Operations", kws: ["operacoes fisicas", "operacao fisica", "operacao", "producao", "industrial", "manutencao", "operador", "tecnico", "fabrica", "mecanico", "eletricista", "soldador", "usinagem", "montador", "linha de producao"] },
    { id: "logistica", name: "Logística", icon: "<i class='fa-solid fa-truck-ramp-box'></i>", label_pt: "Logística", label_en: "Logistics & Supply Chain", kws: ["logistica", "almoxarife", "almoxarifado", "estoque", "expedicao", "recebimento", "transporte", "frotas", "frete", "empilhadeira", "inventario", "supply chain"] },
    { id: "administrativo", name: "Administrativo", icon: "<i class='fa-solid fa-briefcase'></i>", label_pt: "Administrativo", label_en: "Administrative & Finance", kws: ["administrativo", "auxiliar administrativo", "assistente administrativo", "financeiro", "recursos humanos", "rh", "recepcao", "faturamento", "contabilidade", "fiscal", "secretaria", "departamento pessoal"] },
    { id: "criativos", name: "Criativos", icon: "<i class='fa-solid fa-palette'></i>", label_pt: "Criativos", label_en: "Creative & Design", kws: ["criativos", "design", "designer", "editor de video", "motion", "copywriter", "arte finalista", "ui", "ux", "midia social", "social media", "audiovisual", "ilustrador"] },
    { id: "inteligencia_vendas", name: "Inteligência de Vendas", icon: "<i class='fa-solid fa-user-tie'></i>", label_pt: "Inteligência de Vendas", label_en: "Sales Intelligence", kws: ["inteligencia de vendas", "sales intelligence", "b2b", "account executive", "inside sales", "gerente de contas", "comercial", "executivo de vendas", "pre-vendas", "outbound", "closer"] },
    { id: "engenharia_dados", name: "Engenharia de Dados", icon: "<i class='fa-solid fa-database'></i>", label_pt: "Engenharia de Dados", label_en: "Data Engineering", kws: ["engenharia de dados", "data engineer", "engenheiro de dados", "etl", "data pipeline", "spark", "hadoop", "airflow", "snowflake", "bigquery", "sql"] },
    { id: "growth_engineer", name: "Growth & Tráfego", icon: "<i class='fa-solid fa-bullhorn'></i>", label_pt: "Growth & Tráfego", label_en: "Growth & Traffic", kws: ["growth", "trafego", "ads", "gtm", "ga4", "pixel", "facebook", "google ads", "meta ads", "tiktok ads", "media buyer", "inbound", "seo", "crm"] },
    { id: "performance", name: "Performance & Mídia", icon: "<i class='fa-solid fa-chart-pie'></i>", label_pt: "Performance & Mídia", label_en: "Performance & Media", kws: ["performance", "midia paga", "paid media", "gestor de trafego", "tráfego pago"] },
    { id: "ia_ops", name: "IA-Ops", icon: "<i class='fa-solid fa-robot'></i>", label_pt: "IA-Ops", label_en: "IA-Ops Specialist", kws: ["n8n", "make", "zapier", "inteligencia artificial", "ia generativa", "chatgpt", "llm", "prompt engineer", "agentes ia"] },
    { id: "sdr_tecnico", name: "SDR Técnico", icon: "<i class='fa-solid fa-phone'></i>", label_pt: "SDR Técnico", label_en: "Technical SDR", kws: ["sdr", "bdr", "inside sales", "prospeccao", "sales development", "vendas", "closer", "outbound"] },
    { id: "analytics_engineer", name: "Analytics Engineer", icon: "<i class='fa-solid fa-chart-line'></i>", label_pt: "Analytics Engineer", label_en: "Analytics Engineer", kws: ["analytics engineer", "power bi", "powerbi", "data analyst", "analista de dados", "looker", "metabase", "dbt", "databricks"] },
    { id: "server_side_tracking", name: "Server-Side Tracking", icon: "<i class='fa-solid fa-gear'></i>", label_pt: "Server-Side Tracking", label_en: "Server-Side Tracking", kws: ["server-side", "gtm server", "stape", "meta capi", "conversions api", "tracking server", "tag manager"] },
    { id: "outros", name: "Outros", icon: "<i class='fa-solid fa-folder'></i>", label_pt: "Outros", label_en: "Others", kws: ["outros", "geral", "suporte", "design", "devops"] }
];
```

#### Step 2: Refactor `renderCategoryDrawers()` Mega-Menu Accordions (around line 1404)
Update `groups` definition to group categories into 5 professional drawers with FontAwesome icons:
```javascript
function renderCategoryDrawers() {
    const bar = document.getElementById('category-drawers');
    const lang = currentLang;

    const groups = [
        {
            title: "<i class='fa-solid fa-industry'></i> Operações & Logística",
            open: true,
            items: [
                PROFESSION_CATEGORIES.find(c => c.id === 'operacoes_fisicas'),
                PROFESSION_CATEGORIES.find(c => c.id === 'logistica')
            ].filter(Boolean)
        },
        {
            title: "<i class='fa-solid fa-building'></i> Gestão & Administrativo",
            open: true,
            items: [
                PROFESSION_CATEGORIES.find(c => c.id === 'administrativo'),
                PROFESSION_CATEGORIES.find(c => c.id === 'inteligencia_vendas'),
                PROFESSION_CATEGORIES.find(c => c.id === 'sdr_tecnico')
            ].filter(Boolean)
        },
        {
            title: "<i class='fa-solid fa-palette'></i> Criativos & Marketing",
            open: false,
            items: [
                PROFESSION_CATEGORIES.find(c => c.id === 'criativos'),
                PROFESSION_CATEGORIES.find(c => c.id === 'growth_engineer'),
                PROFESSION_CATEGORIES.find(c => c.id === 'performance')
            ].filter(Boolean)
        },
        {
            title: "<i class='fa-solid fa-microchip'></i> IA, Dados & Tech",
            open: false,
            items: [
                PROFESSION_CATEGORIES.find(c => c.id === 'engenharia_dados'),
                PROFESSION_CATEGORIES.find(c => c.id === 'ia_ops'),
                PROFESSION_CATEGORIES.find(c => c.id === 'analytics_engineer'),
                PROFESSION_CATEGORIES.find(c => c.id === 'server_side_tracking')
            ].filter(Boolean)
        },
        {
            title: "<i class='fa-solid fa-layer-group'></i> Visão Geral & Outros",
            open: false,
            items: [
                PROFESSION_CATEGORIES.find(c => c.id === 'all'),
                PROFESSION_CATEGORIES.find(c => c.id === 'outros')
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

#### Step 3: Verify `matchesCategory()` (around line 1063)
Ensure matching evaluates `catObj.name` in addition to `catObj.label_pt`:
```javascript
if (profLower) {
    const catLabelNorm = normStr(catObj.label_pt || '');
    const catNameNorm = normStr(catObj.name || '');
    if (profLower === catLabelNorm || profLower.includes(catLabelNorm) || profLower === catNameNorm || profLower.includes(catNameNorm)) return true;
}
```

---

## 5. Verification Method

To verify implementation accuracy and non-regression:

1. **Static HTML Structural Inspection**:
   - Check `static/index.html` using a Python script or regex to confirm all 14 categories (`operacoes_fisicas`, `logistica`, `administrativo`, `criativos`, `inteligencia_vendas`, `engenharia_dados`, etc.) exist in `PROFESSION_CATEGORIES`.
   - Confirm all 5 professional group drawers are present in `renderCategoryDrawers()`.

2. **Automated Filter Validation Test**:
   - Run existing unit test suite:
     ```powershell
     python -m pytest test_filter_validation.py -v
     ```
   - Confirm zero unicode emoji failures and full FontAwesome icon compliance.

3. **FastAPI Route Verification**:
   - Start local app server:
     ```powershell
     python app.py
     ```
   - Request dashboard endpoint `/` or `/api/jobs?profession=Operações%20Físicas` to confirm proper responses and UI loading.
