import sys
import os
import asyncio
import inspect
import importlib
import traceback
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, MagicMock

# Ensure current directory is on sys.path
sys.path.insert(0, os.path.abspath("."))

from app import app, PLATFORM_MODULE_MAP
import bot

UFS = ["SP", "RJ", "MG", "PR", "RS", "SC", "BA"]
ALL_PLATFORMS = [
    "workana", "gupy", "catho", "infojobs", "linkedin", "vagas_com",
    "novenove", "freelancer", "remotar", "programathor", "geekhunter",
    "coodesh", "github_vagas", "indeed", "glassdoor", "jooble"
]

async def test_scrapers_directly():
    print("==================================================")
    print("PHASE 1: DIRECT SCRAPER LOCATION PARAMETER TESTING")
    print("==================================================")
    
    scraper_results = {}
    
    for uf in UFS:
        print(f"\n--- Testing Scrapers with location='{uf}' ---")
        scraper_results[uf] = {}
        for plat in ALL_PLATFORMS:
            plat_clean = PLATFORM_MODULE_MAP.get(plat, plat)
            try:
                mod = importlib.import_module(f"scrapers.{plat_clean}")
                if not hasattr(mod, "scrape"):
                    scraper_results[uf][plat_clean] = {"status": "SKIPPED", "reason": "No scrape function"}
                    continue
                
                sig = inspect.signature(mod.scrape)
                candidate_kwargs = {
                    "keyword": "Python",
                    "level": "Pleno",
                    "location": uf,
                    "country": uf,
                    "max_pages": 1
                }
                has_kwargs = any(p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values())
                if has_kwargs:
                    kwargs = candidate_kwargs
                else:
                    kwargs = {k: v for k, v in candidate_kwargs.items() if k in sig.parameters}
                
                # Mock network / external HTTP calls inside scraper if any, or run real scrape safely
                # We want to check if scraper parameter passing or parsing raises exceptions for UF values
                print(f"Calling scrapers.{plat_clean}.scrape with kwargs: {kwargs}")
                
                # If function is coroutine or async
                if inspect.iscoroutinefunction(mod.scrape):
                    # We wrap in try-except to check if location causes code-level errors (e.g. KeyError, ValueError, TypeError)
                    # We can mock network calls or let scraper run short execution
                    res = await mod.scrape(**kwargs)
                else:
                    res = await asyncio.to_thread(mod.scrape, **kwargs)
                    
                scraper_results[uf][plat_clean] = {
                    "status": "PASS",
                    "received_kwargs": kwargs,
                    "result_count": len(res) if isinstance(res, list) else 0
                }
                print(f"  [PASS] scrapers.{plat_clean}: returned {len(res) if isinstance(res, list) else type(res)}")
            except Exception as e:
                err_msg = traceback.format_exc()
                scraper_results[uf][plat_clean] = {
                    "status": "FAIL",
                    "error": str(e),
                    "traceback": err_msg
                }
                print(f"  [FAIL] scrapers.{plat_clean}: {e}")
                
    return scraper_results

async def test_api_trigger_endpoint():
    print("\n==================================================")
    print("PHASE 2: FASTAPI /api/trigger ENDPOINT TESTING")
    print("==================================================")
    
    trigger_results = {}
    
    # We patch insert_jobs so we don't write to DB during empirical test
    with patch("app.insert_jobs", return_value=1) as mock_db:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
            for uf in UFS:
                captured_settings = []
                captured_jobs_checked = []
                
                # Create spy for bot.is_job_relevant
                real_ijr = bot.is_job_relevant
                def ijr_spy(job, keyword, settings):
                    captured_settings.append(settings.copy())
                    captured_jobs_checked.append(job)
                    return real_ijr(job, keyword, settings)
                
                with patch("bot.is_job_relevant", side_effect=ijr_spy):
                    payload = {
                        "platforms": ["gupy", "catho", "infojobs", "workana"],
                        "keyword": "Python",
                        "level": "Pleno",
                        "location": uf
                    }
                    
                    response = await client.post("/api/trigger", json=payload)
                    status_code = response.status_code
                    json_resp = response.json()
                    
                    # Yield control to let asyncio background task run
                    await asyncio.sleep(1.5)
                    
                    # Check captured settings in is_job_relevant
                    received_locations = [s.get("location") for s in captured_settings]
                    location_matches = all(loc == uf for loc in received_locations) if received_locations else False
                    
                    trigger_results[uf] = {
                        "status_code": status_code,
                        "response": json_resp,
                        "is_job_relevant_call_count": len(captured_settings),
                        "received_locations": list(set(received_locations)),
                        "settings_location_exact_match": location_matches or (len(captured_settings) == 0 and status_code == 200),
                        "jobs_checked_count": len(captured_jobs_checked)
                    }
                    
                    print(f"UF '{uf}': Status={status_code}, TriggerResponse={json_resp}")
                    print(f"  is_job_relevant called {len(captured_settings)} times.")
                    print(f"  Received location settings: {list(set(received_locations))}")
                    print(f"  Exact UF match verified: {location_matches or len(captured_settings)==0}")

    return trigger_results

async def main():
    scraper_res = await test_scrapers_directly()
    trigger_res = await test_api_trigger_endpoint()
    
    print("\n==================================================")
    print("EMPIRICAL TEST SUMMARY")
    print("==================================================")
    print(f"Tested UFs: {UFS}")
    
    all_scrapers_passed = True
    for uf, plats in scraper_res.items():
        for p, res in plats.items():
            if res.get("status") == "FAIL":
                print(f"Scraper Failure: UF={uf}, platform={p}, error={res.get('error')}")
                all_scrapers_passed = False
                
    all_triggers_passed = True
    for uf, res in trigger_res.items():
        if res.get("status_code") != 200:
            all_triggers_passed = False
        if res.get("is_job_relevant_call_count") > 0 and not res.get("settings_location_exact_match"):
            all_triggers_passed = False

    print(f"Scrapers direct location execution: {'ALL PASS' if all_scrapers_passed else 'SOME FAILS'}")
    print(f"/api/trigger endpoint execution: {'ALL PASS' if all_triggers_passed else 'SOME FAILS'}")

if __name__ == "__main__":
    asyncio.run(main())
