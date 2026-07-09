## 2026-07-07T23:31:02Z
You are worker_deep_audit_1. Your working directory is C:\Users\99196\OneDrive\Documentos\vagas_bot\.agents\worker_deep_audit_1\.
Your task is to implement the following codebase fixes to make all tests pass and ensure 100% stability:

1. In `scrapers/glassdoor.py`:
   - Relax the page load validation check to support mock testing. Replace:
     `if "glassdoor" in content.lower() and len(content) > 5000:`
     with:
     `if ("glassdoor" in content.lower() or "mock" in content.lower()) and len(content) > 20:`
   
2. In `scrapers/ai_filter.py`:
   - Change the validation exception catch block's return reason to "Erro no modelo estruturado." to pass `test_ia_ranking_handles_groq_malformed_json`.
   
3. In `auto_apply.py`:
   - Make the signatures of `run_auto_apply` and `apply_to_job` backward-compatible.
   - Specifically, if the third parameter (`candidate`) is a string, treat it as `mock_ats_url` and use a default candidate dict: `{"name": "Diego Candidate", "email": "diego@example.com"}`.
   
4. In `scrapers/gmail.py`:
   - Handle invalid base64 padding and alternative encoding formats (like ISO-8859-1) dynamically in email body decoding.
   - Place the inner email-parsing logic inside `for msg in messages:` in its own try-except block so a single bad email does not abort the whole scraper.
   
5. In `verify_seniority.py`:
   - Use a threading lock for list mutations on `captured_keywords`.
   - Wrap the test execution in a `try...finally` block to guarantee cleanup of `TEST_DB_PATH`.

6. Run the test suite:
   - Run `python run_tests.py` using `run_command` and check the test results. All 56 tests must pass.

MANDATORY INTEGRITY WARNING:
> DO NOT CHEAT. All implementations must be genuine. DO NOT
> hardcode test results, create dummy/facade implementations, or
> circumvent the intended task. A Forensic Auditor will independently
> verify your work. Integrity violations WILL be detected and your
> work WILL be rejected.

Send a message to parent (id: 1003085d-58dd-4e3f-bc1b-208b56a955f6) when done with the test suite execution results and a list of modified files.
