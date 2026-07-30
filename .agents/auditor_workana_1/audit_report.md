## Forensic Audit Report

**Work Product**: `bot.py`, `scrapers/workana.py`, and `tests/test_workana_settings.py`
**Profile**: General Project
**Verdict**: CLEAN

### Phase Results

#### Phase 1: Source Code Analysis
- **Hardcoded test results**: PASS — No hardcoded test results, expected outputs, or bypasses were found in the source code of `scrapers/workana.py` or `bot.py`.
- **Facade implementations**: PASS — The pagination loop, random delays, status code handling (such as HTTP 429), and BeautifulSoup selector logic in `scrapers/workana.py` are dynamically implemented. The settings toggle and language shield (`escudo_ptbr`) in `bot.py` represent actual memory manipulation and runtime filtering using `langdetect`. The auto-apply bypass checks for previous applications via a database lookup (`is_applied`) and prevents repeated attempts correctly.
- **Pre-populated artifact detection**: PASS — No fabricated logs, verification files, or pre-calculated outputs are present in the test suite directory. All test cases execute live, dynamically mock only standard library interfaces (such as HTTP requests and sleep duration), and execute actual functional code.

#### Phase 2: Behavioral Verification
- **Build and run**: PASS — The test suite was executed locally using `python -m pytest tests/test_workana_settings.py` and completed successfully with all 4 tests passing.
- **Output verification**: PASS — Verified that mock responses and settings changes lead to the correct internal state changes and filtering behavior, matching the required specifications.
- **Dependency audit**: PASS — Third-party library usage (e.g., `requests`, `bs4`, `langdetect`) is standard and appropriate for scraping, database storage, and Telegram event handling. No core functionality is delegated to external black-box precompiled binaries.

---

### Evidence

#### 1. Pytest Output
```
============================= test session starts =============================
platform win32 -- Python 3.14.5, pytest-9.0.3, pluggy-1.6.0
rootdir: C:\Users\99196\OneDrive\Documentos\vagas_bot
plugins: anyio-4.13.0, Flask-Dance-7.1.0, asyncio-1.4.0, mock-3.15.1
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 4 items

tests\test_workana_settings.py ....                                      [100%]

============================== warnings summary ===============================
..\..\..\AppData\Roaming\Python\Python314\site-packages\PyPDF2\__init__.py:21
  C:\Users\99196\AppData\Roaming\Python\Python314\site-packages\PyPDF2\__init__.py:21: DeprecationWarning: PyPDF2 is deprecated. Please move to the pypdf library instead.
    warnings.warn(

tests/test_workana_settings.py::test_escudo_ptbr_toggle_changes_setting_in_memory
  C:\Users\99196\AppData\Roaming\Python\Python314\site-packages\websockets\legacy\__init__.py:6: DeprecationWarning: websockets.legacy is deprecated; see https://websockets.readthedocs.io/en/stable/howto/upgrade.html for upgrade instructions
    warnings.warn(  # deprecated in 14.0 - 2024-11-09

tests/test_workana_settings.py::test_escudo_ptbr_toggle_changes_setting_in_memory
  C:\Users\99196\AppData\Roaming\Python\Python314\site-packages\uvicorn\protocols\websockets\websockets_impl.py:17: DeprecationWarning: websockets.server.WebSocketServerProtocol is deprecated
    from websockets.server import WebSocketServerProtocol

tests/test_workana_settings.py::test_escudo_ptbr_toggle_changes_setting_in_memory
  C:\Users\99196\AppData\Roaming\Python\Python314\site-packages\_pytest\threadexception.py:58: PytestUnhandledThreadExceptionWarning: Exception in thread Thread-1 (run)
  
  Traceback (most recent call last):
    File "C:\Users\99196\AppData\Roaming\Python\Python314\site-packages\uvicorn\server.py", line 172, in startup
      server = await loop.create_server(
               ^^^^^^^^^^^^^^^^^^^^^^^^^
      ...<5 lines>...
      )
      ^
    File "C:\Python314\Lib\asyncio\base_events.py", line 1638, in create_server
      raise OSError(err.errno, msg) from None
  OSError: [Errno 10048] error while attempting to bind on address ('127.0.0.1', 8081): [winerror 10048] normalmente é permitida apenas uma utilização de cada endereço de soquete (protocolo/endereço de rede/porta)
  
  During handling of the above exception, another exception occurred:
  
  Traceback (most recent call last):
    File "C:\Python314\Lib\threading.py", line 1082, in _bootstrap_inner
      self._context.run(self.run)
      ~~~~~~~~~~~~~~~~~^^^^^^^^^^
    File "C:\Python314\Lib\threading.py", line 1024, in run
      self._target(*self._args, **self._kwargs)
      ~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    File "C:\Users\99196\AppData\Roaming\Python\Python314\site-packages\uvicorn\server.py", line 75, in run
      return asyncio_run(self.serve(sockets=sockets), loop_factory=self.config.get_loop_factory())
    File "C:\Python314\Lib\asyncio\runners.py", line 204, in run
      return runner.run(main)
             ~~~~~~~~~~^^^^^^
    File "C:\Python314\Lib\asyncio\runners.py", line 127, in run
      return self._loop.run_until_complete(task)
             ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^
    File "C:\Python314\Lib\asyncio\base_events.py", line 706, in run_until_complete
      self.run_forever()
      ~~~~~~~~~~~~~~~~^^
    File "C:\Python314\Lib\asyncio\base_events.py", line 677, in run_forever
      self._run_once()
      ~~~~~~~~~~~~~~^^
    File "C:\Python314\Lib\asyncio\base_events.py", line 2057, in _run_once
      handle._run()
      ~~~~~~~~~~~^^
    File "C:\Python314\Lib\asyncio\events.py", line 94, in _run
      self._context.run(self._callback, *self._args)
      ~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    File "C:\Users\99196\AppData\Roaming\Python\Python314\site-packages\uvicorn\server.py", line 79, in serve
      await self._serve(sockets)
    File "C:\Users\99196\AppData\Roaming\Python\Python314\site-packages\uvicorn\server.py", line 94, in _serve
      await self.startup(sockets=sockets)
    File "C:\Users\99196\AppData\Roaming\Python\Python314\site-packages\uvicorn\server.py", line 182, in startup
      sys.exit(1)
      ~~~~~~~~^^^
  SystemExit: 1

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
======================== 4 passed, 4 warnings in 8.06s ========================
```

#### 2. Key Code Snippets Inspected

- **Workana Pagination Loop (`scrapers/workana.py:25-45`):**
  ```python
  for page in range(1, max_pages + 1):
      if len(jobs) >= 30:
          break
          
      if page > 1:
          time.sleep(random.uniform(2.0, 4.5))
          
      url = f"https://www.workana.com/jobs?query={search_kw}&page={page}"
      ...
      if r is not None and r.status_code == 429:
          break
  ```

- **Escudo PT-BR Toggle Handler (`bot.py:254-260`):**
  ```python
  @dp.callback_query(F.data == "toggle_escudo_ptbr")
  async def toggle_escudo_ptbr(callback: CallbackQuery):
      await callback.answer()
      chat_id = callback.message.chat.id
      settings = get_user_settings(chat_id)
      settings["escudo_ptbr"] = not settings.get("escudo_ptbr", True)
      await callback.message.edit_reply_markup(reply_markup=get_settings_markup(chat_id))
  ```

- **Auto-Apply Bypass Logic (`bot.py:1210-1216`):**
  ```python
  # Verifica se já se candidatou
  already_applied = await asyncio.to_thread(is_applied, link)
  if already_applied:
      apply_result = {}
  else:
      # Tenta Auto-Apply silenciosamente
      apply_result = await asyncio.to_thread(auto_apply.auto_apply, job, str(chat_id))
  ```
