# Analysis and Proposed Fixes: Telegram Status Loop & 99Freelas Disablement

## Executive Summary
This report analyzes two distinct issues in `bot.py`:
1. **Indeed Status Stuck in 'Buscando...'**: The Telegram dashboard message fails to show the final state of the Indeed scraper. This is due to a race condition where the background `status_updater` task terminates immediately when `is_hunting` is set to `False`, failing to perform one final edit to the Telegram message. Because Indeed is a slow scraper (doing deep description lookups), it is typically the last to finish, making it the primary victim of this race condition. Additionally, if any scraper fails all three retry attempts, it remains stuck on a `"⚠️ Retry 3/3"` status due to suppressed exceptions.
2. **Permanent Disablement of 99freelas**: The `novenove` scraper is configured as a freelance platform in `bot.py`. We provide the exact changes to `bot.py` to disable it permanently from both the default configurations and the user interface.

---

## 1. Indeed Status Stuck in 'Buscando...'

### 1.1 Problem Location
The issue lies in `bot.py`, specifically within the `_do_hunt` method (lines 439-552), which contains:
- The background `status_updater` loop (lines 468-479).
- The `fetch_plat` helper function (lines 522-544).
- The termination of hunting (`is_hunting = False` on line 546).

Here is the relevant code segment from `bot.py`:
```python
465:     plat_status = {p: "⏳ Buscando..." for p in active_plats}
466:     is_hunting = True
467:     
468:     async def status_updater():
469:         while is_hunting:
470:             status_text = f"⏳ *Monitor de Caçada: {keyword}*\n\n"
471:             for p, stat in plat_status.items():
472:                 status_text += f"*{p.replace('_', ' ').title()}*: {stat}\n"
473:             try:
474:                 await status_msg.edit_text(status_text, parse_mode="Markdown")
475:             except Exception:
476:                 pass
477:             await asyncio.sleep(4)
478:             
479:     updater_task = asyncio.create_task(status_updater())
...
545:     results = await asyncio.gather(*(fetch_plat(p) for p in active_plats))
546:     is_hunting = False
```

And inside `fetch_plat` (lines 522-544):
```python
522:     async def fetch_plat(plat):
523:         logger.info(f"🚀 Iniciando scraper: {plat.upper()}")
524:         try:
525:             module = importlib.import_module(f"scrapers.{plat}")
526:             for tentativa in range(3):
527:                 try:
528:                     if plat in ['jsearch', 'jooble', 'github_vagas', 'novenove', 'freelancer', 'meta_ads', 'indeed', 'linkedin', 'gmail', 'glassdoor', 'infojobs']:
529:                         res = await asyncio.to_thread(module.scrape, keyword=search_keyword, level=settings["level"], country=settings["location"])
530:                     else:
531:                         res = await asyncio.to_thread(module.scrape, keyword=search_keyword, level=settings["level"])
532:                     plat_status[plat] = f"✅ {len(res)} vagas"
533:                     logger.info(f"✅ Scraper {plat.upper()} finalizado. Vagas encontradas (brutas): {len(res)}")
534:                     return res
535:                 except Exception as inner_e:
536:                     logger.warning(f"⚠️ Instabilidade no scraper {plat.upper()} (Tentativa {tentativa+1}/3): {inner_e}")
537:                     plat_status[plat] = f"⚠️ Retry {tentativa+1}/3"
538:                     if tentativa < 2:
539:                         await asyncio.sleep(2)
540:         except Exception as e:
541:             logger.exception(f"❌ Erro fatal ao carregar scraper {plat.upper()}: {e}")
542:         plat_status[plat] = "❌ Falhou"
543:         return []
```

### 1.2 Root Cause Analysis
1. **The status updater race condition**:
   - The `status_updater` loop runs while `is_hunting` is `True` and sleeps for 4 seconds between edits.
   - When the scrapers finish, `asyncio.gather` completes. Immediately after, `is_hunting = False` is set on line 546.
   - If `status_updater` was sleeping when the scrapers completed, it wakes up, evaluates `is_hunting` as `False`, exits the `while` loop, and terminates **without sending a final message update**.
   - As a result, the last written status to Telegram is from the previous loop iteration.
   - Since `scrapers/indeed.py` performs deep scraping (performing individual page loads or HTTP request calls for *each* scraped job to extract full descriptions, with a 1s delay per job), it is almost always the slowest scraper and finishes last.
   - The status change for Indeed from `"⏳ Buscando..."` to `"✅ X vagas"` or `"❌ Falhou"` happens at the very end of `asyncio.gather`. Since the loop exits immediately after, the Telegram message is left in the state it was before Indeed finished: showing Indeed as `"⏳ Buscando..."` forever.

2. **Supressed Scraper Failures**:
   - In `fetch_plat`, if the scraper fails on all 3 attempts, `except Exception as inner_e` catches the exception.
   - Since the exception is caught inside the loop, it does not propagate to the outer `try-except` block (line 524-540).
   - The function exits the loop naturally and executes `return []` at the end of the `try` block. It **never reaches line 542** (`plat_status[plat] = "❌ Falhou"`).
   - Thus, the scraper status on the dashboard remains stuck showing `"⚠️ Retry 3/3"` instead of `"❌ Falhou"`.

### 1.3 Proposed Fixes

#### Fix A: Final Update in `status_updater`
To resolve the race condition, we must perform one final UI update inside the `status_updater` task after the `while is_hunting` loop terminates.
```python
    async def status_updater():
        while is_hunting:
            status_text = f"⏳ *Monitor de Caçada: {keyword}*\n\n"
            for p, stat in plat_status.items():
                status_text += f"*{p.replace('_', ' ').title()}*: {stat}\n"
            try:
                await status_msg.edit_text(status_text, parse_mode="Markdown")
            except Exception:
                pass
            await asyncio.sleep(4)
        
        # --- FINAL POST-HUNT UPDATE ---
        status_text = f"⏳ *Monitor de Caçada: {keyword}*\n\n"
        for p, stat in plat_status.items():
            status_text += f"*{p.replace('_', ' ').title()}*: {stat}\n"
        try:
            await status_msg.edit_text(status_text, parse_mode="Markdown")
        except Exception:
            pass
```

#### Fix B: Correct Status on Failure
To ensure that a scraper which fails all 3 attempts is correctly marked as `"❌ Falhou"`, we should set `plat_status[plat] = "❌ Falhou"` when the retry loop exits without returning.
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
                    logger.warning(f"⚠️ Instabilidade no scraper {plat.upper()} (Tentativa {tentativa+1}/3): {inner_e}")
                    plat_status[plat] = f"⚠️ Retry {tentativa+1}/3"
                    if tentativa < 2:
                        await asyncio.sleep(2)
            
            # If the loop finishes without returning, all attempts failed
            plat_status[plat] = "❌ Falhou"
        except Exception as e:
            logger.exception(f"❌ Erro fatal ao carregar scraper {plat.upper()}: {e}")
            plat_status[plat] = "❌ Falhou"
        return []
```

---

## 2. Disabling 99Freelas ('novenove') Scraper

### 2.1 Configuration Location in `bot.py`
The 99freelas scraper (`novenove`) is configured and displayed in:
1. `FREELANCE_PLATFORMS` definition (line 64):
   ```python
   64: FREELANCE_PLATFORMS = ["workana", "novenove"]
   ```
2. `DEFAULT_SETTINGS` dictionary (line 77):
   ```python
   77:         "novenove": True,
   ```
3. Settings inline keyboard layout in `get_settings_markup` (line 150):
   ```python
   149:         [InlineKeyboardButton(text=f"Workana: {'✅ ON' if p['workana'] else '❌ OFF'}", callback_data="toggle_workana"),
   150:          InlineKeyboardButton(text=f"99Freelas: {'✅ ON' if p['novenove'] else '❌ OFF'}", callback_data="toggle_novenove")],
   ```

*(Note: The Web Dashboard `static/index.html` does not include `novenove` in its list of platforms, so no changes are needed on the frontend).*

### 2.2 Proposed Changes
To disable the 99freelas scraper permanently, the following changes should be applied:

1. **Remove `"novenove"` from `FREELANCE_PLATFORMS`**:
   ```python
   # Line 64 in bot.py
   FREELANCE_PLATFORMS = ["workana"]
   ```

2. **Set `"novenove": False` (or remove it) in `DEFAULT_SETTINGS`**:
   ```python
   # Line 77 in bot.py
       "platforms": {
           "jsearch": True,
           "jooble": True,
           "workana": True,
           "remotar": True,
           "novenove": False,
           "github_vagas": True,
           ...
       }
   ```

3. **Remove the 99Freelas button from `get_settings_markup`**:
   Replace lines 149-150 in `bot.py` to only display the Workana button:
   ```python
   # Lines 149-150 in bot.py
           [InlineKeyboardButton(text=f"Workana: {'✅ ON' if p['workana'] else '❌ OFF'}", callback_data="toggle_workana")],
   ```
   *Alternative design*: If we want to keep the UI clean, we can make the Workana button fill the full width of the row, which this does.

Applying these changes ensures that `novenove` is default-disabled, cannot be turned on through freelance mode commands, and has its toggle button removed from the Telegram settings menu.
