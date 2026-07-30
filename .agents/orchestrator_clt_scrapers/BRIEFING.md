# BRIEFING — 2026-07-17T17:29:52Z

## Mission
Orchestrate the implementation of Python scrapers for CLT job vacancies on platforms like Gupy, Catho, InfoJobs, and Vagas.com.br, and integrate them with the bot.

## 🔒 My Identity
- Archetype: teamwork_preview_orchestrator
- Roles: orchestrator, user_liaison, human_reporter, successor
- Working directory: C:/Users/99196/OneDrive/Documentos/vagas_bot/.agents/orchestrator_clt_scrapers
- Original parent: parent
- Original parent conversation ID: 9bd37d9f-c4fa-4209-9345-4cb66709f84f

## 🔒 My Workflow
- **Pattern**: Project / Canonical
- **Scope document**: C:/Users/99196/OneDrive/Documentos/vagas_bot/.agents/orchestrator_clt_scrapers/SCOPE.md
1. **Decompose**: Decompose the implementation into evaluation/selection, scraper implementation, bot integration, and verification steps.
2. **Dispatch & Execute** (pick ONE):
   - **Direct (iteration loop)**: Explorer -> Worker -> Reviewer -> Challenger -> Auditor
   - **Delegate (sub-orchestrator)**: None
3. **On failure** (in this order):
   - Retry: nudge stuck agent or re-send task
   - Replace: spawn fresh agent with partial progress
   - Skip: proceed without (only if non-critical)
   - Redistribute: split stuck agent's remaining work
   - Redesign: re-partition decomposition
   - Escalate: report to parent (sub-orchestrators only, last resort)
4. **Succession**: At 16 spawns, write handoff.md, spawn successor
- **Work items**:
  1. Evaluate and select viable platforms [pending]
  2. Implement CLT scrapers [pending]
  3. Integrate scrapers in bot.py [pending]
  4. Create and run verification test script [pending]
- **Current phase**: 1
- **Current focus**: Decompose and Plan

## 🔒 Key Constraints
- Evaluate and select the most viable platforms among Gupy, Catho, InfoJobs, and Vagas.com.br.
- Implement scrapers in scrapers/ folder with `async def scrape(keyword, level="Todos", max_pages=...)` format.
- Integrate with bot.py, using bot.is_job_relevant to filter.
- Create verification test script.
- Ensure existing scrapers (Workana) are not broken.
- Never reuse a subagent after it has delivered its handoff — always spawn fresh.

## Current Parent
- Conversation ID: 9bd37d9f-c4fa-4209-9345-4cb66709f84f
- Updated: 2026-07-17T17:29:52Z

## Key Decisions Made
- Selected Gupy, Catho, Vagas.com.br, and InfoJobs as CLT platforms.
- Standardized all CLT scraper signatures to `async def scrape(keyword, level="Todos", max_pages=1, **kwargs)`.
- Implemented Gupy, Catho, Vagas.com scrapers using curl_cffi AsyncSession.
- Implemented InfoJobs scraper using playwright.async_api with Semaphore(3) detail queries to prevent blocking.
- Implemented SyncWrapper helper to guarantee backwards-compatibility with synchronous test imports.
- Created `test_clt_scrapers_live.py` for live endpoint validation.
- Fixed global asyncio.sleep monkeypatch in test suite to prevent event-loop lock hangs.

## Team Roster
| Agent | Type | Work Item | Status | Conv ID |
|-------|------|-----------|--------|---------|
| 6e91878d-e494-4ab5-bb14-3ebd1183f0a5 | teamwork_preview_explorer | Code review & CLT platform evaluation | completed | 6e91878d-e494-4ab5-bb14-3ebd1183f0a5 |
| b3c3d557-0bcb-44c1-a15b-038d0cc94583 | teamwork_preview_worker | Refactor CLT scrapers to async | completed | b3c3d557-0bcb-44c1-a15b-038d0cc94583 |
| efecb6d1-e0a2-4c29-b2b7-ccecca53fc1d | teamwork_preview_worker | Create and run live verification tests | completed | efecb6d1-e0a2-4c29-b2b7-ccecca53fc1d |
| 4b8b068c-e129-442c-86b3-66acd5680f6e | teamwork_preview_auditor | Forensic integrity audit | completed | 4b8b068c-e129-442c-86b3-66acd5680f6e |

## Succession Status
- Succession required: no
- Spawn count: 4 / 16
- Pending subagents: none
- Predecessor: none
- Successor: not yet spawned

## Active Timers
- Heartbeat cron: task-19
- Safety timer: none
- On succession: kill all timers before spawning successor
- On context truncation: run manage_task(Action="list") — re-create if missing

## Artifact Index
- C:/Users/99196/OneDrive/Documentos/vagas_bot/.agents/orchestrator_clt_scrapers/SCOPE.md — Milestone scope and interface contracts
- C:/Users/99196/OneDrive/Documentos/vagas_bot/.agents/orchestrator_clt_scrapers/progress.md — Execution progress heartbeat
