# Search Keyword and Seniority Level Analysis Report

This analysis examines how the search keyword and the seniority level filter (`settings["level"]`) are defined, read, and passed to scrapers in the `vagas_bot` codebase. It also recommends the safest implementation to dynamically append the seniority level to the search keyword.

---

## 1. Definition and Usage of `settings["level"]`

In `vagas_bot/bot.py`, the seniority level setting is defined and managed as follows:

*   **Initialization (Lines 67–87):** It is initialized to `"Todos"` in `DEFAULT_SETTINGS`:
    ```python
    DEFAULT_SETTINGS = {
        "level": "Todos",
        ...
    }
    ```
*   **Loading/Retrieving (Lines 91–95):** The helper `get_user_settings(chat_id)` retrieves the settings dictionary for a specific user:
    ```python
    def get_user_settings(chat_id):
        chat_id = str(chat_id)
        if chat_id not in user_settings_db:
            user_settings_db[chat_id] = copy.deepcopy(DEFAULT_SETTINGS)
        return user_settings_db[chat_id]
    ```
*   **User Update - Inline Buttons (Lines 167–176):** Users can toggle settings via inline keyboard callbacks. The `"change_level"` handler cycles through `["Todos", "Júnior", "Pleno", "Sênior"]`:
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
*   **User Update - NLP Parsing (Lines 762–793):** When a user enters text, the AI intent extractor extracts variables, updating `settings["level"]` (lines 784–785):
    ```python
    if level in ["Todos", "Júnior", "Pleno", "Sênior"]:
        settings["level"] = level
    ```
*   **Post-Scraping Relevance Filtering (Lines 364–373):** In `is_job_relevant(job, keyword, settings)`, the setting is normalized and used to filter out job titles that do not match the level constraints:
    ```python
    user_level = normalize_str(settings.get('level', 'Todos'))
    ...
    if user_level == 'junior':
        if any(re.search(rf'\b{w}\b', title_norm) for w in senior_terms + pleno_terms):
            return False
    elif user_level == 'pleno':
        ...
    ```

---

## 2. Scraper Invocation & Keyword Passing

In `vagas_bot/bot.py`, the search process is driven by the internal function `_do_hunt` (lines 438–760). 

*   **Keyword Mapping (Lines 528):** The Telegram selected keyword is mapped to a search keyword term using `search_mapping`:
    ```python
    search_keyword = search_mapping.get(keyword, keyword)
    ```
*   **Scraper Loading & Invocation (Lines 530–553):** Within `_do_hunt`, the scrapers are imported dynamically and executed concurrently inside `fetch_plat(plat)`:
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
                    plat_status[plat] = f"✅ {len(res)} vagas"
                    logger.info(f"✅ Scraper {plat.upper()} finalizado. Vagas encontradas (brutas): {len(res)}")
                    return res
                except Exception as inner_e:
                    ...
    ```
    This function is launched in parallel for all active platforms (Line 555):
    ```python
    results = await asyncio.gather(*(fetch_plat(p) for p in active_plats))
    ```

---

## 3. Implementation Recommendations

### The "Duplicate Append" Challenge
Five of the scraper modules (`github_vagas.py`, `jooble.py`, `jsearch.py`, `remotar.py`, and `workana.py`) already contain internal logic that checks if the `level` parameter is different from `"Todos"`, and if so, appends it to the query. For example, `scrapers/jsearch.py` lines 8-9:
```python
if level != "Todos":
    search_kw += f" {level}"
```
If we simply modify `search_keyword` in `bot.py` to append the level and pass it along with `level=settings["level"]` to those scrapers, they will append the level again, querying term combinations like `"Python Júnior Júnior"`.

To implement the requirement safely, we propose two main solutions:

---

### Option A: Modify `bot.py` to Append Level and Pass `level="Todos"` to Scrapers (RECOMMENDED)

This is the cleanest and most robust approach. It updates the keyword centrally in `bot.py` and disables the scrapers' internal level appends by passing `level="Todos"`. We then restore the correct `level` value on the returned job results to prevent breaking the database schemas or downstream filters.

#### Before (bot.py):
```python
    search_keyword = search_mapping.get(keyword, keyword)
    
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
```

#### After (bot.py - Proposed):
```python
    search_keyword = search_mapping.get(keyword, keyword)
    
    # 1. Append seniority level to the search keyword if it's not "Todos"
    actual_level = settings.get("level", "Todos")
    if actual_level != "Todos":
        search_keyword = f"{search_keyword} {actual_level}"
    
    async def fetch_plat(plat):
        logger.info(f"🚀 Iniciando scraper: {plat.upper()}")
        try:
            module = importlib.import_module(f"scrapers.{plat}")
            for tentativa in range(3):
                try:
                    # 2. Pass level="Todos" to the scrapers so they do not append the level again
                    if plat in ['jsearch', 'jooble', 'github_vagas', 'novenove', 'freelancer', 'meta_ads', 'indeed', 'linkedin', 'gmail', 'glassdoor', 'infojobs']:
                        res = await asyncio.to_thread(module.scrape, keyword=search_keyword, level="Todos", country=settings["location"])
                    else:
                        res = await asyncio.to_thread(module.scrape, keyword=search_keyword, level="Todos")
                    
                    # 3. Restore the correct level inside each job dict so that database entries and filters remain accurate
                    if res:
                        for job in res:
                            job["level"] = actual_level
                            
                    plat_status[plat] = f"✅ {len(res)} vagas"
                    logger.info(f"✅ Scraper {plat.upper()} finalizado. Vagas encontradas (brutas): {len(res)}")
                    return res
                except Exception as inner_e:
```

*   **Pros:** Easy to implement, doesn't touch scraper files, completely eliminates duplicate keyword terms (e.g. `"Júnior Júnior"`), preserves database/log integrity.
*   **Cons:** Overwrites `job["level"]` post-scraping, but since scrapers only set this to the passed `level` parameter, it has no side-effects.

---

### Option B: Conditional Appending in `bot.py`

This option keeps `settings["level"]` unmodified when calling scrapers that already support appending it, and only appends it for scrapers that do not natively support it.

#### After (bot.py - Proposed):
```python
    search_keyword = search_mapping.get(keyword, keyword)
    actual_level = settings.get("level", "Todos")
    
    async def fetch_plat(plat):
        logger.info(f"🚀 Iniciando scraper: {plat.upper()}")
        try:
            # Check if scraper natively appends level. If not, append it to the keyword parameter.
            natively_appends = plat in ['jsearch', 'jooble', 'github_vagas', 'remotar', 'workana']
            custom_keyword = search_keyword
            if actual_level != "Todos" and not natively_appends:
                custom_keyword = f"{search_keyword} {actual_level}"
                
            module = importlib.import_module(f"scrapers.{plat}")
            for tentativa in range(3):
                try:
                    if plat in ['jsearch', 'jooble', 'github_vagas', 'novenove', 'freelancer', 'meta_ads', 'indeed', 'linkedin', 'gmail', 'glassdoor', 'infojobs']:
                        res = await asyncio.to_thread(module.scrape, keyword=custom_keyword, level=actual_level, country=settings["location"])
                    else:
                        res = await asyncio.to_thread(module.scrape, keyword=custom_keyword, level=actual_level)
```

*   **Pros:** Leaves native scraper behavior exactly as-is, keeps database levels correct natively.
*   **Cons:** Hardcoded whitelist of scrapers (`natively_appends`) is error-prone and hard to maintain as scrapers are added, updated, or deleted.

---

## 4. Verification Method

To verify either implementation:

1.  **Unit / Integration Test:** Run the existing scraper test runner to verify it executes successfully:
    ```powershell
    python vagas_bot/scrapers/run_test.py
    ```
2.  **Manual Verification:**
    *   Set the level to `"Júnior"` or `"Sênior"` in the Telegram Bot configuration UI (or using `/start` and clicking "Configurações").
    *   Trigger a search (e.g., click `"Python"` or `"Especialista em IA"`).
    *   Inspect `erros_robo.log` or the console output to check that the search query contains the level (e.g., `Iniciando scraper: LINKEDIN` with keyword `Python Júnior`) and that no duplicate suffix (e.g., `Python Júnior Júnior`) appears in the logs or search URL parameters.
