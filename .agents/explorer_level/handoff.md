# Handoff Report — explorer_level

## 1. Observation
The following file paths and line ranges were inspected:
*   **`vagas_bot/bot.py`**:
    *   Lines 67–87:
        ```python
        DEFAULT_SETTINGS = {
            "level": "Todos",
            ...
        }
        ```
    *   Lines 91–95:
        ```python
        def get_user_settings(chat_id):
            chat_id = str(chat_id)
            if chat_id not in user_settings_db:
                user_settings_db[chat_id] = copy.deepcopy(DEFAULT_SETTINGS)
            return user_settings_db[chat_id]
        ```
    *   Lines 167–176 (`change_level` CallbackQuery handler):
        ```python
        @dp.callback_query(F.data == "change_level")
        async def change_level(callback: CallbackQuery):
            await callback.answer()
            chat_id = callback.message.chat.id
            settings = get_user_settings(chat_id)
            levels = ["Todos", "Júnior", "Pleno", "Sênior"]
            idx = levels.index(settings["level"])
            settings["level"] = levels[(idx + 1) % len(levels)]
            await callback.message.edit_reply_markup(reply_markup=get_settings_markup(chat_id))
        ```
    *   Line 528:
        ```python
        search_keyword = search_mapping.get(keyword, keyword)
        ```
    *   Lines 530–553 (`fetch_plat` inner function):
        ```python
        async def fetch_plat(plat):
            logger.info(f"🚀 Iniciando scraper: {plat.upper()}")
            try:
                module = importlib.import_module(f"scrapers.{plat}")
                for tentativa in range(3):
                    try:
                        if plat in ['jsearch', 'jooble', 'github_vagas', 'novenove', 'freelancer', 'meta_ads', 'indeed', 'linkedin', 'gmail', 'glassdoor', 'infojobs']:
                            res = await asyncio.to_thread(module.scrape, keyword=search_keyword, level=settings["level"], country=settings["location"])
                        else:
                            res = await asyncio.to_thread(module.scrape, keyword=search_keyword, level=settings["level"])
                        ...
        ```
*   **Scrapers in `vagas_bot/scrapers/`**:
    *   `workana.py` (line 9): `if level != "Todos": search_kw += f" {level}"`
    *   `remotar.py` (line 8): `if level != "Todos": search_kw += f"+{level}"`
    *   `jsearch.py` (lines 8–9): `if level != "Todos": search_kw += f" {level}"`
    *   `jooble.py` (lines 15–16): `if level != "Todos": search_kw += f" {level}"`
    *   `github_vagas.py` (lines 13–14): `if level != "Todos": query += f" {level}"`
    *   All other scrapers (such as `freelancer.py`, `linkedin.py`, etc.) do not dynamically append `level` in their query parameters.

---

## 2. Logic Chain
1. `settings["level"]` is retrieved via `get_user_settings(chat_id)` and can be configured as `"Todos"`, `"Júnior"`, `"Pleno"`, or `"Sênior"` (from Observation 1).
2. The user starts a job hunt, calling `_do_hunt(keyword, ...)` in `bot.py` which retrieves `search_keyword = search_mapping.get(keyword, keyword)` and invokes scrapers in parallel by calling their `scrape` function (from Observation 1).
3. If we append `settings["level"]` to `search_keyword` in `bot.py` and pass `level=settings["level"]` to all scrapers, those scrapers that already append the level internally (`workana.py`, `remotar.py`, `jsearch.py`, `jooble.py`, `github_vagas.py`) will append the level again, resulting in query keywords like `"Python Júnior Júnior"` (from Observation 2).
4. To fulfill the requirement cleanly without modifying existing scraper files:
   - We must append the level to `search_keyword` in `bot.py` when it is not `"Todos"`.
   - We should pass `level="Todos"` to the scraper modules' `scrape` function calls so they skip their internal append checks.
   - We must overwrite the `level` key on each returned job dict with the actual user level so database insertions and post-scraping filters keep working.

---

## 3. Caveats
*   **API Limits and Behavior**: We did not execute queries against live RapidAPI endpoints (such as `JSearch`) as we do not have API keys. The scraper logic is assumed to behave exactly as read from their source code.
*   **Database Constraints**: We assume that setting `job["level"]` post-scraping is sufficient for the application's database. This matches what `database.py` receives.

---

## 4. Conclusion
We recommend implementing Option A in `vagas_bot/bot.py`. It updates `_do_hunt` to append the level to `search_keyword` if the level is not `"Todos"`, calls `module.scrape` with `level="Todos"` (to prevent duplicate appends), and restores `job["level"] = settings["level"]` on the resulting items before returning. This is fully self-contained and avoids editing scraper modules or maintaining custom lists of scrapers.

---

## 5. Verification Method
1. **Scraper Test Harness**: Ensure the scrapers run without syntax errors using:
   ```powershell
   python vagas_bot/scrapers/run_test.py
   ```
2. **Manual Integration Test**:
   * Run the bot locally (`python vagas_bot/bot.py`).
   * Select a seniority level (e.g. "Sênior") in config settings.
   * Run a search query (e.g. "Python").
   * Inspect stdout/stderr logs and verify the console shows `Iniciando scraper` with `Python Sênior` and no duplicated suffix.
