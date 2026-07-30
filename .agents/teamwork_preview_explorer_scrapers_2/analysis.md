# Code Exploration Analysis Report — Backend Job Models, Schemas & Payload Handlers

**Agent**: `teamwork_preview_explorer_scrapers_2`  
**Date**: 2026-07-29  
**Repository**: `vagas_bot`  

---

## 1. Executive Summary

This report documents the architectural requirements for scraper job payloads, backend database schemas, normalization dictionaries, and downstream payload compatibility in the `vagas_bot` repository.

Investigation targets inspected:
- `database.py`: Database schema (`jobs` table), `insert_jobs()`, `get_jobs()`.
- `scrapers/ai_filter.py`: `ALLOWED_PROFESSIONS`, `classify_profession_fallback()`, `JobEvaluation` schema.
- `bot.py`: `CO_OCCURRENCE_RULES`, `SEARCH_MAPPING`, `classify_job_profession()`, `is_job_relevant()`.
- `app.py`: `/api/jobs`, `/api/search`, `run_initial_seed_search()`, background hunt loops.
- `scrapers/` (`linkedin.py`, `gupy.py`, `workana.py`, etc.): Payload output structures.

---

## 2. Required Fields in Job Payloads Returned by Scrapers

When scrapers execute `scrape(...)`, they return a list of dictionaries (`List[Dict[str, Any]]`). Downstream processing (specifically `insert_jobs()` in `database.py`) performs validation before writing to SQLite.

### 2.1 Strictly Required (Mandatory) Payload Fields

If any of these 3 fields are missing, `None`, empty string (`""`), or invalid (`"#"`), `insert_jobs()` silently ignores the record and skips insertion:

| Field Name | Type | Validation Rule in `insert_jobs()` | Example |
|---|---|---|---|
| `link` | `str` | Must not be empty, `None`, or `'#'`. Used as SQLite Primary Key `id` and `link`. | `"https://www.linkedin.com/jobs/view/123456"` |
| `title` | `str` | Must not be empty string or `None`. | `"Desenvolvedor Python Backend"` |
| `platform` | `str` | Must not be empty string or `None`. | `"LinkedIn"`, `"Gupy"`, `"Workana"` |

### 2.2 Standard Payload Fields with Fallback Defaults

The downstream database layer handles missing optional fields using fallback defaults:

| Field Name | Expected Type | DB Insertion Fallback Default | Description |
|---|---|---|---|
| `company` | `str` | `'N/A'` (or `'Empresa Confidencial'`) | Employer/Company name |
| `budget` | `str` | `'A combinar'` | Salary / project budget info |
| `job_type` | `str` | `'CLT'` | Contract model (`"CLT"`, `"PJ"`, `"Freelancer"`) |
| `profession` | `str` | Classified via `classify_profession_fallback()` | Category / profession keyword |
| `level` | `str` | `'Todos'` | Seniority level (`"Júnior"`, `"Pleno"`, `"Sênior"`, `"Todos"`) |
| `requirements` | `str` | `'Requisitos descritos no link da vaga.'` | Full job description / skills text |
| `location` | `str` | `'Remoto/Brasil'` | Job location |
| `lat` | `float` / `None` | `None` | Geolocation latitude |
| `lon` | `float` / `None` | `None` | Geolocation longitude |
| `lang` | `str` | `'pt'` | Job language code (`"pt"`, `"en"`) |

---

## 3. Downstream Database Insertion Flow & Validation of `profession` / `category`

### 3.1 SQLite Database Schema (`database.py`)

The SQLite database table `jobs` is created with the following schema:

```sql
CREATE TABLE IF NOT EXISTS jobs (
    id TEXT PRIMARY KEY,
    title TEXT,
    company TEXT,
    budget TEXT,
    link TEXT,
    platform TEXT,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    job_type TEXT,
    profession TEXT,
    level TEXT,
    requirements TEXT,
    location TEXT,
    lat REAL,
    lon REAL,
    lang TEXT
);
```

> **Key Architectural Finding**: The SQLite DB schema contains a column named `profession`, but **does NOT have a separate `category` column** in table `jobs`. The `category` attribute is computed in-memory during filtering/bot execution (`classify_job_profession()` in `bot.py`).

### 3.2 Insertion & Validation Lifecycle

```
[Scraper Payload Dict]
        │
        ▼
[bot.classify_job_profession(job)]  ──► Sets job['category'] and job['profession'] in-memory
        │
        ▼
[database.insert_jobs(jobs)]
        │
        ├── Raw profession extracted: job.get('profession')
        │
        ├── Classification fallback: clean_profession = classify_profession_fallback(title, raw_prof)
        │       │
        │       ├── Checks if raw_prof is in ALLOWED_PROFESSIONS (in scrapers/ai_filter.py)
        │       └── If not, uses Regex on title to map to ALLOWED_PROFESSIONS
        │
        ▼
[SQL INSERT INTO jobs (..., profession, ...)]  ──► Saved to SQLite `jobs.db`
```

---

## 4. Normalization and Mapping Analysis for the 6 New Categories

### 4.1 Allowed Professions List (`scrapers/ai_filter.py`)

Currently, `scrapers/ai_filter.py` defines an explicit list of allowed profession strings:

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

### 4.2 Bot Taxonomy & Search Mappings (`bot.py`)

In `bot.py`, `SEARCH_MAPPING` and `CO_OCCURRENCE_RULES` map incoming search keywords and titles for the 6 strategic categories:

1. **Categoria 1: Operações Físicas e Industriais** (`"soldador caldeireiro"`, `"operador cnc"`, `"auxiliar de producao"`)
2. **Categoria 2: Logística e Expedição** (`"auxiliar de logistica"`, `"escriturario bancario"`)
3. **Categoria 3: Varejo, Comercial e Segurança** (`"consultor de vendas varejo"`, `"vigilante patrimonial"`)
4. **Categoria 4: Criativos de Performance e Audiovisual** (`"designer de performance"`, `"sound designer"`)
5. **Categoria 5: Inteligência de Vendas Avançada** (`"gestor de performance avancado"`, `"sdr tecnico b2b"`)
6. **Categoria 6: Engenharia de IA e Infraestrutura** (`"especialista tracking elite"`, `"arquiteto automacao ia ops"`, `"desenvolvedor web fullstack"`)

`classify_job_profession(job)` in `bot.py` populates `job['profession']` (e.g. `'Operador de Produção'`) and `job['category']` (e.g. `'Operações Físicas'`).

### 4.3 Category Compatibility Requirement

If a scraper sets `job['profession']` to a string NOT present in `ALLOWED_PROFESSIONS` (in `scrapers/ai_filter.py`), `classify_profession_fallback()` will re-classify it into one of the 6 allowed professions or `"Outros"`. To ensure full preservation of new category names:
- Scraper payloads should output standard `profession` names that correspond to `SEARCH_MAPPING` keys in `bot.py`.
- If new categories must be persisted verbatim in `jobs.db`, `ALLOWED_PROFESSIONS` in `scrapers/ai_filter.py` must include those category names.

---

## 5. Specification for 100% Downstream Payload Compatibility

To ensure 100% downstream compatibility across all scrapers, database workflows, FastAPI endpoints (`/api/jobs`), and Telegram bot handlers:

1. **Return Type & Signature**:
   - Function signature: `async def scrape(keyword="...", level="Todos", location="", country="", max_pages=10, **kwargs)` (or synchronous `def scrape(...)`).
   - Return type: `List[Dict[str, Any]]`.

2. **Mandatory Dictionary Keys**:
   ```python
   {
       "platform": str,      # Required (non-empty)
       "title": str,         # Required (non-empty)
       "link": str,          # Required (valid URL, non-empty, != '#')
       "company": str,       # Optional (defaults to "Empresa Confidencial" / "N/A")
       "budget": str,        # Optional (defaults to "A Combinar")
       "job_type": str,      # Optional ("CLT", "PJ", "Freelancer")
       "profession": str,    # Optional (keyword or category name)
       "level": str,         # Optional ("Júnior", "Pleno", "Sênior", "Todos")
       "requirements": str,  # Optional (job description/requirements)
       "location": str,      # Optional ("Brasil (Remoto)", "Londrina/PR", etc.)
   }
   ```
