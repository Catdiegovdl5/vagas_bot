# Investigation Report: vagas_bot Enhancements

## Summary of Core Findings
1. **Settings Menu**: Stored in a global, volatile in-memory dictionary (`user_settings_db`) in `bot.py` and resets on reload. A toggle for `"🛡️ Escudo PT-BR"` can be implemented by adding an `"escudo_ptbr"` key to the dictionary, rendering a button in the configuration markup, and handling the callback to toggle its boolean state.
2. **Language Shield**: Implemented directly in the search flow of `bot.py` (via `langdetect.detect` on the job requirements). It can be bypassed if the settings value for `"escudo_ptbr"` is toggled off, avoiding the gringo job cleanup stage.
3. **Workana Scraper**: Employs `curl_cffi` to extract embedded Vue.js data from a `<search>` tag's `:results-initials` attribute. Currently loops pages `[1, 2]`; pagination can be scaled dynamically using a customizable loop with conditions to stop on empty results, and delays can be introduced via thread-safe `time.sleep` intervals between requests.
4. **Candidate Status & DB**: Utilizes a SQLite table `applied_jobs` in `jobs.db` to store candidate applications via job URLs (`link` column). The bot queries `is_applied(link)` to render the appropriate button and updates the database asynchronously using `mark_applied(link)` via a callback handler.

---

## 1. Telegram Bot Settings Menu

### Current Architecture
- **In-Memory Store**: Settings are stored in the global dictionary `user_settings_db` (`bot.py:101`).
- **Initial Configuration**: Populated on first demand via `get_user_settings(chat_id)` (`bot.py:103`) which clones `DEFAULT_SETTINGS` (`bot.py:74-99`) using deep-copy logic.
- **Persistence**: Purely transient in-memory. If the bot is restarted, all user settings revert to their default states.

### Important Code Locations
| File Path | Lines | Purpose |
|---|---|---|
| `bot.py` | `74 - 99` | Definition of `DEFAULT_SETTINGS` dictionary structure. |
| `bot.py` | `101 - 107` | In-memory database dictionary (`user_settings_db`) and utility `get_user_settings(chat_id)`. |
| `bot.py` | `155 - 173` | UI construction inside `get_settings_markup(chat_id)` defining inline buttons. |
| `bot.py` | `175 - 260` | Specific inline callback handlers modifying settings fields (`location`, `level`, `contract`, `platforms`, etc.) and updating views. |

### Proposed Implementation: 🛡️ Escudo PT-BR Toggle Button

To add a toggle button `"🛡️ Escudo PT-BR: ON/OFF"`, the following modifications are suggested:

#### A. Add key to `DEFAULT_SETTINGS` in `bot.py` (near Line 98):
```python
DEFAULT_SETTINGS = {
    "level": "Todos",
    "location": "Brasil (Remoto)",
    "contract": "Todos", # Todos, PJ, CLT, Freelancer
    "education": "Todos", # Todos, Sem Formação
    "platforms": {
        # ... (platform configurations)
    },
    "ai_filter": True,
    "escudo_ptbr": True  # New key: defaults to True (ON)
}
```

#### B. Display the button in `get_settings_markup(chat_id)` in `bot.py` (near Line 171):
```python
def get_settings_markup(chat_id):
    settings = get_user_settings(chat_id)
    p = settings["platforms"]
    return InlineKeyboardMarkup(inline_keyboard=[
        # ... (existing buttons)
        [InlineKeyboardButton(text=f"📧 Gmail Alertas: {'✅ ON' if p['gmail'] else '❌ OFF'}", callback_data="toggle_gmail")],
        [InlineKeyboardButton(text=f"🛡️ Escudo PT-BR: {'✅ ON' if settings.get('escudo_ptbr', True) else '❌ OFF'}", callback_data="toggle_escudo_ptbr")],
        [InlineKeyboardButton(text="🔙 Voltar ao Início", callback_data="main_menu")]
    ])
```

#### C. Handle callback trigger for `"toggle_escudo_ptbr"` in `bot.py` (near Line 260):
```python
@dp.callback_query(F.data == "toggle_escudo_ptbr")
async def toggle_escudo_ptbr(callback: CallbackQuery):
    await callback.answer()
    chat_id = callback.message.chat.id
    settings = get_user_settings(chat_id)
    settings["escudo_ptbr"] = not settings.get("escudo_ptbr", True)
    await callback.message.edit_reply_markup(reply_markup=get_settings_markup(chat_id))
```

---

## 2. Language Detection & Shield Filter

### Current Implementation
- **Mechanism**: The bot relies on the `langdetect` library to analyze job requirements texts.
- **Language Detection Logic** (`bot.py:1129-1134`):
  ```python
  def is_brazilian_job(text):
      try:
          if len(text) < 20: return True
          return detect(text) == 'pt'
      except:
          return True
  ```
- **Filter logic** (`bot.py:1137-1144`):
  Runs a brutal pre-filter loop where a job is retained (`vagas_br`) only if its platform is recognized as a freelance platform (e.g. Workana, 99Freelas, Freelancer) **OR** if `is_brazilian_job(requirements)` returns `True`. If neither is true, the job is classified as a "gringo job" and deleted from the collection.

### Proposed Bypass Implementation
To honor the setting `"escudo_ptbr"`, we read the boolean state and conditionalize the entire cleaning mechanism.

#### Modified code in `bot.py` (near Line 1126):
```python
    # Check if Escudo PT-BR is enabled
    escudo_enabled = settings.get("escudo_ptbr", True)
    
    if escudo_enabled:
        await message.answer(f"🛡️ *Escudo PT-BR Ativado!*\nLimpando vagas gringas antes do processamento final...", parse_mode="Markdown")
        from langdetect import detect
        
        def is_brazilian_job(text):
            try:
                if len(text) < 20: return True
                return detect(text) == 'pt'
            except:
                return True
                
        # Pré-filtro brutal: Se não for PT-BR E não for plataforma freelance, lixo.
        vagas_br = []
        for job in all_jobs:
            plat_lower = job.get('platform', '').lower()
            is_freela_plat = any(p in plat_lower for p in ['workana', '99freelas', 'freelancer'])
            
            # Passa direto se for freelance, ou se for PT-BR
            if is_freela_plat or is_brazilian_job(job.get('requirements', '')):
                vagas_br.append(job)
                
        if len(vagas_br) < len(all_jobs):
            await message.answer(f"🗑️ *Limpeza concluída:* {len(all_jobs) - len(vagas_br)} vagas gringas foram deletadas!", parse_mode="Markdown")
    else:
        # Bypassed: keep all jobs regardless of language
        vagas_br = all_jobs
```

---

## 3. Workana Scraper: Implementation, Pagination & Delays

### Current Implementation
- **File**: `scrapers/workana.py`
- **Requesting**: Employs `curl_cffi` (impersonating `chrome110`) or falls back to `requests` to fetch HTML.
- **Parsing**: Workana is a Vue.js application. Initial search results are stored inside a `<search>` tag's `:results-initials` attribute, which contains a JSON string of jobs. This is parsed via `BeautifulSoup` and loaded using `json.loads`.
- **Iteration Range**: Hardcoded loop `for page in [1, 2]:` (maximum 2 pages).
- **Cap limit**: Hardcoded termination if `len(jobs) >= 30`.
- **Rate limiting/Delays**: No delays are currently implemented between page requests.

### Proposed Enhancements: Dynamic Pagination & Delay Control
Since the scraper executes inside `asyncio.to_thread` from `bot.py:1046`, using standard synchronous delays (`time.sleep`) is perfectly safe. It blocks only the worker thread and does not block the main event loop.

#### Implementation Proposal in `scrapers/workana.py` (Line 10):
```python
import time
import random

def scrape(keyword="Python", level="Todos", max_pages=5, max_jobs=50):
    jobs = []
    try:
        search_kw = keyword
        if level != "Todos": search_kw += f" {level}"
        search_kw = urllib.parse.quote(search_kw)
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'Accept-Language': 'pt-BR,pt;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        }
        
        for page in range(1, max_pages + 1):
            if len(jobs) >= max_jobs:
                break
                
            # Introduce delay to prevent HTTP 429 rate limit errors (only between page calls)
            if page > 1:
                time.sleep(random.uniform(2.0, 4.5))
                
            url = f"https://www.workana.com/jobs?query={search_kw}&page={page}"
            
            r = None
            if requests_cffi:
                try:
                    r = requests_cffi.get(url, headers=headers, impersonate="chrome110", timeout=15)
                except Exception:
                    r = None
            if r is None:
                import requests
                r = requests.get(url, headers=headers, timeout=15)
                
            if r.status_code == 429:
                print("Erro 429 na Workana. Abortando paginação.")
                break
                
            soup = BeautifulSoup(r.text, 'html.parser')
            
            search_tag = soup.find('search')
            if not search_tag or not search_tag.has_attr(':results-initials'):
                break  # Stop pagination if Vue container tag is missing
                
            data = json.loads(search_tag[':results-initials'])
            results = data.get('results', [])
            
            if not results:
                break  # Stop pagination if page returns empty results
                
            for item in results:
                if len(jobs) >= max_jobs:
                    break
                
                # ... (existing item extracting and appending code)
```

---

## 4. Job Candidate Checking and "✅ Já me candidatei" Button

### DB Schema and Queries

The persistence logic and SQL queries reside inside `database.py`.

#### A. Database Schema
- **File**: `jobs.db` (SQLite)
- **Table Definition** (`database.py:35-40`):
  ```sql
  CREATE TABLE IF NOT EXISTS applied_jobs (
      link TEXT PRIMARY KEY,
      applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  )
  ```
  The unique job URL (`link`) is stored as the Primary Key.

#### B. SQL Queries/Functions
- **Check Status** (`database.py:99-107`):
  ```python
  def is_applied(link: str) -> bool:
      conn = get_connection()
      try:
          c = conn.cursor()
          c.execute('SELECT 1 FROM applied_jobs WHERE link = ?', (link,))
          return c.fetchone() is not None
      finally:
          conn.close()
  ```
- **Update Status** (`database.py:109-117`):
  ```python
  def mark_applied(link: str):
      conn = get_connection()
      try:
          c = conn.cursor()
          c.execute('INSERT OR IGNORE INTO applied_jobs (link) VALUES (?)', (link,))
          conn.commit()
      finally:
          conn.close()
  ```

---

### Telegram UI Integration & Callback Flow

1. **Checking & Rendering Buttons during Search Loop** (`bot.py:1196-1208`):
   As each job is iterated over, the bot calls `is_applied` inside a background thread:
   ```python
   # Verifica se já se candidatou
   already_applied = await asyncio.to_thread(is_applied, link)
   
   # Botões de ação
   if already_applied:
       buttons = [
           [InlineKeyboardButton(text="✅ Já me Candidatei", callback_data="noop_applied")],
           [InlineKeyboardButton(text="🔗 Ver Vaga Novamente", url=link)]
       ]
   else:
       buttons = [
           [InlineKeyboardButton(text="🎯 Aplicar para a Vaga", url=link)],
           [InlineKeyboardButton(text="✋ Já me Candidatei", callback_data=f"mark_applied_{link}")]
       ]
   ```

2. **Triggering Status Update via Callback Query** (`bot.py:397-419`):
   When a user clicks the "✋ Já me Candidatei" button, the bot processes the callback query:
   ```python
   @dp.callback_query(F.data.startswith("mark_applied_"))
   async def handle_mark_applied(callback: CallbackQuery):
       """Marca a vaga como candidatada e atualiza o botão."""
       link = callback.data.replace("mark_applied_", "", 1)
       await asyncio.to_thread(mark_applied, link)
       await callback.answer("✅ Marcado como candidatado!", show_alert=False)
       
       # Modifies the buttons dynamically to avoid sending a new message
       try:
           old_markup = callback.message.reply_markup
           new_rows = []
           for row in old_markup.inline_keyboard:
               new_row = []
               for btn in row:
                   if btn.callback_data and btn.callback_data.startswith("mark_applied_"):
                       new_row.append(InlineKeyboardButton(text="✅ Já me Candidatei", callback_data="noop_applied"))
                   else:
                       new_row.append(btn)
               new_rows.append(new_row)
           await callback.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(inline_keyboard=new_rows))
       except Exception:
           pass
   ```
   *Note: Re-rendering inline keybuttons with `noop_applied` prevents the user from clicking the mark button multiple times.*
