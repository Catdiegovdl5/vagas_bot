# HANDOFF REPORT — Explorer Carreiras 1

## 1. Observation
- **File Examined**: `C:\Users\99196\OneDrive\Documentos\vagas_bot\bot.py` (Total Lines: 1802, Total Bytes: 95535).
- **Command Handlers Present**:
  - `bot.py:110`: `@dp.message(Command("start"))` executes `show_main_menu(message)`.
  - `bot.py:114`: `@dp.message(Command("logs"))` tailing error logs.
  - No existing `/carreiras` command handler.
- **Main Menu Implementations**:
  - `bot.py:140-144`: `persistent_markup = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🎯 Caçar Vagas"), KeyboardButton(text="🛠 Configurações")]], resize_keyboard=True, is_persistent=True)`
  - `bot.py:150-155`: `def get_main_menu_markup()` returns `InlineKeyboardMarkup` with buttons `hunt_menu`, `mega_iniciantes`, `settings_menu`.
- **Text & Callback Routing**:
  - `bot.py:1633`: `@dp.message(F.text == "🎯 Caçar Vagas")`
  - `bot.py:1649`: `@dp.message(F.text == "🛠 Configurações")`
  - `bot.py:1656`: `@dp.message(F.text)` catches generic free text for NLP search.
- **Telegram Limits**:
  - Telegram Bot API enforces max 64 bytes on `callback_data`. Exceeding 64 bytes raises `BadRequest: BUTTON_DATA_INVALID`.
- **Tests**:
  - `test_menu_expansion.py` tests `get_main_menu_markup()`, `get_settings_markup()`, and ensures maximum 15 buttons per markup.

## 2. Logic Chain
1. *From Observation*: `bot.py` handles `/start` via `Command("start")` and shows both `ReplyKeyboardMarkup` and `InlineKeyboardMarkup`.
2. *Deduction*: Adding `/carreiras` requires registering `@dp.message(Command("carreiras"))` and `@dp.message(F.text == "🎓 Trilha de Carreiras")` before the generic `@dp.message(F.text)` handler at line 1656.
3. *Deduction*: Adding the menu button requires inserting `KeyboardButton(text="🎓 Trilha de Carreiras")` into `ReplyKeyboardMarkup` and `InlineKeyboardButton(text="🎓 Trilha de Carreiras", callback_data="car:main")` into `get_main_menu_markup()`.
4. *From Observation*: Telegram limits `callback_data` to 64 bytes.
5. *Deduction*: Using a compact prefix scheme `car:*` (`car:main`, `car:p:<pid>`, `car:r:<pid>`, `car:t:<pid>:<step>`, `car:j:<pid>`) consumes between 7 and 9 bytes per callback, leaving >50 bytes margin and preventing any runtime Telegram API errors.
6. *From Observation*: `test_menu_expansion.py` validates button count <= 15.
7. *Deduction*: The career path screens (6 buttons max) fit comfortably within the 15-button limit without violating existing test constraints.

## 3. Caveats
- Progress tracking in the proposed snippet uses in-memory dictionary `user_career_progress`. If bot restarts, user checklist toggles reset unless persisted to SQLite table in `database.py`.
- Keywords for career job search (`car:j:<pid>`) invoke `_do_hunt`. Ensure corresponding keywords are mapped in `SEARCH_MAPPING`, `CO_OCCURRENCE_RULES`, and `blacklist` dictionary if strict filtering is enabled.

## 4. Conclusion
The integration design for 'Guia de Profissionalização e Trilha de Carreira' is complete, fully specified, and ready for implementation. It introduces 5 elite professions (Server-Side Tracking, Growth Engineer, Analytics Engineer, IA-Ops, SDR Técnico), provides interactive checklist capabilities, enforces ultra-short `callback_data` (7-9 bytes), and integrates seamlessly into `/start`, `/carreiras`, and main menus without breaking existing job search functionality.

## 5. Verification Method
1. Inspect `analysis.md` for full proposed code snippets, dictionary data, and callback schema.
2. Run pytest suite on menu expansion test to verify baseline compliance:
   `python C:\Users\99196\OneDrive\Documentos\vagas_bot\test_menu_expansion.py`
3. After implementation of proposals, verify `/carreiras` and `"🎓 Trilha de Carreiras"` button trigger `show_carreiras_menu` and that all callback data strings are under 15 bytes.
