import os
import sqlite3
import pytest
import sys

# Set up test DB path
TEST_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tests", "jobs_test.db")

# Mock database.DB_PATH
import database
database.DB_PATH = TEST_DB_PATH

# Initialize DB
database.init_db()

# Add missing columns
conn = sqlite3.connect(TEST_DB_PATH)
c = conn.cursor()
cols = [
    ("score", "INTEGER"),
    ("status", "TEXT"),
    ("reason", "TEXT")
]
for col_name, col_type in cols:
    try:
        c.execute(f"ALTER TABLE jobs ADD COLUMN {col_name} {col_type}")
    except sqlite3.OperationalError:
        pass
try:
    c.execute("DELETE FROM jobs")
except Exception:
    pass
conn.commit()
conn.close()

# Import auto_apply
import auto_apply as aa

print("Inserting test job...")
conn = sqlite3.connect(TEST_DB_PATH)
c = conn.cursor()
c.execute(
    "INSERT INTO jobs (id, title, company, budget, link, platform, requirements, score, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
    ("https://example.com/job/fail-test", "Python Expert", "Fail Corp", "R$ 15.000,00", "https://example.com/job/fail-test", "Glassdoor", "Mock requirements", 95, "pending")
)
conn.commit()

# Verify it was inserted
c.execute("SELECT status FROM jobs WHERE link = ?", ("https://example.com/job/fail-test",))
row = c.fetchone()
print("Before run_auto_apply, fetchone:", row)

conn.close()

# Run auto apply
print("Running run_auto_apply...")
applied = aa.run_auto_apply(TEST_DB_PATH, "temp_curriculo.pdf", "http://127.0.0.1:8888/apply")
print("applied count returned:", applied)

# Verify after run
conn = sqlite3.connect(TEST_DB_PATH)
c = conn.cursor()
c.execute("SELECT status FROM jobs WHERE link = ?", ("https://example.com/job/fail-test",))
row = c.fetchone()
print("After run_auto_apply, fetchone:", row)
conn.close()

# Clean up
if os.path.exists(TEST_DB_PATH):
    os.remove(TEST_DB_PATH)
