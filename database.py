import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from prioriti.database import get_connection, init_db, get_jobs, insert_jobs, mark_applied, mark_ignored

if __name__ == "__main__":
    init_db()
