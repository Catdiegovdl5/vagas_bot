# Handoff Report - Keyword Review & Regex Boundary Fix

## 1. Observation

- **File Path**: `C:\Users\99196\OneDrive\Documentos\vagas_bot\bot.py`
  - **Lines 485-491**:
    ```python
        if user_contract == 'clt':
            if (re.search(r' pj ', full_text) or 'freelancer' in full_text or 'pessoa juridica' in full_text) and 'clt' not in full_text:
                return False
        elif user_contract == 'pj':
            if ('clt' in full_text or 'carteira assinada' in full_text) and not re.search(r' pj ', full_text):
                return False
    ```
  - **Lines 496-504**:
    ```python
        if user_level == 'junior':
            if any(re.search(rf' {w} ', title_norm) for w in senior_terms + pleno_terms):
                return False
        elif user_level == 'pleno':
            if any(re.search(rf' {w} ', junior_terms + senior_terms) for w in junior_terms + senior_terms): # Note: actually in code is: any(re.search(rf' {w} ', title_norm) for w in junior_terms + senior_terms)
                return False
        elif user_level == 'senior':
            if any(re.search(rf' {w} ', title_norm) for w in junior_terms + pleno_terms):
                return False
    ```
  - **Lines 508-515**:
    ```python
        # 1. Global Title Blacklist check (excluding terms in user search keyword)
        active_global_blacklist = [term for term in global_title_blacklist if term not in kw_norm]
        if any(re.search(rf' {re.escape(term)} ', title_norm) for term in active_global_blacklist):
            return False
            
        # 2. Local Niche-specific Blacklist check
        if kw_norm in blacklist:
            if any(re.search(rf' {re.escape(w)} ', title_norm) for w in blacklist[kw_norm]):
                return False
    ```

- **Commands Executed**:
  - Compiling bot.py: `python -c "import py_compile; py_compile.compile('bot.py')"` (Exit code: 0)
  - Running test_keywords.py: `python test_keywords.py` (Passed)
  - Running main test suite: `python run_tests.py` (Passed 57 tests)
  - Adversarial check for blacklist at start/end of string:
    `python -c "from bot import is_job_relevant, DEFAULT_SETTINGS; job = {'title': 'Desenvolvedor Python Professor', 'requirements': 'Requisitos'}; print(is_job_relevant(job, 'Backend Python', DEFAULT_SETTINGS))"` -> Output: `True` (Expected: `False` due to `"professor"` blacklist)
  - Adversarial check for level filter regression:
    `python -c "from bot import is_job_relevant, DEFAULT_SETTINGS; settings = DEFAULT_SETTINGS.copy(); settings['level'] = 'junior'; job = {'title': 'Senior Python Developer', 'requirements': 'Requisitos'}; print(is_job_relevant(job, 'Backend Python', settings))"` -> Output: `True` (Expected: `False` since user level is `'junior'` and job level is `'Senior'`)
  - Adversarial check for contract filter regression:
    `python -c "from bot import is_job_relevant, DEFAULT_SETTINGS; settings = DEFAULT_SETTINGS.copy(); settings['contract'] = 'clt'; job = {'title': 'Desenvolvedor Python PJ', 'requirements': 'Requisitos'}; print(is_job_relevant(job, 'Backend Python', settings))"` -> Output: `True` (Expected: `False` since user contract is `'clt'` and job contract is `'PJ'`)

---

## 2. Logic Chain

1. In `is_job_relevant` under `bot.py`, the filtering criteria for blacklisted words, senior/junior levels, and the `"pj"` contract type are evaluated using regular expression searches of the form `re.search(rf' {term} ', text)`.
2. This regular expression requires a literal space character both immediately preceding and immediately following the target term.
3. If a target term appears at the start of the string (where it has no preceding character) or at the end of the string (where it has no succeeding character), or adjacent to a punctuation mark (e.g. slashes, hyphens, colons), the literal space condition is not met.
4. Consequently, `re.search(rf' {term} ', text)` evaluates to `None` (fails to match).
5. As observed in the test commands, this enables blacklisted terms (`"professor"`), conflicting seniority levels (`"Senior"`), and conflicting contract types (`"PJ"`) to slip past the filters undetected.
6. The test suite (`test_keywords.py` and main tests) does not detect this issue because all its rejected test cases fail the positive matching rules anyway, creating a false impression of correctness.

---

## 3. Caveats

- We assumed that word boundaries `\b` are the intended mechanism for matching terms in Brazilian Portuguese job listings. This is correct as Portuguese uses standard alphabetic characters, which are recognized by `\b`.
- We only reviewed `bot.py` and its test suites; we did not examine the frontend/Telegram bot messaging execution.

---

## 4. Conclusion

- **Verdict**: **REQUEST_CHANGES**
- The keyword filtering implementation in `bot.py` contains a critical correctness flaw due to the use of space characters rather than word boundary (`\b`) matchers in regular expressions. This breaks blacklist enforcement, seniority filtering, and contract type checks.

---

## 5. Verification Method

To verify the issue and validate the fix, run the following commands in the workspace:

1. **Verify the current broken behavior**:
   ```powershell
   python -c "from bot import is_job_relevant, DEFAULT_SETTINGS; job = {'title': 'Desenvolvedor Python Professor', 'requirements': 'Requisitos'}; print(is_job_relevant(job, 'Backend Python', DEFAULT_SETTINGS))"
   # Output will be True, but should be False (since 'professor' is blacklisted)
   ```
2. **Verify level filtering behavior**:
   ```powershell
   python -c "from bot import is_job_relevant, DEFAULT_SETTINGS; settings = DEFAULT_SETTINGS.copy(); settings['level'] = 'junior'; job = {'title': 'Senior Python Developer', 'requirements': 'Requisitos'}; print(is_job_relevant(job, 'Backend Python', settings))"
   # Output will be True, but should be False (since a junior user should not match a senior job)
   ```

3. **Verify the fix**:
   Once the regex patterns `rf' {term} '` are changed to `rf'\b{term}\b'` (or similar word boundary check) in `bot.py`, running the above commands should return `False`.

---

# QUALITY & ADVERSARIAL REVIEW REPORTS

## Review Summary

**Verdict**: **REQUEST_CHANGES**

## Findings

### [Critical] Finding 1 — Flawed regex boundaries in Blacklist filtering
- **What**: Blacklisted words are not filtered out when they appear at the start/end of the job title.
- **Where**: `bot.py` (Lines 508-515)
- **Why**: The code uses `rf' {term} '` which fails to match words at boundaries.
- **Suggestion**: Replace `rf' {re.escape(term)} '` with `rf'\b{re.escape(term)}\b'`.

### [Critical] Finding 2 — Flawed level filtering
- **What**: Seniority levels are not filtered correctly, allowing Junior users to match Senior titles.
- **Where**: `bot.py` (Lines 496-504)
- **Why**: The code uses space padding `rf' {w} '` instead of word boundaries.
- **Suggestion**: Replace `rf' {w} '` with `rf'\b{w}\b'`.

### [Major] Finding 3 — Flawed contract filtering
- **What**: The contract type filter fails to detect PJ jobs when `"PJ"` appears at the end of the title or next to punctuation.
- **Where**: `bot.py` (Lines 485-491)
- **Why**: It uses the pattern `r' pj '`.
- **Suggestion**: Replace `r' pj '` with `r'\bpj\b'`.

## Verified Claims

- Python syntax compilation → verified via `py_compile` → **pass**
- Keyword verification test suite (`test_keywords.py`) → verified via python execution → **pass** (but does not test blacklist boundary cases)
- Main project test suite (`run_tests.py`) → verified via command execution → **pass** (57 tests passed, but coverage does not catch the regex boundary bugs)

## Coverage Gaps

- Missing test cases in `test_keywords.py` for verifying that jobs satisfying positive rules but containing blacklisted words/wrong seniority/wrong contracts at boundaries are correctly rejected. — Risk level: **High** — Recommendation: Add explicit boundary tests to `test_keywords.py`.

---

## Challenge Summary

**Overall risk assessment**: **HIGH**

## Challenges

### [High] Challenge 1 — Edge case failure for word boundaries
- **Assumption challenged**: Space literal checks `rf' {term} '` are sufficient to enforce boundaries.
- **Attack scenario**: A job titled `"Senior Python Developer"` matches Group 2 (`"desenvolv*"`) and Group 1 (`"python"`), but because `"Senior"` is at the start, the space-literal check for `"senior"` fails, allowing it to bypass the Junior exclusion list.
- **Blast radius**: Candidates will receive irrelevant/incorrectly matched job recommendations (e.g. Juniors seeing Senior roles, CLT users seeing PJ-only roles, and spam/blacklisted jobs).
- **Mitigation**: Update all boundaries to use standard `\b` word boundary operators.

## Stress Test Results

- `"Professor de Python"` under `"Backend Python"` → Expected: `False`, Got: `False` (Passes only because positive rules fail)
- `"Desenvolvedor Python Professor"` under `"Backend Python"` → Expected: `False` (blacklist), Got: `True` (**FAIL**)
- `"Senior Python Developer"` for a Junior user under `"Backend Python"` → Expected: `False`, Got: `True` (**FAIL**)
- `"Desenvolvedor Python PJ"` for a CLT user under `"Backend Python"` → Expected: `False`, Got: `True` (**FAIL**)
