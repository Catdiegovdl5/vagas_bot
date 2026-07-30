# Adversarial Challenge Report — Seniority Level Regression & Isolation Testing

**Author**: challenger_2  
**Date**: 2026-07-21  
**Target File**: `bot.py`  

---

## Challenge Summary

**Overall risk assessment**: **LOW** (Zero Functional Regression / Codebase Implementation Robust)

Empirical stress testing across 600+ synthetic job vectors and multiple existing test suites confirms that:
1. `'iniciantes tudo'` (and its alias `'iniciantes stuff'`) functions as a strict logical union of `'jovem aprendiz'` and `'ganhar experiência'`.
2. Existing seniority levels (`'júnior'`, `'pleno'`, `'sênior'`, `'jovem aprendiz'`, `'ganhar experiência'`, `'todos'`) behave **identically** to before, with zero cross-contamination or isolation violations.
3. Full string normalization (`normalize_str`) ensures accent-insensitive and case-insensitive matching across all level definitions (e.g. `'Júnior'` vs `'junior'`, `'Sênior'` vs `'senior'`, `'Ganhar Experiência'` vs `'ganhar experiencia'`, `'Iniciantes Tudo'` vs `'iniciantes tudo'`).

---

## Challenges

### [Low Risk] Challenge 1: Minimum Description Length Requirement in Test Harnesses vs Production
- **Assumption challenged**: A job with a short description (e.g. `< 15` characters like `"Nivel pleno."`) will pass level filtering if the title is generic.
- **Attack scenario**: `test_seniority_filter.py` passed `job3` with `requirements = "Nivel pleno."` (12 characters) under platform `"GeekHunter"`. The test expected `True`, but `is_job_relevant` returned `False`.
- **Root Cause & Finding**: Line 1120 of `bot.py` enforces a minimum quality threshold:
  ```python
  if not is_freelance_platform and len(reqs_norm) < 15 and job_platform not in ['linkedin', 'indeed']:
      return False
  ```
  The rejection was caused by the global 15-character quality filter, NOT by seniority filtering logic. When `requirements` length is `>= 15` chars (e.g. `"Nivel pleno para atuação em dados."`), the job returns `True` as expected.
- **Mitigation**: Update test datasets in unit tests to provide realistic descriptions of `>= 15` characters or use supported platform tags (`linkedin`, `indeed`).

### [Info] Challenge 2: Global Title Blacklist Exemption Scoping for Beginner Levels
- **Assumption challenged**: Global title blacklist terms (such as `"voluntario"`) might cause discrepancies between `'jovem aprendiz'` and `'iniciantes tudo'`.
- **Attack scenario**: Test job with title `"Voluntário Jovem Aprendiz de TI"`.
- **Behavior observed**:
  - `user_level == "jovem aprendiz"`: Blacklist check rejects `"voluntario"`.
  - `user_level == "iniciantes stuff"` / `"iniciantes tudo"`: `"voluntario"` is exempted from the title blacklist (line 1228), allowing volunteer beginner roles to pass.
- **Assessment**: Intended design. `'ganhar experiência'` and `'iniciantes tudo'` explicitly exempt `"voluntario"` / `"voluntary"` from the global title blacklist so volunteer roles for experience-building are preserved.

---

## Stress Test Results

| Test Battery / Scenario | Total Cases | Expected Behavior | Actual Behavior | Result |
| :--- | :---: | :--- | :--- | :---: |
| **Union Identity Battery** (`iniciantes tudo` == `aprendiz` OR `ganhar_exp`) | 600 | `iniciantes tudo` accepts if and only if job matches `aprendiz` OR `ganhar_exp` | 600/600 exact matches (100.0%) | **PASS** |
| **Junior Isolation** | 100 | Rejects Pleno/Senior jobs; accepts Junior jobs | 100% rejected Pleno/Senior; accepted Junior | **PASS** |
| **Pleno Isolation** | 100 | Rejects Junior/Senior jobs; accepts Pleno jobs | 100% rejected Junior/Senior; accepted Pleno | **PASS** |
| **Senior Isolation** | 100 | Rejects Junior/Pleno jobs; accepts Senior jobs | 100% rejected Junior/Pleno; accepted Senior | **PASS** |
| **Jovem Aprendiz Isolation** | 100 | Requires `aprendiz` / `menor aprendiz` terms | 100% strictly enforced | **PASS** |
| **Ganhar Experiência Isolation** | 100 | Requires target exp terms; rejects higher level terms (`jr`/`pl`/`sr`) | 100% strictly enforced | **PASS** |
| **Alias & Accent Normalization** | 24 | Case and accent variants (`júnior`/`junior`, `iniciantes tudo`/`Iniciantes Tudo`) evaluate identically | 100% identical outputs | **PASS** |
| **Existing Test Suite (`test_iniciantes.py`)** | 3 | All assertions pass | 3/3 PASS | **PASS** |
| **Existing Test Suite (`test_experience.py`)** | 10 | All assertions pass | 10/10 PASS | **PASS** |

---

## Unchallenged Areas

- **Live Telegram Network Handlers**: Telegram API callback sending was mocked during unit testing and not challenged against live Telegram servers.
- **External Web Scraper Network Live Responses**: Scrapers were evaluated via unit test payloads and mocks rather than live network requests to avoid IP bans during automated test runs.
