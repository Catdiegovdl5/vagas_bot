# CHALLENGE REPORT — Empirical Stress Test of `is_job_relevant` (`user_level = 'iniciantes tudo'`)

**Author**: challenger_1 (EMPIRICAL CHALLENGER / Critic / Specialist)  
**Target Module**: `bot.py` -> `is_job_relevant()`  
**Target Level Setting**: `user_level = 'iniciantes tudo'` (and `iniciantes stuff`)  
**Date**: 2026-07-21  

---

## 1. Overall Risk Assessment: **CRITICAL**

Empirical stress testing of `is_job_relevant` for the `iniciantes tudo` setting revealed **three critical logical defects** and **one secondary keyword mismatch defect**. 

Out of 14 structured stress-test cases:
- **Passed**: 6 cases
- **Failed (Discrepancies)**: 8 cases

The defects lead to both severe **False Positives** (passing mid/senior developer jobs as zero-experience volunteer jobs) and **False Negatives** (blocking legitimate volunteer database/networking jobs).

---

## 2. Flaw Breakdown & Vulnerability Analysis

### Flaw 1: Substring Matching Bug on `"ong"` in `target_exp_terms` (CRITICAL)
- **Assumption Challenged**: Substring search (`term in full_text`) is sufficient to identify volunteer/ONG opportunities.
- **Mechanism**: `target_exp_terms` contains `"ong"`. `is_job_relevant` evaluates `has_target_exp = any(term in full_text for term in target_exp_terms)` using simple string inclusion (`in`).
- **Attack Scenario**: Any standard software job description mentioning technologies or words like `"MongoDB"`, `"longo"`, `"alongamento"`, `"strong"`, or `"among"` contains `"ong"`.
- **Blast Radius**: Massive false-positive leak. Mid-level and senior developer roles requiring MongoDB without explicit "junior/pleno/senior" titles pass as `is_ganhar_exp = True` under `iniciantes tudo`.
- **Empirical Proof**: `SUBSTR-01`, `SUBSTR-02`, `SUBSTR-03` all returned `True` (passed) for regular developer jobs requiring MongoDB or long-term projects.

---

### Flaw 2: Seniority Check Bypass in `is_aprendiz` (HIGH)
- **Assumption Challenged**: Checking `is_aprendiz or is_ganhar_exp` guarantees that only beginner-appropriate jobs pass.
- **Mechanism**: The boolean expression is `(is_aprendiz or is_ganhar_exp)`. While `is_ganhar_exp` explicitly verifies `not has_higher_terms`, `is_aprendiz` ONLY verifies `any(match_exact_word(full_text, w) for w in aprendiz_terms)` without checking for higher seniority levels.
- **Attack Scenario**: A job titled `"Aprendiz Pleno"` or `"Jovem Aprendiz Sênior"` has `is_aprendiz = True`. Thus, `(is_aprendiz or is_ganhar_exp)` evaluates to `True or False` -> `True`.
- **Blast Radius**: False positive acceptance of jobs requesting mid-level ("Pleno") or senior ("Sênior") experience simply because the job title includes "Aprendiz".
- **Empirical Proof**: `CONF-01` ("Aprendiz Pleno") and `CONF-02` ("Jovem Aprendiz Sênior") both returned `True` (passed).

---

### Flaw 3: Regex Word Boundary False Rejection on `"PL/SQL"` and `"SR-IOV"` (HIGH)
- **Assumption Challenged**: `match_exact_word(full_text, w)` with `(?<![a-z0-9])w(?![a-z0-9])` correctly isolates seniority indicators `pl` (Pleno) and `sr` (Sênior).
- **Mechanism**: Non-alphanumeric characters like `/` or `-` trigger regex word boundaries.
  - In `"PL/SQL"`, `/` is non-alphanumeric, so `match_exact_word("pl/sql", "pl")` matches `"pl"` as an exact word.
  - In `"sr-iov"`, `-` is non-alphanumeric, so `match_exact_word("sr-iov", "sr")` matches `"sr"`.
- **Attack Scenario**: A legitimate volunteer or open-source database job requiring PL/SQL or networking job mentioning SR-IOV gets `has_higher_terms = True`.
- **Blast Radius**: Legitimate zero-experience volunteer jobs in database administration or cloud infrastructure are incorrectly flagged as "Pleno" or "Sênior" and rejected.
- **Empirical Proof**: `BOUNDARY-01` and `BOUNDARY-02` returned `False` (rejected). Direct verification confirmed `match_exact_word("voluntario em redes sr-iov", "sr") == True`.

---

### Flaw 4: Short Keyword Co-Occurrence Rejection ("Dev") (MEDIUM)
- **Mechanism**: When searching for short keyword `"Dev"`, `kw_norm` is `"dev"`. `check_co_occurrence` uses `match_exact_word` for unmapped keywords, searching for exact word `\bdev\b`.
- **Attack Scenario**: Job titles using full Portuguese word `"Desenvolvedor"` fail to match `\bdev\b`.
- **Blast Radius**: User searching for keyword "Dev" misses jobs titled "Desenvolvedor Voluntário".
- **Empirical Proof**: `TC02` with keyword `"Dev"` returned `False` due to `check_co_occurrence`, whereas with keyword `"Desenvolvedor"` passed level evaluation.

---

## 3. Empirical Test Results Matrix

The following table summarizes results from `.agents/challenger_1/stress_test_iniciantes.py`:

| Test ID | Category | Job Title | Input Reqs / Terms | Expected | Got | Level Filter Status | Full Func Status |
| :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: |
| **SUB-01** | Standard Valid | Jovem Aprendiz de TI | Suporte básico e aprendizado | True | True | **PASS** | **PASS** |
| **SUB-02** | Standard Valid | Desenvolvedor Voluntário | Projeto social para ONG | True | True | **PASS** | **PASS** |
| **SUB-03** | Standard Valid | Projeto Open Source | Código aberto sem experiência | True | True | **PASS** | **PASS** |
| **CONF-01** | Conflicting Level | Aprendiz Pleno | Jovem aprendiz nível pleno | False | True | **FAIL (Leak)** | **FAIL (Leak)** |
| **CONF-02** | Conflicting Level | Jovem Aprendiz Sênior | Apoiar equipe sênior | False | True | **FAIL (Leak)** | **FAIL (Leak)** |
| **CONF-03** | Conflicting Level | Voluntário Sênior | Perfil sênior em arquitetura | False | False | **PASS** | **PASS** |
| **CONF-04** | Conflicting Level | Open Source Sênior | Liderança sênior | False | False | **PASS** | **PASS** |
| **CONF-05** | Conflicting Level | Dev Júnior 1 ano exp | 1 ano de experiência prévia | False | False | **PASS** | **PASS** |
| **SUBSTR-01**| Substring Bug | Desenvolvedor Python | Requisitos: MongoDB, FastAPI | False | True | **FAIL (Leak)** | **FAIL (Leak)** |
| **SUBSTR-02**| Substring Bug | Engenheiro Software | Projeto de longo prazo | False | True | **FAIL (Leak)** | **FAIL (Leak)** |
| **SUBSTR-03**| Substring Bug | Analista Sistemas | Strong skills in architecture | False | True | **FAIL (Leak)** | **FAIL (Leak)** |
| **BOUND-01** | Word Boundary | Desenvolvedor Voluntário | Projeto social com PL/SQL | True | False | **FAIL (Block)** | **FAIL (Block)** |
| **BOUND-02** | Word Boundary | Projeto Open Source | Stored procedures em PL/SQL | True | False | **FAIL (Block)** | **FAIL (Block)** |
| **CASE-01** | Case & Accents | JOVEM APRENDIZ DE TI | UPPERCASE TEXT | True | True | **PASS** | **PASS** |
| **CASE-02** | Case & Accents | DESENVOLVEDOR VOLUNTÁRIO| PROJETO CÓDIGO ABERTO | True | True | **PASS** | **PASS** |

---

## 4. Proposed Fixes & Mitigations

### 1. Fix Substring Matching in `target_exp_terms`
Replace raw substring matching `term in full_text` with `match_exact_word(full_text, term)` or word boundary regex for single-word terms like `"ong"`.
```python
# FIX: Use word boundaries for short terms like 'ong'
target_exp_terms = [
    "voluntario", "voluntariado", "ong", "projeto social",
    "open source", "codigo aberto",
    "sem experiencia", "nao exige experiencia", "primeiro emprego", "estagio inicial"
]
has_target_exp = any(match_exact_word(full_text, term) if len(term.split()) == 1 else term in full_text for term in target_exp_terms)
```

### 2. Fix Seniority Exclusion for `is_aprendiz`
Enforce `not has_higher_terms` or title-level seniority check on `is_aprendiz`.
```python
# FIX: Ensure Aprendiz jobs do not contain conflicting senior/pleno titles
has_higher_terms = any(match_exact_word(full_text, w) for w in higher_terms)
title_has_higher = any(match_exact_word(title_norm, w) for w in higher_terms)

is_aprendiz = any(match_exact_word(full_text, w) for w in aprendiz_terms) and not title_has_higher
is_ganhar_exp = has_target_exp and not has_higher_terms

if not (is_aprendiz or is_ganhar_exp):
    return False
```

### 3. Fix Regex Boundary for `pl` and `sr`
Exclude technology tokens like `"pl/sql"` and `"sr-iov"` before evaluating `higher_terms`.
```python
# FIX: Sanitize technical acronyms before matching 'pl' and 'sr'
sanitized_text = re.sub(r'\bpl/sql\b', 'plsql', full_text)
sanitized_text = re.sub(r'\bsr-iov\b', 'sriov', sanitized_text)

has_higher_terms = any(match_exact_word(sanitized_text, w) for w in higher_terms)
```

---

## 5. Harness Execution Command

To re-verify at any time, run:
```bash
python .agents/challenger_1/stress_test_iniciantes.py
```
