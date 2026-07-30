# Forensic Audit Report — Milestone 3

## Work Product and Profile
- **Work Product**: `vagas_bot` project located at `C:\Users\99196\OneDrive\Documentos\vagas_bot`
- **Profile**: General Project (Demo Mode)
- **Auditor Identity**: `auditor_m3_2`
- **Date/Time**: 2026-07-16T15:45:00-03:00

## Verdict
**Verdict**: **CLEAN** (No Integrity Violations Detected)

*Note: While there are no integrity violations (cheating, facades, or hardcoded test overrides), there is a functional codebase bug that causes one E2E test to fail (see Detailed Phase Results below).*

---

## Detailed Phase Results

### Phase 1: Source Code Analysis

1. **Hardcoded Test Results Check**: **PASS**
   - **Verification**: Searched all production files (`bot.py`, `app.py`, `database.py`, `scrapers/ai_filter.py`) for strings or variables containing expected test outputs, pre-set test statuses, or fake success return values.
   - **Findings**: No hardcoded test results were found. All modules perform genuine processing of data inputs (e.g. normalizing text, applying regex patterns, parsing JSON from Groq, and calling SQLAlchemy/sqlite3).

2. **Facade / Dummy Implementation Check**: **PASS**
   - **Verification**: Examined core interfaces and functions, particularly `is_job_relevant` in `bot.py` and `score_job_match` in `scrapers/ai_filter.py`, to confirm they implement genuine algorithmic logic.
   - **Findings**: The High-Precision Filtering Engine (HPFE) is implemented genuinely using multi-level filtering:
     - Localization matching (strict checking of "remoto" vs hybrid/presencial and local cities like Londrina/Assaí).
     - Contract matching (CLT vs PJ vs Freelance).
     - Experience matching (Junior, Pleno, Senior terms).
     - Global title blacklist and niche-specific blacklists.
     - Co-occurrence verification using `check_co_occurrence` based on the `CO_OCCURRENCE_RULES` dictionary.
     - `score_job_match` in `scrapers/ai_filter.py` performs key-rotated, semaphore-constrained async calls to the `llama-3.3-70b-versatile` model on Groq and overlays hard-coded safety constraints.

3. **Pre-populated Artifact Check**: **PASS**
   - **Verification**: Searched the workspace for pre-generated logs or mock outputs intended to satisfy verification scripts.
   - **Findings**: The SQLite database schema is built dynamically for tests in `tests/jobs_test.db` and is not pre-populated.

---

### Phase 2: Behavioral Verification

4. **Verification Script `test_motor.py` Execution**: **PASS**
   - **Command**: `python test_motor.py`
   - **Result**: **16/16 tests passed** (100% precision). All true-positives were approved, and all 11 false-positives (such as "Enfermeira com python", "Atendente de Lanchonete IA", and "Costureira para Confecção") were correctly blocked.

5. **E2E Test Suite `run_tests.py` Execution**: **FAIL (Functional Defect)**
   - **Command**: `python run_tests.py`
   - **Result**: **56/57 tests passed** (1 failure).
   - **Failure Details**: The test `tests/test_tier1.py::test_especialista_ia_generativa_keywords` failed:
     ```python
     job1 = {
         "title": "Copywriter ChatGPT",
         "requirements": "Criação de textos usando inteligência artificial."
     }
     assert is_job_relevant(job1, "Especialista em IA Generativa", DEFAULT_SETTINGS) is True
     ```
     - **Cause**: In `bot.py`, the `CO_OCCURRENCE_RULES` dictionary is missing the key `"especialista em ia generativa"`. As a result, when `is_job_relevant` is called with this keyword, it falls back to the generic fallback logic. The generic fallback splits the keyword into significant words (minimum 3 characters, removing stopwords), resulting in `["especialista", "generativa"]`. Since the job title/requirements for the creative job "Copywriter ChatGPT" do not contain the word `"especialista"`, the check returns `False` and the test fails.
     - *Note*: An alternative version `bot.py.mine` in the workspace contains the correct mapping (lines 551-578) but is not the active file used by the test runner.

6. **Telegram Bot `bot.py` Startup Check**: **PASS**
   - **Verification**: Examined `bot.py`'s startup entry point.
   - **Findings**: The initialization code is highly robust:
     - `init_db()` is called during import to ensure SQLite tables exist.
     - In `main()`, the call to `bot.set_chat_menu_button()` is wrapped in a `try/except` block, logging warnings on failure instead of crashing.
     - The main polling call `dp.start_polling(bot)` is wrapped inside an infinite `while True` loop that catches connection errors (e.g., token issues or session conflicts) and retries after 5 seconds, preventing startup crashes.

---

## Evidence

### E2E Test Suite Run Log Summary (from `python run_tests.py`):
```log
============================= test session starts =============================
platform win32 -- Python 3.14.5, pytest-9.0.3, pluggy-1.6.0 -- C:\Python314\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\99196\OneDrive\Documentos\vagas_bot
plugins: anyio-4.13.0, Flask-Dance-7.1.0, asyncio-1.4.0, mock-3.15.1
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collecting ... collected 57 items

tests/test_adversarial_challenges.py::test_senior_candidate_with_experience_job PASSED [  1%]
tests/test_adversarial_challenges.py::test_graduate_candidate_with_degree_job PASSED [  3%]
tests/test_adversarial_challenges.py::test_foreign_currency_and_english_leakage PASSED [  5%]
...
tests/test_tier1.py::test_especialista_ia_generativa_keywords FAILED     [ 49%]
...
tests/test_tier4.py::test_app_workflow_full_pipeline_cycle PASSED        [100%]

================================== FAILURES ===================================
__________________ test_especialista_ia_generativa_keywords ___________________

    def test_especialista_ia_generativa_keywords():
        from bot import is_job_relevant, DEFAULT_SETTINGS
    
        # 1. Test case: Copywriter ChatGPT
        job1 = {
            "title": "Copywriter ChatGPT",
            "requirements": "Criação de textos usando inteligência artificial."
        }
>       assert is_job_relevant(job1, "Especialista em IA Generativa", DEFAULT_SETTINGS) is True
E       AssertionError: assert False is True
E        +  where False = <function is_job_relevant at 0x0000027458A1FCC0>({'requirements': 'Criação de textos usando inteligência artificial.', 'title': 'Copywriter ChatGPT'}, 'Especialista em IA Generativa', {'ai_filter': True, 'contract': 'Todos', 'education': 'Todos', 'level': 'Todos', ...})

tests\test_tier1.py:447: AssertionError
=========================== short test summary info ===========================
FAILED tests/test_tier1.py::test_especialista_ia_generativa_keywords - Assert...
======================== 1 failed, 56 passed in 22.65s ========================
```

### `test_motor.py` Run Output:
```log
=================================================================
   VAGAS SNIPER BOT — TESTE DO MOTOR DE BUSCA
=================================================================
  PASS  [OK] VP: Dev Python Backend com Django
  PASS  [OK] VP: Analista de Dados Python
  PASS  [OK] VP: Especialista IA Generativa
  PASS  [OK] VP: Dev React Frontend
  PASS  [OK] VP: Desenvolvedor RPA
  PASS  [BLOQUEAR] FP: Enfermeira com python - DEVE BLOQUEAR
  PASS  [BLOQUEAR] FP: Médico vet com python no estoque - DEVE BLOQUEAR
  PASS  [BLOQUEAR] FP: Motorista com python - DEVE BLOQUEAR
  PASS  [BLOQUEAR] FP: Atendente onde 'IA' é nome da empresa - DEVE BLOQUEAR
  PASS  [BLOQUEAR] FP: Costureira sem IA generativa - DEVE BLOQUEAR
  PASS  [BLOQUEAR] FP: Balconista onde 'React' é nome do sistema - DEVE BLOQUEAR
  PASS  [BLOQUEAR] FP: Repositor com Power BI - DEVE BLOQUEAR
  PASS  [BLOQUEAR] FP: Recepcionista em empresa cujo nome é ML - DEVE BLOQUEAR
  PASS  [BLOQUEAR] FP: Professor sem vaga de TI - DEVE BLOQUEAR
  PASS  [BLOQUEAR] FP: Auxiliar limpeza da empresa RPA Clean - DEVE BLOQUEAR
  PASS  [BLOQUEAR] FP: Corretor de imóveis - DEVE BLOQUEAR

=================================================================
  Resultado: 16/16 testes passaram
  Falsos-Positivos bloqueados: 11/11 (100%)

  >> MOTOR APROVADO! 100% dos falsos-positivos bloqueados.
```

### `bot.py` Startup / Exception Handling Design (Lines 1300-1317):
```python
async def main():
    print("Bot Nativo Ligado e Aguardando Comandos!")
    try:
        await bot.set_chat_menu_button()
    except Exception as e:
        print(f"Warning: Failed to set chat menu button on startup: {e}")
    
    while True:
        try:
            await dp.start_polling(bot)
        except Exception as e:
            print(f"Erro de conexão no Telegram: {e}")
            print("Tentando reconectar em 5 segundos...")
            import asyncio
            await asyncio.sleep(5)
```
