import asyncio
import os
import sqlite3
import database
from unittest.mock import MagicMock, AsyncMock

# Set up test database path
TEST_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "jobs_test.db")
database.DB_PATH = TEST_DB_PATH

# Clean test db
if os.path.exists(TEST_DB_PATH):
    os.remove(TEST_DB_PATH)
database.init_db()

from bot import _do_hunt, get_user_settings, is_job_relevant, normalize_str
import scrapers.infojobs

async def run_reproduction():
    mock_chat = MagicMock()
    mock_chat.id = 99999
    
    mock_message = MagicMock()
    mock_message.chat = mock_chat
    
    mock_status_msg = AsyncMock()
    mock_status_msg.edit_text = AsyncMock()
    mock_status_msg.reply = AsyncMock()
    mock_message.answer = AsyncMock(return_value=mock_status_msg)
    
    settings = get_user_settings(99999)
    settings["level"] = "Sênior"
    settings["platforms"] = {p: False for p in settings["platforms"]}
    settings["platforms"]["infojobs"] = True
    
    original_scrape = scrapers.infojobs.scrape
    scrapers.infojobs.scrape = lambda keyword, level="Todos", country="Brasil": [
        {
            "platform": "InfoJobs",
            "title": "Python Developer",
            "company": "Test Company",
            "budget": "A Combinar",
            "link": "https://example.com/job/test-1",
            "job_type": "CLT",
            "profession": "Python",
            "level": level,
            "requirements": "Procura-se desenvolvedor Python Sênior experiente com conhecimentos de Django e APIs REST."
        }
    ]
    
    # Let's inspect the relevancy logic first:
    job = scrapers.infojobs.scrape("Python Sênior", "Todos")[0]
    filter_settings = settings.copy()
    filter_settings["level"] = "Todos"
    relevant = is_job_relevant(job, "Python", filter_settings)
    print("Is job relevant:", relevant)
    
    try:
        await _do_hunt("Python", mock_message)
    finally:
        scrapers.infojobs.scrape = original_scrape
        
    conn = sqlite3.connect(database.DB_PATH)
    c = conn.cursor()
    c.execute("SELECT title, level, platform FROM jobs")
    jobs = c.fetchall()
    conn.close()
    
    print("Jobs in database:", jobs)

asyncio.run(run_reproduction())
