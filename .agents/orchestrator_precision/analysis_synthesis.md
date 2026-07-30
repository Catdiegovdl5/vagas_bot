# Synthesis of Codebase Analysis — Milestone 1

## Consensus
All three Explorer subagents reached consensus on the primary causes of the E2E failures and the proposed high-precision filter engine design:

1. **Unprotected Startup Call**: `bot.py` crashes on startup at line 991 because `await bot.set_chat_menu_button()` is called outside the retry polling loop.
2. **Decommissioned Groq LLM**: The decommissioned model `llama3-70b-8192` caused errors, leading to a simplified text-based mock filter in `scrapers/ai_filter.py` that does not define `API_KEYS` (causing import errors in tests) and lacks language/currency locks.
3. **SQLite Write Locks**: Manual database connections in `tests/test_tier1.py` are left open when tests abort due to assertion failures, resulting in persistent write locks and locking the DB file.
4. **Keyword Filtering Gaps**: Simple keyword check in `bot.py` doesn't check title allowlists or handle word order variations, and the `/api/trigger` endpoint in `app.py` inserts jobs into the database without validation.

## Solution Architecture
1. **Unprotected Startup Call**: Wrap `await bot.set_chat_menu_button()` in a try-catch block inside the polling loop, or handle it gracefully.
2. **Fix `ai_filter.py`**:
   - Re-introduce the `API_KEYS` variable.
   - Update the fallback model in `scrapers/ai_filter.py` to a supported model (like `llama-3.3-70b-versatile` or whatever is active), or ensure the mock/classic filter passes the E2E tests and implements the hard-locks (USD/Euro, English requirements for junior positions).
3. **Fix SQLite Locks**: Modify tests to use a context manager (`with sqlite3.connect(...) as conn:`) or ensure `finally: conn.close()` is always executed to release database locks.
4. **High-Precision Filtering Engine (HPFE)**:
   - Implement `job_filter.py` (or integrate into `bot.py` and `scrapers/ai_filter.py`) using:
     - Title allowlist groups (AND of ORs to handle order independence).
     - Title blocklists (niche and global).
     - Word boundary exact match (`\bword\b`) in full text.
   - Run this check in both `bot.py` and `app.py`'s `/api/trigger` before storing jobs.
