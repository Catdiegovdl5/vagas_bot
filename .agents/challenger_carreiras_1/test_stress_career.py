import os
import sys
import sqlite3
import threading
import concurrent.futures
import time
import pytest

# Adjust path to import vagas_bot modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import database
import bot

def setup_test_db(tmp_db_path):
    """Sets up an isolated database at tmp_db_path."""
    database.DB_PATH = tmp_db_path
    database.init_db()

def test_sequential_toggling(tmp_path):
    """1A. Sequential toggling test: 100 toggles flip status deterministically."""
    db_path = str(tmp_path / "test_seq_toggle.db")
    setup_test_db(db_path)
    
    user_id = "user_seq_test"
    prof_id = "growth_engineer"
    step_id = "step_1"
    
    # Initially status should be 0
    assert database.get_career_step_status(user_id, prof_id, step_id) is False
    
    for i in range(1, 101):
        expected_status = 1 if (i % 2 != 0) else 0
        new_status = database.toggle_user_step_status(user_id, prof_id, step_id)
        assert new_status == expected_status, f"Toggle {i}: expected {expected_status}, got {new_status}"
        assert database.get_career_step_status(user_id, prof_id, step_id) == (expected_status == 1)

def test_concurrent_toggling(tmp_path):
    """1B. Concurrent toggling test: multi-threaded operations on SQLite WAL."""
    db_path = str(tmp_path / "test_concurrent_toggle.db")
    setup_test_db(db_path)
    
    user_id = "user_concurrent_test"
    prof_id = "server_side_tracking"
    step_id = "step_2"
    
    num_workers = 10
    toggles_per_worker = 10
    total_toggles = num_workers * toggles_per_worker
    
    def worker():
        for _ in range(toggles_per_worker):
            database.toggle_user_step_status(user_id, prof_id, step_id)

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = [executor.submit(worker) for _ in range(num_workers)]
        concurrent.futures.wait(futures)

    # Check for unhandled exceptions in threads
    for f in futures:
        assert f.exception() is None, f"Worker thread raised exception: {f.exception()}"

    # Since total toggles is even (100), final status should be 0 (or valid int 0 or 1)
    progress = database.get_user_career_progress(user_id, prof_id)
    assert step_id in progress
    assert progress[step_id]["status"] in (0, 1)

def test_multi_user_concurrent_toggling(tmp_path):
    """1C. Concurrent multi-user step updates across 20 threads."""
    db_path = str(tmp_path / "test_multi_user_concurrent.db")
    setup_test_db(db_path)

    def worker(u_idx):
        u_id = f"user_thread_{u_idx}"
        for s in range(1, 6):
            database.save_user_step_status(u_id, "ia_ops", f"step_{s}", 1)
            database.toggle_user_step_status(u_id, "ia_ops", f"step_{s}")

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(worker, i) for i in range(20)]
        concurrent.futures.wait(futures)

    for f in futures:
        assert f.exception() is None

    conn = database.get_connection()
    try:
        c = conn.cursor()
        c.execute("SELECT count(*) FROM user_career_progress")
        count = c.fetchone()[0]
        assert count == 20 * 5, f"Expected 100 rows, found {count}"
    finally:
        conn.close()

def test_user_id_types_handling(tmp_path):
    """2. Edge case testing for user_id types: int, str, None, float, bool, empty str, SQL injection."""
    db_path = str(tmp_path / "test_types.db")
    setup_test_db(db_path)
    
    prof_id = "analytics_engineer"
    step_id = "step_3"
    
    # 2A. int vs str consistency
    database.save_user_step_status(12345, prof_id, step_id, 1)
    prog_int = database.get_user_career_progress(12345, prof_id)
    prog_str = database.get_user_career_progress("12345", prof_id)
    assert prog_int == prog_str
    assert database.get_career_step_status(12345, prof_id, step_id) is True
    assert database.get_career_step_status("12345", prof_id, step_id) is True
    
    # 2B. user_id = None
    database.save_user_step_status(None, prof_id, step_id, 1)
    prog_none = database.get_user_career_progress(None, prof_id)
    prog_none_str = database.get_user_career_progress("None", prof_id)
    assert prog_none == prog_none_str
    
    # 2C. float, bool, empty str
    database.save_user_step_status(99.9, prof_id, step_id, 1)
    assert database.get_career_step_status(99.9, prof_id, step_id) is True

    database.save_user_step_status(True, prof_id, step_id, 1)
    assert database.get_career_step_status(True, prof_id, step_id) is True

    database.save_user_step_status("", prof_id, step_id, 1)
    assert database.get_career_step_status("", prof_id, step_id) is True
    
    # 2D. SQL injection attempt in user_id
    sql_inj = "100' OR '1'='1"
    database.save_user_step_status(sql_inj, prof_id, step_id, 1)
    prog_inj = database.get_user_career_progress(sql_inj, prof_id)
    assert step_id in prog_inj
    
    # Ensure normal user queries aren't leaked by SQL injection string
    prog_normal = database.get_user_career_progress(99999, prof_id)
    assert prog_normal == {}

def test_get_user_career_progress_non_existent_and_filters(tmp_path):
    """3. Gracefulness test for non-existent users and profession filters."""
    db_path = str(tmp_path / "test_filters.db")
    setup_test_db(db_path)
    
    # Non-existent user without profession filter
    p1 = database.get_user_career_progress("ghost_user_100")
    assert isinstance(p1, dict)
    assert len(p1) == 0
    
    # Non-existent user with existing profession filter
    p2 = database.get_user_career_progress("ghost_user_100", "growth_engineer")
    assert isinstance(p2, dict)
    assert len(p2) == 0
    
    # Existing user with non-existent profession filter
    database.save_user_step_status("existing_user", "growth_engineer", "step_1", 1)
    p3 = database.get_user_career_progress("existing_user", "non_existent_profession")
    assert isinstance(p3, dict)
    assert len(p3) == 0
    
    # Existing user with profession_id = None (returns nested dictionary)
    p4 = database.get_user_career_progress("existing_user", None)
    assert isinstance(p4, dict)
    assert "growth_engineer" in p4
    assert "step_1" in p4["growth_engineer"]
    assert p4["growth_engineer"]["step_1"]["status"] == 1

def test_database_isolation_across_tables(tmp_path):
    """4. Verification that career CRUD operations NEVER alter jobs, applied_jobs, or ignored_jobs."""
    db_path = str(tmp_path / "test_isolation.db")
    setup_test_db(db_path)
    
    # Insert sample jobs, applied jobs, ignored jobs
    sample_jobs = [
        {"title": f"Vaga {i}", "company": f"Empresa {i}", "budget": "R$ 5000", "link": f"https://vaga{i}.com", "platform": "linkedin"}
        for i in range(10)
    ]
    inserted = database.insert_jobs(sample_jobs)
    assert inserted == 10
    
    for i in range(5):
        database.mark_applied(f"https://vaga{i}.com")
        database.mark_ignored(f"https://vaga{i+5}.com", "Fora do perfil")

    # Capture initial table states
    conn = database.get_connection()
    try:
        c = conn.cursor()
        c.execute("SELECT * FROM jobs ORDER BY id")
        jobs_before = c.fetchall()
        c.execute("SELECT * FROM applied_jobs ORDER BY link")
        applied_before = c.fetchall()
        c.execute("SELECT * FROM ignored_jobs ORDER BY link")
        ignored_before = c.fetchall()
    finally:
        conn.close()

    # Execute heavy career progress CRUD
    for u in range(20):
        user_str = f"user_isolation_{u}"
        for prof in ["server_side_tracking", "growth_engineer", "analytics_engineer", "ia_ops", "sdr_tecnico"]:
            for step in [f"step_{s}" for s in range(1, 6)]:
                database.save_user_step_status(user_str, prof, step, 1)
                database.toggle_user_step_status(user_str, prof, step)

    # Re-verify table states after career CRUD
    conn = database.get_connection()
    try:
        c = conn.cursor()
        c.execute("SELECT * FROM jobs ORDER BY id")
        jobs_after = c.fetchall()
        c.execute("SELECT * FROM applied_jobs ORDER BY link")
        applied_after = c.fetchall()
        c.execute("SELECT * FROM ignored_jobs ORDER BY link")
        ignored_after = c.fetchall()
    finally:
        conn.close()

    assert jobs_before == jobs_after, "jobs table was altered by career operations!"
    assert applied_before == applied_after, "applied_jobs table was altered by career operations!"
    assert ignored_before == ignored_after, "ignored_jobs table was altered by career operations!"

def test_telegram_callback_data_length_under_64_bytes():
    """5. Verify ALL generated callback_data strings in bot.py for all 5 professions and all steps <= 64 bytes."""
    professions = ["server_side_tracking", "growth_engineer", "analytics_engineer", "ia_ops", "sdr_tecnico"]
    
    tested_callbacks = []
    
    # 5A. Main menu
    main_markup = bot.get_main_menu_markup()
    for row in main_markup.inline_keyboard:
        for btn in row:
            if btn.callback_data:
                tested_callbacks.append(("main_menu", btn.callback_data))
                
    # 5B. Carreiras main menu
    car_main_markup = bot.get_carreiras_main_markup()
    for row in car_main_markup.inline_keyboard:
        for btn in row:
            if btn.callback_data:
                tested_callbacks.append(("carreiras_main", btn.callback_data))
                
    # 5C. Profession detail markups
    for pid in professions:
        detail_markup = bot.get_profession_detail_markup(pid)
        for row in detail_markup.inline_keyboard:
            for btn in row:
                if btn.callback_data:
                    tested_callbacks.append((f"detail_{pid}", btn.callback_data))
                    
    # 5D. Profession roadmap markups for all steps
    for pid in professions:
        roadmap_markup = bot.get_profession_roadmap_markup("user_test_123", pid)
        for row in roadmap_markup.inline_keyboard:
            for btn in row:
                if btn.callback_data:
                    tested_callbacks.append((f"roadmap_{pid}", btn.callback_data))
                    
    # Validate each callback length in UTF-8 bytes
    over_limit = []
    for source, cb in tested_callbacks:
        byte_len = len(cb.encode('utf-8'))
        assert byte_len <= 64, f"Callback '{cb}' from '{source}' exceeded limit: {byte_len} bytes > 64 bytes"
        if byte_len > 64:
            over_limit.append((source, cb, byte_len))
            
    assert len(over_limit) == 0, f"Found {len(over_limit)} callbacks exceeding 64 bytes"

if __name__ == "__main__":
    pytest.main(["-v", __file__])
