# Audit Report: Requirement R1 — Work Mode Drawers (Remoto / Presencial / Híbrido)

## 1. Observation

### 1.1 UI Markup & Component Structure (`static/index.html`)
- **Location**: `static/index.html` (Line 496):
  ```html
  <!-- Linha 2: Gavetas de Modelo de Trabalho (Remoto, Presencial, Híbrido) -->
  <div class="category-drawers-bar" id="workmodel-drawers"></div>
  ```
- **Category Array Definition** (Lines 629–634):
  ```javascript
  const WORKMODEL_CATEGORIES = [
      { id: "all", icon: "<i class='fa-solid fa-globe'></i>", label_pt: "Todas as Modalidades", label_en: "All Work Models" },
      { id: "remoto", icon: "<i class='fa-solid fa-house-laptop'></i>", label_pt: "100% Remoto", label_en: "100% Remote" },
      { id: "presencial", icon: "<i class='fa-solid fa-building'></i>", label_pt: "Presencial", label_en: "On-site" },
      { id: "hibrido", icon: "<i class='fa-solid fa-arrows-split-up-and-left'></i>", label_pt: "Híbrido", label_en: "Hybrid" }
  ];
  ```

### 1.2 Frontend State & Event Handlers (`static/index.html`)
- **State Initialization** (Line 645):
  ```javascript
  let selectedWorkModel = "all";
  ```
- **Pill Click Handler & Filtering Flow** (Lines 969–974):
  ```javascript
  function selectWorkModel(wmId) {
      selectedWorkModel = wmId;
      currentPage = 1;
      renderWorkModelDrawers();
      filterData();
  }
  ```
- **Drawer Rendering & Count Calculation** (Lines 895–926):
  ```javascript
  function renderWorkModelDrawers() {
      const bar = document.getElementById('workmodel-drawers');
      const lang = currentLang;
      let html = '';

      WORKMODEL_CATEGORIES.forEach(wm => {
          let count = 0;
          if (wm.id === 'all') {
              count = allData.length;
          } else {
              count = allData.filter(j => {
                  const reqLower = (j.requirements || '').toLowerCase() + ' ' + (j.title || '').toLowerCase();
                  if (wm.id === 'remoto') return reqLower.includes('remoto') || reqLower.includes('home office') || reqLower.includes('remote');
                  if (wm.id === 'presencial') return reqLower.includes('presencial');
                  if (wm.id === 'hibrido') return reqLower.includes('hibrido') || reqLower.includes('híbrido');
                  return false;
              }).length;
          }
          ...
  ```
- **Filter Evaluation Logic in `filterData()`** (Lines 1019–1025):
  ```javascript
  let matchWm = true;
  if (selectedWorkModel !== 'all') {
      const fullText = (titleLower + ' ' + reqLower);
      if (selectedWorkModel === 'remoto') matchWm = fullText.includes('remoto') || fullText.includes('home office') || fullText.includes('remote');
      else if (selectedWorkModel === 'presencial') matchWm = fullText.includes('presencial');
      else if (selectedWorkModel === 'hibrido') matchWm = fullText.includes('hibrido') || fullText.includes('híbrido');
  }
  ```

### 1.3 Backend & Database Structure (`app.py`, `database.py`)
- `app.py` exposes `/api/jobs` returning `{"jobs": get_jobs()}` (Line 46).
- `database.py` manages table `jobs` (Lines 16–33). Schema includes: `id, title, company, budget, link, platform, added_at, job_type, profession, level, requirements`.
- There is **no dedicated `work_model` column** in the SQLite database schema; work mode is dynamically computed on the client side from `title` and `requirements`.

---

## 2. Logic Chain

1. **Feminine & Plural Term Matching Flaw**:
   - *Observation*: In JavaScript, `'vaga remota'.includes('remoto')` evaluates to `false`. `'modalidade híbrida'.includes('híbrido')` evaluates to `false`. `'vagas presenciais'.includes('presencial')` evaluates to `false`.
   - *Reasoning*: `renderWorkModelDrawers()` and `filterData()` use simple `.includes('remoto')`, `.includes('presencial')`, and `.includes('hibrido')`.
   - *Deduction*: Portuguese job postings heavily utilize feminine forms ("Vaga 100% Remota", "Atuação Híbrida") and plural forms ("Vagas Presenciais"). Any job post formatted as feminine or plural is currently miscounted as `0` and excluded when clicking the drawer pill.

2. **Overlapping & False Positive Classification**:
   - *Observation*: `if (wm.id === 'remoto') return reqLower.includes('remoto') || reqLower.includes('home office') || reqLower.includes('remote');` runs independently of `presencial` or `hibrido`.
   - *Reasoning*: A job post stating *"Modelo Híbrido: 2 dias no escritório (presencial) e 3 dias em home office"* contains both `"presencial"`, `"híbrido"`, and `"home office"`.
   - *Deduction*: This job matches ALL THREE drawers (Remoto, Presencial, and Híbrido). When a user clicks **100% Remoto**, hybrid jobs appear. When a user clicks **Presencial**, hybrid jobs appear. Furthermore, a 100% remote job stating *"Não é presencial"* will match the Presencial drawer because `.includes('presencial')` evaluates to `true`.

3. **Code Duplication & Inconsistency**:
   - *Observation*: Work mode matching logic is duplicated identically in two separate functions: `renderWorkModelDrawers()` (lines 906-910) and `filterData()` (lines 1021-1024).
   - *Reasoning*: Having duplicate string-matching blocks increases maintenance risk. Also, `renderWorkModelDrawers` concatenates `requirements + title` while `filterData` concatenates `title + requirements`.

4. **1-Click UX & Instant Filtering Assessment**:
   - *Observation*: Clicking a drawer pill invokes `selectWorkModel(wmId)` -> updates state `selectedWorkModel` -> resets `currentPage = 1` -> updates UI pill state via `.active` -> triggers `filterData()`.
   - *Deduction*: The UI structure, styling, 1-click event listeners, state tracking, active tab highlighting, and PT/EN i18n support are **functioning correctly and respond instantly**. The defects reside strictly in the text matching algorithm used to determine work model eligibility.

---

## 3. Caveats

- **Backend Scrapers**: Scrapers extract raw text into `title` and `requirements`. Some platforms (e.g. Workana, Remotar) are 100% remote by default, but if the scraped text doesn't contain explicit keywords like "remoto", "remote", or "home office", the current client-side filter falls back to excluding them unless "Todas as Modalidades" is selected.
- **Database Schema**: No schema changes to `jobs.db` were attempted or inspected beyond read-only queries, as client-side filtering can handle work mode detection directly if given robust regex patterns.

---

## 4. Conclusion

Requirement R1: **Work Mode Drawers (Remoto / Presencial / Híbrido)** is **partially implemented**. 

### Strengths:
- HTML markup structure (`#workmodel-drawers`) is clean and co-located with category and seniority drawers.
- CSS styling with dark/light theme variables and active states works smoothly.
- 1-click instant filtering state management (`selectWorkModel`) and PT/EN language translation work as expected.

### Critical Deficiencies:
1. **Feminine / Plural Word Mismatch**: "remota", "remotas", "híbrida", "hibrida", "híbridas", "presenciais" are ignored by current `.includes()` checks.
2. **Hybrid Overlap into 100% Remote**: Hybrid jobs matching "home office" leak into the 100% Remoto filter.
3. **Negative Phrase False Positives**: Text like "Não é presencial" triggers the Presencial drawer filter.

### Recommended Fix (Proposed Implementation Patch for Implementer):

Replace duplicate inline checks in `static/index.html` with a unified helper function `getJobWorkModel(job)`:

```javascript
function getJobWorkModel(job) {
    const title = (job.title || '').toLowerCase();
    const reqs = (job.requirements || '').toLowerCase();
    const loc = (job.location || '').toLowerCase();
    
    // Normalize accents (NFD)
    const norm = (title + ' ' + reqs + ' ' + loc).normalize('NFD').replace(/[\u0300-\u036f]/g, '');

    const hasHybrid = /\b(hibrid[oa]s?|hybrid)\b/.test(norm);
    const hasRemote = /\b(remot[oa]s?|home\s*office|remote|teletrabalho|wfh|work\s*from\s*home|anywhere)\b/.test(norm);
    const hasPresential = /\b(presencia[li]s?|onsite|on-site)\b/.test(norm);

    // Enforce hierarchy: Hybrid takes priority, followed by Remote vs Presencial
    if (hasHybrid) return 'hibrido';
    if (hasRemote && !hasPresential) return 'remoto';
    if (hasPresential && !hasRemote) return 'presencial';
    if (hasRemote) return 'remoto';
    if (hasPresential) return 'presencial';
    return 'outros';
}
```

Then update `renderWorkModelDrawers()`:
```javascript
count = allData.filter(j => {
    if (wm.id === 'all') return true;
    return getJobWorkModel(j) === wm.id;
}).length;
```

And update `filterData()`:
```javascript
let matchWm = true;
if (selectedWorkModel !== 'all') {
    matchWm = (getJobWorkModel(j) === selectedWorkModel);
}
```

---

## 5. Verification Method

### Step 1: File Inspection
- Inspect `static/index.html` at lines 895–926 and 1019–1025. Verify whether `getJobWorkModel` helper or regex pattern matching `remot[oa]s?`, `hibrid[oa]s?`, `presencia[li]s?` is implemented.

### Step 2: Browser / Unit Verification Test Case
- Load dashboard page in browser or test JS snippets against mock job objects:
  - Job A: `{title: "Vaga 100% Remota - Dev Python", requirements: "Atuação home office"}` -> Expected: Drawer `100% Remoto`.
  - Job B: `{title: "Desenvolvedor React", requirements: "Atuação em modelo híbrido (2 dias presencial, 3 dias remoto)"}` -> Expected: Drawer `Híbrido` (NOT 100% Remoto).
  - Job C: `{title: "Analista de Suporte", requirements: "Vagas presenciais em São Paulo"}` -> Expected: Drawer `Presencial`.

### Step 3: Invalidation Condition
- If a job with title `"Vaga Remota"` or requirements `"Modalidade Híbrida"` shows a pill count of `0` or fails to filter on click, the fix is invalid.
