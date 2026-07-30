# Handoff Report — Milestone 3 (Regression & Suite Review)

**Reviewer Agent**: Reviewer 2 (`teamwork_preview_reviewer_exp_2`)  
**Working Directory**: `C:\Users\99196\OneDrive\Documentos\vagas_bot\.agents\teamwork_preview_reviewer_exp_2`  
**Target Codebase**: `C:\Users\99196\OneDrive\Documentos\vagas_bot`  
**Verdict**: **REQUEST_CHANGES**  

---

## 1. Observation

Direct command execution and output logs gathered during testing:

### Execution 1: `python test_experience.py`
- **Command**: `python test_experience.py`
- **Exit Code**: 0 (PASSED)
- **Output**:
```
============================================================
RUNNING TEST SUITE: test_experience.py ('Ganhar Experiência')
============================================================
[PASS] 1. Vaga 'Dev Voluntário em ONG' -> True
[PASS] 2. Vaga 'Dev - Estágio Inicial Sem Experiência' -> True
[PASS] 3. Vaga 'Dev Júnior 1 ano de experiência' -> False (blocked by 'júnior')
[PASS] 4. Vaga 'Dev - Projeto Open Source para Iniciantes' -> True
[PASS] 5a. Vaga 'Dev Pleno' -> False (blocked by 'pleno')
[PASS] 5b. Vaga 'Dev Sênior' -> False (blocked by 'sênior')
[PASS] 5c. Vaga 'Dev Python' sem termos de experiência -> False
[PASS] 5d. Vaga 'Dev Voluntário Pleno' -> False (has target term but blocked by 'pleno')
[PASS] 5e. Vaga 'Desenvolvedor Sem Experiência' -> True
[PASS] 5f. Vaga 'Desenvolvedor Voluntary Project' -> True (voluntary exempted)
============================================================
ALL EXPERIENCE LEVEL TEST CASES PASSED SUCCESSFULLY! Exit code 0.
```

### Execution 2: `python test_motor.py`
- **Command**: `python test_motor.py`
- **Exit Code**: 0 (PASSED)
- **Output**:
```
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

### Execution 3: `python test_keywords.py`
- **Command**: `python test_keywords.py`
- **Exit Code**: 1 (FAILED)
- **Output**:
```
Successfully imported is_job_relevant and normalize_str from bot.py

--- Running Approved Cases ---
Title: 'Desenvolvedor Python' | Keyword: 'Backend Python' -> Got: False | Expected: True
FAIL!
Title: 'Especialista em IA Generativa' | Keyword: 'Especialista em IA Generativa' -> Got: False | Expected: True
FAIL!
Title: 'Estagiário de Programação' | Keyword: 'Estagiário de TI / Programação' -> Got: False | Expected: True
FAIL!
Title: 'Auxiliar Administrativo' | Keyword: 'Auxiliar Administrativo' -> Got: False | Expected: True
FAIL!
Title: 'Gestor de Tráfego Pago' | Keyword: 'Gestor de Tráfego / Performance' -> Got: False | Expected: True
FAIL!

--- Running Rejected Cases ---
Title: 'Professor de Python' | Keyword: 'Backend Python' -> Got: False | Expected: False
PASS
Title: 'Tutor de IA' | Keyword: 'Especialista em IA' -> Got: False | Expected: False
PASS
Title: 'Estagiário de Direito' | Keyword: 'Desenvolvedor Júnior / Estagiário' -> Got: False | Expected: False
PASS
Title: 'Auxiliar de Limpeza' | Keyword: 'Auxiliar Administrativo' -> Got: False | Expected: False
PASS
Title: 'Faxineiro' | Keyword: 'Auxiliar Administrativo' -> Got: False | Expected: False
PASS

--- Running Boundary Cases ---
Title: 'Desenvolvedor Python Professor' | Keyword: 'Backend Python' | Settings: {'level': 'Todos', 'location': 'Brasil (Remoto)', 'contract': 'Todos', 'education': 'Todos', 'platforms': {}, 'ai_filter': False} -> Got: False | Expected: False
PASS
Title: 'Professor de Desenvolvedor Python' | Keyword: 'Backend Python' | Settings: {'level': 'Todos', 'location': 'Brasil (Remoto)', 'contract': 'Todos', 'education': 'Todos', 'platforms': {}, 'ai_filter': False} -> Got: False | Expected: False
PASS
Title: 'Senior Python Developer' | Keyword: 'Backend Python' | Settings: {'level': 'junior', 'location': 'Brasil (Remoto)', 'contract': 'Todos', 'education': 'Todos', 'platforms': {}, 'ai_filter': False} -> Got: False | Expected: False
PASS
Title: 'Desenvolvedor Python Pleno' | Keyword: 'Backend Python' | Settings: {'level': 'junior', 'location': 'Brasil (Remoto)', 'contract': 'Todos', 'education': 'Todos', 'platforms': {}, 'ai_filter': False} -> Got: False | Expected: False
PASS
Title: 'Desenvolvedor Python PJ' | Keyword: 'Backend Python' | Settings: {'level': 'Todos', 'location': 'Brasil (Remoto)', 'contract': 'clt', 'education': 'Todos', 'platforms': {}, 'ai_filter': False} -> Got: False | Expected: False
PASS
Title: 'Desenvolvedor Python - PJ' | Keyword: 'Backend Python' | Settings: {'level': 'Todos', 'location': 'Brasil (Remoto)', 'contract': 'clt', 'education': 'Todos', 'platforms': {}, 'ai_filter': False} -> Got: False | Expected: False
PASS
Title: 'Junior Python Developer' | Keyword: 'Backend Python' | Settings: {'level': 'junior', 'location': 'Brasil (Remoto)', 'contract': 'Todos', 'education': 'Todos', 'platforms': {}, 'ai_filter': False} -> Got: False | Expected: True
FAIL!
Title: 'Desenvolvedor Python PJ' | Keyword: 'Backend Python' | Settings: {'level': 'Todos', 'location': 'Brasil (Remoto)', 'contract': 'pj', 'education': 'Todos', 'platforms': {}, 'ai_filter': False} -> Got: False | Expected: True
FAIL!
Title: 'Desenvolvedor Python' | Keyword: 'Backend Python' | Settings: {'level': 'Todos', 'location': 'Brasil (Remoto)', 'contract': 'clt', 'education': 'Todos', 'platforms': {}, 'ai_filter': False} -> Got: False | Expected: True
FAIL!

Some tests FAILED!
```

### Execution 4: `python run_tests.py` (Pytest Suite)
- **Command**: `python run_tests.py`
- **Exit Code**: 1 (FAILED — 64 passed, 5 failed)
- **Failed Tests Summary**:
  1. `tests/test_relevance_stress.py::test_verb_ia_vs_acronym_ia` - FAILED
  2. `tests/test_seniority_harness.py::test_do_hunt_keyword_transformation_levels` - FAILED
  3. `tests/test_seniority_harness.py::test_do_hunt_concurrency_and_performance` - FAILED
  4. `tests/test_tier1.py::test_especialista_ia_generativa_keywords` - FAILED
  5. `tests/test_verify_multi_niche.py::test_developer_niche` - FAILED

---

## 2. Logic Chain

1. **Observation**: Executing `python test_keywords.py` yielded 8 failures out of 19 test cases, causing a non-zero exit code (1).
2. **Observation**: Executing `python run_tests.py` (Pytest suite) yielded 5 failures out of 69 test cases (`test_relevance_stress.py`, `test_seniority_harness.py`, `test_tier1.py`, `test_verify_multi_niche.py`).
3. **Reasoning**:
   - In `bot.py`, recent modifications to `check_co_occurrence` and `is_job_relevant` introduced severe false-negative filtering for valid job postings when search keywords differ slightly from exact `CO_OCCURRENCE_RULES` keys (e.g. `Backend Python`, `Estagiário de TI / Programação`, `Gestor de Tráfego / Performance`).
   - Specifically, `check_co_occurrence` in `bot.py:918-925` splits search keywords into significant words and demands an exact match for EVERY word in `text_norm`. When search keyword is `"Backend Python"` and job title is `"Desenvolvedor Python"` (with empty requirements), `"backend"` fails exact word matching, returning `False` for valid python developer jobs.
   - Conversely, `test_tier1.py::test_especialista_ia_generativa_keywords` and `test_verify_multi_niche.py::test_developer_niche` fail because `is_job_relevant` returns `True` for non-matching jobs (false positives for non-Python software dev jobs and non-AI writing jobs).
4. **Conclusion**: Modifications in `bot.py` introduced functional regressions to existing test suites `test_keywords.py` and `pytest`. Per project quality standards, work products with failing regression test suites cannot be approved.

---

## 3. Caveats

- Tests for live web scrapers (`scrapers/catho.py`, `scrapers/workana.py`, etc.) that query external HTTP endpoints directly were not run against live endpoints due to sandbox network boundaries (`CODE_ONLY` mode). Unit/mock tests were executed.
- `test_experience.py` (10/10) and `test_motor.py` (16/16) passed completely without regressions.

---

## 4. Conclusion

- **Verdict**: **REQUEST_CHANGES**
- **Critical Findings**:
  - `test_keywords.py`: FAILED with 8 failed cases due to false negatives in `is_job_relevant` co-occurrence fallback logic.
  - `python run_tests.py` / `pytest`: FAILED with 5 test failures across `test_relevance_stress.py`, `test_seniority_harness.py`, `test_tier1.py`, and `test_verify_multi_niche.py`.

---

## 5. Verification Method

To independently verify all findings:

```powershell
cd C:\Users\99196\OneDrive\Documentos\vagas_bot

# 1. Run experience tests (Passes)
python test_experience.py

# 2. Run motor tests (Passes)
python test_motor.py

# 3. Run keywords tests (Fails - exit code 1)
python test_keywords.py

# 4. Run pytest suite (Fails - 5 failures, exit code 1)
python run_tests.py
```
