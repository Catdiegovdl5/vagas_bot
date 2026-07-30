# Handoff Report — Audit Requirement R2: City / State / Region Filter and Quick Pills

## 1. Observation

### HTML Markup (`static/index.html`)
- **Location Filter Section & Quick Pills** (lines 464–475):
  ```html
  <!-- Filtro 2: Cidade / Estado / Região -->
  <div class="filter-section">
      <div class="filter-title"><i class="fa-solid fa-location-dot"></i> Cidade / Região</div>
      <input type="text" id="loc-input" class="input-text" style="padding-left:10px; margin-bottom:8px;" placeholder="ex: São Paulo, Curitiba, RJ..." oninput="debounceFilter()">
      <div style="display:flex; flex-wrap:wrap; gap:4px;">
          <button class="drawer-pill" style="font-size:10px; padding:2px 6px;" onclick="setLocFilter('')">Todas</button>
          <button class="drawer-pill" style="font-size:10px; padding:2px 6px;" onclick="setLocFilter('São Paulo')">São Paulo</button>
          <button class="drawer-pill" style="font-size:10px; padding:2px 6px;" onclick="setLocFilter('Rio de Janeiro')">Rio de Janeiro</button>
          <button class="drawer-pill" style="font-size:10px; padding:2px 6px;" onclick="setLocFilter('Curitiba')">Curitiba</button>
          <button class="drawer-pill" style="font-size:10px; padding:2px 6px;" onclick="setLocFilter('Exterior')">Exterior</button>
      </div>
  </div>
  ```

- **Live Hunt Modal Location Input** (lines 591–595):
  ```html
  <div style="margin-bottom:12px;">
      <label style="display:block; font-size:12px; font-weight:600; color:var(--text-secondary); margin-bottom:4px;">Cidade / Região:</label>
      <input type="text" id="hunt-loc" style="width:100%; height:32px; background:var(--bg-canvas); border:1px solid var(--border-default); border-radius:6px; color:var(--text-primary); padding:0 10px;" placeholder="ex: São Paulo, Brasil, Remoto">
  </div>
  ```

### JavaScript Event Handlers & Filtering (`static/index.html`)
- **Quick Pill Click Handler** (lines 762–765):
  ```javascript
  function setLocFilter(city) {
      document.getElementById('loc-input').value = city;
      filterData();
  }
  ```
- **Text Input Debounce Handler** (lines 767–770):
  ```javascript
  function debounceFilter() {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(filterData, 200);
  }
  ```
- **Frontend Filter Execution** (lines 991, 1003–1006):
  ```javascript
  const locQuery = (document.getElementById('loc-input').value || '').toLowerCase();
  ...
  let matchLoc = true;
  if (locQuery) {
      matchLoc = titleLower.includes(locQuery) || reqLower.includes(locQuery) || companyLower.includes(locQuery);
  }
  ```

### Backend API & Database Logic (`app.py`, `database.py`, `bot.py`)
- **`/api/jobs` Endpoint (`app.py` lines 45–47)**:
  Calls `get_jobs()` from `database.py`.
- **`get_jobs()` Query (`database.py` lines 81–104)**:
  `SELECT title, company, budget, link, platform, added_at, job_type, profession, level, requirements FROM jobs`. Note: No `location` column is returned in the API payload.
- **Backend Live Hunt Trigger (`app.py` lines 157–207 & `bot.py` lines 1988–2021)**:
  `/api/trigger` receives `location` from live search modal and filters scraped jobs via `is_job_relevant` in `bot.py`, which performs NFD accent stripping via `normalize_str(s)`.

---

## 2. Logic Chain

1. **Quick Pill Interaction**: Clicking a pill ('Todas', 'São Paulo', 'Rio de Janeiro', 'Curitiba', 'Exterior') calls `setLocFilter(city)`, which updates `#loc-input.value` and directly calls `filterData()`. This provides instant UI feedback without waiting for debounce.
2. **Text Input Interaction**: Typing into `#loc-input` fires `oninput="debounceFilter()"`, executing `filterData()` after a 200ms delay to avoid lagging on fast typing.
3. **Filtering Scope**: In `filterData()`, `locQuery` is tested against `title`, `requirements`, and `company` of each job object using `.toLowerCase()`. Because `/api/jobs` does not return a dedicated `location` field, location matching relies on the city name being present in the title, requirements, or company text.
4. **Accent Handling Defect**:
   - `filterData()` uses `.toLowerCase()` but **does not perform accent / diacritics normalization** (e.g., `unicodedata` or `String.prototype.normalize("NFD")`).
   - Consequently, searching `"Sao Paulo"` will NOT match job titles containing `"São Paulo"` (and vice-versa).
   - Clicking quick pill `'São Paulo'` sets `locQuery = 'são paulo'`, which fails to match jobs stored as `'Sao Paulo'` or `'SAO PAULO'`.
5. **Quick Pill 'Exterior' Behavior**: The `'Exterior'` pill sets `locQuery = 'exterior'`. It will only match jobs where the word `"exterior"` is explicitly written in the title or description text, missing jobs specifying international cities (e.g., "Lisbon", "Miami", "Buenos Aires").
6. **Backend vs Frontend Asymmetry**: Backend filtering in `bot.py` (`is_job_relevant`) strips accents via `normalize_str()` (NFD unicode normalization), whereas the frontend JS in `static/index.html` lacks accent normalization.

---

## 3. Caveats

- Analysis was performed via static code inspection and tracing; live browser runtime DOM tests were not executed.
- If scrapers do not include location names in `title` or `requirements`, frontend location filtering will not match those jobs since `/api/jobs` does not supply a separate `location` field.

---

## 4. Conclusion

Requirement R2 is **partially implemented**:
- **Pills & Event Handlers**: ✅ Working correctly. Pill clicks update `#loc-input` and trigger instant filtering. Text input uses 200ms debounce.
- **Case Insensitivity**: ✅ Handled via `.toLowerCase()`.
- **Accent Handling**: ❌ Missing in frontend JS. "Sao Paulo" and "São Paulo" do not match each other.
- **Location Field Scope**: ⚠️ Frontend checks `title`, `requirements`, and `company` because `/api/jobs` does not include a `location` field in its returned JSON objects.
- **Pill 'Exterior'**: ⚠️ Relies on literal string match for "exterior".

### Proposed Diff / Solution Snippet for Frontend Accent Normalization
To resolve the accent sensitivity issue in `static/index.html`:
```javascript
function normStr(str) {
    return (str || '').normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
}

// In filterData():
const locQuery = normStr(document.getElementById('loc-input').value);
...
if (locQuery) {
    matchLoc = normStr(j.title).includes(locQuery) || normStr(j.requirements).includes(locQuery) || normStr(j.company).includes(locQuery);
}
```

---

## 5. Verification Method

To independently verify these findings:

1. **Inspect Quick Pills & Handlers**:
   - View `static/index.html` lines 468–474 (`setLocFilter` calls) and lines 762–770 (`setLocFilter` and `debounceFilter` definitions).
2. **Inspect Filtering Logic & Accent Sensitivity**:
   - View `static/index.html` lines 991 and 1003–1006 (`filterData` matching logic). Observe that no diacritics stripping function is applied to `locQuery` or job strings.
3. **Inspect Database & API Payload**:
   - View `database.py` lines 81–104 (`get_jobs` query). Confirm `location` column is absent from `SELECT` statement and returned dicts.
4. **Invalidation Conditions**:
   - The findings are invalidated if `filterData()` is updated with accent normalization (`normalize("NFD")`) or if `/api/jobs` is modified to include a `location` field in its JSON response.
