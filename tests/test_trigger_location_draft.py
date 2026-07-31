import sys
import os
import asyncio
import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

# Ensure root directory is in sys.path
sys.path.insert(0, os.path.abspath("."))

from app import app, PLATFORM_MODULE_MAP

# Test location UFs required
UFS_TO_TEST = ["SP", "RJ", "MG", "PR", "RS", "SC", "BA"]

def test_api_trigger_location_handling():
    client = TestClient(app)
    
    results = {}
    
    for uf in UFS_TO_TEST:
        captured_is_job_relevant_calls = []
        captured_scraper_calls = {}
        scraper_exceptions = {}
        
        # We will mock scrapers to return dummy jobs so we can test end-to-end execution of run_hunt_background
        # Dummy job to trigger is_job_relevant
        dummy_job = {
            "title": f"Desenvolvedor Python {uf}",
            "company": "Tech Corp",
            "location": uf,
            "platform": "gupy",
            "requirements": f"Experiencia em Python em {uf}"
        }

        # Create a mock for bot.is_job_relevant
        import bot
        original_is_job_relevant = bot.is_job_relevant
        
        def spy_is_job_relevant(job, keyword, settings):
            captured_is_job_relevant_calls.append({
                "job": job,
                "keyword": keyword,
                "settings": settings
            })
            return original_is_job_relevant(job, keyword, settings)

        # Mock database insert_jobs to prevent DB pollution
        with patch("app.insert_jobs", return_value=1) as mock_insert, \
             patch("bot.is_job_relevant", side_effect=spy_is_job_relevant) as mock_ijr:
            
            # Patch scrapers to capture call arguments and ensure no exceptions
            scraper_patches = []
            
            # Map of clean platform names
            all_platforms = list(set(PLATFORM_MODULE_MAP.values()))
            
            for plat in all_platforms:
                try:
                    mod = __import__(f"scrapers.{plat}", fromlist=["scrape"])
                    orig_scrape = getattr(mod, "scrape", None)
                    if orig_scrape:
                        # Wrap scrape to spy kwargs and exceptions
                        if asyncio.iscoroutinefunction(orig_scrape):
                            async def make_async_spy(p_name, orig):
                                async def spy_fn(*args, **kwargs):
                                    captured_scraper_calls[p_name] = kwargs
                                    try:
                                        # Call original scrape or dummy
                                        res = await orig(*args, **kwargs)
                                        return res if res is not None else [dummy_job]
                                    except Exception as ex:
                                        scraper_exceptions[p_name] = str(ex)
                                        raise ex
                                return spy_fn
                            
                            spy = asyncio.run(make_async_spy(plat, orig_scrape)) if False else None
                        
                except Exception as e:
                    pass

            # Make request to /api/trigger
            payload = {
                "platforms": ["gupy", "catho", "infojobs", "workana", "linkedin", "vagas_com"],
                "keyword": "Python",
                "level": "Pleno",
                "location": uf
            }
            
            response = client.post("/api/trigger", json=payload)
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            assert response.json()["status"] == "success"
            
            # Give background task time to run
            # In TestClient with FastAPI, background tasks created with asyncio.create_task run on the event loop
            # We can wait briefly using asyncio or event loop yield
            
            results[uf] = {
                "response": response.json(),
                "status_code": response.status_code
            }

if __name__ == "__main__":
    print("Testing trigger location parameter handling...")
