## 2026-07-21T12:03:39Z
You are the Implementer for Milestone 2: Ganhar Experiência Seniority Filter in Sniper Bot (bot.py, static/index.html, and test_experience.py).
Your working directory is: C:\Users\99196\OneDrive\Documentos\vagas_bot\.agents\teamwork_preview_worker_exp_1

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A Forensic Auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Tasks to implement:

1. UI Implementation (static/index.html):
- Open C:\Users\99196\OneDrive\Documentos\vagas_bot\static\index.html.
- Locate the Seniority Level radio buttons section (around line 487-495, inside <div style="display:flex; gap:10px; flex-wrap: wrap;">).
- Add "Ganhar Experiência" as a radio button alongside existing options (Júnior, Pleno, Sênior, Jovem Aprendiz, Todos):
  <label style="display:flex; align-items:center; gap:5px;"><input type="radio" name="seniority" value="ganhar experiência"> Ganhar Experiência</label>
- Ensure that selecting it submits value="ganhar experiência" in the level field during filtering.

2. Filter Logic Implementation (bot.py):
- Open C:\Users\99196\OneDrive\Documentos\vagas_bot\bot.py.
- Update change_level (around line 189) if levels list is present to include "Ganhar Experiência", e.g. levels = ["Todos", "Júnior", "Pleno", "Sênior", "Jovem Aprendiz", "Ganhar Experiência"] (check exact existing list).
- In is_job_relevant(job, keyword, settings) (around line 949 onwards):
  - Handle user_level == "ganhar experiencia" (note normalize_str(settings.get('level', 'Todos')) strips accents and lowercases to "ganhar experiencia").
  - When user_level == "ganhar experiencia":
    - REQUIRE that full_text (normalized title + requirements) contains AT LEAST ONE of the target terms:
      - "voluntario", "voluntariado", "ong", "projeto social"
      - "open source", "codigo aberto"
      - "sem experiencia", "nao exige experiencia", "primeiro emprego", "estagio inicial"
    - If NONE of these target terms are present in full_text, return False!
    - BLOCK jobs that contain higher seniority terms in title or requirements: "junior", "jr", "pleno", "pl", "senior", "sr".
  - Global Title Blacklist Exemption:
    - In is_job_relevant where active_global_blacklist is built from global_title_blacklist:
      global_title_blacklist contains "voluntario" and "voluntary".
      When user_level == "ganhar experiencia", exempt "voluntario" and "voluntary" from active_global_blacklist (e.g. active_global_blacklist = [term for term in global_title_blacklist if term not in kw_norm and not (user_level == "ganhar experiencia" and term in ("voluntario", "voluntary"))]).

3. Create Test Script (test_experience.py):
- Create C:\Users\99196\OneDrive\Documentos\vagas_bot\test_experience.py.
- Import is_job_relevant from bot.
- Define programmatic test cases for user_level = 'ganhar experiência':
  1. Vaga "Dev Voluntário em ONG" -> True
  2. Vaga "Estágio Inicial Sem Experiência" -> True
  3. Vaga "Dev Júnior 1 ano de experiência" -> False
  4. Vaga "Projeto Open Source para Iniciantes" -> True
  5. Additional boundary test cases (e.g. "Dev Pleno", "Dev Sênior", "Dev Python" with no exp terms).
- Assert all conditions. Print clear test pass/fail results. Exit with code 0 on success.

4. Run Verification Commands:
- Run python test_experience.py to verify all experience level test cases pass.
- Run existing test suites (e.g. python test_motor.py, python test_keywords.py, or pytest) to verify NO REGRESSIONS were introduced.
- Document exact execution commands and outputs in your handoff report.

Write your handoff report to: C:\Users\99196\OneDrive\Documentos\vagas_bot\.agents\teamwork_preview_worker_exp_1\handoff.md.
