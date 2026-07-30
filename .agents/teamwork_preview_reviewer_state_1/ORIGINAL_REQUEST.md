## 2026-07-21T20:35:30Z
You are Reviewer 1. Perform a code review of R1 changes in `app.py` and `scrapers/*.py`.

Your working directory is: `C:/Users/99196/OneDrive/Documentos/vagas_bot/.agents/teamwork_preview_reviewer_state_1`

Review Checklist:
1. Verify `app.py` `run_hunt_background`: Check if `location` is extracted from request payload and correctly passed to `module.scrape` via `inspect.signature` or kwargs.
2. Check `scrapers/*.py` function signatures and ensure `location` is accepted and used when constructing search query URLs or API params where appropriate.
3. Check error handling and backward compatibility (e.g. defaulting `location` to "Todos" when omitted).
4. Run python test execution if needed.

Write your review report to `C:/Users/99196/OneDrive/Documentos/vagas_bot/.agents/teamwork_preview_reviewer_state_1/review.md` and `handoff.md`.
Send a message with your verdict (PASS/FAIL) once done.
