import sqlite3
import os

db_path = "jobs.db"
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # List tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables in jobs.db:", tables)
    
    for table_name in [t[0] for t in tables]:
        cursor.execute(f"PRAGMA table_info({table_name});")
        info = cursor.fetchall()
        print(f"Table info for {table_name}:")
        for col in info:
            print(f"  Col: {col[1]} ({col[2]})")
            
        cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
        count = cursor.fetchone()[0]
        print(f"  Total rows: {count}")
    
    conn.close()
else:
    print("jobs.db does not exist!")
