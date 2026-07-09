import asyncio
import os
import sqlite3
import pytest
from unittest.mock import MagicMock, AsyncMock

# Monkeypatch database.DB_PATH before it is used by other imports
import database
TEST_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "jobs_test.db")
database.DB_PATH = TEST_DB_PATH

# Initialize database
if os.path.exists(TEST_DB_PATH):
    os.remove(TEST_DB_PATH)
database.init_db()

import scrapers.infojobs
from bot import _do_hunt, get_user_settings

async def main():
    # Setup mock message
    mock_chat = MagicMock()
    mock_chat.id = 99999
    mock_message = MagicMock()
    mock_message.chat = mock_chat
    mock_status_msg = AsyncMock()
    mock_status_msg.edit_text = AsyncMock()
    mock_status_msg.reply = AsyncMock()
    mock_message.answer = AsyncMock(return_value=mock_status_msg)

    # Configure settings
    settings = get_user_settings(99999)
    settings["level"] = "Sênior"
    settings["platforms"] = {p: False for p in settings["platforms"]}
    settings["platforms"]["infojobs"] = True

    # Patch scraper
    original_scrape = scrapers.infojobs.scrape
    
    # Let's inspect the keyword and arguments passed to scrape
    def spy_scrape(keyword, level="Todos", country="Brasil"):
        print(f"--- scrape called with: keyword={keyword}, level={level}, country={country} ---")
        return [
            {
                "platform": "InfoJobs",
                "title": f"Python Developer ({level})", # Let's see if this is what test_tier1.py has!
                "company": "Test Company",
                "budget": "A Combinar",
                "link": "https://example.com/job/test-1",
                "job_type": "CLT",
                "profession": "Python",
                "level": level,
                "requirements": "Procura-se desenvolvedor Python Sênior experiente com conhecimentos de Django e APIs REST."
            }
        ]
        
    scrapers.infojobs.scrape = spy_scrape

    try:
        await _do_hunt("Python", mock_message)
    finally:
        scrapers.infojobs.scrape = original_scrape

    # Check jobs in test database
    conn = sqlite3.connect(database.DB_PATH)
    c = conn.cursor()
    c.execute("SELECT title, level, platform FROM jobs")
    jobs = c.fetchall()
    conn.close()

    print("Jobs in DB after hunt:", jobs)

asyncio.run(main())
