# Plan - AI Creative Job Filtering Implementation

## Objectives
1. Modify filtering rules in `bot.py` and `scrapers/ai_filter.py` to accept creative/marketing jobs that utilize AI (ChatGPT, Midjourney, Claude, etc.).
2. Create `verify_ai_creative_jobs.py` to mathematically mock and test 5 creative AI jobs (approved) and 5 non-AI jobs (rejected).
3. Ensure the test script runs with a 100% green output without exceptions.

## Steps
### Step 1: Modify `bot.py` Filtering Rules
- Update `"especialista em ia generativa"` rules under the `rules` dictionary in `is_job_relevant` function.
- Add marketing/creative keywords to the second group to allow jobs like "Copywriter com ChatGPT", "Gestor de Tráfego com IA", "Designer Midjourney", etc.

### Step 2: Relax AI Filter Constraints in `scrapers/ai_filter.py`
- Modify Rule 8 ("Regra de Ouro IA") in `score_job_match` to accept performance marketing and content creation jobs that explicitly integrate generative AI tools (ChatGPT, Midjourney, Claude, etc.).

### Step 3: Create `verify_ai_creative_jobs.py`
- Write a Python script that mocks job dicts.
- Import `is_job_relevant` from `bot.py`.
- Mock settings: `level="Todos"`, `location="Todos"`, `contract="Todos"`.
- Verify that 5 creative AI jobs are approved (evaluate to True).
- Verify that 5 non-AI jobs are rejected (evaluate to False).
- Run with 100% green output and clear print statements.

### Step 4: Run Verification Tests
- Run `verify_ai_creative_jobs.py` and ensure it runs cleanly.
