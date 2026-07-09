# Plan: Seniority Level Filtering Implementation

## Mission
Modify `bot.py` to append the seniority level (if it is not "Todos") to the search keyword before calling the scrapers.

## Milestones and Steps

### Milestone 1: Exploration and Analysis
- **Goal**: Find the exact structure of settings and scrapers in `bot.py`, and how keywords are passed.
- **Steps**:
  1. Dispatch `teamwork_preview_explorer` to analyze `bot.py` and understand how the keyword and level settings are read and passed to the scrapers.
  2. The explorer should identify the precise lines in `bot.py` where:
     - `settings["level"]` is checked or accessed.
     - The scrapers are called (e.g. `fetch_plat` or in the search loop).
     - The keyword is handled.
  3. The explorer should output an analysis report detailing the proposed logical changes.

### Milestone 2: Implementation
- **Goal**: Apply the central seniority level concatenation.
- **Steps**:
  1. Dispatch `teamwork_preview_worker` to modify `bot.py`.
  2. The worker should implement:
     - Check if `settings["level"]` is different from `"Todos"`.
     - Concatenate the level to the keyword (e.g. `f"{search_keyword} {settings['level']}"`).
     - Pass the modified keyword to the scraper calls.
  3. Verify that the file compiles and has no syntax/import errors.

### Milestone 3: Verification, Testing and Auditing
- **Goal**: Ensure the change is robust and doesn't break other features.
- **Steps**:
  1. Dispatch `teamwork_preview_reviewer` to review the modifications made to `bot.py`.
  2. Dispatch `teamwork_preview_challenger` to run integration checks or unit tests to verify:
     - Scrapers receive the formatted search keyword when a level is set.
     - Scrapers receive the base search keyword when the level is "Todos".
  3. Dispatch `teamwork_preview_auditor` to audit the implementation.
  4. Ensure no integrity violations.

## Verification Criteria
- The modified keyword is passed to all active scrapers when `settings["level"]` != "Todos".
- Standard execution of `bot.py` is unaffected.
