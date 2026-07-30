# Handoff Report — Code Review & Acceptance Verification (Milestone 3: "Ganhar Experiência")

## 1. Observation

### Code Review Findings:
- **`static/index.html` (Line 494)**:
  ```html
  <label style="display:flex; align-items:center; gap:5px;"><input type="radio" name="seniority" value="ganhar experiência"> Ganhar Experiência</label>
  ```
  The radio button correctly sends `"ganhar experiência"` when selected. In `startHunting()` JS function (Line 623), `const level = document.querySelector('input[name="seniority"]:checked').value;` sends this value to the backend endpoint `/api/trigger`.

- **`bot.py` (Lines 1028 - 1038)**:
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
  Normalized string comparison handles accents (`"ganhar experiência"` -> `"ganhar experiencia"`).

- **`bot.py` (Line 1068)**:
  ```python
      active_global_blacklist = [term for term in global_title_blacklist if term not in kw_norm and not (user_level == "ganhar experiencia" and term in ("voluntario", "voluntary"))]
  ```
  The global title blacklist contains `"voluntario"` and `"voluntary"`. When `user_level == "ganhar experiencia"`, those two terms are excluded from the active global title blacklist, allowing titles containing `"Voluntário"` or `"Voluntary"` to pass through for this user level while remaining blocked for other user levels.

- **`test_experience.py`**:
  Contains 10 test cases testing positive relevance matches, higher seniority blocking, lack of experience terms, title blacklist exemption, and combined conditions.

### Test Execution Command & Result:
Command: `python test_experience.py`
Output:
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

### Integrity & Anti-Cheating Inspection:
- No hardcoded test cases or shortcut return values exist inside `bot.py`.
- Implementation in `bot.py` uses dynamic pattern matching and normalization logic.
- Independent execution of `python test_experience.py` produced 10/10 PASS status with exit code 0.

---

## 2. Logic Chain

1. **Observation**: `static/index.html` line 494 defines `<input type="radio" name="seniority" value="ganhar experiência">`.
   **Reasoning**: Selecting this radio option provides `"ganhar experiência"` to the payload sent via `/api/trigger`.

2. **Observation**: `bot.py` line 955 normalizes `settings['level']` using `normalize_str`, turning `"ganhar experiência"` into `"ganhar experiencia"`.
   **Reasoning**: Case and accent normalization guarantees reliable string matching against `user_level == 'ganhar experiencia'`.

3. **Observation**: When `user_level == 'ganhar experiencia'`, `is_job_relevant` checks if any of `target_exp_terms` are present in `full_text`.
   **Reasoning**: Jobs without explicit entry-level/learning keywords ("voluntario", "sem experiencia", "open source", etc.) are correctly filtered out (e.g. Test 5c "Dev Python" returns `False`).

4. **Observation**: `is_job_relevant` checks if any of `higher_terms` (`"junior"`, `"jr"`, `"pleno"`, `"pl"`, `"senior"`, `"sr"`) match via `match_exact_word`.
   **Reasoning**: Jobs targeting higher experience levels are filtered out even if they mention a target term (e.g. Test 5d "Dev Voluntário Pleno" returns `False`).

5. **Observation**: `active_global_blacklist` excludes `"voluntario"` and `"voluntary"` ONLY when `user_level == "ganhar experiencia"`.
   **Reasoning**: Volunteer titles are permitted for users seeking experience, while remaining globally blacklisted for users on other experience settings.

6. **Observation**: Running `python test_experience.py` in the environment executes all 10 test scenarios and exits with code 0.
   **Reasoning**: All acceptance criteria for Milestone 3 are satisfied and verified by automated testing and code inspection.

---

## 3. Caveats

- **"PL/SQL" Edge Case**: `higher_terms` includes `"pl"`, which is also used across `bot.py` for matching "Pleno". Because `match_exact_word` uses non-alphanumeric boundaries (`(?<![a-z0-9])pl(?![a-z0-9])`), a job mentioning `PL/SQL` (with a forward slash) would match `"pl"` and be rejected. This is consistent with existing `bot.py` behavior for `pleno_terms = ['pleno', 'pl']`.
- **No further caveats**: Code changes are contained, well-tested, and introduce no regression to other seniority levels.

---

## 4. Conclusion

**Verdict**: **APPROVE**

All acceptance criteria for Milestone 3 (R1 and R2) are fully met:
- **R1**: Seniority option "Ganhar Experiência" correctly sends `"ganhar experiência"`.
- **R2**: `is_job_relevant` handles `user_level == "ganhar experiencia"`, validates target terms, blocks higher seniority levels, and exempts volunteer terms from the global title blacklist.
- **Verification**: `test_experience.py` passes 100% of test cases cleanly with exit code 0.

---

## 5. Verification Method

To independently verify this handoff:
1. Run the test script from the project root:
   ```cmd
   python test_experience.py
   ```
2. Verify terminal output shows `ALL EXPERIENCE LEVEL TEST CASES PASSED SUCCESSFULLY! Exit code 0.`
3. Inspect `static/index.html` line 494 and `bot.py` lines 1028-1038 & 1068.
