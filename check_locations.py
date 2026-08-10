from database import get_connection
import sqlite3
conn = get_connection()
conn.row_factory = sqlite3.Row
cursor = conn.cursor()
rows = cursor.execute('SELECT location, COUNT(*) as cnt FROM jobs GROUP BY location ORDER BY cnt DESC LIMIT 20').fetchall()
for r in rows:
    print(f"  {r['cnt']:5d}x  {repr(r['location'])}")
conn.close()
