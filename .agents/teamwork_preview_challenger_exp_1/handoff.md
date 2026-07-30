# Handoff Report: Milestone 3 - Empirical Edge Case Adversarial Testing

## 1. Observation

- **Tested Target**: `is_job_relevant(job, keyword, settings)` function in `bot.py` (lines 949–1078).
- **Tested User Level**: `user_level = 'ganhar experiência'` (or `'Ganhar Experiência'`).
- **Harness Script**: Executed `stress_test.py` located at `C:\Users\99196\OneDrive\Documentos\vagas_bot\.agents\teamwork_preview_challenger_exp_1\stress_test.py`.
- **Empirical Execution Command**:
  `python C:\Users\99196\OneDrive\Documentos\vagas_bot\.agents\teamwork_preview_challenger_exp_1\stress_test.py`
- **Overall Result**: 11 out of 14 test cases passed (78.6% overall pass rate).

### Detailed Results by Test Category

| Category | Description / Scenarios | Total | Passed | Failed | Pass Rate |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **1. Mixed case / accents** | "PROJETO SOCIAL", "Código Aberto", "Sem Experiência" | 3 | 3 | 0 | 100.0% |
| **2. Boundary terms** | "voluntariado em ONG", "primeiro emprego de TI" | 2 | 2 | 0 | 100.0% |
| **3. Conflicting seniority** | "Voluntário Júnior", "Projeto Open Source Pleno", "Sênior Sem Experiência" | 3 | 3 | 0 | 100.0% |
| **4. Missing target terms** | "Desenvolvedor Python Remote", "Estágio em TI 2 anos exp" | 2 | 2 | 0 | 100.0% |
| **5. Adversarial / Flaws** | False positives ("involuntario", "congresso"), Regex collision ("PL/SQL"), Accented setting level | 4 | 1 | 3 | 25.0% |
| **Total** | | **14** | **11** | **3** | **78.6%** |

---

## 2. Logic Chain

1. **Normalization & Case Handling**:
   - `is_job_relevant` uses `normalize_str(s)` which applies `unicodedata.normalize('NFD', str(s))` and strips non-ASCII accents while converting to lowercase.
   - Hence, "PROJETO SOCIAL", "Código Aberto", and "Sem Experiência" correctly normalize to `"projeto social"`, `"codigo aberto"`, and `"sem experiencia"`.
   - Category 1 tests pass 100%.

2. **Boundary Terms**:
   - `target_exp_terms` list contains `"voluntariado"`, `"ong"`, and `"primeiro emprego"`.
   - "voluntariado em ONG" matches `"voluntariado"` and `"ong"`. "primeiro emprego de TI" matches `"primeiro emprego"`.
   - Category 2 tests pass 100%.

3. **Conflicting Seniority Handling**:
   - For `user_level == 'ganhar experiencia'`, `is_job_relevant` executes:
     `higher_terms = ["junior", "jr", "pleno", "pl", "senior", "sr"]`
     `if any(match_exact_word(full_text, w) for w in higher_terms): return False`
   - Jobs titled "Voluntário Júnior", "Projeto Open Source Pleno", or "Sênior Sem Experiência" match `junior`, `pleno`, or `senior` via `match_exact_word`.
   - They are correctly rejected (`False`). Category 3 tests pass 100%.

4. **Missing Target Terms**:
   - If a job contains no terms from `target_exp_terms`, `if not any(term in full_text for term in target_exp_terms): return False` triggers.
   - "Desenvolvedor Python Remote" and "Estágio em TI 2 anos exp" (where "estagio" alone is not in `target_exp_terms`, only "estagio inicial") are correctly rejected (`False`). Category 4 tests pass 100%.

5. **Discovered Failure Modes / Vulnerabilities (Category 5 Flaws)**:
   - **Flaw A (Raw Substring Check for Target Terms)**:
     - Line 1034 in `bot.py`: `if not any(term in full_text for term in target_exp_terms):`
     - Uses Python's `in` operator (substring search) instead of word boundary matching (`match_exact_word`).
     - *Empirical Failure 1*: A job mentioning "Desligamento involuntario" contains `"voluntario"` as a substring of `"involuntario"`. `is_job_relevant` returns `True` (False Positive).
     - *Empirical Failure 2*: A job mentioning "congresso de TI" contains `"ong"` as a substring of `"congresso"`. `is_job_relevant` returns `True` (False Positive).
   - **Flaw B (Regex Word Boundary Collision in Seniority Filter)**:
     - Line 615 in `bot.py`: `pattern = rf'(?<![a-z0-9]){re.escape(word)}(?![a-z0-9])'`
     - For `word = "pl"` in `higher_terms`, the pattern matches `pl` if it is preceded and followed by non-alphanumeric characters.
     - In `"PL/SQL"`, `/` is non-alphanumeric. Thus, `match_exact_word("... pl/sql", "pl")` evaluates to `True`.
     - *Empirical Failure 3*: A legitimate volunteer job mentioning "PL/SQL" (e.g., "Desenvolvedor Python Voluntário - Conhecimento em PL/SQL") is falsely classified as requiring "Pleno" seniority and is rejected (`False`) (False Negative).

---

## 3. Caveats

- **Scope Limit**: The stress test harness focused specifically on `user_level = 'ganhar experiência'` across 14 target scenarios. Other user levels (`junior`, `pleno`, `senior`) were not exhaustively stress tested in this harness run.
- **Co-occurrence interaction**: Tests were performed using `keyword = "Desenvolvedor Python"`. Different search keywords with custom co-occurrence rules (e.g. `especialista em ia`) may interact with the experience filter.

---

## 4. Conclusion

- **Core Requirements**: `is_job_relevant` satisfies basic requirements for `user_level = 'ganhar experiência'` across mixed case/accents, boundary terms, conflicting seniority, and missing target terms (100% pass rate across categories 1–4).
- **Adversarial Vulnerabilities**: 3 empirical bugs were isolated:
  1. Substring false positive on `voluntario` inside words like `involuntario`.
  2. Substring false positive on `ong` inside words like `congresso`, `longo`, `prolongado`.
  3. False rejection of `PL/SQL` jobs due to `pl` regex boundary matching on `/`.

---

## 5. Verification Method

To independently verify these results:

1. Execute the stress test harness script from terminal:
   ```cmd
   python C:\Users\99196\OneDrive\Documentos\vagas_bot\.agents\teamwork_preview_challenger_exp_1\stress_test.py
   ```
2. Verify console output:
   - Category 1 (Mixed case / accents): 3/3 Passed
   - Category 2 (Boundary terms): 2/2 Passed
   - Category 3 (Conflicting seniority): 3/3 Passed
   - Category 4 (Missing target terms): 2/2 Passed
   - Category 5 (Adversarial / Flaws): 3 Failures recorded (Tests #11, #12, #13)

---

## Adversarial Challenge Report

### Challenge Summary

**Overall risk assessment**: MEDIUM

### Challenges

#### [Medium] Challenge 1: Substring False Positives in `target_exp_terms`
- **Assumption challenged**: Assuming Python `in` operator (`term in full_text`) is sufficient to detect target experience terms.
- **Attack scenario**: Job title/description containing unrelated words with embedded subwords (e.g., "involuntario" contains "voluntario", "congresso"/"longo" contains "ong").
- **Blast radius**: Irrelevant corporate or event jobs are delivered to entry-level users seeking volunteer/experience opportunities.
- **Mitigation**: Replace `term in full_text` at line 1034 with `match_exact_word(full_text, term)`.

#### [Medium] Challenge 2: Regex Boundary Collision for "PL/SQL" in Seniority Rejection
- **Assumption challenged**: Assuming `(?<![a-z0-9])pl(?![a-z0-9])` only matches the seniority abbreviation "PL" (Pleno).
- **Attack scenario**: Job description mentioning technical skill "PL/SQL".
- **Blast radius**: Valid entry-level / volunteer jobs requiring database skills (PL/SQL) are falsely rejected.
- **Mitigation**: Update `higher_terms` check or `match_exact_word` to exclude `PL/SQL` / `PL-SQL` from matching standalone `PL`.

---

### Summary Table of Harness Results

```
================================================================================
EMPIRICAL STRESS TEST SUITE: is_job_relevant ('ganhar experiência')
================================================================================
[PASS] Test #1: PROJETO SOCIAL (Uppercase)
[PASS] Test #2: Código Aberto (Mixed case & accents)
[PASS] Test #3: Sem Experiência (Mixed case & accents)
[PASS] Test #4: voluntariado em ONG
[PASS] Test #5: primeiro emprego de TI
[PASS] Test #6: Voluntário Júnior
[PASS] Test #7: Projeto Open Source Pleno
[PASS] Test #8: Sênior Sem Experiência
[PASS] Test #9: Desenvolvedor Python Remote
[PASS] Test #10: Estágio em TI 2 anos exp
[FAIL] Test #11: False positive substring 'involuntario'
[FAIL] Test #12: False positive substring 'congresso' ('ong')
[FAIL] Test #13: PL/SQL in Voluntário job
[PASS] Test #14: Accented settings level: 'Ganhar Experiência'
================================================================================
TOTAL: 11/14 Passed (78.6%) | Failed: 3
================================================================================
```
