# Plan - vagas_bot Precision Phase

## Objective
Refactor and fix the Telegram Job Search Bot to eliminate runtime errors and implement a high-precision job search engine with title allowlists and blocklists.

## Execution Strategy
We will execute this phase sequentially across three milestones:
1. **Milestone 1: Exploration & Diagnosis**
   - Spawn a `teamwork_preview_explorer` to analyze existing files (`bot.py`, `app.py`, `database.py`, etc.).
   - Identify existing runtime exceptions and why the bot is crashing or failing to initialize.
   - Analyze how filtering is currently implemented and how keyword matching is done.
   - Propose allowlist/blocklist approach for job title filtering.

2. **Milestone 2: Implementation & Refactoring**
   - Spawn a `teamwork_preview_worker` to write the filter engine.
   - Update bot logic to integrate the filter engine.
   - Resolve all syntax, initialization, and runtime errors in `bot.py` and other modules.

3. **Milestone 3: Verification & Auditing**
   - Spawn a `teamwork_preview_challenger` to write `test_motor.py` containing mock jobs, including 10+ tricky false positives.
   - Run verification tests to ensure all false positives are blocked and true positives pass.
   - Verify that `python bot.py` starts and processes requests without crashing.
   - Run `teamwork_preview_auditor` to perform forensic audit.
