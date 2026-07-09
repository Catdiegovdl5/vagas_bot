## 2026-07-07T18:43:00Z
You are a teamwork_preview_challenger. Your task is to write a script or test harness to empirically verify the correctness of the centralized seniority level filtering implementation.

Your objectives:
1. Write a test script or harness that tests the behavior of `_do_hunt`'s keyword transformation in `bot.py` with multiple seniority levels: "Todos", "Júnior", "Pleno", "Sênior", "None", and empty strings.
2. Verify that the correct search keyword (either with or without the suffix) is constructed and passed to the scraping process, and that the returned job dictionary contains the original level (e.g. "Sênior" instead of "Todos").
3. Verify that there are no exceptions or performance regressions during concurrent execution of `_do_hunt` (you can mock the scraper modules to return mock data immediately).
4. Run your test harness, verify it passes, and write your report to `C:\Users\99196\OneDrive\Documentos\vagas_bot\.agents\challenger_level_1\challenge.md`.
5. Send a message back to me (conversation ID: 5cb4152d-4810-4c8d-8709-f0d9655e30c6) when you are done.
