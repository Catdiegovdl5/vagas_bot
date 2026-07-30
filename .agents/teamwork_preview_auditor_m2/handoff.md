# Forensic Audit Report — Milestone 2: Scraper Configuration & Macro-Searches

**Work Product**: Milestone 2 Code Changes (`bot.py`, `app.py`, `tests/test_milestone2_macro_searches.py`, `scrapers/*.py`)
**Profile**: General Project
**Integrity Enforcement Mode**: Development / Demo / Benchmark (All Verified)
**Verdict**: CLEAN

---

## 1. Observation

### Codebase & File Verification
- `bot.py` (lines 1381–1396): Inspected `global_title_blacklist`. Terms `"pintor"` and `"mecanico"` are NOT present in `global_title_blacklist`, allowing industrial physical operation roles ("Pintor Industrial", "Mecânico Industrial") to pass global title filtering.
- `bot.py` (lines 1538–1801): Inspected `CO_OCCURRENCE_RULES`. Contains comprehensive co-occurrence keyword groups for all 6 broad macro categories:
  - `"operacoes fisicas"`, `"industria"`, `"logistica"`, `"administrativo"`, `"criativos"`, `"design"`, `"inteligencia de vendas"`, `"vendas"`, `"engenharia de dados"`, as well as specific sub-professions (`"pintor industrial"`, `"mecanico industrial"`, `"almoxarife"`, `"executivo de vendas"`).
- `bot.py` (lines 1949–2089): Inspected `SEARCH_MAPPING`. All 6 broad category macro keywords map to lowercase normalized keys.
- `bot.py` (lines 2093–2234): Inspected `classify_job_profession(job)`. Implements a multi-tiered tagger (Priority 1: Specific Sub-Professions; Priority 2: Macro Category Keywords in Title; Priority 3: Fallback in requirements/full text).
- `bot.py` (lines 2236–2454): Inspected `is_job_relevant(job, keyword, settings)`. Applies global blacklist, niche blacklist, location filter, and `check_co_occurrence(full_text, kw_norm, job=job)`.
- `app.py` (lines 684–730): `run_initial_seed_search()` and `background_periodic_hunt_loop()` correctly query macro keywords (`"Indústria"`, `"Logística"`, `"Administrativo"`, `"Design"`, `"Vendas"`, `"Engenharia de Dados"`, etc.) across scrapers and pass results to `classify_job_profession()` before DB insertion.
- `tests/test_milestone2_macro_searches.py` (162 lines, 5 test cases): Validated test suite assertions and coverage.

### Empirical Test Execution
- Executed `python -m unittest tests/test_milestone2_macro_searches.py`:
  ```
  Ran 5 tests in 0.012s
  OK
  ```
- Executed full test suite (`python -m unittest discover tests`):
  ```
  Ran 16 tests in 0.066s
  OK
  ```
- Executed custom forensic stress script testing 13 positive and negative cross-domain job cases against `is_job_relevant()`:
  - `"Indústria"` + Pintor Industrial / Mecânico Industrial → PASS (Relevant)
  - `"Logística"` + Almoxarife Sênior → PASS (Relevant)
  - `"Administrativo"` + Assistente Financeiro → PASS (Relevant)
  - `"Design"` + Designer Gráfico Sr → PASS (Relevant)
  - `"Vendas"` + Executivo de Vendas → PASS (Relevant)
  - `"Engenharia de Dados"` + Data Engineer → PASS (Relevant)
  - `"Indústria"` + Advogado Trabalhista → PASS (Rejected)
  - `"Logística"` + Gestor de Tráfego Pago → PASS (Rejected)
  - `"Administrativo"` + Desenvolvedor Python → PASS (Rejected)
  - `"Criativos"` + Mecânico de Manutenção → PASS (Rejected)
  - `"Vendas"` + Engenheiro de Dados → PASS (Rejected)
  - `"Engenharia de Dados"` + Atendente de Vendas → PASS (Rejected)

---

## 2. Logic Chain

1. **Hardcoded Test Results Check**: Checked `tests/test_milestone2_macro_searches.py` for static boolean returns, dummy assertions, or pre-canned responses. All assertions execute `is_job_relevant()` and `classify_job_profession()` dynamically with full dictionary inputs and evaluate authentic return values.
2. **Facade Implementation Check**: Verified `classify_job_profession()` and `is_job_relevant()`. Neither function acts as a stub or facade. Both perform real string normalization, regular expression word-boundary matching, multi-tier classification, and co-occurrence checks across keyword groups.
3. **Pre-populated Artifact Check**: No pre-calculated log files or fake test result artifacts were found pre-populating the test environment.
4. **Circumvention & Blacklist Verification**: Confirmed that removing `"pintor"` and `"mecanico"` from `global_title_blacklist` does not introduce false positive leakage, as niche blacklists (`blacklist["criativos"]`, `blacklist["administrativo"]`, etc.) and `CO_OCCURRENCE_RULES` strictly enforce cross-domain rejection for non-industrial searches.
5. **Scraper Integration**: Scraper modules (`gupy.py`, `catho.py`, `infojobs.py`, `workana.py`) dynamically process incoming macro search keywords without mocking or hardcoded shortcuts.

---

## 3. Caveats

- Live HTTP network traffic to job portals during unit testing was not executed to prevent rate-limiting; scrapers were verified via unit tests and mock response handling in the test suite.
- DB persistence was verified via test SQLite connections (`jobs_test.db`).

---

## 4. Conclusion

Milestone 2 implementation satisfies all functional and architectural requirements without integrity violations:
- No hardcoded test results or fake assertions.
- No dummy/facade implementations.
- No logic circumvention or illegitimate bypasses.
- Genuine classification and co-occurrence rule enforcement verified empirically across all 6 broad macro categories.

**Verdict**: **CLEAN**

---

## 5. Verification Method

To independently verify this forensic audit, execute the following commands in PowerShell from `C:\Users\99196\OneDrive\Documentos\vagas_bot`:

1. Run Milestone 2 unit test suite:
   ```powershell
   python -m unittest tests/test_milestone2_macro_searches.py
   ```
2. Run full project test suite:
   ```powershell
   python -m unittest discover tests
   ```
3. Run empirical classification and cross-domain rejection stress test:
   ```powershell
   python -c "import bot; print('Pintor in blacklist:', 'pintor' in bot.global_title_blacklist); print('Test Pintor Industrial:', bot.is_job_relevant({'title': 'Pintor Industrial', 'requirements': 'Fábrica'}, 'Indústria', {'level':'Todos'})); print('Test Advogado in Indústria:', bot.is_job_relevant({'title': 'Advogado Trabalhista', 'requirements': 'Jurídico'}, 'Indústria', {'level':'Todos'}))"
   ```
