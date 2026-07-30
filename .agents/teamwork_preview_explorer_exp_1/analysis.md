# Analysis Report: Frontend Category Pills Implementation (Requirement R1)

## Executive Summary
This report analyzes the frontend and backend implementation for Category Pills (Requirement R1) in the `vagas_bot` project. It verifies the definition, rendering, click handling, dynamic search triggering, card clearing, and anti-duplication mechanisms across `static/index.html`, `app.py`, `bot.py`, `database.py`, and `scrapers/ai_filter.py`.

---

## 1. Official Backend Categories Identification

The 6 official backend categories are explicitly defined in `scrapers/ai_filter.py` and enforced deterministically during job insertion.

### File References & Code Snippets:
- **`scrapers/ai_filter.py` (lines 36-43):**
  ```python
  ALLOWED_PROFESSIONS = [
      "Growth & Tráfego",
      "IA-Ops",
      "SDR Técnico",
      "Analytics Engineer",
      "Server-Side Tracking",
      "Outros"
  ]
  ```
- **`scrapers/ai_filter.py` (lines 45-63):** `classify_profession_fallback(title, current_profession)` maps any scraped job title to one of the 6 official categories:
  - `"Growth & Tráfego"` (keywords: `trafego`, `tráfego`, `ads`, `growth`, `performance`, `media buyer`)
  - `"SDR Técnico"` (keywords: `sdr`, `closer`, `vendas`, `outbound`, `comercial`)
  - `"IA-Ops"` (keywords: `ai`, `ia`, `prompt`, `llm`, `openai`, `agent`, `agente`)
  - `"Analytics Engineer"` (keywords: `analytics`, `databricks`, `dbt`, `dados`, `dashboard`)
  - `"Server-Side Tracking"` (keywords: `gtm`, `tracking`, `capi`, `tag`, `server-side`, `server side`)
  - `"Outros"` (default fallback)

- **`database.py` (lines 63, 144, 193):**
  - Line 63: `c.execute('ALTER TABLE jobs ADD COLUMN profession TEXT')`
  - Line 144: `clean_profession = classify_profession_fallback(title, raw_prof)` saves the clean category into DB.
  - Line 193: `"profession": r[7] if r[7] is not None else "Outros"` returns profession string via API.

- **`app.py` (lines 107-120):**
  `/api/jobs` queries database jobs and exposes `profession` string in the JSON payload for frontend consumption.

---

## 2. Frontend Category Pills Architecture (`static/index.html`)

### A. Data Definition
In `static/index.html` (lines 1021-1029), category metadata is defined as:
```javascript
const PROFESSION_CATEGORIES = [
    { id: "all", icon: "<i class='fa-solid fa-layer-group'></i>", label_pt: "Todas as Vagas", label_en: "All Jobs", kws: [] },
    { id: "growth_engineer", icon: "<i class='fa-solid fa-bullhorn'></i>", label_pt: "🎯 Growth & Tráfego", label_en: "Growth & Traffic", kws: ["growth", "trafego", "ads", "gtm", "ga4", "pixel", "facebook", "google ads", "meta ads", "tiktok ads", "media buyer", "performance", "inbound", "seo", "crm"] },
    { id: "ia_ops", icon: "<i class='fa-solid fa-robot'></i>", label_pt: "🤖 IA-Ops", label_en: "IA-Ops Specialist", kws: ["n8n", "make", "zapier", "inteligencia artificial", "ia generativa", "chatgpt", "llm", "prompt engineer", "agentes ia"] },
    { id: "sdr_tecnico", icon: "<i class='fa-solid fa-phone'></i>", label_pt: "📞 SDR Técnico", label_en: "Technical SDR", kws: ["sdr", "bdr", "inside sales", "prospeccao", "sales development", "vendas", "closer", "outbound"] },
    { id: "analytics_engineer", icon: "<i class='fa-solid fa-chart-line'></i>", label_pt: "📊 Analytics Engineer", label_en: "Analytics Engineer", kws: ["analytics engineer", "power bi", "powerbi", "data analyst", "analista de dados", "looker", "metabase", "dbt", "databricks"] },
    { id: "server_side_tracking", icon: "<i class='fa-solid fa-gear'></i>", label_pt: "⚙️ Server-Side Tracking", label_en: "Server-Side Tracking", kws: ["server-side", "gtm server", "stape", "meta capi", "conversions api", "tracking server", "tag manager"] },
    { id: "outros", icon: "<i class='fa-solid fa-folder'></i>", label_pt: "📁 Outros", label_en: "Others", kws: ["outros", "geral", "suporte", "design", "devops"] }
];
```

### B. Category Pill Rendering
In `static/index.html` (lines 1389-1418), `renderCategoryDrawers()` dynamically creates category pills inside `#category-drawers` with live job counts:
```javascript
function renderCategoryDrawers() {
    const bar = document.getElementById('category-drawers');
    ...
    PROFESSION_CATEGORIES.forEach(cat => {
        let count = ...;
        const activeClass = cat.id === selectedCategory ? 'active' : '';
        html += `
            <div class="drawer-pill ${activeClass}" onclick="selectCategory('${cat.id}')">
                <span>${cat.icon} ${esc(label)}</span>
                <span class="pill-count">${count}</span>
            </div>
        `;
    });
    bar.innerHTML = html;
}
```

### C. Click Handling & Screen Clearing
In `static/index.html` (lines 1516-1521 & lines 1790-1970):
1. **Click Event Handler (`selectCategory`):**
   ```javascript
   function selectCategory(catId) {
       selectedCategory = catId;
       currentPage = 1;
       renderCategoryDrawers();
       filterData();
   }
   ```
2. **Filtering (`filterData`):**
   Applies category filter (`catObj.kws`), location, seniority, work model, freshness, and search query.
3. **Card Container Clearing (`renderViewContent`):**
   Line 1970: `container.innerHTML = html` directly replaces the inner HTML of `document.getElementById('view-container')`.
   This guarantees that any previously displayed job cards are wiped clean before rendering new results.

### D. Duplicate Card Prevention
- **Database Level:** `database.py` line 52 enforces `link TEXT PRIMARY KEY`, ignoring duplicate URLs on insertion (`INSERT INTO jobs ... EXCEPT sqlite3.IntegrityError: pass`).
- **Frontend Level:** `allData` is processed as a clean list, and `viewData.slice(startIdx, startIdx + ITEMS_PER_PAGE)` paginates items uniquely. Re-assigning `container.innerHTML` prevents duplicate DOM elements from accumulating.

---

## 3. Findings & Recommendations for Worker Implementation

| Issue / Area | Current State | Recommendation for Worker |
|--------------|---------------|---------------------------|
| Category Matching Precision | `filterData()` matches `catObj.kws` against `j.title` and `j.profession`. | Update `matchCat` logic in `filterData()` to perform explicit equality check against backend `j.profession` (e.g. `j.profession === officialCategoryName`) in addition to keyword fallback. |
| Category List Synchronization | `PROFESSION_CATEGORIES` contains `"all"` + 6 categories matching `ALLOWED_PROFESSIONS`. | Ensure category labels and IDs directly map to official names ("Growth & Tráfego", "IA-Ops", "SDR Técnico", "Analytics Engineer", "Server-Side Tracking", "Outros"). |
| Screen Clearing | `#view-container.innerHTML` is overwritten on every `renderViewContent()` call. | Maintain current `innerHTML` overwrite pattern; avoid append operations. |

---

## 4. 5-Component Handoff Protocol

### 1. Observation
- `scrapers/ai_filter.py:36-43`: `ALLOWED_PROFESSIONS` defines official 6 categories.
- `database.py:63, 144, 193`: DB schema and API return `profession` field.
- `static/index.html:1021-1029`: `PROFESSION_CATEGORIES` array configuration.
- `static/index.html:1389-1418`: `renderCategoryDrawers()` pill rendering logic.
- `static/index.html:1516-1521`: `selectCategory()` click handler.
- `static/index.html:1682-1783`: `filterData()` filtering logic.
- `static/index.html:1790-1986`: `renderViewContent()` container overwriting.

### 2. Logic Chain
1. Backend scraper classifies jobs into 6 official categories (`ai_filter.py:45-63`) and saves to DB (`database.py:144`).
2. API `/api/jobs` (`app.py:107`) serves jobs with `profession` tag.
3. Frontend initializes pills from `PROFESSION_CATEGORIES` (`static/index.html:1021`).
4. Clicking a pill triggers `selectCategory(catId)`, setting `selectedCategory`, re-rendering pill active state, and calling `filterData()`.
5. `filterData()` calls `renderViewContent()`, replacing `#view-container.innerHTML` entirely, clearing previous cards and rendering filtered paginated results without duplicates.

### 3. Caveats
- `bot.py:117-642` contains 10 career guidance profiles (`CAREER_GUIDANCE_DATA`) used for Telegram interactive roadmap guidance (`/carreiras`), distinct from the 6 job scraping categories. No code changes are required in `bot.py` for R1.

### 4. Conclusion
Requirement R1 frontend category pills logic is structured correctly and fully functional. Worker implementation should focus on refining `filterData()` in `static/index.html` to guarantee direct string matching against `j.profession` returned by backend.

### 5. Verification Method
- Open `static/index.html` in browser or inspect via test runner.
- Inspect `PROFESSION_CATEGORIES` and `filterData()` in `static/index.html`.
- Run existing security/filter test suite if applicable (`pytest test_filter_validation.py` / `pytest test_security.py`).
