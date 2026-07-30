# Handoff Report — Workana Scraper Integration Analysis

This report documents the findings regarding how the Workana scraper interacts with the main bot.py, identifying workflow steps, keyword mappings, expansion logic, status database queries, and an observed integration gap.

## 1. Observation

### Scraper Invocation & Execution Cycle
- `bot.py` line 71: Defines `FREELANCE_PLATFORMS = ["workana"]`
- `bot.py` line 2198: Imports the scraper dynamically using `module = importlib.import_module(f"scrapers.{plat}")` where `plat` is `"workana"`.
- `bot.py` line 2204: Invokes the scraper inside `asyncio.to_thread`:
  ```python
  res = await asyncio.to_thread(module.scrape, keyword=plat_search_keyword, level="Todos")
  ```
- `bot.py` line 2223: Gathers scraper executions concurrently:
  ```python
  results = await asyncio.gather(*(fetch_plat(p) for p in active_plats))
  ```

### CO_OCCURRENCE_RULES
- `bot.py` lines 611-612: Defines `CO_OCCURRENCE_RULES` with entries such as:
  ```python
  CO_OCCURRENCE_RULES = {
      "especialista em ia": [
          [
              "ia", "ai", "inteligencia artificial", ...
          ],
          [
              "especialista", "consultor", ...
          ]
      ],
      ...
  }
  ```
- `bot.py` line 1883: Defines relevance check function:
  ```python
  def check_co_occurrence(text_norm, kw_norm, job=None):
      if kw_norm in CO_OCCURRENCE_RULES:
          ...
  ```

### Keyword Mapping & Scraper Expansion
- `bot.py` lines 2064-2066: Defines the search keywords map:
  ```python
  search_mapping = {
      "Especialista em IA": "Especialista IA",
      ...
  }
  ```
- `bot.py` lines 2192-2196: Selects query keyword based on whether the platform is freelance:
  ```python
  is_freelance = plat in ['workana', '99freelas', 'freelancer']
  plat_search_keyword = base_keyword
  if actual_level != "Todos" and not is_freelance:
      plat_search_keyword = f"{base_keyword} {actual_level}"
  ```
- `scrapers/workana.py` lines 15-24:
  ```python
  import bot
  import unicodedata
  kw_norm = "".join(c for c in unicodedata.normalize('NFKD', keyword) if unicodedata.category(c) != 'Mn').lower()
  search_kw = keyword
  
  if kw_norm in bot.CO_OCCURRENCE_RULES:
      # Pegar os 2 primeiros termos do Grupo A (ex: "ia", "ai" ou "python", "django")
      grupo_a = bot.CO_OCCURRENCE_RULES[kw_norm][0]
      termos = grupo_a[:2]
      search_kw = " ".join(termos)
  ```

### Candidate/Applied Status Handling
- `database.py` lines 36-40:
  ```python
  c.execute('''
      CREATE TABLE IF NOT EXISTS applied_jobs (
          link TEXT PRIMARY KEY,
          applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
  ''')
  ```
- `database.py` lines 99-107:
  ```python
  def is_applied(link: str) -> bool:
      """Retorna True se o usuário já se candidatou a essa vaga."""
      conn = get_connection()
      try:
          c = conn.cursor()
          c.execute('SELECT 1 FROM applied_jobs WHERE link = ?', (link,))
          return c.fetchone() is not None
      finally:
          conn.close()
  ```
- `database.py` lines 109-117:
  ```python
  def mark_applied(link: str):
      """Marca uma vaga como 'já candidatado'."""
      conn = get_connection()
      try:
          c = conn.cursor()
          c.execute('INSERT OR IGNORE INTO applied_jobs (link) VALUES (?)', (link,))
          conn.commit()
      ...
  ```
- `bot.py` lines 2353-2358:
  ```python
  already_applied = await asyncio.to_thread(is_applied, link)
  if already_applied:
      apply_result = {}
  else:
      apply_result = await asyncio.to_thread(auto_apply.auto_apply, job, str(chat_id))
  ```
- `bot.py` lines 2368-2377: Renders UI buttons differently depending on `already_applied`:
  - If `already_applied`: Buttons are `✅ Já me Candidatei` (inactive) and `🔗 Ver Vaga Novamente` (url).
  - If not: Buttons are `🎯 Aplicar para a Vaga` (url) and `✋ Já me Candidatei` (triggers manual callback).
- `bot.py` lines 413-429: Manual callback handler inserts link into `applied_jobs`:
  ```python
  @dp.callback_query(F.data == "mark_applied_btn")
  async def handle_mark_applied(callback: CallbackQuery):
      ...
      await asyncio.to_thread(mark_applied, link)
      await callback.answer("✅ Marcado como candidatado!", show_alert=False)
      # Edits buttons inline markup to show "✅ Já me Candidatei"
  ```

---

## 2. Logic Chain

1. **Scraper Execution**: Based on dynamic imports using `importlib` and concurrent execution inside `asyncio.to_thread` wrappers (under `_do_hunt` -> `fetch_plat` -> `module.scrape`), we deduce that scrapers are designed as blocking functions and execute concurrently across platforms without stalling the Telegram bot's event loop.
2. **Keyword Omission**: By checking `plat in ['workana', '99freelas', 'freelancer']` to determine `is_freelance`, `bot.py` ensures that seniority levels are not appended (e.g. `"Especialista IA Sênior"`) to queries targeting freelance platforms. This is done to prevent overly narrow queries on boards with small volumes.
3. **Keyword Expansion Mismatch (Integration Gap)**:
   - In `bot.py`, search keywords from user menus (e.g., `"Especialista em IA"`) map to simplified queries via `search_mapping` (e.g., `"Especialista IA"`).
   - The value `plat_search_keyword = "Especialista IA"` is sent to `workana.py`'s `scrape(keyword=...)`.
   - `workana.py` checks `kw_norm = "especialista ia"` against `bot.CO_OCCURRENCE_RULES`.
   - However, the key inside `bot.CO_OCCURRENCE_RULES` is `"especialista em ia"` (with the preposition `"em"`).
   - Because of this string mismatch, the dictionary lookup fails. This prevents the keyword from expanding to the first two terms of Group A (e.g. `"ia ai"`) inside the scraper, resulting in querying Workana for the raw, unexpanded string `"Especialista IA"`.
   - This occurs for multiple niches (e.g. `"Especialista em IA"`, `"Engenheiro de IA"`, `"Desenvolvedor de Agentes IA"`, `"Analista de Power BI"`, `"Analista de Analytics"`, `"Analista de Marketing Digital"`, `"Especialista em SEO"`, `"Analista de CRM"`, and `"Analista de RH"`).
4. **Status Verification**: By checking SQLite database table `applied_jobs` using `is_applied` and updating it with `mark_applied` (either automatically upon successful `auto_apply` or manually via a Telegram message callback query trigger `mark_applied_btn`), the bot prevents duplicate application attempts and reflects the user's progress dynamically on the Telegram UI.

---

## 3. Caveats
- No code was modified in this analysis (read-only mode strictly enforced).
- The actual behavior of the Workana site (such as dynamic Vue.js payloads parsing) was not validated live due to the CODE_ONLY network restriction constraint. We assumed the parser logic in `workana.py` is currently functional.

---

## 4. Conclusion
The Workana scraper is tightly integrated into the bot's concurrent execution cycle. However, a mapping mismatch exists between `search_mapping` and `CO_OCCURRENCE_RULES` for several niches, preventing the scraper from leveraging Group A keyword expansions on the Workana search queries. The candidate and applied status handling is robustly handled via sqlite3 queries to `jobs.db` (`applied_jobs` table) with concurrent/background safety achieved using WAL journal mode.

---

## 5. Verification Method
- **Files to Inspect**:
  - `bot.py` (for `search_mapping`, `CO_OCCURRENCE_RULES`, and dynamic import in `_do_hunt`)
  - `scrapers/workana.py` (for the lookup `kw_norm in bot.CO_OCCURRENCE_RULES`)
  - `database.py` (for schema and SQL logic querying `applied_jobs`)
- **Test execution**:
  - Run the test suite: `pytest tests/test_workana_settings.py` to ensure settings and toggle integrations behave correctly.
- **Invalidation Condition**: If `bot.CO_OCCURRENCE_RULES` is refactored to align directly with mapped search query values, the keyword expansion lookup gap will disappear.
