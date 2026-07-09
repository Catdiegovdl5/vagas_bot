## 2026-07-07T18:57:00Z
You are a teamwork_preview_challenger. Your task is to write a script or test harness to empirically verify the correctness of the centralized seniority level filtering implementation.

Your objectives:
1. Write a test script or harness that tests the behavior of `_do_hunt`'s keyword transformation in `bot.py` with multiple seniority levels: "Todos", "Júnior", "Pleno", "Sênior", "None", and empty strings.
2. Verify that the correct search keyword (either with or without the suffix) is constructed and passed to the scraping process, and that the returned job dictionary contains the original level (e.g. "Sênior" instead of "Todos").
3. Verify that there are no exceptions or performance regressions during concurrent execution of `_do_hunt` (you can mock the scraper modules to return mock data immediately).
4. Run your test harness, verify it passes, and write your report to `C:\Users\99196\OneDrive\Documentos\vagas_bot\.agents\challenger_level_2_resumed\challenge.md`.
5. Send a message back to me when you are done.

## 2026-07-07T18:57:38Z
Resume work at C:\Users\99196\OneDrive\Documentos\vagas_bot. Read ORIGINAL_REQUEST.md in C:\Users\99196\OneDrive\Documentos\vagas_bot\.agents\challenger_level_2_resumed for detailed instructions. Execute the test harness, verify results, and report back via send_message.
