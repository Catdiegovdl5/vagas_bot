# Analysis Report: Proposal Copilot Button Restriction (Requirement R2)

**Agent**: Explorer 2 (`teamwork_preview_explorer_exp_2`)  
**Date**: 2026-07-29  
**Status**: Read-Only Analysis Complete  

---

## 1. Executive Summary & Objective

Requirement R2 dictates that the **"Criar Proposta com IA"** button (and associated Proposal Copilot trigger buttons) must **ONLY** be displayed on job cards/rows originating from freelancer platforms:
- **Workana**
- **99Freelas** (canonical identifier: `99Freelas` / `novenove`)

Corporate job platforms (such as **LinkedIn, Infojobs, Gupy, Catho, Coodesh, Remotar, ProgramaThor, GeekHunter, Jooble, Indeed, Glassdoor, Vagas.com**, etc.) must **NEVER** display this proposal creation button.

This investigation inspected `static/index.html`, database schema in `database.py`, API endpoints in `app.py`, and scraper definitions in `scrapers/` to locate all button rendering instances, evaluate job object platform field storage, analyze edge cases, and provide actionable implementation steps for the Worker agent.

---

## 2. Rendering Locations in `static/index.html`

The frontend application (`static/index.html`) is a Single Page Application (SPA) that renders job listings across multiple view modes:

### 2.1 Cards View (`viewMode === 'cards'`)
- **File Path**: `static/index.html`
- **Line Range**: 1938–1965
- **Current Code**:
  ```javascript
  1938: const platLower = (j.platform || '').toLowerCase();
  1939: const isFreelance = platLower.includes('workana') || platLower.includes('99freelas') || platLower.includes('novenove');
  ...
  1963: ${isFreelance ? `<button class="btn btn-primary" style="background-color:#1f6beb;" onclick="openProposalCopilot('${escAttr(j.title)}', '${escAttr(reqText)}', '${escAttr(j.platform)}')"><i class="fa-solid fa-wand-magic-sparkles"></i> ✍️ Criar Proposta com IA</button>` : `<span></span>`}
  ```
- **Button Label**: `<i class="fa-solid fa-wand-magic-sparkles"></i> ✍️ Criar Proposta com IA`

### 2.2 Table View (`viewMode === 'table'`)
- **File Path**: `static/index.html`
- **Line Range**: 1913–1928
- **Current Code**:
  ```javascript
  1913: const platLower = (j.platform || '').toLowerCase();
  1914: const isFreelance = platLower.includes('workana') || platLower.includes('99freelas') || platLower.includes('novenove');
  ...
  1924: ${isFreelance ? `<button class="btn btn-primary" style="height:26px; padding:0 8px; background-color:#1f6beb;" onclick="openProposalCopilot('${escAttr(j.title)}', '${escAttr(j.requirements || j.title)}', '${escAttr(j.platform)}')"><i class="fa-solid fa-wand-magic-sparkles"></i> Proposta</button>` : ''}
  ```
- **Button Label**: `<i class="fa-solid fa-wand-magic-sparkles"></i> Proposta`

### 2.3 Kanban View (`viewMode === 'kanban'`)
- **File Path**: `static/index.html`
- **Line Range**: 1838–1847
- **Current Code**:
  ```javascript
  1838: const platLower = (j.platform || '').toLowerCase();
  1839: const isFreelance = platLower.includes('workana') || platLower.includes('99freelas') || platLower.includes('novenove');
  ...
  1845: ${isFreelance ? `<button class="btn btn-secondary" style="font-size:10px; height:24px;" onclick="openProposalCopilot('${encodeURIComponent(j.title)}', '${encodeURIComponent(j.platform)}', '${encodeURIComponent((j.requirements||'').substring(0,300))}')"><i class="fa-solid fa-wand-magic-sparkles"></i> IA</button>` : ''}
  ```
- **Button Label**: `<i class="fa-solid fa-wand-magic-sparkles"></i> IA`
- **⚠️ Bug Found**: In Kanban View (line 1845), argument 2 is passed as `j.platform` and argument 3 as `requirements`. However, `openProposalCopilot` signature (line 2281) expects `(jobTitle, jobRequirements, platform)`. This swaps requirements and platform when clicking from Kanban view.

### 2.4 Split View (`viewMode === 'split'`)
- **File Path**: `static/index.html`
- **Line Range**: 1859–1887
- **Observation**: Split view detail pane currently omits the Proposal Copilot button entirely.

### 2.5 Job Details Drawer Modal (`openDrawer(link)`)
- **File Path**: `static/index.html`
- **Line Range**: 2070–2092
- **Observation**: Job Details drawer currently omits the Proposal Copilot button.

---

## 3. Job Object Platform Attribute Analysis

In the backend ecosystem (`app.py`, `database.py`, `scrapers/`):
- **Database Schema**: Column is named `platform` in SQLite `jobs` table (`database.py` line 57).
- **Scraper Output**: Scrapers assign string values to `"platform"` (e.g. `scrapers/novenove.py` sets `"platform": "99Freelas"`, `scrapers/workana.py` sets `"platform": "Workana"`).
- **API Serializer**: Endpoint `/api/jobs` returns a list of dictionaries with key `"platform"`.
- **Legacy / Variant Fields**: In some legacy scripts or alternative response models, `source`, `origem`, or `plataforma` may be present.

### Defensive Field Resolution Strategy
To handle any edge case where alternative field names exist on `job` objects, frontend code must resolve platform dynamically using:
```javascript
const rawPlatform = job.platform || job.source || job.origem || job.plataforma || '';
```

---

## 4. Enforcement Logic & Edge Cases

To strictly enforce Requirement R2:
1. **Strict Allowlist Model**: Avoid blocklists (which fail when new corporate scrapers are added). Implement a strict allowlist containing ONLY `"workana"`, `"99freelas"`, and `"novenove"`.
2. **Case Insensitivity**: Convert platform string to lowercase (`.toLowerCase()`).
3. **Whitespace Trimming**: Strip leading and trailing whitespace (`.trim()`).
4. **Null Safety**: Guarantee string conversion for `null` or `undefined` properties (`String(rawPlatform)`).

### Centralized Helper Function (`isProposalAllowed`)
Place a global helper function in `static/index.html`:

```javascript
function isProposalAllowed(job) {
    if (!job) return false;
    const rawPlatform = job.platform || job.source || job.origem || job.plataforma || '';
    const plat = String(rawPlatform).toLowerCase().trim();
    if (!plat) return false;
    
    // Strict allowlist: ONLY Workana and 99Freelas (including 'novenove')
    return plat.includes('workana') || plat.includes('99freelas') || plat.includes('novenove');
}
```

### Truth Table Verification
| Job Platform Property | Result of `isProposalAllowed(job)` | Proposal Button Displayed? |
|---|---|---|
| `"Workana"` | `true` | ✅ YES |
| `"workana"` | `true` | ✅ YES |
| `" 99Freelas "` | `true` | ✅ YES |
| `"novenove"` | `true` | ✅ YES |
| `"LinkedIn"` | `false` | ❌ NO |
| `"Gupy"` | `false` | ❌ NO |
| `"Catho"` | `false` | ❌ NO |
| `"InfoJobs"` | `false` | ❌ NO |
| `"Coodesh"` | `false` | ❌ NO |
| `"Freelancer.com"` | `false` | ❌ NO |
| `"ProgramaThor"` | `false` | ❌ NO |
| `"GeekHunter"` | `false` | ❌ NO |
| `null` / `undefined` | `false` | ❌ NO |

---

## 5. Summary of Identified Issues & Actionable Recommendations

1. **Centralize Button Visibility**: Replace scattered inline platform checks in `static/index.html` (lines 1839, 1914, 1939) with calls to `isProposalAllowed(j)`.
2. **Fix Argument Order Bug in Kanban View**: Line 1845 incorrectly passes `j.platform` as 2nd parameter to `openProposalCopilot`. Correct parameter order to `openProposalCopilot(title, requirements, platform)`.
3. **Ensure Consistency Across All Views**: Apply `isProposalAllowed(j)` check in Cards, Table, Kanban, and optionally Split View / Drawer.

---
*Report generated by Explorer 2 for Worker implementation.*
