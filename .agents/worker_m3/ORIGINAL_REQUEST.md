## 2026-07-08T13:35:40Z
Create a script named `C:/Users/99196/OneDrive/Documentos/vagas_bot/verify_ai_creative_jobs.py`.
This script must import `is_job_relevant` from `bot.py`.
The script must define a settings dictionary with `level="Todos"`, `location="Todos"`, `contract="Todos"`.
Define 5 creative AI jobs that should be approved under the keyword 'Especialista em IA Generativa'.
Define 5 non-AI jobs that should be rejected under the keyword 'Especialista em IA Generativa'.
For each job, call `is_job_relevant(job, "Especialista em IA Generativa", settings)` and mathematically assert that it returns True for AI jobs and False for non-AI jobs.
Execute and print clean helpful logs showing 100% success.
Run the script using Python.
Write summary to handoff.md.
Send a message to parent.
