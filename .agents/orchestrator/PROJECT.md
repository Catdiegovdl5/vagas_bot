# Project: Native Scraper Query Refactoring for 6 New Profession Categories

## Architecture
- Backend: Python (`bot.py`), Scraper engine (`scrapers/*.py`), Database layer (`database.py`).
- Data Flow:
  1. UI / API triggers hunt with one of the 6 new profession categories or sub-profession keywords.
  2. `bot.py` maps the category/term via `MAGIC_CATEGORIES`, `SEARCH_MAPPING`, and `CO_OCCURRENCE_RULES`.
  3. `scrapers/*.py` (Gupy, InfoJobs, Workana, LinkedIn, Catho, Vagas_com, etc.) inject native key terms into platform search parameters/APIs to fetch targeted job cards.
  4. Scraper output payloads return normalized job dictionaries containing `title`, `company`, `platform`, `link`, `profession`/`category`, `location`, etc.
  5. Downstream DB flow (`database.py`) validates and stores job objects matching internal schema.

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| 1 | Architecture & Codebase Discovery | Explore `scrapers/`, internal DB schemas/payloads, and `tests/` structure | None | DONE |
| 2 | Scraper Parameterization & Keyword Injection | Refactor scrapers in `scrapers/` (Gupy, InfoJobs, Workana, LinkedIn, Vagas_com, Catho) and `bot.py` category mapping to support native search for 6 new categories | M1 | IN_PROGRESS |
| 3 | Payload Schema Synchronization | Ensure `profession` and `category` fields match database schema and downstream insertion flows | M2 | IN_PROGRESS |
| 4 | Test Adaptation & Verification | Adapt/create tests in `tests/` testing at least 3-4 scrapers with new categories | M2, M3 | IN_PROGRESS |
| 5 | Review, Stress Verification & Forensic Audit | Reviewers, Challengers, and Forensic Auditor verification (CLEAN verdict) | M4 | PLANNED |

## Interface Contracts & Taxonomy Mappings
- **6 New Categories**:
  1. `Operações Físicas`: Operador CNC, Pintor Industrial, Mecânico Industrial, Soldador, Eletricista, Operador de Produção, Conferente
  2. `Logística`: Assistente de Logística, Auxiliar de Logística, Almoxarife, Operador de Empilhadeira, Auxiliar de Expedição, Motorista
  3. `Administrativo`: Assistente Administrativo, Auxiliar Administrativo, Recepcionista, Auxiliar de Escritório, Data Entry, Digitador
  4. `Criativos de Performance`: Designer Conversional, Copywriter, Criador de Anúncios, Motion Designer, Editor de Vídeo, Gestor de Tráfego
  5. `Inteligência de Vendas`: SDR, BDR, Inside Sales, Analista de Sales Ops, Executivo de Vendas, CRM, Analista de Vendas
  6. `Engenharia de IA/Dados`: Engenheiro de Dados, Engenheiro de IA, Machine Learning, Data Engineer, Cientista de Dados, Analista de Dados

## Code Layout
- `scrapers/`: `gupy.py`, `infojobs.py`, `workana.py`, `linkedin.py`, `vagas_com.py`, `catho.py`, `glassdoor.py`, etc.
- Core: `bot.py`, `database.py`
- `tests/`: `tests/test_tier1.py`, `tests/test_milestone2_macro_searches.py`, `tests/test_scrapers_macro_categories.py`
