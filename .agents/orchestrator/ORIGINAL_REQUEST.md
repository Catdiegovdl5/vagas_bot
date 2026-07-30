# Original User Request

## 2026-07-29T10:40:41Z

Expand the Vagas Sniper Bot to support a new, extensive taxonomy of professions (ranging from Industrial/Blue Collar to Data/AI Engineering) and update the scrapers to correctly query and fetch jobs for these new categories.

Requirements:
R1. UI Taxonomy Update: Update `static/index.html` to merge the 6 new categories provided by the user (Operações Físicas, Logística, Administrativo, Criativos, Inteligência de Vendas, e Engenharia de Dados) with the current drawers. Transform the category system into a comprehensive mega-menu of professional drawers.
R2. Scraper Configuration (Macro-Searches): Update the scraping logic (and any keyword mapping configurations, like `CO_OCCURRENCE_RULES` if applicable) to support the new taxonomy. Configure scrapers to execute macro-searches for broad categories (e.g., "Indústria", "Logística") and rely on local filtering to classify specific sub-professions (like "Pintor Industrial" or "Almoxarife").

Acceptance Criteria:
- UI & JS Integrity:
  - `static/index.html` renders new mega-menu drawers properly.
  - Profession mapping (IDs, keywords, names) is correctly defined in JS constants.
  - No syntax errors or broken JS logic are introduced.
- Python Syntax & Scraper Integrity:
  - All modified Python scrapers and config files pass `python -m py_compile <file>`.
  - Macro-search keywords are logically implemented without breaking existing job ingestion loop.
