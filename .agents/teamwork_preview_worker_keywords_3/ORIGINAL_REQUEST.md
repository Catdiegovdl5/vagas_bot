## 2026-07-13T20:26:24Z

You are teamwork_preview_worker.
Your working directory is C:\Users\99196\OneDrive\Documentos\vagas_bot\.agents\teamwork_preview_worker_keywords_3

Your task is to fix regex word boundary bugs for blacklist, level, and contract checks inside `bot.py`, and expand the test suite in `test_keywords.py`.

Context:
- The previous implementation in `bot.py` used literal spaces (e.g. `rf' {term} '` or `r' pj '`) to match boundaries for blacklisted keywords, level checks, and contract checks.
- This fails to match terms that appear at the beginning or end of strings, or adjacent to punctuation marks.
- You must replace all these space-boundary patterns with `\b` word boundaries (e.g. `rf'\b{re.escape(term)}\b'`).

Steps:
1. Initialize your BRIEFING.md and progress.md.
2. Read the reviewer's handoff report at C:\Users\99196\OneDrive\Documentos\vagas_bot\.agents\teamwork_preview_reviewer_keywords_2\handoff.md.
3. Read `bot.py` and inspect lines 480 to 520 (specifically where contract, level, global blacklist, and local blacklist check boundaries are performed).
4. Replace all literal space check patterns (like `rf' {w} '`, `r' pj '`, `rf' {re.escape(term)} '`) with `\b` word boundary regex patterns (like `rf'\b{w}\b'`, `r'\bpj\b'`, `rf'\b{re.escape(term)}\b'`).
5. Read and edit `test_keywords.py` to:
   - Add new test cases verifying correct boundary detection (e.g. "Desenvolvedor Python Professor" is rejected under "Backend Python" due to the global blacklist; "Senior Python Developer" is rejected for Junior level; "Desenvolvedor Python PJ" is rejected for CLT contract).
6. Compile `bot.py` to ensure it is syntactically valid:
   - Run `python -m py_compile bot.py`
7. Run the keyword verification test suite:
   - Run `python test_keywords.py`
8. Run the main project test suite to verify everything passes:
   - Run `python run_tests.py` or run `pytest` if configured.
9. Write changes.md and handoff.md in your working directory.
10. Notify the parent (conversation ID: 40e05eba-f7bc-4692-b760-1b706f11a7a6).

MANDATORY INTEGRITY WARNING:
> DO NOT CHEAT. All implementations must be genuine. DO NOT
> hardcode test results, create dummy/facade implementations, or
> circumvent the intended task. A Forensic Auditor will independently
> verify your work. Integrity violations WILL be detected and your
> work WILL be rejected.
