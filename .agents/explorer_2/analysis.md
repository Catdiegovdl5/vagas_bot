# Analysis Report: `is_job_relevant` and `user_level == 'iniciantes tudo'` Logic

## Executive Summary
This document presents an analysis of `bot.py` located at `C:/Users/99196/OneDrive/Documentos/vagas_bot/bot.py`, specifically focusing on the `is_job_relevant` function (lines 1094–1223) and how user experience level filtering (`user_level`) is processed. Based on the current implementation for `'jovem aprendiz'` and `'ganhar experiência'`, this report formulates the exact Python logic required to support a new level category: `'iniciantes tudo'`.

---

## 1. Overview of `is_job_relevant` Architecture
The `is_job_relevant(job, keyword, settings)` function is responsible for determining whether a scraped job listing meets the user's search criteria.

### Call Context & Dependencies
- **Invoked from**: `_do_hunt` (lines 1346) during the local filtering stage (`# ------ FILTRO SUPREMO LOCAL ------`).
- **Inputs**:
  - `job` (dict): Contains keys `title`, `requirements`, `platform`, `location`, `company`, `link`, `budget`, etc.
  - `keyword` (str): Search term requested by the user.
  - `settings` (dict): User configuration containing keys like `level`, `location`, `contract`, `education`, etc.

### Core Processing Steps inside `is_job_relevant`:
1. **Normalization (lines 1095–1103)**:
   - Maps user keyword via `SEARCH_MAPPING`.
   - Normalizes text string fields (`title_norm`, `reqs_norm`, `full_text = title_norm + " " + reqs_norm`) using `normalize_str()` (NFD decomposition, ASCII encoding, lowercase).
   - Normalizes settings parameters: `user_level = normalize_str(settings.get('level', 'Todos'))`.
2. **Title Pre-filtering (lines 1105–1106)**: Rejects listings containing `'banco de talentos'` or `'talent pool'`.
3. **Description Quality Filter (lines 1120–1122)**: Rejects non-freelance jobs with description length < 15 characters (excluding LinkedIn/Indeed).
4. **Location & Contract Type Filters (lines 1124–1150)**: Enforces remote/presential and CLT/PJ contract preferences.
5. **Level Filtering (`user_level`) (lines 1152–1185)**: Evaluates seniorities (`'junior'`, `'pleno'`, `'senior'`, `'jovem aprendiz'`, `'ganhar experiencia'`).
6. **Deep Description Seniority Check (lines 1187–1211)**: Uses regex patterns on `reqs_norm` to verify required seniority level if title does not explicitly contain level terms (applies to `'junior'`, `'pleno'`, `'senior'`).
7. **Blacklist Filtering (lines 1213–1221)**:
   - `global_title_blacklist`: Rejects unwanted professions (Academic, Legal, Medical, Physical Labor, Volunteer).
   - `blacklist`: Niche-specific keyword blacklist.
8. **Co-occurrence Rules (line 1223)**: Evaluates term group occurrences via `check_co_occurrence(full_text, kw_norm, job=job)`.

---

## 2. Deep Dive: `user_level` Normalization and Existing Criteria

### String Normalization Behavior
When `user_level` is extracted from settings:
```python
user_level = normalize_str(settings.get('level', 'Todos'))
```
The `normalize_str` function (lines 473-476) removes diacritics and converts to lower case:
- `"Jovem Aprendiz"` $\rightarrow$ `'jovem aprendiz'`
- `"Ganhar Experiência"` $\rightarrow$ `'ganhar experiencia'`
- `"Iniciantes Tudo"` $\rightarrow$ `'iniciantes tudo'`

### Existing Criteria Breakdown

#### A. 'jovem aprendiz' Logic (lines 1171–1173)
```python
aprendiz_terms = ['aprendiz', 'jovem aprendiz', 'menor aprendiz']
...
elif user_level == 'jovem aprendiz':
    if not any(match_exact_word(full_text, w) for w in aprendiz_terms):
        return False
```
- **Evaluation Rule**: Evaluates to `True` (passes level check) IF AND ONLY IF `full_text` contains at least one term from `aprendiz_terms` as an exact word boundary match (`match_exact_word`).
- **Rejection Rule**: If no term from `aprendiz_terms` is found in `full_text`, the job is rejected (`return False`).

#### B. 'ganhar experiência' Logic (lines 1174–1184 & 1214)
```python
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
And in `global_title_blacklist` handling (line 1214):
```python
active_global_blacklist = [term for term in global_title_blacklist if term not in kw_norm and not (user_level == "ganhar experiencia" and term in ("voluntario", "voluntary"))]
```
- **Evaluation Rule**: Evaluates to `True` IF AND ONLY IF:
  1. `full_text` contains at least one substring matching `target_exp_terms`.
  2. `full_text` does NOT contain any exact word match from `higher_terms` (`"junior"`, `"jr"`, `"pleno"`, `"pl"`, `"senior"`, `"sr"`).
  3. `global_title_blacklist` excludes `"voluntario"` / `"voluntary"` so volunteer jobs are not blocked by the global title blacklist.

---

## 3. Formulation of Logic for `user_level == 'iniciantes tudo'`

### Specification
`user_level == 'iniciantes tudo'` must evaluate to `True` (pass the level filter) if the job satisfies **EITHER**:
1. The `'jovem aprendiz'` criteria (`is_jovem_aprendiz`), **OR**
2. The `'ganhar experiência'` criteria (`is_ganhar_experiencia`).

### Precise Boolean Logic Derivation
- Let `is_jovem_aprendiz` = `any(match_exact_word(full_text, w) for w in aprendiz_terms)`
- Let `is_ganhar_experiencia` = `any(term in full_text for term in target_exp_terms) and not any(match_exact_word(full_text, w) for w in higher_terms)`
- Let `passes_iniciantes_tudo` = `is_jovem_aprendiz or is_ganhar_experiencia`
- Rejection condition: `if not (is_jovem_aprendiz or is_ganhar_experiencia): return False`

### Global Blacklist Interaction
Because `'ganhar experiência'` permits volunteer roles (e.g. titles containing `"voluntario"` or `"voluntary"`), `'iniciantes tudo'` must also bypass the `"voluntario"` exclusion in `active_global_blacklist` (line 1214). Otherwise, a valid volunteer listing satisfying the `'ganhar experiência'` criteria would be prematurely rejected by `global_title_blacklist` on line 1215.

---

## 4. Proposed Code Modifications in `bot.py`

### Modification 1: `user_level` evaluation in `is_job_relevant` (lines 1171–1185)

```python
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
    elif user_level == 'iniciantes tudo':
        is_jovem_aprendiz = any(match_exact_word(full_text, w) for w in aprendiz_terms)
        
        target_exp_terms = [
            "voluntario", "voluntariado", "ong", "projeto social",
            "open source", "codigo aberto",
            "sem experiencia", "nao exige experiencia", "primeiro emprego", "estagio inicial"
        ]
        higher_terms = ["junior", "jr", "pleno", "pl", "senior", "sr"]
        is_ganhar_experiencia = (
            any(term in full_text for term in target_exp_terms)
            and not any(match_exact_word(full_text, w) for w in higher_terms)
        )
        
        if not (is_jovem_aprendiz or is_ganhar_experiencia):
            return False
```

### Modification 2: `active_global_blacklist` handling (line 1214)

```python
    # 1. Global Title Blacklist check (excluding terms in user search keyword)
    active_global_blacklist = [
        term for term in global_title_blacklist 
        if term not in kw_norm and not (user_level in ("ganhar experiencia", "iniciantes tudo") and term in ("voluntario", "voluntary"))
    ]
    if any(match_exact_word(title_norm, term) for term in active_global_blacklist):
        return False
```

---

## 5. Additional Considerations for Full Integration
To complete the support of `'Iniciantes Tudo'` across `bot.py`:
1. **Menu Options (`change_level` line 189)**:
   Add `"Iniciantes Tudo"` to the selectable levels list:
   `levels = ["Todos", "Júnior", "Pleno", "Sênior", "Jovem Aprendiz", "Ganhar Experiência", "Iniciantes Tudo"]`
2. **NLP Text Parser (`handle_free_text` lines 1572–1579)**:
   Optionally map phrases like `'iniciantes tudo'` or `'todos iniciantes'` to `'Iniciantes Tudo'`.

---

## Conclusion
The formulated logic guarantees that setting `user_level` to `'iniciantes tudo'` seamlessly evaluates job relevance according to either the `'jovem aprendiz'` standard OR the `'ganhar experiência'` standard, maintaining full compatibility with global title blacklists and existing normalization pipelines.
