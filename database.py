import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "jobs.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.execute('PRAGMA journal_mode=WAL')
    return conn

def init_db():
    conn = get_connection()
    try:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY,
                title TEXT,
                company TEXT,
                budget TEXT,
                link TEXT,
                platform TEXT,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        try: c.execute('ALTER TABLE jobs ADD COLUMN job_type TEXT')
        except: pass
        try: c.execute('ALTER TABLE jobs ADD COLUMN profession TEXT')
        except: pass
        try: c.execute('ALTER TABLE jobs ADD COLUMN level TEXT')
        except: pass
        try: c.execute('ALTER TABLE jobs ADD COLUMN requirements TEXT')
        except: pass
        conn.commit()
    finally:
        conn.close()

def insert_jobs(jobs):
    conn = get_connection()
    try:
        c = conn.cursor()
        inserted = 0
        for job in jobs:
            try:
                link = job.get('link')
                title = job.get('title')
                platform = job.get('platform')
                if not link or not title or not platform:
                    continue
                c.execute('INSERT INTO jobs (id, title, company, budget, link, platform, job_type, profession, level, requirements) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                          (link, title, job.get('company', 'N/A'), job.get('budget', 'A combinar'), link, platform, job.get('job_type', 'CLT'), job.get('profession', 'Tech'), job.get('level', 'ND'), job.get('requirements', 'Requisitos descritos no link da vaga.')))
                inserted += 1
            except sqlite3.IntegrityError:
                pass # duplicate
        conn.commit()
        return inserted
    finally:
        conn.close()

def get_jobs():
    conn = get_connection()
    try:
        c = conn.cursor()
        c.execute('SELECT title, company, budget, link, platform, added_at, job_type, profession, level, requirements FROM jobs ORDER BY added_at DESC')
        rows = c.fetchall()
        
        jobs = []
        for r in rows:
            jobs.append({
                "title": r[0],
                "company": r[1],
                "budget": r[2],
                "link": r[3],
                "platform": r[4],
                "added_at": r[5],
                "job_type": r[6] if (len(r)>6 and r[6] is not None) else "CLT",
                "profession": r[7] if (len(r)>7 and r[7] is not None) else "Tech",
                "level": r[8] if (len(r)>8 and r[8] is not None) else "ND",
                "requirements": r[9] if (len(r)>9 and r[9] is not None) else "Requisitos na página."
            })
        return jobs
    finally:
        conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized.")

# Alias para compatibilidade
get_all_jobs = get_jobs
