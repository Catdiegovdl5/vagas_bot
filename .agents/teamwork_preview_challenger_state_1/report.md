# Empirical Verification Report — State Location Search & Adversarial Testing

**Agent**: Challenger 1 (retried)  
**Date**: 2026-07-21  
**Target Repository**: `C:/Users/99196/OneDrive/Documentos/vagas_bot`  
**Working Directory**: `C:/Users/99196/OneDrive/Documentos/vagas_bot/.agents/teamwork_preview_challenger_state_1`

---

## 1. Executive Summary

Empirical testing was conducted across existing state location test suites (`test_location_state.py` and `test_location_uf.py`) as well as an adversarial stress suite (`test_location_adversarial_challenger.py`).

- **Existing Test Suites**:
  - `python test_location_uf.py`: **21 / 21 PASS (100%)**
  - `python test_location_state.py`: **18 / 18 PASS (100%)**
- **Adversarial Stress Test Suite**:
  - `python test_location_adversarial_challenger.py`: **150 / 152 PASS (98.68%)**
  - **2 Empirical Vulnerabilities / Failure Modes Discovered**.

---

## 2. Test Execution Details & Metrics

### 2.1 Existing Test Suite: `test_location_uf.py`
- **Command Executed**: `python test_location_uf.py`
- **Total Tests**: 21
- **Passed**: 21
- **Failed**: 0
- **Pass Rate**: 100%
- **Key Categories Covered**:
  1. Anti-false-positive word boundary matching (e.g. `Especialista` containing `sp` rejected for SP filter).
  2. Direct UF acronym matching for core states (SP, RJ, MG, PR, RS, SC, BA, DF).
  3. 100% Remote job retention across state filters.
  4. Cross-state rejection (State A job rejected when filtering for State B).
  5. Unfiltered search wildcard acceptance.

### 2.2 Existing Test Suite: `test_location_state.py`
- **Command Executed**: `python test_location_state.py`
- **Total Tests**: 18
- **Passed**: 18
- **Failed**: 0
- **Pass Rate**: 100%
- **Key Categories Covered**:
  1. End-to-end parameter passing in `app.py` (`/api/trigger` passing `location="SP"` to `is_job_relevant`).
  2. Complete audit of all 27 Brazilian UFs in `bot.py` (`UF_MAP`), `static/index.html` (`#state-select`), and JavaScript frontend (`UF_MAP`).
  3. 100% Remote job retention & state/city location matching.

---

## 3. Adversarial Stress Testing Results (`test_location_adversarial_challenger.py`)

- **Command Executed**: `python test_location_adversarial_challenger.py`
- **Total Tests**: 152
- **Passed**: 150
- **Failed**: 2
- **Pass Rate**: 98.68%

### Breakdown by Stress Dimension:

| Category | Description | Tests Run | Pass | Fail | Pass Rate |
|---|---|---|---|---|---|
| **Cat 1: Accents & Diacritics** | Mixed casing, diacritics removal (São Paulo vs sao paulo, Ceará, Amapá, Paraná, Maranhão, Piauí, Rondônia, Goiás, Pará, Espírito Santo) | 22 | 22 | 0 | 100% |
| **Cat 2: Anti-False-Positives** | Substring collision avoidance across all 27 UFs (e.g. `ACesso`, `ALto`, `AMbiente`, `APlicacao`, `BAckend`, `CEntro`, `ESpecialista`, `pDF`, `reSPonsavel`) and punctuation boundary tests (`SP.`, `SP,`, `SP-Brasil`, `(SP)`, `SP/RJ`) | 31 | 31 | 0 | 100% |
| **Cat 3: Vulnerabilities & Collisions** | Preposition collisions and cross-state name substring collisions | 2 | 0 | 2 | 0% |
| **Cat 4: Remote-State Combos** | Combinations of 100% remote jobs (Gupy, Remotar, Workana, Catho) with specific state filters, and presencial cross-rejections | 10 | 10 | 0 | 100% |
| **Cat 5: 27 UFs Full Coverage & Cross-Rejection** | Acronym match, full state name match, and cross-state rejection for all 27 Brazilian states | 81 | 81 | 0 | 100% |
| **Cat 6: Settings Edge Cases** | Wildcard values (`Todos`, `todas`, `qualquer`, `all`, `""`) and extra whitespace padding | 6 | 6 | 0 | 100% |

---

## 4. Empirical Vulnerabilities Found (Failure Modes)

### Vulnerability 1: Preposition Collision for Pará (PA)
- **Description**: In Portuguese job descriptions, the preposition `"para"` (meaning "for" or "to") is extremely common (e.g. `"Vaga presencial para trabalhar no Rio de Janeiro RJ"`).
- **Failure Mode**: When searching with `location="pa"`, `UF_MAP["PA"]` includes `"para"`. `normalize_str` converts the text to `"vaga presencial para trabalhar no rio de janeiro rj"`. The word boundary regex or substring check matches `"para"`, causing non-Pará jobs in Rio de Janeiro or São Paulo to be **incorrectly accepted** when filtering for Pará (`PA`).
- **Reproducing Test Case**:
  ```python
  job_rj_preposition = make_job("Dev Python", "Vaga presencial para trabalhar no Rio de Janeiro RJ", "Rio de Janeiro - RJ")
  res_pa_bug = is_job_relevant(job_rj_preposition, "Dev Python", make_settings(location="pa"))
  # Result: True (Expected: False)
  ```
- **Blast Radius**: High false positive rate when filtering jobs for Pará (PA).
- **Suggested Defense**: Disambiguate `"para"` in `UF_MAP["PA"]` by requiring context (e.g. state context, capital "Belém", or checking if `"para"` is used as a preposition vs state name).

### Vulnerability 2: Substring Collision between MT (Mato Grosso) and MS (Mato Grosso do Sul)
- **Description**: The full name of Mato Grosso do Sul (`"Mato Grosso do Sul"`) contains the full name of Mato Grosso (`"Mato Grosso"`).
- **Failure Mode**: When searching for jobs in Mato Grosso (`location="mt"`), `UF_MAP["MT"]` checks if the job text contains `"mato grosso"`. A job physically located in Mato Grosso do Sul (e.g., `"Vaga presencial em Campo Grande no estado de Mato Grosso do Sul MS"`) contains `"mato grosso do sul"`, which satisfies `.includes("mato grosso")`.
- **Reproducing Test Case**:
  ```python
  job_ms_state = make_job("Dev Python", "Vaga presencial em Campo Grande no estado de Mato Grosso do Sul MS", "Campo Grande - MS")
  res_mt_bug = is_job_relevant(job_ms_state, "Dev Python", make_settings(location="mt"))
  # Result: True (Expected: False)
  ```
- **Blast Radius**: Jobs in MS (Mato Grosso do Sul) leak into MT (Mato Grosso) search results.
- **Suggested Defense**: When matching `"mato grosso"`, ensure negative lookahead/exclusion for `"mato grosso do sul"`, or order state name checks such that longer state names match first and prevent shorter state name collisions.

---

## 5. Verification Commands

To independently verify these results, execute:
```bash
# 1. Standard test suites
python test_location_uf.py
python test_location_state.py

# 2. Adversarial stress suite
python test_location_adversarial_challenger.py
```
