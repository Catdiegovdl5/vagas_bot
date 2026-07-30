# Handoff Report: Analysis of `is_job_relevant` & `user_level == 'iniciantes tudo'`

## 1. Observation
- **Target File**: `C:/Users/99196/OneDrive/Documentos/vagas_bot/bot.py`
- **Function Inspected**: `is_job_relevant(job, keyword, settings)` (lines 1094–1223).
- **String Normalization (lines 473-476, 1101)**:
  `user_level = normalize_str(settings.get('level', 'Todos'))`
  Where `normalize_str("Iniciantes Tudo")` yields `'iniciantes tudo'`, `"Jovem Aprendiz"` yields `'jovem aprendiz'`, and `"Ganhar Experiência"` yields `'ganhar experiencia'`.
- **Existing 'jovem aprendiz' criteria (lines 1155, 1171-1173)**:
  ```python
  aprendiz_terms = ['aprendiz', 'jovem aprendiz', 'menor aprendiz']
  ...
  elif user_level == 'jovem aprendiz':
      if not any(match_exact_word(full_text, w) for w in aprendiz_terms):
          return False
  ```
- **Existing 'ganhar experiência' criteria (lines 1174-1184)**:
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
- **Global Blacklist Exception (line 1214)**:
  ```python
  active_global_blacklist = [term for term in global_title_blacklist if term not in kw_norm and not (user_level == "ganhar experiencia" and term in ("voluntario", "voluntary"))]
  ```

## 2. Logic Chain
1. **From Observation on Normalization**: `user_level` string matching uses normalized lowercase strings. Thus, checking `user_level == 'iniciantes tudo'` matches the normalized setting `'Iniciantes Tudo'`.
2. **From Observation on 'jovem aprendiz'**: A job satisfies the `'jovem aprendiz'` criteria iff `any(match_exact_word(full_text, w) for w in aprendiz_terms)` is `True`.
3. **From Observation on 'ganhar experiência'**: A job satisfies the `'ganhar experiência'` criteria iff `any(term in full_text for term in target_exp_terms)` is `True` AND `not any(match_exact_word(full_text, w) for w in higher_terms)` is `True`.
4. **From Objective Requirement**: `user_level == 'iniciantes tudo'` must return `True` (pass the level filter) if EITHER the `'jovem aprendiz'` criteria OR the `'ganhar experiência'` criteria is met. Therefore, if `not (is_jovem_aprendiz or is_ganhar_experiencia)`, the function must return `False`.
5. **From Observation on Global Blacklist Exception**: Because `'ganhar experiência'` permits volunteer jobs (e.g. titles with `"voluntario"`), `active_global_blacklist` on line 1214 must be updated to check `user_level in ("ganhar experiencia", "iniciantes tudo")` so volunteer jobs under `'iniciantes tudo'` are not blocked by the global title blacklist.

## 3. Caveats
- The investigation was purely read-only per constraints; no modifications were made to `bot.py`.
- Level setting UI options in `change_level` (line 189) and NLP level extraction in `handle_free_text` (line 1572) should also be updated when implementing this feature in `bot.py` to allow users to select `"Iniciantes Tudo"`.

## 4. Conclusion
The exact Python logic for `user_level == 'iniciantes tudo'` is:
```python
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
And updating line 1214:
```python
    active_global_blacklist = [
        term for term in global_title_blacklist 
        if term not in kw_norm and not (user_level in ("ganhar experiencia", "iniciantes tudo") and term in ("voluntario", "voluntary"))
    ]
```
The full report has been saved to `C:/Users/99196/OneDrive/Documentos/vagas_bot/.agents/explorer_2/analysis.md`.

## 5. Verification Method
1. **File Inspection**:
   Inspect `C:/Users/99196/OneDrive/Documentos/vagas_bot/.agents/explorer_2/analysis.md` and `C:/Users/99196/OneDrive/Documentos/vagas_bot/bot.py`.
2. **Unit Test / Evaluation Case**:
   - Test `is_job_relevant` with `settings = {'level': 'Iniciantes Tudo'}` against:
     a) Job with title `"Jovem Aprendiz de TI"` $\rightarrow$ Should return `True`.
     b) Job with description `"Sem experiência necessária, projeto social"` $\rightarrow$ Should return `True`.
     c) Job with title `"Desenvolvedor Pleno Python"` $\rightarrow$ Should return `False`.
     d) Job with title `"Voluntario de Dados"` (without junior/pleno/senior terms) $\rightarrow$ Should return `True`.
