# Persistent Career Progress Tracking Database Analysis Report

**Date**: 2026-07-21  
**Author**: Teamwork Explorer (`explorer_carreiras_2`)  
**Target File**: `C:\Users\99196\OneDrive\Documentos\vagas_bot\database.py`  
**DB File**: `C:\Users\99196\OneDrive\Documentos\vagas_bot\jobs.db` (and `jobs_test.db` in test suite)

---

## Executive Summary

This report provides the architecture, database schema design, and Python helper implementation for persistent career progress tracking ("Guia de Profissionalização e Trilha de Carreira"). 

The implementation introduces a dedicated SQLite table `user_career_progress` and four helper functions (`init_career_db()`, `save_user_step_status()`, `get_user_career_progress()`, and `toggle_user_step_status()`). The design strictly enforces:
1. **Complete Data Isolation**: Career progress resides in its own dedicated table and NEVER reads, writes, or modifies job vacancy tables (`jobs`, `applied_jobs`, `ignored_jobs`).
2. **Idempotency**: DDL uses `CREATE TABLE IF NOT EXISTS` and `CREATE INDEX IF NOT EXISTS`. Data persistence uses `UPSERT` (`INSERT ... ON CONFLICT DO UPDATE`).
3. **Thread-Safety & Concurrency**: Leverages `database.py`'s existing connection pool pattern (`get_connection()`) with Write-Ahead Logging (`PRAGMA journal_mode=WAL`) and `timeout=10`.
4. **Test Suite Compatibility**: Seamlessly respects `database.DB_PATH` monkeypatching used in `tests/conftest.py`.

---

## 1. Existing `database.py` Code Analysis

### 1.1 Table Inventory & Schema Assessment
The current `database.py` manages three core tables in SQLite (`jobs.db`):
- `jobs`:
  - Primary Key: `id TEXT`
  - Columns: `title`, `company`, `budget`, `link`, `platform`, `added_at`, `job_type`, `profession`, `level`, `requirements`.
  - Used by scrapers, AI filter, FastAPI backend (`app.py`), and Telegram bot (`bot.py`).
- `applied_jobs`:
  - Primary Key: `link TEXT`
  - Columns: `applied_at TIMESTAMP`.
  - Tracks vacancies to which user applications were submitted.
- `ignored_jobs`:
  - Primary Key: `link TEXT`
  - Columns: `reason TEXT`, `ignored_at TIMESTAMP`.
  - Tracks permanently skipped vacancies.

### 1.2 Connection Management & Thread Safety
- **Connection Factory**: `get_connection()` creates connections on demand with `timeout=10` and enables `WAL` mode (`PRAGMA journal_mode=WAL`).
- **Thread Isolation**: Connections are not stored in global variables or shared across threads. Each helper function opens a fresh connection inside `get_connection()`, executes SQL, commits, and closes it in a `finally:` block.
- **Concurrency**: WAL mode allows concurrent read operations during write transactions. This prevents `sqlite3.OperationalError: database is locked` when Telegram bot callback queries run concurrently with scrapers or web app requests.

---

## 2. Schema Design: `user_career_progress`

### 2.1 Table Structure & Primary Key Strategy
To track a user's progress through certification/specialization steps across 5 elite professions (Server-Side Tracking, Growth Engineer, Analytics Engineer, IA-Ops, SDR Técnico), each record represents the completion state of a specific `(user_id, profession_id, step_id)` triplet.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `user_id` | `TEXT` | `NOT NULL` | Telegram User ID or system User ID (e.g. `'123456789'`). Stored as `TEXT` for universal type safety across Python `int`/`str`. |
| `profession_id` | `TEXT` | `NOT NULL` | Unique identifier for career path (e.g. `'server_side_tracking'`, `'growth_engineer'`, `'analytics_engineer'`, `'ia_ops'`, `'sdr_tecnico'`). |
| `step_id` | `TEXT` | `NOT NULL` | Step or certification slug (e.g. `'gtm_ss'`, `'meta_capi'`, `'stape'`, `'ga4_ss'`). |
| `status` | `INTEGER` | `DEFAULT 0` | Completion status: `0` = pending/uncompleted, `1` = completed. |
| `updated_at` | `TIMESTAMP` | `DEFAULT CURRENT_TIMESTAMP` | Timestamp of last status change. |

**Primary Key**: `PRIMARY KEY (user_id, profession_id, step_id)`  
Guarantees uniqueness per user/profession/step triplet, preventing duplicate records.

**Indexes**:
`CREATE INDEX IF NOT EXISTS idx_user_career_progress_lookup ON user_career_progress (user_id, profession_id);`  
Accelerates lookup queries when fetching all steps of a given profession for a specific user.

### 2.2 DDL Specification
```sql
CREATE TABLE IF NOT EXISTS user_career_progress (
    user_id TEXT NOT NULL,
    profession_id TEXT NOT NULL,
    step_id TEXT NOT NULL,
    status INTEGER DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, profession_id, step_id)
);

CREATE INDEX IF NOT EXISTS idx_user_career_progress_lookup 
ON user_career_progress (user_id, profession_id);
```

---

## 3. Helper Functions Specification & Implementation

### 3.1 `init_career_db()`
Idempotently creates the `user_career_progress` table and lookup index. Safe to invoke multiple times during application initialization.

```python
def init_career_db():
    """Inicializa a tabela user_career_progress no banco de dados de forma idempotente."""
    conn = get_connection()
    try:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS user_career_progress (
                user_id TEXT NOT NULL,
                profession_id TEXT NOT NULL,
                step_id TEXT NOT NULL,
                status INTEGER DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, profession_id, step_id)
            )
        ''')
        c.execute('''
            CREATE INDEX IF NOT EXISTS idx_user_career_progress_lookup 
            ON user_career_progress (user_id, profession_id)
        ''')
        conn.commit()
    finally:
        conn.close()
```

### 3.2 `save_user_step_status(user_id, profession_id, step_id, status=1)`
Saves or updates the completion status for a given step. Employs `UPSERT` logic (`INSERT ... ON CONFLICT DO UPDATE`) to ensure atomic update operations.

```python
def save_user_step_status(user_id, profession_id: str, step_id: str, status: int = 1) -> bool:
    """
    Salva ou atualiza o status de progresso do usuário em uma etapa de carreira.
    Utiliza UPSERT idempotente para evitar duplicação ou violação de chave primária.
    """
    conn = get_connection()
    try:
        c = conn.cursor()
        c.execute('''
            INSERT INTO user_career_progress (user_id, profession_id, step_id, status, updated_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id, profession_id, step_id) DO UPDATE SET
                status = excluded.status,
                updated_at = CURRENT_TIMESTAMP
        ''', (str(user_id), profession_id, step_id, int(status)))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()
```

### 3.3 `get_user_career_progress(user_id, profession_id=None)`
Retrieves progress state for a user.
- If `profession_id` is supplied: returns `{step_id: {"status": int, "updated_at": str}}`.
- If `profession_id` is `None`: returns `{profession_id: {step_id: {"status": int, "updated_at": str}}}`.

```python
def get_user_career_progress(user_id, profession_id: str = None) -> dict:
    """
    Recupera o progresso de carreira do usuário.
    Retorna dicionário mapeando step_id -> {status, updated_at}.
    """
    conn = get_connection()
    try:
        c = conn.cursor()
        if profession_id:
            c.execute('''
                SELECT step_id, status, updated_at
                FROM user_career_progress
                WHERE user_id = ? AND profession_id = ?
            ''', (str(user_id), profession_id))
            rows = c.fetchall()
            return {row[0]: {"status": row[1], "updated_at": row[2]} for row in rows}
        else:
            c.execute('''
                SELECT profession_id, step_id, status, updated_at
                FROM user_career_progress
                WHERE user_id = ?
            ''', (str(user_id),))
            rows = c.fetchall()
            result = {}
            for prof, step, stat, updated in rows:
                if prof not in result:
                    result[prof] = {}
                result[prof][step] = {"status": stat, "updated_at": updated}
            return result
    finally:
        conn.close()
```

### 3.4 `toggle_user_step_status(user_id, profession_id, step_id)`
Helper for Telegram InlineKeyboardButton callbacks. Toggles step status between `0` (uncompleted) and `1` (completed) and returns the new status integer.

```python
def toggle_user_step_status(user_id, profession_id: str, step_id: str) -> int:
    """
    Alterna o status da etapa (0 -> 1 ou 1 -> 0) e salva.
    Retorna o novo status.
    """
    progress = get_user_career_progress(user_id, profession_id)
    current_status = progress.get(step_id, {}).get("status", 0)
    new_status = 0 if current_status == 1 else 1
    save_user_step_status(user_id, profession_id, step_id, new_status)
    return new_status
```

### 3.5 Integration into `init_db()`
`init_db()` should be updated to call `init_career_db()`:

```python
def init_db():
    conn = get_connection()
    try:
        # Existing tables ...
        # ...
        conn.commit()
    finally:
        conn.close()
    
    # Garantir inicialização idempotente da tabela de carreiras
    init_career_db()
```

---

## 4. Idempotency & Data Isolation Verification

### 4.1 Data Isolation Guarantee
- The table `user_career_progress` operates independently.
- No career tracking helper function issues queries against `jobs`, `applied_jobs`, or `ignored_jobs`.
- Job vacancy operations (`insert_jobs`, `get_jobs`, `mark_applied`, `mark_ignored`) remain completely unaltered.

### 4.2 Idempotency Guarantee
- Calling `init_career_db()` or `init_db()` repeatedly will not fail or duplicate data because of `IF NOT EXISTS`.
- Calling `save_user_step_status()` repeatedly with the same parameters updates `updated_at` without throwing duplicate key errors.

### 4.3 Verification Results
Execution of scratch test script verified:
- `init_career_db()` idempotency across multiple runs.
- `save_user_step_status()` inserting and updating rows atomically.
- `toggle_user_step_status()` toggling state seamlessly (0 -> 1 -> 0).
- Automatic database cleanup and zero interference with job tables.

---

## 5. Proposed Diff Patch for `database.py`

```patch
--- database.py
+++ database.py
@@ -49,6 +49,7 @@
         conn.commit()
     finally:
         conn.close()
+    init_career_db()
 
 def insert_jobs(jobs):
     conn = get_connection()
@@ -140,3 +141,83 @@
         conn.commit()
     finally:
         conn.close()
+
+def init_career_db():
+    """Inicializa a tabela user_career_progress no banco de dados de forma idempotente."""
+    conn = get_connection()
+    try:
+        c = conn.cursor()
+        c.execute('''
+            CREATE TABLE IF NOT EXISTS user_career_progress (
+                user_id TEXT NOT NULL,
+                profession_id TEXT NOT NULL,
+                step_id TEXT NOT NULL,
+                status INTEGER DEFAULT 0,
+                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
+                PRIMARY KEY (user_id, profession_id, step_id)
+            )
+        ''')
+        c.execute('''
+            CREATE INDEX IF NOT EXISTS idx_user_career_progress_lookup 
+            ON user_career_progress (user_id, profession_id)
+        ''')
+        conn.commit()
+    finally:
+        conn.close()
+
+def save_user_step_status(user_id, profession_id: str, step_id: str, status: int = 1) -> bool:
+    """
+    Salva ou atualiza o status de progresso do usuário em uma etapa de carreira.
+    """
+    conn = get_connection()
+    try:
+        c = conn.cursor()
+        c.execute('''
+            INSERT INTO user_career_progress (user_id, profession_id, step_id, status, updated_at)
+            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
+            ON CONFLICT(user_id, profession_id, step_id) DO UPDATE SET
+                status = excluded.status,
+                updated_at = CURRENT_TIMESTAMP
+        ''', (str(user_id), profession_id, step_id, int(status)))
+        conn.commit()
+        return True
+    except Exception as e:
+        conn.rollback()
+        raise e
+    finally:
+        conn.close()
+
+def get_user_career_progress(user_id, profession_id: str = None) -> dict:
+    """
+    Recupera o progresso de carreira do usuário.
+    """
+    conn = get_connection()
+    try:
+        c = conn.cursor()
+        if profession_id:
+            c.execute('''
+                SELECT step_id, status, updated_at
+                FROM user_career_progress
+                WHERE user_id = ? AND profession_id = ?
+            ''', (str(user_id), profession_id))
+            rows = c.fetchall()
+            return {row[0]: {"status": row[1], "updated_at": row[2]} for row in rows}
+        else:
+            c.execute('''
+                SELECT profession_id, step_id, status, updated_at
+                FROM user_career_progress
+                WHERE user_id = ?
+            ''', (str(user_id),))
+            rows = c.fetchall()
+            result = {}
+            for prof, step, stat, updated in rows:
+                if prof not in result:
+                    result[prof] = {}
+                result[prof][step] = {"status": stat, "updated_at": updated}
+            return result
+    finally:
+        conn.close()
+
+def toggle_user_step_status(user_id, profession_id: str, step_id: str) -> int:
+    """
+    Alterna o status da etapa (0 -> 1 ou 1 -> 0) e salva.
+    """
+    progress = get_user_career_progress(user_id, profession_id)
+    current_status = progress.get(step_id, {}).get("status", 0)
+    new_status = 0 if current_status == 1 else 1
+    save_user_step_status(user_id, profession_id, step_id, new_status)
+    return new_status
```
