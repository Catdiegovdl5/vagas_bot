import os
import json
import pytest
import time
from unittest.mock import MagicMock, AsyncMock
from aiogram.types import CallbackQuery

# Helper imports from our bot
from bot import (
    toggle_escudo_ptbr,
    get_user_settings,
    user_settings_db,
    _do_hunt,
    is_applied
)
import scrapers.workana as workana

@pytest.mark.asyncio
async def test_escudo_ptbr_toggle_changes_setting_in_memory():
    chat_id = 123456
    # Reset setting first
    if str(chat_id) in user_settings_db:
        del user_settings_db[str(chat_id)]
    
    settings = get_user_settings(chat_id)
    assert settings["escudo_ptbr"] is True
    
    # Create mocked CallbackQuery
    callback = MagicMock()
    callback.message.chat.id = chat_id
    callback.answer = AsyncMock()
    callback.message.edit_reply_markup = AsyncMock()
    
    await toggle_escudo_ptbr(callback)
    
    assert settings["escudo_ptbr"] is False
    callback.answer.assert_called_once()
    callback.message.edit_reply_markup.assert_called_once()
    
    # Toggle again
    await toggle_escudo_ptbr(callback)
    assert settings["escudo_ptbr"] is True


@pytest.mark.asyncio
async def test_escudo_ptbr_false_retains_gringo_jobs(monkeypatch):
    import importlib
    
    chat_id = 78910
    if str(chat_id) in user_settings_db:
        del user_settings_db[str(chat_id)]
        
    settings = get_user_settings(chat_id)
    settings["escudo_ptbr"] = False
    settings["platforms"] = {p: False for p in settings["platforms"]}
    settings["platforms"]["indeed"] = True
    
    # Mock scraper to return one gringo job
    class MockScraper:
        def scrape(self, keyword, level="Todos", country=None):
            return [{
                "platform": "Indeed",
                "title": "Gringo Python Developer",
                "company": "Gringo Corp",
                "budget": "None",
                "link": "https://example.com/gringo-job",
                "requirements": "This is an english job description. We do not want PT-BR shield to filter this out when disabled."
            }]
            
    def mock_import_module(name):
        if name == "scrapers.indeed":
            return MockScraper()
        return importlib.import_module(name)
        
    monkeypatch.setattr(importlib, "import_module", mock_import_module)
    
    # Mock message.answer to not do real telegram calls
    mock_chat = MagicMock()
    mock_chat.id = chat_id
    mock_message = MagicMock()
    mock_message.chat = mock_chat
    
    mock_status_msg = AsyncMock()
    mock_status_msg.edit_text = AsyncMock()
    mock_message.answer = AsyncMock(return_value=mock_status_msg)
    
    inserted_jobs = []
    def mock_insert_jobs(jobs):
        inserted_jobs.extend(jobs)
        
    monkeypatch.setattr("bot.insert_jobs", mock_insert_jobs)
    monkeypatch.setattr("auto_apply.auto_apply", lambda job, chat_id: {})
    
    await _do_hunt("Python", mock_message)
    
    # The job should be in inserted_jobs because escudo_ptbr is False
    assert len(inserted_jobs) == 1
    assert inserted_jobs[0]["title"] == "Gringo Python Developer"
    
    # Now verify with escudo_ptbr = True (it should filter it out)
    if str(chat_id) in user_settings_db:
        del user_settings_db[str(chat_id)]
    settings = get_user_settings(chat_id)
    settings["escudo_ptbr"] = True
    settings["platforms"] = {p: False for p in settings["platforms"]}
    settings["platforms"]["indeed"] = True
    
    inserted_jobs.clear()
    await _do_hunt("Python", mock_message)
    
    # The job is in English and platform is Indeed (not freelance),
    # so it should be filtered out when escudo_ptbr is True.
    assert len(inserted_jobs) == 0


@pytest.mark.asyncio
async def test_workana_scraper_pagination_delays_and_termination(monkeypatch):
    import asyncio
    # Mock asyncio.sleep to record sleep calls and avoid slow tests
    sleep_calls = []
    original_sleep = asyncio.sleep
    async def mock_asyncio_sleep(seconds):
        if seconds >= 1.0:
            sleep_calls.append(seconds)
        await original_sleep(0)
        
    monkeypatch.setattr(asyncio, "sleep", mock_asyncio_sleep)
    
    # Setup Playwright mocks
    from scrapers.workana import async_playwright
    
    requested_urls = []
    is_429_test = [False]
    
    # Mock elements inside card
    mock_title_el = AsyncMock()
    mock_title_el.inner_text = AsyncMock(return_value="Vue Developer")
    mock_title_el.get_attribute = AsyncMock(return_value="/job/vue-developer-123")
    
    mock_desc_el = AsyncMock()
    mock_desc_el.inner_text = AsyncMock(return_value="Vue requirements")
    
    mock_budget_el = AsyncMock()
    mock_budget_el.inner_text = AsyncMock(return_value="500 USD")
    
    async def card_query_selector(sel):
        if sel in ['.project-title a', 'a.project-title', '.project-title', 'a']:
            return mock_title_el
        elif sel in ['.project-details', '.project-description']:
            return mock_desc_el
        elif sel in ['.budget', '.project-budget']:
            return mock_budget_el
        return None
        
    mock_card1 = AsyncMock()
    mock_card1.query_selector = AsyncMock(side_effect=card_query_selector)
    
    async def mock_query_selector_all(sel):
        current_url = requested_urls[-1] if requested_urls else ""
        if "page=1" in current_url:
            return [mock_card1]
        else:
            return []
            
    # Mock Page
    mock_page = AsyncMock()
    
    async def mock_goto(url, timeout=None, wait_until=None):
        requested_urls.append(url)
        status = 200
        if "page=2" in url and is_429_test[0]:
            status = 429
        res = MagicMock()
        res.status = status
        return res
        
    mock_page.goto = AsyncMock(side_effect=mock_goto)
    mock_page.wait_for_selector = AsyncMock()
    mock_page.query_selector_all = AsyncMock(side_effect=mock_query_selector_all)
    
    # Mock Context
    mock_context = AsyncMock()
    mock_context.new_page = AsyncMock(return_value=mock_page)
    
    # Mock Browser
    mock_browser = AsyncMock()
    mock_browser.new_context = AsyncMock(return_value=mock_context)
    mock_browser.close = AsyncMock()
    
    # Mock p (Playwright Object)
    mock_p = MagicMock()
    mock_p.chromium.launch = AsyncMock(return_value=mock_browser)
    
    # Mock async context manager returning mock_p
    mock_playwright_cm = AsyncMock()
    mock_playwright_cm.__aenter__.return_value = mock_p
    
    # Monkeypatch async_playwright
    monkeypatch.setattr("scrapers.workana.async_playwright", MagicMock(return_value=mock_playwright_cm))
    
    # Call scrape with max_pages=3
    jobs = await workana.scrape(keyword="Vue", level="Todos", max_pages=3)
    
    # Assertions
    assert len(jobs) == 1
    assert jobs[0]["title"] == "Vue Developer"
    assert jobs[0]["link"] == "https://www.workana.com/job/vue-developer-123"
    
    # Verify pagination stopped at page 2 (didn't request page 3)
    assert len(requested_urls) == 2
    assert "page=1" in requested_urls[0]
    assert "page=2" in requested_urls[1]
    
    # Verify delay was called for page 2 (since page > 1)
    assert len(sleep_calls) == 1
    assert 2.0 <= sleep_calls[0] <= 5.5
    
    # Now let's test termination on HTTP 429
    requested_urls.clear()
    sleep_calls.clear()
    is_429_test[0] = True
    
    jobs = await workana.scrape(keyword="Vue", level="Todos", max_pages=3)
    assert len(jobs) == 1
    # Stopped on page 2 because of 429
    assert len(requested_urls) == 2


@pytest.mark.asyncio
async def test_auto_apply_skipped_if_already_applied(monkeypatch):
    import importlib
    
    chat_id = 992233
    if str(chat_id) in user_settings_db:
        del user_settings_db[str(chat_id)]
        
    settings = get_user_settings(chat_id)
    settings["platforms"] = {p: False for p in settings["platforms"]}
    settings["platforms"]["indeed"] = True
    
    # Mock scraper to return a job
    class MockScraper:
        def scrape(self, keyword, level="Todos", country=None):
            return [{
                "platform": "Indeed",
                "title": "Already Applied Job",
                "company": "Company A",
                "budget": "None",
                "link": "https://example.com/already-applied",
                "requirements": "We need a Python developer."
            }]
            
    def mock_import_module(name):
        if name == "scrapers.indeed":
            return MockScraper()
        return importlib.import_module(name)
        
    monkeypatch.setattr(importlib, "import_module", mock_import_module)
    
    # Mock is_applied to return True
    def mock_is_applied(link):
        if link == "https://example.com/already-applied":
            return True
        return False
    monkeypatch.setattr("bot.is_applied", mock_is_applied)
    
    # Mock auto_apply to track if it is called
    auto_apply_called = []
    def mock_auto_apply(job, user_chat_id):
        auto_apply_called.append(job)
        return {"contact_email": "test@example.com"}
        
    monkeypatch.setattr("auto_apply.auto_apply", mock_auto_apply)
    
    # Mock messaging
    mock_chat = MagicMock()
    mock_chat.id = chat_id
    mock_message = MagicMock()
    mock_message.chat = mock_chat
    
    mock_status_msg = AsyncMock()
    mock_status_msg.edit_text = AsyncMock()
    mock_message.answer = AsyncMock(return_value=mock_status_msg)
    
    # Mock insert_jobs
    monkeypatch.setattr("bot.insert_jobs", lambda jobs: None)
    
    await _do_hunt("Python", mock_message)
    
    # Since is_applied returned True, auto_apply should not have been called!
    assert len(auto_apply_called) == 0


@pytest.mark.asyncio
async def test_workana_search_scope_expansion(monkeypatch):
    from scrapers.workana import async_playwright
    
    requested_urls = []
    
    # Mock Page
    mock_page = AsyncMock()
    
    async def mock_goto(url, timeout=None, wait_until=None):
        requested_urls.append(url)
        res = MagicMock()
        res.status = 200
        return res
        
    mock_page.goto = AsyncMock(side_effect=mock_goto)
    mock_page.wait_for_selector = AsyncMock()
    mock_page.query_selector_all = AsyncMock(return_value=[])
    
    # Mock Context
    mock_context = AsyncMock()
    mock_context.new_page = AsyncMock(return_value=mock_page)
    
    # Mock Browser
    mock_browser = AsyncMock()
    mock_browser.new_context = AsyncMock(return_value=mock_context)
    mock_browser.close = AsyncMock()
    
    # Mock p (Playwright Object)
    mock_p = MagicMock()
    mock_p.chromium.launch = AsyncMock(return_value=mock_browser)
    
    mock_playwright_cm = AsyncMock()
    mock_playwright_cm.__aenter__.return_value = mock_p
    
    monkeypatch.setattr("scrapers.workana.async_playwright", MagicMock(return_value=mock_playwright_cm))
    
    # Test 1: Mapped key - "Especialista IA"
    requested_urls.clear()
    await workana.scrape(keyword="Especialista IA", level="Todos", max_pages=1)
    assert len(requested_urls) == 1
    # "Especialista IA" -> normalized "especialista ia" -> mapped "especialista em ia" -> group A top term "ia" -> "ia"
    assert "query=ia" in requested_urls[0]
    
    # Test 2: Mapped key - "ai developer"
    requested_urls.clear()
    await workana.scrape(keyword="ai developer", level="Todos", max_pages=1)
    assert len(requested_urls) == 1
    # "ai developer" -> normalized "ai developer" -> mapped "desenvolvedor de agentes ia" -> group A top term "agente" -> "agente"
    assert "query=agente" in requested_urls[0]

    # Test 3: Normal keyword - "Python"
    requested_urls.clear()
    await workana.scrape(keyword="Python", level="Todos", max_pages=1)
    assert len(requested_urls) == 1
    assert "query=Python" in requested_urls[0]
