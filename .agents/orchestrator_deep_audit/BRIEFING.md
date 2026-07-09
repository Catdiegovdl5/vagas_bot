# BRIEFING — 2026-07-07T23:25:25Z

## Mission
Perform Deep Audit and Bug Fixing on the vagas_bot project to achieve 100% stability, addressing all bugs in the audit report.

## 🔒 My Identity
- Archetype: teamwork_preview_orchestrator
- Roles: orchestrator, user_liaison, human_reporter, successor
- Working directory: C:\Users\99196\OneDrive\Documentos\vagas_bot\.agents\orchestrator_deep_audit
- Original parent: parent
- Original parent conversation ID: 1003085d-58dd-4e3f-bc1b-208b56a955f6

## 🔒 My Workflow
- **Pattern**: Project
- **Scope document**: C:\Users\99196\OneDrive\Documentos\vagas_bot\PROJECT.md
1. **Decompose**: Decompose the bug fixes and deep audit into manageable implementation steps or milestones.
2. **Dispatch & Execute** (pick ONE):
   - **Direct (iteration loop)**: Iterate via Explorer, Worker, Reviewer, Challenger, and Auditor.
3. **On failure** (in this order):
   - Retry: nudge stuck agent or re-send task
   - Replace: spawn fresh agent with partial progress
   - Skip: proceed without (only if non-critical)
   - Redistribute: split stuck agent's remaining work
   - Redesign: re-partition decomposition
   - Escalate: report to parent (sub-orchestrators only, last resort)
4. **Succession**: Self-succeed when cumulative sub-agent spawn count >= 16.
- **Work items**:
  1. Fix core system bugs (bot.py, app.py, database.py, auto_apply.py) [done]
  2. Fix scrapers and filter bugs (scrapers/*) [done]
  3. Verify code passes all tests and is stable [done]
- **Current phase**: 4
- **Current focus**: Handoff and completion

## 🔒 Key Constraints
- NEVER write, modify, or create source code files directly.
- NEVER run build/test commands yourself — require workers to do so.
- Audit verdict is a binary veto.
- Do not reuse a subagent after it has delivered its handoff — always spawn fresh.

## Current Parent
- Conversation ID: 1003085d-58dd-4e3f-bc1b-208b56a955f6
- Updated: not yet

## Key Decisions Made
- Initialized deep audit and planning phase.

## Team Roster
| Agent | Type | Work Item | Status | Conv ID |
|---|---|---|---|---|
| explorer_deep_audit_1 | teamwork_preview_explorer | Verify codebase issues and run tests baseline | completed | b921f077-9867-4135-8087-4dca9152332c |
| worker_deep_audit_1 | teamwork_preview_worker | Implement fixes and run verification tests | completed | f9ccd73c-b4ec-44bc-8675-4c6eaaf7dd88 |
| auditor_deep_audit_1 | teamwork_preview_auditor | Perform forensic integrity audit and run verification tests | completed | ab515b04-a165-4f2b-9bc7-4b779f378dc4 |

## Succession Status
- Succession required: no
- Spawn count: 3 / 16
- Pending subagents: none
- Predecessor: none
- Successor: not yet spawned

## Active Timers
- Heartbeat cron: none
- Safety timer: none
- On succession: kill all timers before spawning successor
- On context truncation: run manage_task(Action="list") — re-create if missing

## Artifact Index
- C:\Users\99196\OneDrive\Documentos\vagas_bot\.agents\orchestrator_deep_audit\progress.md — progress tracker
- C:\Users\99196\OneDrive\Documentos\vagas_bot\.agents\orchestrator_deep_audit\BRIEFING.md — persistent briefing state
