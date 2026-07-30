# Detailed Analysis Report: `is_job_relevant` and Design of `test_iniciantes.py`

## 1. Executive Summary

This report documents the read-only investigation of the test suite in `vagas_bot` (`C:/Users/99196/OneDrive/Documentos/vagas_bot`) and the underlying filtering function `is_job_relevant` located in `bot.py` (lines 1094–1223). 

The goal of this analysis is to evaluate how beginner job criteria ("Ganhar Experiência", "Jovem Aprendiz", "Júnior") are processed and to provide a complete design for `test_iniciantes.py` that validates the following three core acceptance criteria:
1. **Vaga "Dev Voluntário"** under criterion **"Ganhar Experiência"** $\rightarrow$ **`True`**
2. **Vaga "Jovem Aprendiz de TI"** under criterion **"Jovem Aprendiz"** $\rightarrow$ **`True`**
3. **Vaga "Dev Júnior 1 ano de experiência"** under criterion **"Ganhar Experiência"** / **"Jovem Aprendiz"** $\rightarrow$ **`False`**

---

## 2. Analysis of Existing Test Files

The `vagas_bot` codebase utilizes a hybrid testing structure consisting of root-level standalone test scripts and a Pytest test battery under `tests/`.

### 2.1 `test_experience.py`
- **Location**: `C:/Users/99196/OneDrive/Documentos/vagas_bot/test_experience.py`
- **Focus**: Tests the `"Ganhar Experiência"` level setting in `is_job_relevant`.
- **Key Mechanics**:
  - Sets `test_settings = {"level": "ganhar experiência", "location": "Brasil (Remoto)", "contract": "Todos", "education": "Todos", "platforms": {}, "ai_filter": False}`.
  - Defines array of tuples `(Title, Requirements, Keyword, Expected Result, Description)`.
  - Iterates over cases, invoking `is_job_relevant(job, keyword, test_settings)`.
  - Outputs `[PASS]` / `[FAIL]` per case with colorized formatting and exits via `sys.exit(0)` or `os._exit(1)`.
- **Relevant Test Cases**:
  - Line 29: `"Dev Voluntário em ONG"` $\rightarrow$ `True`
  - Line 43: `"Dev Júnior 1 ano de experiência"` $\rightarrow$ `False` (blocked by `"júnior"`)

### 2.2 `test_motor.py`
- **Location**: `C:/Users/99196/OneDrive/Documentos/vagas_bot/test_motor.py`
- **Focus**: Tests search keyword co-occurrence (`CO_OCCURRENCE_RULES`) and false-positive blocking (e.g. "Enfermeira com python").
- **Key Mechanics**: Isolates `normalize_str`, `match_exact_word`, and `check_co_occurrence` to test True Positives vs False Positives independently of location/level settings.

### 2.3 `test_keywords.py`
- **Location**: `C:/Users/99196/OneDrive/Documentos/vagas_bot/test_keywords.py`
- **Focus**: Tests niche keyword mapping (`SEARCH_MAPPING`), global blacklist terms, and contract/level boundaries.
- **Key Mechanics**:
  - Tests 5 approved cases, 5 rejected cases, and 10 boundary cases.
  - Verifies that global blacklist terms (e.g., `"professor"`, `"faxineiro"`) correctly reject irrelevant jobs.

### 2.4 `run_tests.py`
- **Location**: `C:/Users/99196/OneDrive/Documentos/vagas_bot/run_tests.py`
- **Focus**: Pytest test suite orchestrator.
- **Key Mechanics**:
  - Invokes `pytest.main(["-v", "-p", "no:warnings", tests_dir])` targeting the `tests/` directory.
  - Returns exit code `0` on success.

### 2.5 `tests/` Directory Suite (`test_tier1.py` - `test_tier4.py`, `conftest.py`)
- Standard Pytest test modules targeting database queries, scrapers, AI filters, and seniority harness.
- `conftest.py` provides database initialization (`setup_test_db`) and mocks for `playwright`, `groq`, `requests`, and background ATS servers.

---

## 3. Analysis of `is_job_relevant` Evaluation Engine (`bot.py`)

The filtering function `is_job_relevant(job, keyword, settings)` executes a multi-stage filtering pipeline:

```
[Input Job] ──> 1. Keyword Mapping & Text Normalization
            ──> 2. Talent Pool Blacklist Check ("banco de talentos")
            ──> 3. Platform & Location Filter (Remoto / Local)
            ──> 4. Contract Filter (CLT vs PJ)
            ──> 5. Level / Seniority Filter (Ganhar Experiência / Jovem Aprendiz / Júnior / Pleno / Sênior)
            ──> 6. Global Title Blacklist Check (with Exception Rules)
            ──> 7. Niche Local Blacklist Check
            ──> 8. Search Engine Co-Occurrence Check (CO_OCCURRENCE_RULES)
            ──> [Result: True / False]
```

### 3.1 Level Filter Logic Breakdown for Beginner Profiles (`bot.py:1162–1184`)

```python
    junior_terms = ['junior', 'jr', 'estagio', 'estagiario', 'trainee', 'assistente', 'auxiliar']
    senior_terms = ['senior', 'sr', 'especialista', 'coordenador', 'gerente', 'diretor', 'tech lead', 'head', 'lead', 'executivo', 'executive', 'architect', 'arquiteto', 'vp', 'manager', 'gestor']
    pleno_terms = ['pleno', 'pl']
    aprendiz_terms = ['aprendiz', 'jovem aprendiz', 'menor aprendiz']
    
    ...
    elif user_level == 'jovem aprendiz':
        if not any(match_exact_word(full_text, w) for w in aprendiz_terms):
            return False
    elif user_level == 'ganhar experiencia':
        target_exp_terms = [
            "voluntario", "voluntariado", "ong", "projeto social",
            "open source", "codigo aberto",
            "sem experiencia", "nao exige experiencia", "primeiro emprego", "estagio inicial"
        ]
        if not any(term in full_text for term in target_exp_terms):
            return False
        higher_terms = ["junior", "jr", "pleno", "pl", "senior", "sr"]
        if any(match_exact_word(full_text, w) for w in higher_terms):
            return False
```

### 3.2 Global Title Blacklist Exemption Rule (`bot.py:1213–1216`)

The global blacklist (`global_title_blacklist`, line 478) includes terms like `"professor"`, `"advogado"`, `"voluntario"`, `"voluntary"`.

To allow voluntary jobs when candidate level is `"Ganhar Experiência"`, `is_job_relevant` filters out `"voluntario"` and `"voluntary"` from `active_global_blacklist`:

```python
    active_global_blacklist = [term for term in global_title_blacklist if term not in kw_norm and not (user_level == "ganhar experiencia" and term in ("voluntario", "voluntary"))]
    if any(match_exact_word(title_norm, term) for term in active_global_blacklist):
        return False
```

---

## 4. Evaluation of Acceptance Criteria

| Criteria # | Test Case Description | User Level Setting | Expected Result | Evaluation Mechanics |
| :--- | :--- | :--- | :---: | :--- |
| **1** | Vaga **"Dev Voluntário"** | `"Ganhar Experiência"` | **`True`** | 1. `full_text` matches `"voluntario"` in `target_exp_terms`. <br>2. `higher_terms` (`junior`, `pleno`, `senior`) are absent. <br>3. `"voluntario"` is excluded from `active_global_blacklist` for `"ganhar experiencia"`. <br>4. Keyword `"Dev"` matches co-occurrence rules. |
| **2** | Vaga **"Jovem Aprendiz de TI"** | `"Jovem Aprendiz"` | **`True`** | 1. `full_text` matches `"jovem aprendiz"` in `aprendiz_terms`. <br>2. No global or local blacklists block `"aprendiz"`. <br>3. Keyword `"TI"` or `"Dev"` matches co-occurrence rules. |
| **3** | Vaga **"Dev Júnior 1 ano de experiência"** | `"Ganhar Experiência"` | **`False`** | 1. `higher_terms` contains `"junior"`. <br>2. `match_exact_word(full_text, "junior")` matches `"júnior"`. <br>3. Function immediately returns `False`. |
| **3b** | Vaga **"Dev Júnior 1 ano de experiência"** | `"Jovem Aprendiz"` | **`False`** | 1. `aprendiz_terms` (`['aprendiz', 'jovem aprendiz', 'menor aprendiz']`) are absent. <br>2. Function immediately returns `False`. |

---

## 5. Design of `test_iniciantes.py`

Below is the complete proposed source code for `test_iniciantes.py`. It features dual compatibility:
- Executable via `pytest` (standard `test_*` functions).
- Executable as a CLI script (`python test_iniciantes.py`) returning exit code 0 or 1.

```python
"""
test_iniciantes.py - Suíte de Testes para Perfis Iniciantes (Ganhar Experiência & Jovem Aprendiz)

Valida os critérios de aceitação:
1. Vaga "Dev Voluntário" (critério Ganhar Experiência) -> True
2. Vaga "Jovem Aprendiz de TI" (critério Aprendiz) -> True
3. Vaga "Dev Júnior 1 ano de experiência" -> False
"""

import sys
import os
import pytest

# Configura encoding stdout para suporte ao terminal Windows
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Garante que o diretório raiz esteja no sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from bot import is_job_relevant
except ImportError:
    # Se rodar dentro de subdiretório de testes
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from bot import is_job_relevant


# ─────────────────────────────────────────────
# CONFIGURAÇÕES DE TESTE DE PERFIS INICIANTES
# ─────────────────────────────────────────────

SETTINGS_GANHAR_EXPERIENCIA = {
    "level": "Ganhar Experiência",
    "location": "Brasil (Remoto)",
    "contract": "Todos",
    "education": "Todos",
    "platforms": {},
    "ai_filter": False
}

SETTINGS_JOVEM_APRENDIZ = {
    "level": "Jovem Aprendiz",
    "location": "Brasil (Remoto)",
    "contract": "Todos",
    "education": "Todos",
    "platforms": {},
    "ai_filter": False
}


# ─────────────────────────────────────────────
# CASOS DE TESTE PRINCIPAIS (MATRIZ DE ACEITAÇÃO)
# ─────────────────────────────────────────────

TEST_CASES_INICIANTES = [
    # (Job Dict, Keyword, Settings, Expected, Description)
    (
        {
            "title": "Dev Voluntário",
            "requirements": "Desenvolvimento de software voluntário para causa social.",
            "platform": "linkedin",
            "location": "Remoto"
        },
        "Dev",
        SETTINGS_GANHAR_EXPERIENCIA,
        True,
        "1. Vaga 'Dev Voluntário' (critério Ganhar Experiência) -> True"
    ),
    (
        {
            "title": "Jovem Aprendiz de TI",
            "requirements": "Vaga para jovem aprendiz atuando na área de tecnologia da informação.",
            "platform": "linkedin",
            "location": "Remoto"
        },
        "Dev",
        SETTINGS_JOVEM_APRENDIZ,
        True,
        "2. Vaga 'Jovem Aprendiz de TI' (critério Aprendiz) -> True"
    ),
    (
        {
            "title": "Dev Júnior 1 ano de experiência",
            "requirements": "Buscamos desenvolvedor júnior com 1 ano de experiência prévia.",
            "platform": "linkedin",
            "location": "Remoto"
        },
        "Dev",
        SETTINGS_GANHAR_EXPERIENCIA,
        False,
        "3a. Vaga 'Dev Júnior 1 ano de experiência' (critério Ganhar Experiência) -> False"
    ),
    (
        {
            "title": "Dev Júnior 1 ano de experiência",
            "requirements": "Buscamos desenvolvedor júnior com 1 ano de experiência prévia.",
            "platform": "linkedin",
            "location": "Remoto"
        },
        "Dev",
        SETTINGS_JOVEM_APRENDIZ,
        False,
        "3b. Vaga 'Dev Júnior 1 ano de experiência' (critério Jovem Aprendiz) -> False"
    ),
    # Casos de Borda Adicionais para Validação de Perfil Iniciante
    (
        {
            "title": "Desenvolvedor - Projeto Open Source para Iniciantes",
            "requirements": "Contribuição para código aberto e auxílio a novos desenvolvedores.",
            "platform": "github_vagas",
            "location": "Remoto"
        },
        "Desenvolvedor",
        SETTINGS_GANHAR_EXPERIENCIA,
        True,
        "4. Vaga 'Open Source para Iniciantes' (critério Ganhar Experiência) -> True"
    ),
    (
        {
            "title": "Dev Pleno",
            "requirements": "Desenvolvedor pleno com 3 anos de experiência.",
            "platform": "linkedin",
            "location": "Remoto"
        },
        "Dev",
        SETTINGS_GANHAR_EXPERIENCIA,
        False,
        "5. Vaga 'Dev Pleno' (critério Ganhar Experiência) -> False (bloqueado por pleno)"
    ),
    (
        {
            "title": "Estagiário de Programação TI",
            "requirements": "Vaga de estágio inicial para estudantes de TI sem experiência.",
            "platform": "catho",
            "location": "Remoto"
        },
        "Dev",
        SETTINGS_GANHAR_EXPERIENCIA,
        True,
        "6. Vaga 'Estágio Inicial Sem Experiência' (critério Ganhar Experiência) -> True"
    )
]


# ─────────────────────────────────────────────
# TESTES COMPATÍVEIS COM PYTEST
# ─────────────────────────────────────────────

def test_dev_voluntario_ganhar_experiencia():
    """Valida Critério 1: Dev Voluntário sob Ganhar Experiência deve passar (True)."""
    job = {
        "title": "Dev Voluntário",
        "requirements": "Desenvolvimento de software voluntário para causa social.",
        "platform": "linkedin",
        "location": "Remoto"
    }
    assert is_job_relevant(job, "Dev", SETTINGS_GANHAR_EXPERIENCIA) is True


def test_jovem_aprendiz_ti():
    """Valida Critério 2: Jovem Aprendiz de TI sob Jovem Aprendiz deve passar (True)."""
    job = {
        "title": "Jovem Aprendiz de TI",
        "requirements": "Vaga para jovem aprendiz atuando na área de tecnologia da informação.",
        "platform": "linkedin",
        "location": "Remoto"
    }
    assert is_job_relevant(job, "Dev", SETTINGS_JOVEM_APRENDIZ) is True


def test_dev_junior_com_experiencia_rejeitado():
    """Valida Critério 3: Dev Júnior 1 ano de experiência deve ser rejeitado (False)."""
    job = {
        "title": "Dev Júnior 1 ano de experiência",
        "requirements": "Buscamos desenvolvedor júnior com 1 ano de experiência prévia.",
        "platform": "linkedin",
        "location": "Remoto"
    }
    assert is_job_relevant(job, "Dev", SETTINGS_GANHAR_EXPERIENCIA) is False
    assert is_job_relevant(job, "Dev", SETTINGS_JOVEM_APRENDIZ) is False


@pytest.mark.parametrize("job,keyword,settings,expected,desc", TEST_CASES_INICIANTES)
def test_iniciantes_matrix(job, keyword, settings, expected, desc):
    """Execução parametrizada da matriz de testes iniciantes via Pytest."""
    assert is_job_relevant(job, keyword, settings) == expected


# ─────────────────────────────────────────────
# EXECUTOR CLI STANDALONE
# ─────────────────────────────────────────────

def run_cli():
    print("=" * 65)
    print("   SUÍTE DE TESTES: test_iniciantes.py (Vagas Iniciantes)")
    print("=" * 65)

    failed_count = 0
    for job, keyword, settings, expected, desc in TEST_CASES_INICIANTES:
        result = is_job_relevant(job, keyword, settings)
        status = "PASS" if result == expected else "FAIL"
        if result != expected:
            failed_count += 1
            print(f"[FAIL] {desc}")
            print(f"       Obtido: {result} | Esperado: {expected} | Título: {job['title']}")
        else:
            print(f"[PASS] {desc}")

    print("=" * 65)
    if failed_count == 0:
        print("TODOS OS TESTES DE INICIANTES PASSARAM COM SUCESSO! Code: 0")
        sys.exit(0)
    else:
        print(f"SUÍTE DE TESTES FALHOU COM {failed_count} ERROS! Code: 1")
        sys.exit(1)


if __name__ == "__main__":
    run_cli()
```

---

## 6. Verification Method

To verify the test suite once implemented:

1. **Standalone CLI Execution**:
   ```bash
   python test_iniciantes.py
   ```
   *Expected Output*: Exit code `0` and 100% `[PASS]` output.

2. **Pytest Integration**:
   ```bash
   pytest -v test_iniciantes.py
   ```
   *Expected Output*: `7 passed in X.XXs`.

3. **Full Test Suite Execution**:
   ```bash
   python run_tests.py
   ```
