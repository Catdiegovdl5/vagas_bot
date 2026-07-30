# HANDOFF REPORT — Stress Test of `is_job_relevant` for `user_level = 'iniciantes tudo'`

## 1. Observation
- Target logic located in `bot.py:1185-1198`:
  ```python
  elif user_level in ('iniciantes stuff', 'iniciantes tudo'):
      is_aprendiz = any(match_exact_word(full_text, w) for w in aprendiz_terms)
      target_exp_terms = [
          "voluntario", "voluntariado", "ong", "projeto social",
          "open source", "codigo aberto",
          "sem experiencia", "nao exige experiencia", "primeiro emprego", "estagio inicial"
      ]
      has_target_exp = any(term in full_text for term in target_exp_terms)
      higher_terms = ["junior", "jr", "pleno", "pl", "senior", "sr"]
      has_higher_terms = any(match_exact_word(full_text, w) for w in higher_terms)
      is_ganhar_exp = has_target_exp and not has_higher_terms
      
      if not (is_aprendiz or is_ganhar_exp):
          return False
  ```
- Executed empirical test harness `.agents/challenger_1/stress_test_iniciantes.py` via command:
  `python .agents/challenger_1/stress_test_iniciantes.py`
- Output summary: Total 14 test cases | Passed 6 | Failed 8.
- Specific verbatim failures observed:
  1. `SUBSTR-01` (MongoDB): `"ong" in full_text` returned `True` for `"Desenvolvedor Backend Python - Requisitos: MongoDB, FastAPI"`, giving `has_target_exp = True` and passing regular dev jobs as beginner jobs.
  2. `CONF-01` ("Aprendiz Pleno"): `is_aprendiz` returned `True`, bypassing `has_higher_terms` check and passing "Aprendiz Pleno" as a valid beginner job.
  3. `BOUNDARY-01` ("PL/SQL"): `match_exact_word("pl/sql", "pl")` returned `True`, setting `has_higher_terms = True` and falsely rejecting legitimate volunteer PL/SQL jobs.
  4. `match_exact_word("voluntario em redes sr-iov", "sr")` returned `True`.

## 2. Logic Chain
1. *From Observation 1*: `has_target_exp` checks `term in full_text` for `"ong"` using substring inclusion.
2. *From Observation 3 & 4 (SUBSTR-01)*: Words like `"MongoDB"`, `"longo"`, and `"strong"` contain `"ong"`. Therefore, any non-beginner job mentioning MongoDB or long-term projects sets `has_target_exp = True`. When no senior terms exist, `is_ganhar_exp` becomes `True`, causing a severe False Positive leak.
3. *From Observation 1 & 4 (CONF-01)*: `is_aprendiz` does not check `not has_higher_terms`. A title combining "Aprendiz" and "Pleno" evaluates `(is_aprendiz or is_ganhar_exp)` to `(True or False)` -> `True`, causing a False Positive leak.
4. *From Observation 1 & 4 (BOUNDARY-01)*: `match_exact_word(text, "pl")` uses regex `(?<![a-z0-9])pl(?![a-z0-9])`. Non-alphanumeric characters like `/` in `"PL/SQL"` or `-` in `"SR-IOV"` trigger word boundaries, causing `"pl"` and `"sr"` to match technical acronyms. This sets `has_higher_terms = True` and incorrectly rejects valid volunteer/open-source jobs (False Negative block).

## 3. Caveats
- AI filter evaluation (`settings["ai_filter"] = True`) was disabled in this test suite to strictly isolate the deterministic boolean logic in `is_job_relevant`.
- Platform-specific description length rules (< 15 chars) were tested under standard length inputs (> 15 chars).

## 4. Conclusion
The current implementation of `is_job_relevant` for `user_level = 'iniciantes tudo'` suffers from **CRITICAL flaws**:
1. Substring collision on `"ong"` leaking MongoDB/long-term jobs to beginners.
2. Unchecked seniority bypass in `is_aprendiz` accepting "Aprendiz Pleno".
3. Regex word boundary false rejections blocking legitimate "PL/SQL" and "SR-IOV" volunteer/open-source jobs.

## 5. Verification Method
1. Inspect findings in `.agents/challenger_1/challenge_report.md`.
2. Run test harness:
   `python .agents/challenger_1/stress_test_iniciantes.py`
3. Verification passes when all 14 test cases pass after implementing the suggested mitigations in `bot.py`.
