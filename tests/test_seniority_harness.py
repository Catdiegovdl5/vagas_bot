import asyncio
import importlib
import pytest
from unittest.mock import MagicMock, AsyncMock
from bot import _do_hunt, get_user_settings, user_settings_db

# Mock scraper module generator
class MockScraperModule:
    def __init__(self, name):
        self.__name__ = name
        self.called_args = []

    def scrape(self, keyword, level="Todos", country=None):
        # Record the exact arguments used to call scrape
        self.called_args.append({
            "keyword": keyword,
            "level": level,
            "country": country
        })
        # Conforms to the standard scraper schema
        return [
            {
                "platform": "MockPlatform",
                "title": f"Engineer for {keyword}",
                "company": "Test Inc",
                "budget": "10000",
                "link": f"https://example.com/job-{keyword.replace(' ', '-')}",
                "requirements": "This is a mockup job description of sufficient length to pass any basic validations."
            }
        ]

@pytest.mark.asyncio
async def test_do_hunt_keyword_transformation_levels(monkeypatch):
    """
    Test the behavior of _do_hunt's keyword transformation with multiple seniority levels:
    'Todos', 'Júnior', 'Pleno', 'Sênior', 'None', and empty strings.
    """
    # 1. Setup mock messaging
    mock_chat = MagicMock()
    mock_chat.id = 12345
    
    mock_message = MagicMock()
    mock_message.chat = mock_chat
    
    mock_status_msg = AsyncMock()
    mock_status_msg.edit_text = AsyncMock()
    mock_status_msg.reply = AsyncMock()
    mock_message.answer = AsyncMock(return_value=mock_status_msg)
    
    # 2. Setup mock scrapers registry
    mock_modules = {}
    
    def mock_import_module(name):
        if name.startswith("scrapers."):
            if name not in mock_modules:
                mock_modules[name] = MockScraperModule(name)
            return mock_modules[name]
        return importlib.import_module(name)
        
    monkeypatch.setattr(importlib, "import_module", mock_import_module)

    # We will test these seniority level configurations
    test_cases = [
        {"level": "Todos", "expected_suffix": ""},
        {"level": "Júnior", "expected_suffix": " Júnior"},
        {"level": "Pleno", "expected_suffix": " Pleno"},
        {"level": "Sênior", "expected_suffix": " Sênior"},
        {"level": "None", "expected_suffix": " None"},
        {"level": "", "expected_suffix": " "},
    ]

    for case in test_cases:
        level = case["level"]
        expected_suffix = case["expected_suffix"]
        
        # Reset mock modules
        mock_modules.clear()
        
        # Reset settings for user
        chat_id = "12345"
        if chat_id in user_settings_db:
            del user_settings_db[chat_id]
        settings = get_user_settings(chat_id)
        settings["level"] = level
        settings["location"] = "Brasil (Remoto)"
        # Configure platforms to test one specific platform (e.g. infojobs)
        settings["platforms"] = {p: False for p in settings["platforms"]}
        settings["platforms"]["infojobs"] = True
        
        # We search for "Backend Python" which maps to "Python Backend" in search_mapping
        keyword = "Backend Python"
        expected_base_kw = "Python Backend"
        expected_search_kw = f"{expected_base_kw}{expected_suffix}"
        
        # Trigger hunt
        await _do_hunt(keyword, mock_message)
        
        # Verify infojobs scraper was called
        scraper_mod_name = "scrapers.infojobs"
        assert scraper_mod_name in mock_modules, f"Scraper module {scraper_mod_name} was not imported"
        calls = mock_modules[scraper_mod_name].called_args
        assert len(calls) == 1, "Scraper scrape was not called exactly once"
        
        # Verify the parameters passed to scraper
        called_kw = calls[0]["keyword"]
        called_lvl = calls[0]["level"]
        
        # The correct search keyword (either with or without the suffix) must be constructed
        assert called_kw == expected_search_kw, f"For level '{level}', expected keyword '{expected_search_kw}', got '{called_kw}'"
        
        # Scraper should receive 'level="Todos"' as per bot.py implementation
        assert called_lvl == "Todos", f"For level '{level}', scraper was called with level '{called_lvl}', expected 'Todos'"


@pytest.mark.asyncio
async def test_do_hunt_concurrency_and_performance(monkeypatch):
    """
    Verify that there are no exceptions or performance regressions during concurrent execution of _do_hunt.
    """
    mock_chat = MagicMock()
    mock_chat.id = 54321
    
    mock_message = MagicMock()
    mock_message.chat = mock_chat
    
    mock_status_msg = AsyncMock()
    mock_status_msg.edit_text = AsyncMock()
    mock_status_msg.reply = AsyncMock()
    mock_message.answer = AsyncMock(return_value=mock_status_msg)
    
    # Mock importlib to return immediate mock scraper modules
    mock_modules = {}
    
    def mock_import_module(name):
        if name.startswith("scrapers."):
            if name not in mock_modules:
                mock_modules[name] = MockScraperModule(name)
            return mock_modules[name]
        return importlib.import_module(name)
        
    monkeypatch.setattr(importlib, "import_module", mock_import_module)
    
    # Configure user settings for concurrent execution
    chat_id = "54321"
    settings = get_user_settings(chat_id)
    settings["level"] = "Pleno"
    settings["location"] = "Brasil (Remoto)"
    # Enable multiple platforms to increase concurrency load
    settings["platforms"] = {
        "linkedin": True,
        "glassdoor": True,
        "infojobs": True,
        "indeed": True,
        "jooble": True
    }
    
    # Define several different search keywords to run concurrently
    concurrent_keywords = [
        "Backend Python",
        "Especialista em IA",
        "AI Coder",
        "Analista de Dados",
        "Desenvolvedor Júnior"
    ]
    
    # Run all hunters concurrently
    import time
    start_time = time.time()
    
    tasks = [
        _do_hunt(kw, mock_message) for kw in concurrent_keywords
    ]
    
    # This gathers and executes all concurrently. If there are database lock issues
    # or shared state bugs, this should raise exceptions.
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    end_time = time.time()
    duration = end_time - start_time
    
    # Check for exceptions
    for i, res in enumerate(results):
        assert not isinstance(res, Exception), f"Concurrent execution {i} failed with exception: {res}"
        
    # Check that performance is reasonable (e.g. 5 concurrent hunts with mocks should finish in under 3.0 seconds)
    assert duration < 3.0, f"Performance regression: concurrent execution took {duration:.2f} seconds, expected < 3.0s"
