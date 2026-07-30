# Changes

## Bugfix: regex word boundaries in `has_any` in `bot.py`

### Modified Files:
- `bot.py`

### Details:
1. Modified `has_any` in `bot.py` (lines 519-531) to use regex word boundary anchors `\b` rather than space padding (`rf' {re.escape(w)} '` or similar). This allows keywords at the start or end of a string to match correctly even if there is no leading or trailing space.
   - Wildcards (words ending with `*`): uses `rf'\b{re.escape(w[:-1])}\w*'`
   - Exact matches: uses `rf'\b{re.escape(w)}\b'`
2. Under `"especialista em ia generativa"` rules (line 554), updated `"design"` to `"design*"` to correctly match `"designer"` when evaluating roles with the new exact word boundary matching, fixing `test_especialista_ia_generativa_keywords` in `tests/test_tier1.py`.

### Verification:
- Compiled `bot.py` using `python -m py_compile bot.py` (clean exit).
- Ran keyword validation suite `python test_keywords.py` (Passed all 10 cases).
- Ran full test suite `python run_tests.py` (Passed all 57 tests).
