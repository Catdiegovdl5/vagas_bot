## 2026-07-21T12:41:52Z
You are worker_1. Your working directory is C:/Users/99196/OneDrive/Documentos/vagas_bot/.agents/worker_1.

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A Forensic Auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Your task is to implement the unified filter 'Iniciantes Tudo' in Sniper Bot:

1. Update UI (`static/index.html`):
   - Locate the radio button container for seniority levels in screen-settings (around line 488).
   - Add the new radio option:
     `<label style="display:flex; align-items:center; gap:5px;"><input type="radio" name="seniority" value="iniciantes tudo"> Iniciantes Tudo (Jovem Aprendiz + Ganhar Experiência)</label>`

2. Update Backend (`bot.py`):
   - In `is_job_relevant(job, settings)`:
     Add support for `user_level == 'iniciantes stuff'` / `'iniciantes tudo'` (normalized):
     A job is relevant if it matches EITHER 'jovem aprendiz' criteria OR 'ganhar experiência' criteria.
     Reuse/combine existing filter logic.
   - Also update active_global_blacklist logic (around line 1214) to allow 'voluntario'/'voluntary' when `user_level in ("ganhar experiencia", "iniciantes tudo")`.

3. Create programmatic test (`test_iniciantes.py`):
   - Test `is_job_relevant` directly with `user_level = 'iniciantes tudo'`.
   - Validate:
     * Vaga "Dev Voluntário" (critério Ganhar Experiência) -> True
     * Vaga "Jovem Aprendiz de TI" (critério Aprendiz) -> True
     * Vaga "Dev Júnior 1 ano de experiência" -> False

4. Run all test suites:
   - Run python/pytest on `test_iniciantes.py`, `test_experience.py`, `test_motor.py`, `test_keywords.py`, and `run_tests.py` (or whatever test runner scripts exist).
   - Verify that 100% of tests pass.

5. Deliver report:
   - Document changes and test execution results in C:/Users/99196/OneDrive/Documentos/vagas_bot/.agents/worker_1/changes.md and handoff.md.
   - Send handoff message to parent with build/test results.
