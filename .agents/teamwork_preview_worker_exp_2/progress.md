# Progress Log

Last visited: 2026-07-21T12:23:00Z

- Initialized briefing and original request.
- Analyzed root causes and test failures.
- Promoted `search_mapping` to module-level `SEARCH_MAPPING` in `bot.py`.
- Updated `CO_OCCURRENCE_RULES` and `blacklist` with entries for `python backend` and `desenvolvedor junior / estagiario`.
- Updated `is_job_relevant` to use `clean_kw = SEARCH_MAPPING.get(keyword, keyword)`.
- Fixed `check_co_occurrence` short-description fallback to verify every group matches in title.
- Ran all verification commands (`python test_experience.py`, `python test_motor.py`, `python test_keywords.py`, `python run_tests.py`).
- All tests passed 100% with exit code 0.
- Task complete.
