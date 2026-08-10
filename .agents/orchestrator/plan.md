# Master Plan — vagas_bot Refactoring & Quality Assurance

## Overview
This master plan outlines the project lifecycle following the Teamwork Project Pattern.

## Scope & Requirements
1. **R1: Diagnóstico e Correção de Inicialização (Launcher & Bat)**:
   Fix infinite restart loop in `launcher.py` when Telegram token is missing from `.env`, ensuring FastAPI web server starts cleanly on port 8000. Ensure `iniciar_tudo.bat`, `start_bot.bat`, and `start.bat` are verified.
2. **R2: Otimização de SEO & Schema.org (Prompt 1)**:
   Keep `/sitemap.xml` and `/api/job/{job_id}/schema.json` active and synchronized with Schema.org JobPosting markup in `static/index.html`.
3. **R3: Integridade de Categorias e Exclusão Estrita (Prompt 2)**:
   Ensure job search maintains 0% category leakage using strict `NOT LIKE` exclusions, matching total count strictly with SQLite database.
4. **R4: Resiliência do Frontend e Dashboard (Prompt 3)**:
   Ensure web dashboard at `http://localhost:8000/` loads without console JS errors, undefined variables, or request failures.
5. **R5: Módulo de Autocorreção e Diagnóstico de Erros (Prompt 4)**:
   Maintain `middleware/error_reporter.py` and `core/ai_self_healer.py` recording structured logs in `logs/` and patches in `patches/`.
6. **Git Branch & Delivery**:
   Ensure all changes are saved and committed/pushed on git branch `refactor/organizacao-e-limpeza`.

## Phased Workflow
1. **Phase 0 (Survey)**: Dispatch 3 parallel Explorer subagents to map codebase state, current launcher behaviors, endpoints, queries, frontend scripts, error middleware, and git branch status.
2. **Phase 1 (Decomposition & Test Infra)**: Aggregate survey results, construct `PROJECT.md` and `TEST_INFRA.md`, set up milestone dependencies and E2E test plan.
3. **Phase 2 (Milestone Execution)**: Sequentially / in parallel execute Milestones M1 through M5 using Explorer -> Worker -> Reviewer -> Challenger -> Auditor iteration cycles.
4. **Phase 3 (E2E Hardening & Victory Audit)**: Run full test suite, conduct Forensic Audit, and report completion to Sentinel.
