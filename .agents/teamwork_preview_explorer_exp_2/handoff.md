# Handoff Report: Proposal Copilot Button Restriction (Requirement R2)

**Agent**: Explorer 2 (`teamwork_preview_explorer_exp_2`)  
**Working Directory**: `C:\Users\99196\OneDrive\Documentos\vagas_bot\.agents\teamwork_preview_explorer_exp_2`  
**Handoff Type**: Hard (Task complete)  

---

## 1. Observation

1. **Cards View Button Rendering**:  
   File: `static/index.html` (lines 1938–1965)  
   Verbatim Code:
   ```javascript
   1938: const platLower = (j.platform || '').toLowerCase();
   1939: const isFreelance = platLower.includes('workana') || platLower.includes('99freelas') || platLower.includes('novenove');
   ...
   1963: ${isFreelance ? `<button class="btn btn-primary" style="background-color:#1f6beb;" onclick="openProposalCopilot('${escAttr(j.title)}', '${escAttr(reqText)}', '${escAttr(j.platform)}')"><i class="fa-solid fa-wand-magic-sparkles"></i> ✍️ Criar Proposta com IA</button>` : `<span></span>`}
   ```

2. **Table View Button Rendering**:  
   File: `static/index.html` (lines 1913–1928)  
   Verbatim Code:
   ```javascript
   1913: const platLower = (j.platform || '').toLowerCase();
   1914: const isFreelance = platLower.includes('workana') || platLower.includes('99freelas') || platLower.includes('novenove');
   ...
   1924: ${isFreelance ? `<button class="btn btn-primary" style="height:26px; padding:0 8px; background-color:#1f6beb;" onclick="openProposalCopilot('${escAttr(j.title)}', '${escAttr(j.requirements || j.title)}', '${escAttr(j.platform)}')"><i class="fa-solid fa-wand-magic-sparkles"></i> Proposta</button>` : ''}
   ```

3. **Kanban View Button Rendering & Inverted Arguments Bug**:  
   File: `static/index.html` (lines 1838–1847)  
   Verbatim Code:
   ```javascript
   1838: const platLower = (j.platform || '').toLowerCase();
   1839: const isFreelance = platLower.includes('workana') || platLower.includes('99freelas') || platLower.includes('novenove');
   ...
   1845: ${isFreelance ? `<button class="btn btn-secondary" style="font-size:10px; height:24px;" onclick="openProposalCopilot('${encodeURIComponent(j.title)}', '${encodeURIComponent(j.platform)}', '${encodeURIComponent((j.requirements||'').substring(0,300))}')"><i class="fa-solid fa-wand-magic-sparkles"></i> IA</button>` : ''}
   ```
   *Note*: `openProposalCopilot` signature at line 2281 is `(jobTitle, jobRequirements, platform = "Workana")`. Line 1845 passes `platform` as the 2nd argument instead of `jobRequirements`.

4. **Backend Data Model**:  
   Files: `database.py` (line 57), `app.py` (line 117), `scrapers/novenove.py` (line 45).  
   Job objects store platform in column/attribute `platform`, returning values such as `"99Freelas"`, `"Workana"`, `"LinkedIn"`, `"Gupy"`, `"Catho"`, `"InfoJobs"`, etc.

---

## 2. Logic Chain

1. **From Observation 1, 2, 3**: Inline checks currently use `platLower.includes('workana') || platLower.includes('99freelas') || platLower.includes('novenove')`. While this correctly selects Workana and 99Freelas, the logic is duplicated across multiple view renderers and lacks fallback checks for alternative platform property names (`source`, `origem`, `plataforma`) or protection against non-string/null values.
2. **From Observation 3**: The Kanban view has a parameter order mismatch (`title, platform, requirements` vs `jobTitle, jobRequirements, platform`), causing `openProposalCopilot` to receive platform in the requirements parameter.
3. **From Observation 4**: Scraper platform names are strings with varied casing (`"Workana"`, `"99Freelas"`). Standardizing platform evaluation via a centralized helper `isProposalAllowed(job)` ensures:
   - Case insensitivity (`.toLowerCase()`)
   - Whitespace trimming (`.trim()`)
   - Null-safe string coercion (`String(rawPlatform)`)
   - Defensive fallback property inspection (`job.platform || job.source || job.origem || job.plataforma`)
   - Strict allowlist filtering (`workana`, `99freelas`, `novenove`) so corporate platforms (LinkedIn, Infojobs, Gupy, Catho, Coodesh, etc.) NEVER render the Proposal Copilot button.

---

## 3. Caveats

- **Split View & Drawer**: Split View (`viewMode === 'split'`) and Job Details Drawer currently do not include proposal buttons. If the team decides to add Proposal Copilot buttons there, the same `isProposalAllowed(job)` helper must be used.
- **Backend Model Restrictions**: No backend changes are required for R2 since `job.platform` is already populated and passed to the frontend via `/api/jobs`.

---

## 4. Conclusion

Requirement R2 is ready for implementation by the Worker agent. To enforce that "Criar Proposta com IA" is ONLY rendered for "Workana" and "99Freelas" job cards and NEVER for corporate platforms (LinkedIn, Gupy, Catho, Infojobs, Coodesh, etc.):
1. Add a centralized helper function `isProposalAllowed(job)` in `static/index.html`.
2. Refactor Cards View (line 1939/1963), Table View (line 1914/1924), and Kanban View (line 1839/1845) to call `isProposalAllowed(j)`.
3. Correct the argument order bug in Kanban View line 1845.

---

## 5. Verification Method

1. **Security & Integration Test Command**:  
   Run: `python test_security.py`  
   Expected result: 100% pass (all 4 test suites pass).

2. **Frontend Empirical Verification**:
   - Inspect `static/index.html` to confirm `isProposalAllowed(job)` is called in Cards, Table, and Kanban renderers.
   - Load `http://localhost:8000/` in browser or test JSON data:
     - Workana / 99Freelas job objects -> Render "Criar Proposta com IA" button.
     - LinkedIn / Gupy / Catho / InfoJobs / Coodesh job objects -> Do NOT render proposal button.
