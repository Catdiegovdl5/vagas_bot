# Comprehensive Technical Analysis: Keyword Matching & Test Remediation

## Executive Summary
This report analyzes the root causes behind test failures in `test_keywords.py` and `run_tests.py` (pytest) for `bot.py`, and provides a precise, minimally invasive code fix.

---

## 1. Root Cause Breakdown

### Root Cause A: Flawed Short-Description Fallback in `check_co_occurrence`
- **Location**: `bot.py` (lines 887–899)
- **Mechanism**: The fallback was intended to pass short job descriptions (< 200 chars) if the title satisfied the co-occurrence rules. However, the existing code flattened all co-occurrence groups into `all_group_terms` and executed `for term in all_group_terms: return True`.
- **Impact**: Any short description whose job title matched **even a single word from ANY group** immediately returned `True`, completely bypassing co-occurrence requirements for other groups (such as AI or technical skill requirements).
- **Affected Tests**:
  1. `tests/test_relevance_stress.py::test_verb_ia_vs_acronym_ia`: Title `"Especialista que ia gerenciar a equipe"` returned `True` because `"especialista"` matched Group 1.
  2. `tests/test_tier1.py::test_especialista_ia_generativa_keywords`: Job 6 (`"Redator de Conteúdo Web"`, short reqs) returned `True` because `"redator"` matched Group 1.
  3. `tests/test_verify_multi_niche.py::test_developer_niche`: `job_missing_tech` (`"Desenvolvedor de Software"` with Java reqs) returned `True` because `"desenvolvedor"` matched Group 1.

### Root Cause B: Scope of `search_mapping` & Direct Invocations of `is_job_relevant`
- **Location**: `bot.py` (defined locally inside `_do_hunt` around line 1130)
- **Mechanism**: `search_mapping` translated UI/test display keywords (e.g. `"Backend Python"`, `"Gestor de Tráfego / Performance"`, `"Estagiário de TI / Programação"`, `"Desenvolvedor Júnior / Estagiário"`) into canonical keywords (`"python backend"`, `"gestor de trafego"`, etc.). Because it was trapped inside `_do_hunt`, direct calls to `is_job_relevant` from `test_keywords.py` bypassed keyword translation.
- **Impact**:
  - `kw_norm` became `"backend python"`. Since `"backend python"` was missing from `CO_OCCURRENCE_RULES`, `check_co_occurrence` fell back to strict exact word matching for both `"backend"` and `"python"`. For job title `"Desenvolvedor Python"`, `"backend"` was absent, resulting in `False` (8/19 failures in `test_keywords.py`).

### Root Cause C: `Backend Python` Mapping Expectation in `test_seniority_harness.py`
- **Location**: `bot.py` `search_mapping` vs `tests/test_seniority_harness.py` (line 92)
- **Mechanism**: `test_seniority_harness.py` explicitly tested that `_do_hunt` maps `"Backend Python"` to `"Python Backend"`. In `bot.py`, `"Backend Python"` was mapped to `"desenvolvedor python"`.
- **Impact**:
  - `tests/test_seniority_harness.py::test_do_hunt_keyword_transformation_levels` failed with `AssertionError: For level 'Todos', expected keyword 'Python Backend', got 'desenvolvedor python'`.

### Root Cause D: Missing Rules for `python backend` and `desenvolvedor junior / estagiario`
- **Mechanism**: `test_keywords.py` and legacy search modes test keywords like `"Desenvolvedor Júnior / Estagiário"` and `"Estagiário de TI / Programação"`.
- **Impact**: Without mapping `"Estagiário de TI / Programação"` and `"Desenvolvedor Júnior / Estagiário"` to `"desenvolvedor junior / estagiario"`, and providing `CO_OCCURRENCE_RULES` and `blacklist` entries for `"desenvolvedor junior / estagiario"` and `"python backend"`, approved/rejected cases in `test_keywords.py` failed.

---

## 2. Proposed Precise Fix for `bot.py`

### Step 1: Promote `search_mapping` to Module-Level `SEARCH_MAPPING`
Promote `search_mapping` to a top-level dictionary `SEARCH_MAPPING` in `bot.py` and ensure the following keys are correctly configured:
- `"Backend Python"` -> `"Python Backend"`
- `"Estagiário de TI / Programação"` -> `"desenvolvedor junior / estagiario"`
- `"Desenvolvedor Júnior / Estagiário"` -> `"desenvolvedor junior / estagiario"`
- `"Gestor de Tráfego / Performance"` -> `"gestor de trafego"`

### Step 2: Add Rules in `CO_OCCURRENCE_RULES` and `blacklist`
Add canonical rules for `"python backend"` and `"desenvolvedor junior / estagiario"`:
```python
CO_OCCURRENCE_RULES["python backend"] = [
    ["python", "django", "fastapi", "flask", "pandas", "scrapy", "numpy", "celery", "poetry", "pipenv", "asyncio", "backend"],
    ["desenvolvedor", "desenvolvedora", "programador", "programadora", "engenheiro", "engenheira", "dev", "backend", "back-end", "fullstack", "software engineer"]
]

CO_OCCURRENCE_RULES["desenvolvedor junior / estagiario"] = [
    ["desenvolvedor", "desenvolvedora", "programador", "programadora", "programacao", "dev", "ti", "software", "tecnologia", "sistemas"],
    ["junior", "jr", "jr.", "estagio", "estagiario", "estagiaria", "iniciante", "trainee"]
]

blacklist["python backend"] = ["professor", "tutor", "instrutor", "curso", "vendas", "comercial"]
blacklist["desenvolvedor junior / estagiario"] = ["direito", "pedagogia", "psicologia", "enfermagem", "medicina", "nutricao", "marketing", "vendas", "sdr", "bdr", "designer", "design", "rh", "recepcao", "portaria", "limpeza"]
```

### Step 3: Integrate `SEARCH_MAPPING` at Start of `is_job_relevant`
In `is_job_relevant(job, keyword, settings)`:
```python
clean_kw = SEARCH_MAPPING.get(keyword, keyword)
kw_norm = normalize_str(clean_kw)
```

### Step 4: Fix Short-Description Fallback in `check_co_occurrence`
Replace lines 887–899 in `bot.py` with strict group-matching:
```python
if job and len(job.get('requirements', '').strip()) < 200:
    title_norm = normalize_text_nfkd(job.get('title', ''))
    full_title_text = re.sub(r'(?<![a-z0-9])i\.?a\.?(?![a-z0-9])', 'ia', title_norm)
    title_matches_all_groups = True
    for group in groups:
        group_matched = False
        for word in group:
            word_norm = normalize_text_nfkd(word)
            parts = word_norm.split()
            if all(re.search(r'(?<![a-z0-9])' + re.escape(p) + r'(?![a-z0-9])', full_title_text) for p in parts):
                if "ia" in parts:
                    if not check_ia_validity(job.get('title', '')):
                        continue
                group_matched = True
                break
        if not group_matched:
            title_matches_all_groups = False
            break
    if title_matches_all_groups:
        return True
```

---

## 3. Impact Assessment & Verification

| Test Suite | Pre-Fix Status | Expected Post-Fix Status | Key Verification Points |
|---|---|---|---|
| `test_experience.py` | PASS (10/10) | PASS (10/10) | `user_level == 'ganhar experiencia'` logic unchanged and 100% compliant |
| `test_motor.py` | PASS (16/16) | PASS (16/16) | Co-occurrence logic unaffected |
| `test_keywords.py` | FAIL (8/19 failed) | PASS (19/19) | All approved, rejected, and boundary keyword cases pass |
| `run_tests.py` (pytest) | FAIL (5 failed out of 69) | PASS (69/69) | All 69 pytest stress, tier1, tier2, and harness tests pass |

---

## 4. Verification Command Matrix
```bash
python test_experience.py
python test_motor.py
python test_keywords.py
python run_tests.py
```
