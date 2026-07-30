import sys
import os
import asyncio
from unittest.mock import MagicMock, patch
from httpx import AsyncClient, ASGITransport

PROJECT_ROOT = r"C:\Users\99196\OneDrive\Documentos\vagas_bot"
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import bot
from app import app

async def run_empirical_async_test():
    print("==========================================================")
    print("  EMPIRICAL API /api/trigger LOCATION PARAMETER TEST HARNESS  ")
    print("==========================================================")
    
    test_cases = [
        {"name": "Location SP in Body", "payload": {"platforms": ["workana"], "keyword": "Python", "level": "Senior", "location": "SP"}, "expected_location": "SP"},
        {"name": "Location RJ in Body", "payload": {"platforms": ["workana"], "keyword": "Python", "level": "Senior", "location": "RJ"}, "expected_location": "RJ"},
        {"name": "Location MG in Body", "payload": {"platforms": ["workana"], "keyword": "Python", "level": "Senior", "location": "MG"}, "expected_location": "MG"},
        {"name": "Location Curitiba in Body", "payload": {"platforms": ["workana"], "keyword": "Python", "level": "Senior", "location": "Curitiba"}, "expected_location": "Curitiba"},
        {"name": "Location Todos in Body", "payload": {"platforms": ["workana"], "keyword": "Python", "level": "Senior", "location": "Todos"}, "expected_location": "Todos"},
        {"name": "Omitted Location in Body", "payload": {"platforms": ["workana"], "keyword": "Python", "level": "Senior"}, "expected_location": "Todos"},
        {"name": "Empty Location String in Body", "payload": {"platforms": ["workana"], "keyword": "Python", "level": "Senior", "location": ""}, "expected_location": ""},
    ]
    
    results = []

    dummy_job = {
        "title": "Desenvolvedor Python Senior",
        "company": "Tech Corp",
        "platform": "workana",
        "link": "https://example.com/job1",
        "requirements": "Python, Django, FastAPI",
        "location": "Sao Paulo"
    }

    async def mock_scrape(**kwargs):
        print(f"  [MOCK SCRAPER] Executed with kwargs: {kwargs}")
        return [dummy_job]

    mock_scraper_module = MagicMock()
    mock_scraper_module.scrape = mock_scrape

    transport = ASGITransport(app=app)
    original_is_job_relevant = bot.is_job_relevant

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Standard JSON body tests
        for case in test_cases:
            recorded_calls = []

            def spy_is_job_relevant(job, keyword, settings):
                print(f"  [SPY is_job_relevant] job='{job.get('title')}', keyword='{keyword}', settings={settings}")
                recorded_calls.append({
                    "job": job,
                    "keyword": keyword,
                    "settings": dict(settings)
                })
                return original_is_job_relevant(job, keyword, settings)

            bot.is_job_relevant = spy_is_job_relevant

            with patch("importlib.import_module", return_value=mock_scraper_module), \
                 patch("database.insert_jobs", return_value=1):
                
                payload = case["payload"]
                response = await client.post("/api/trigger", json=payload)
                print(f"\n[TEST CASE: {case['name']}]")
                print(f"  Payload: {payload}")
                print(f"  HTTP Status Code: {response.status_code}")
                print(f"  Response JSON: {response.json()}")

                await asyncio.sleep(0.3)

                if recorded_calls:
                    actual_settings = recorded_calls[0]["settings"]
                    actual_location = actual_settings.get("location")
                    expected_loc = case["expected_location"]
                    match = (actual_location == expected_loc)
                    print(f"  Result: Expected settings['location']='{expected_loc}' | Actual settings['location']='{actual_location}' | Match={match}")
                    results.append({
                        "case_name": case["name"],
                        "expected": expected_loc,
                        "received": actual_location,
                        "passed": match and response.status_code == 200
                    })
                else:
                    print(f"  Result: FAILED — is_job_relevant was not invoked!")
                    results.append({
                        "case_name": case["name"],
                        "expected": case["expected_location"],
                        "received": None,
                        "passed": False
                    })

            bot.is_job_relevant = original_is_job_relevant

        # Edge case test: Query parameter vs JSON Body behavior
        print("\n[EDGE CASE TEST: Query Parameter vs JSON Body]")
        recorded_calls = []

        def spy_is_job_relevant(job, keyword, settings):
            recorded_calls.append({"settings": dict(settings)})
            return original_is_job_relevant(job, keyword, settings)

        bot.is_job_relevant = spy_is_job_relevant
        with patch("importlib.import_module", return_value=mock_scraper_module), \
             patch("database.insert_jobs", return_value=1):
            
            response = await client.post("/api/trigger?location=SP")
            await asyncio.sleep(0.3)
            if recorded_calls:
                loc_received = recorded_calls[0]["settings"].get("location")
                print(f"  POST /api/trigger?location=SP (no body) -> settings['location'] = '{loc_received}'")
                print("  Note: Query parameter is ignored because /api/trigger parses request.json() only.")
                results.append({
                    "case_name": "Query Param location=SP (no body)",
                    "expected": "Todos (fallback)",
                    "received": loc_received,
                    "passed": loc_received == "Todos"
                })
        bot.is_job_relevant = original_is_job_relevant

    print("\n==========================================================")
    print("                     VERDICT SUMMARY                      ")
    print("==========================================================")
    all_passed = True
    for r in results:
        status = "PASS" if r["passed"] else "FAIL"
        if not r["passed"]:
            all_passed = False
        print(f"[{status}] {r['case_name']:<35} | Expected: '{r['expected']}' | Received: '{r['received']}'")

    print("==========================================================")
    if all_passed:
        print("VERDICT: SUCCESS - FastAPI /api/trigger correctly propagates location to settings['location']!")
    else:
        print("VERDICT: FAILURE - Discrepancy detected in location parameter handling!")
        sys.exit(1)

def main():
    asyncio.run(run_empirical_async_test())

if __name__ == "__main__":
    main()
