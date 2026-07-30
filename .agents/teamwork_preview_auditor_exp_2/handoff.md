# Forensic Audit Handoff Report — Milestone 4 (Post-remediation Forensic Integrity Audit)

**Auditor**: Forensic Auditor 2 (`teamwork_preview_auditor_exp_2`)  
**Target Files**: `bot.py`, `static/index.html`, `test_experience.py` in `C:\Users\99196\OneDrive\Documentos\vagas_bot\`  
**Profile**: General Project (Forensic Integrity Audit)  
**Final Verdict**: **CLEAN**

---

## 1. Observation

### File 1: `bot.py`
- **Location**: `C:\Users\99196\OneDrive\Documentos\vagas_bot\bot.py`
- **Lines 184-192**: `change_level` callback handler contains `"Ganhar Experiência"` within `levels = ["Todos", "Júnior", "Pleno", "Sênior", "Jovem Aprendiz", "Ganhar Experiência"]`.
- **Lines 1174-1184**: `user_level == 'ganhar experiencia'` logic in `is_job_relevant`:
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
- **Line 1214**: Blacklist exemption rule for `"ganhar experiencia"`:
  ```python
  active_global_blacklist = [term for term in global_title_blacklist if term not in kw_norm and not (user_level == "ganhar experiencia" and term in ("voluntario", "voluntary"))]
  ```
- **Analysis**: Pure algorithm based on string normalization, word boundary matching (`match_exact_word`), allowed target terms, and higher-seniority rejection terms. No hardcoded title returns or facade shortcuts.

### File 2: `static/index.html`
- **Location**: `C:\Users\99196\OneDrive\Documentos\vagas_bot\static\index.html`
- **Line 494**: Radio option element:
  ```html
  <label style="display:flex; align-items:center; gap:5px;"><input type="radio" name="seniority" value="ganhar experiência"> Ganhar Experiência</label>
  ```
- **Lines 623-643**: Read dynamically via `const level = document.querySelector('input[name="seniority"]:checked').value;` and transmitted via JSON payload to `/api/trigger`.
- **Analysis**: Dynamic UI element integrated into frontend form submission.

### File 3: `test_experience.py`
- **Location**: `C:\Users\99196\OneDrive\Documentos\vagas_bot\test_experience.py`
- **Line 14**: `from bot import is_job_relevant`
- **Lines 26-98**: 10 comprehensive test cases covering positive (NGO volunteer, initial internship without experience required, open source beginner project, voluntary English project, no experience required) and negative cases (junior, pleno, senior, dev python without experience terms, voluntary pleno).
- **Line 112**: `result = is_job_relevant(job, keyword, test_settings)`
- **Lines 113-129**: Direct equality assertion (`result == expected`), reporting pass/fail per case and exiting with code 0 on full success or 1 on failure.
- **Analysis**: Test suite directly invokes `is_job_relevant` and performs authentic assertions without mocking or pre-cooked outputs.

---

## 2. Logic Chain

1. **Hardcoded output check**: Searched `bot.py` and `test_experience.py` for fixed outputs or string matching tailored specifically to bypass tests. None found. `is_job_relevant` evaluates dynamic inputs through generic rule evaluation.
2. **Facade check**: Inspected logic implementation in `bot.py`. `is_job_relevant` checks keyword normalization, target experience terms (`target_exp_terms`), higher seniority disqualification (`higher_terms`), and title blacklist exemptions (`active_global_blacklist`).
3. **Behavioral execution check**: Ran `python test_experience.py`. All 10 test cases executed dynamically and returned `PASS`, exiting with code 0.
4. **Empirical verification with unannounced inputs**: Executed custom test cases (`Dev React Projeto Social`, `Dev PHP Sênior`, `Dev Python`, `Voluntário Dev`) against `is_job_relevant`. Outputs matched expected theoretical behavior (True, False, False, True respectively), confirming dynamic execution.
5. **UI & Telegram Integration**: Confirmed `"ganhar experiência"` is implemented in both Telegram inline keyboard settings (`bot.py`) and Web App options (`static/index.html`).

---

## 3. Caveats

- `pytest test_experience.py` using standard pytest collection looks for functions prefixed with `test_`. Because `test_experience.py` uses a standard script entry point (`def main():` and `if __name__ == '__main__': main()`), it must be executed via `python test_experience.py` (or wrapped in a `test_*` function if pytest autodiscovery is desired). Execution via `python test_experience.py` returned exit code 0.
- No other caveats.

---

## 4. Conclusion

**Verdict**: **CLEAN**

The work products (`bot.py`, `static/index.html`, `test_experience.py`) demonstrate authentic logic implementation without hardcoded outputs, fake checks, or facade code. `test_experience.py` directly invokes `is_job_relevant` and asserts genuine outputs across all test cases.

---

## 5. Verification Method

To independently verify this verdict, run the following commands in PowerShell from `C:\Users\99196\OneDrive\Documentos\vagas_bot`:

```powershell
# 1. Execute experience level test suite
python test_experience.py

# 2. Empirical Python execution of custom test cases
python -c "from bot import is_job_relevant; settings={'level': 'ganhar experiência', 'location': 'Brasil (Remoto)', 'contract': 'Todos'}; print('Custom Case 1 (Voluntario ONG):', is_job_relevant({'title': 'Dev React Projeto Social', 'requirements': 'Desenvolvimento de software voluntario ONG', 'platform': 'linkedin'}, 'Dev', settings)); print('Custom Case 2 (Senior Block):', is_job_relevant({'title': 'Dev PHP Sênior', 'requirements': 'Open source projeto social sem experiencia previa', 'platform': 'linkedin'}, 'Dev', settings))"
```
