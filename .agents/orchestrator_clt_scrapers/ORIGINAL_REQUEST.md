# Original User Request

## 2026-07-17T17:29:52Z

You are the project orchestrator.
Your working directory is: C:/Users/99196/OneDrive/Documentos/vagas_bot/.agents/orchestrator_clt_scrapers
Your identity is: teamwork_preview_orchestrator

Please orchestrate the implementation of Python scrapers for CLT job vacancies on platforms like Gupy, Catho, InfoJobs, and Vagas.com.br.
Refer to the original user request recorded in C:/Users/99196/OneDrive/Documentos/vagas_bot/.agents/ORIGINAL_REQUEST.md.
Follow the requirements and acceptance criteria:
- Evaluate and select the most viable platforms among Gupy, Catho, InfoJobs, and Vagas.com.br.
- Implement the scrapers in the scrapers/ folder following the async def scrape(keyword, level="Todos", max_pages=...) format.
- Integrate them with bot.py and ensure we filter jobs using bot.is_job_relevant.
- Create a test script to verify they work and return the correct structures without errors.
- Ensure existing scrapers (Workana) are not broken.
