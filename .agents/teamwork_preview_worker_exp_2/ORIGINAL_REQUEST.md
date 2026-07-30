## 2026-07-21T12:17:50Z
You are Worker 2 for Milestone 2 Remediation in Sniper Bot (bot.py).
Your working directory is: C:\Users\99196\OneDrive\Documentos\vagas_bot\.agents\teamwork_preview_worker_exp_2

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A Forensic Auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Task:
Apply the remediation fix to C:\Users\99196\OneDrive\Documentos\vagas_bot\bot.py based on Explorer 4's root-cause analysis:

1. Promote search_mapping to module-level SEARCH_MAPPING in bot.py:
   - Include mapping "Backend Python": "Python Backend"
   - Include mapping "Estagiário de TI / Programação": "desenvolvedor junior / estagiario"
   - Include mapping "Desenvolvedor Júnior / Estagiário": "desenvolvedor junior / estagiario"
2. Update CO_OCCURRENCE_RULES and blacklist dictionaries in bot.py:
   - Add entry for "python backend" in CO_OCCURRENCE_RULES and blacklist.
   - Add entry for "desenvolvedor junior / estagiario" in CO_OCCURRENCE_RULES and blacklist.
3. In is_job_relevant(job, keyword, settings):
   - Use clean_kw = SEARCH_MAPPING.get(keyword, keyword) at the start of is_job_relevant.
   - Ensure user_level == "ganhar experiencia" logic remains 100% active and correct:
     - Require at least one target term ("voluntario", "voluntariado", "ong", "projeto social", "open source", "codigo aberto", "sem experiencia", "nao exige experiencia", "primeiro emprego", "estagio inicial").
     - Block higher terms ("junior", "jr", "pleno", "pl", "senior", "sr").
     - Exempt "voluntario" and "voluntary" from active_global_blacklist.
4. Fix the short-description fallback in check_co_occurrence (around lines 887-899 of bot.py):
   - Replace the loop that flattens groups and returns True for any single word.
   - Instead, verify that EVERY group in groups has at least one term matching in title_norm.

5. Run Verification Commands:
   - Run python test_experience.py
   - Run python test_motor.py
   - Run python test_keywords.py
   - Run python run_tests.py (or pytest)
   All test suites MUST pass 100% with exit code 0!

Write your handoff report to C:\Users\99196\OneDrive\Documentos\vagas_bot\.agents\teamwork_preview_worker_exp_2\handoff.md.
