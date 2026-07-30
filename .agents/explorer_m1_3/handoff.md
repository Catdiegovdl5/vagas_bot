# Handoff Report — explorer_m1_3

## 1. Observation
We observed the following in the codebase and test runs of the project located at `C:\Users\99196\OneDrive\Documentos\vagas_bot`:

1. **Unprotected Startup Call**:
   In `bot.py` at line 991:
   ```python
   async def main():
       print("Bot Nativo Ligado e Aguardando Comandos!")
       await bot.set_chat_menu_button()
       
       while True:
           try:
               await dp.start_polling(bot)
   ```
   Calling `bot.set_chat_menu_button()` outside the `try/except` block throws unchecked exceptions on startup if the token is invalid or the network is down.

2. **Decommissioned Groq LLM Model**:
   `erros_robo.log` shows:
   ```log
   2026-07-04 13:21:17 | ERROR | Erro ao extrair JSON: Error code: 400 - {'error': {'message': 'The model `llama3-70b-8192` has been decommissioned and is no longer supported. Please refer to https://console.groq.com/docs/deprecations for a recommendation on which model to use instead.', 'type': 'invalid_request_error', 'code': 'model_decommissioned'}}
   ```

3. **SSL Certificate Errors**:
   `erros_robo.log` shows:
   ```log
   ssl.SSLCertVerificationError: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: self-signed certificate in certificate chain (_ssl.c:1081)
   ```

4. **Missing Import Constant**:
   Running `pytest tests/` fails with:
   ```
   FAILED tests/test_tier2.py::test_ia_ranking_groq_client_no_api_keys - ImportError: cannot import name 'API_KEYS' from 'scrapers.ai_filter'
   ```

5. **Divergent Keyword Filtering Logic**:
   In `bot.py` lines 525-534, keyword verification uses simple exact matching:
   ```python
   if kw_norm in title_norm:
       return True
       
   # Busca Literal Exata: procura a palavra-chave isolada no título ou na descrição
   kw_regex = rf'\b{re.escape(kw_norm)}\b'
   
   if re.search(kw_regex, full_text):
       return True
   ```
   However, `bot.py.mine` has a detailed `rules` dict mapping niches (like `"especialista em ia generativa"`) to co-occurrence groups of terms to match.

6. **FastAPI Web App Filter Bypass**:
   In `app.py` lines 83-92, scraped jobs are directly ingested into the database without running any local keyword or seniority filter (`is_job_relevant`).

---

## 2. Logic Chain
1. Calling `bot.set_chat_menu_button()` before starting the polling loop causes any network/token errors to raise exceptions, halting execution immediately instead of retrying as intended in the loop (Observation 1).
2. The model `llama3-70b-8192` was decommissioned by Groq, and the codebase has been modified to use a mock-free rule-based fallback in `scrapers/ai_filter.py` (Observation 2). This mismatch causes tests designed for the LLM output structure to fail (e.g. `test_sanity_battery_zero_approval`, `test_ia_ranking_handles_groq_malformed_json`).
3. `tests/test_tier1.py` expects `"Copywriter ChatGPT"` to be evaluated as relevant when searching for `"Especialista em IA Generativa"`. Because `bot.py` uses simple exact matching (Observation 5) instead of the niche-specific rules dictionary defined in `bot.py.mine`, the test `test_especialista_ia_generativa_keywords` fails.
4. The dashboard's `/api/trigger` directly calls scrapers and inserts the results into the DB (Observation 6), leaving the database filled with unfiltered or irrelevant jobs when triggered via the Web App.

---

## 3. Caveats
- We did not investigate external Telegram bot connectivity, assuming the environment has the appropriate variables (`TELEGRAM_TOKEN`, `GROQ_API_KEY`) set during runtime.
- We did not change or test any code changes in the active codebase as per the "read-only investigation" constraints.

---

## 4. Conclusion
The startup/runtime exceptions are caused by:
1. Calling connection-dependent API functions outside safety wrappers on startup.
2. A decommissioned AI model (`llama3-70b-8192`) causing Groq integration failures.
3. Missing constants (`API_KEYS`) in the active `ai_filter.py`.
4. Gaps in keyword filtering between `bot.py` (active) and `bot.py.mine` (rules mapping), and the complete bypass of local filtering in `app.py`.

We recommend implementing our High-Precision Filtering Engine (HPFE) designed in `analysis.md` across both `bot.py` and `app.py` to cross-validate exact keyword matches, allowlists (via co-occurrence groups), and global/niche-specific blocklists.

---

## 5. Verification Method
To independently verify the observations:
1. Run `python run_tests.py` or `pytest tests/` in the workspace directory.
2. Confirm the 16 test failures (including `test_especialista_ia_generativa_keywords` and `test_ia_ranking_groq_client_no_api_keys`).
3. Inspect `bot.py` at line 991, `app.py` at line 83, and `scrapers/ai_filter.py` to verify the lack of `API_KEYS` and the simple keyword-matching logic.
4. Verify the analysis and filter design report at `.agents/explorer_m1_3/analysis.md`.
