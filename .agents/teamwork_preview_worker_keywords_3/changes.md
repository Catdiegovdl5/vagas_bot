# Code Changes

## Files Modified

### 1. `bot.py`
- Changed contract filtering patterns (`r' pj '` -> `r'\bpj\b'`) in contract filters for PJ and CLT user preferences.
- Changed seniority levels regex boundary pattern (`rf' {w} '` -> `rf'\b{w}\b'`) for Junior, Pleno, and Senior matching.
- Changed global blacklist pattern (`rf' {re.escape(term)} '` -> `rf'\b{re.escape(term)}\b'`).
- Changed local blacklist pattern (`rf' {re.escape(w)} '` -> `rf'\b{re.escape(w)}\b'`).

### 2. `test_keywords.py`
- Added `boundary_cases` list with comprehensive cases for boundary conditions (e.g., blacklist words at the end/beginning of job titles, seniority levels adjacent to boundaries, contract types next to punctuation).
- Added a loop running `boundary_cases` along with the original approved and rejected cases.
