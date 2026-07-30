# Handoff Report: `is_job_relevant` & `test_iniciantes.py` Design

## 1. Observation
- **Inspected Files**:
  - `C:/Users/99196/OneDrive/Documentos/vagas_bot/bot.py`:
    - Lines 478-493: `global_title_blacklist` includes `"voluntario"`, `"voluntary"`.
    - Lines 1152-1155: Terms definitions: `aprendiz_terms = ['aprendiz', 'jovem aprendiz', 'menor aprendiz']`, `higher_terms = ["junior", "jr", "pleno", "pl", "senior", "sr"]`.
    - Lines 1171-1184:
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
      ```
    - Lines 1213-1216:
      ```python
      active_global_blacklist = [term for term in global_title_blacklist if term not in kw_norm and not (user_level == "ganhar experiencia" and term in ("voluntario", "voluntary"))]
      if any(match_exact_word(title_norm, term) for term in active_global_blacklist):
          return False
      ```
  - `C:/Users/99196/OneDrive/Documentos/vagas_bot/test_experience.py`: Evaluates `"Ganhar Experiência"` level cases and prints PASS/FAIL status.
  - `C:/Users/99196/OneDrive/Documentos/vagas_bot/test_motor.py`: Evaluates keyword co-occurrence rules and false positive blocking.
  - `C:/Users/99196/OneDrive/Documentos/vagas_bot/test_keywords.py`: Evaluates keyword normalization, blacklist matching, and level/contract boundaries.
  - `C:/Users/99196/OneDrive/Documentos/vagas_bot/run_tests.py`: Runs pytest runner targeting `tests/`.

## 2. Logic Chain
1. **Observation**: `bot.py` line 1175 defines `target_exp_terms` containing `"voluntario"`, and line 1214 explicitly exempts `"voluntario"` from `active_global_blacklist` when `user_level == "ganhar experiencia"`.
   - **Reasoning**: A job titled `"Dev Voluntário"` with `level = "Ganhar Experiência"` satisfies `target_exp_terms`, bypasses the title blacklist, and contains no `higher_terms`.
   - **Step Result**: Returns `True` (Criteria 1 validated).

2. **Observation**: `bot.py` line 1171 checks `user_level == 'jovem aprendiz'` requiring `full_text` to match `aprendiz_terms` (`'aprendiz'`, `'jovem aprendiz'`, `'menor aprendiz'`).
   - **Reasoning**: A job titled `"Jovem Aprendiz de TI"` contains `"jovem aprendiz"`, matching `aprendiz_terms`, and is not blocked by blacklists.
   - **Step Result**: Returns `True` (Criteria 2 validated).

3. **Observation**: `bot.py` line 1183 blocks any job under `user_level == 'ganhar experiencia'` if `full_text` contains any word in `higher_terms = ["junior", "jr", "pleno", "pl", "senior", "sr"]`.
   - **Reasoning**: A job titled `"Dev Júnior 1 ano de experiência"` contains `"júnior"` (normalized: `"junior"`), triggering line 1183.
   - **Step Result**: Returns `False` (Criteria 3 validated).

4. **Observation**: `test_experience.py`, `test_motor.py`, and `test_keywords.py` implement standalone CLI execution while `tests/test_*.py` use Pytest.
   - **Reasoning**: `test_iniciantes.py` should combine both Pytest test functions and a `run_cli()` entrypoint so it runs cleanly under both `python test_iniciantes.py` and `pytest`.

## 3. Caveats
- Read-only investigation constraint: Source code under `vagas_bot/` (outside `.agents/explorer_3/`) was not modified. The source code for `test_iniciantes.py` is fully designed and documented in `analysis.md` and `handoff.md`.
- `CO_OCCURRENCE_RULES` in `bot.py` requires keywords like `"Dev"` or `"TI"` to match target group words (e.g. `"desenvolvedor"`, `"dev"`, `"software"`, `"ti"`). The test payloads in `test_iniciantes.py` include requirements text that satisfies these co-occurrence rules.

## 4. Conclusion
The implementation of `is_job_relevant` in `bot.py` already supports the three acceptance criteria for beginner profile filtering. The design for `test_iniciantes.py` has been fully formulated and provided in `analysis.md`.

## 5. Verification Method
1. Inspect detailed analysis and code design in: `C:/Users/99196/OneDrive/Documentos/vagas_bot/.agents/explorer_3/analysis.md`
2. Verify logic against `bot.py` lines 1171–1184 & 1213–1216 using `view_file`.
3. To test `test_iniciantes.py` when written by an implementer:
   - Run `python test_iniciantes.py` (standalone CLI mode)
   - Run `pytest test_iniciantes.py` (Pytest mode)
