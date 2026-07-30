import sys
import os
import asyncio
import inspect
import importlib
import json
import traceback
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, MagicMock

# Set project root in sys.path
sys.path.insert(0, os.path.abspath("."))

from app import app, PLATFORM_MODULE_MAP
import bot

UFS = ["SP", "RJ", "MG", "PR", "RS", "SC", "BA"]

ALL_PLATFORMS = [
    "workana", "gupy", "catho", "infojobs", "linkedin", "vagas_com",
    "novenove", "freelancer", "remotar", "programathor", "geekhunter",
    "coodesh", "github_vagas", "indeed", "glassdoor", "jooble"
]

async def test_fastapi_trigger_endpoint_async():
    print("==================================================")
    print("1. EMPIRICAL TEST: FastAPI AsyncClient /api/trigger")
    print("==================================================")
    
    results = {}
    
    for uf in UFS:
        captured_ijr_settings = []
        captured_scraper_kwargs = {}
        scraper_exceptions = {}
        
        # Build patches for all scrapers so app.py calls mock_scrape which records kwargs & returns dummy jobs
        patchers = []
        for plat in ALL_PLATFORMS:
            plat_clean = PLATFORM_MODULE_MAP.get(plat, plat)
            try:
                mod = importlib.import_module(f"scrapers.{plat_clean}")
                if hasattr(mod, "scrape"):
                    orig_func = mod.scrape
                    dummy_job = {
                        "title": f"Desenvolvedor Python {uf}",
                        "company": f"Tech {uf}",
                        "location": f"Cidade - {uf}",
                        "platform": plat_clean,
                        "requirements": f"Experiencia com Python em {uf} bastante explicita para passar tamanho minimo"
                    }
                    
                    if inspect.iscoroutinefunction(orig_func):
                        async def make_async_mock(p_clean=plat_clean, d_job=dummy_job, **kwargs):
                            captured_scraper_kwargs[p_clean] = kwargs
                            return [d_job]
                        p = patch.object(mod, "scrape", side_effect=make_async_mock)
                    else:
                        def make_sync_mock(p_clean=plat_clean, d_job=dummy_job, **kwargs):
                            captured_scraper_kwargs[p_clean] = kwargs
                            return [d_job]
                        p = patch.object(mod, "scrape", side_effect=make_sync_mock)
                    
                    patchers.append(p)
            except Exception as e:
                scraper_exceptions[plat] = str(e)
                
        # Start all patches
        for p in patchers:
            p.start()
            
        real_ijr = bot.is_job_relevant
        def spy_ijr(job, keyword, settings):
            captured_ijr_settings.append(dict(settings))
            return real_ijr(job, keyword, settings)
            
        with patch("app.insert_jobs", return_value=1), \
             patch("bot.is_job_relevant", side_effect=spy_ijr):
            
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
                payload = {
                    "platforms": ALL_PLATFORMS,
                    "keyword": "Python",
                    "level": "Pleno",
                    "location": uf
                }
                
                response = await client.post("/api/trigger", json=payload)
                status_code = response.status_code
                resp_json = response.json()
                
                # Await pending background tasks created via asyncio.create_task
                pending = [t for t in asyncio.all_tasks() if t != asyncio.current_task()]
                if pending:
                    await asyncio.gather(*pending, return_exceptions=True)
                
            # Stop patches
            for p in patchers:
                p.stop()
                
            # Verification of settings["location"]
            received_locs = [s.get("location") for s in captured_ijr_settings]
            exact_uf_match = all(loc == uf for loc in received_locs) if received_locs else False
            
            results[uf] = {
                "status_code": status_code,
                "response": resp_json,
                "scrapers_called_count": len(captured_scraper_kwargs),
                "is_job_relevant_call_count": len(captured_ijr_settings),
                "settings_locations_received": list(set(received_locs)),
                "exact_uf_verified": exact_uf_match,
                "scraper_kwargs": captured_scraper_kwargs,
                "scraper_exceptions": scraper_exceptions
            }
            
            print(f"\n[UF={uf}] Status={status_code}")
            print(f"  Response: {resp_json}")
            print(f"  Scrapers called: {len(captured_scraper_kwargs)} / {len(ALL_PLATFORMS)}")
            print(f"  is_job_relevant calls: {len(captured_ijr_settings)}")
            print(f"  Received settings['location']: {list(set(received_locs))}")
            print(f"  Exact UF verified: {exact_uf_match}")
            
    return results

def test_scraper_signatures_and_kwargs():
    print("\n==================================================")
    print("2. EMPIRICAL TEST: Scraper Signature & Location Kwargs")
    print("==================================================")
    
    signature_analysis = {}
    for plat in ALL_PLATFORMS:
        plat_clean = PLATFORM_MODULE_MAP.get(plat, plat)
        try:
            mod = importlib.import_module(f"scrapers.{plat_clean}")
            if hasattr(mod, "scrape"):
                sig = inspect.signature(mod.scrape)
                params = dict(sig.parameters)
                has_var_kw = any(p.kind == inspect.Parameter.VAR_KEYWORD for p in params.values())
                
                # Test app.py logic for candidate kwargs
                candidate_kwargs = {
                    "keyword": "Python",
                    "level": "Pleno",
                    "location": "SP",
                    "country": "SP",
                    "max_pages": 10
                }
                if has_var_kw:
                    kwargs_passed = candidate_kwargs
                else:
                    kwargs_passed = {k: v for k, v in candidate_kwargs.items() if k in params}
                    
                signature_analysis[plat_clean] = {
                    "parameters": list(params.keys()),
                    "has_var_keyword": has_var_kw,
                    "kwargs_passed_by_app": kwargs_passed,
                    "location_passed": "location" in kwargs_passed or "country" in kwargs_passed
                }
                print(f"  [{plat_clean}] params={list(params.keys())} -> kwargs_passed={kwargs_passed}")
            else:
                signature_analysis[plat_clean] = {"error": "No scrape function found"}
        except Exception as e:
            signature_analysis[plat_clean] = {"error": str(e)}
            
    return signature_analysis

def test_is_job_relevant_uf_matching():
    print("\n==================================================")
    print("3. EMPIRICAL TEST: is_job_relevant UF Matching Logic")
    print("==================================================")
    
    matching_tests = {
        "SP": [("Dev Python SP", "São Paulo - SP", True), ("Dev Python RJ", "Rio de Janeiro - RJ", False)],
        "RJ": [("Dev Python RJ", "Rio de Janeiro - RJ", True), ("Dev Python SP", "São Paulo - SP", False)],
        "MG": [("Dev Python BH", "Belo Horizonte - MG", True), ("Dev Python PR", "Curitiba - PR", False)],
        "PR": [("Dev Python CWB", "Curitiba - PR", True), ("Dev Python RS", "Porto Alegre - RS", False)],
        "RS": [("Dev Python POA", "Porto Alegre - RS", True), ("Dev Python SC", "Florianópolis - SC", False)],
        "SC": [("Dev Python Floripa", "Florianópolis - SC", True), ("Dev Python BA", "Salvador - BA", False)],
        "BA": [("Dev Python SSA", "Salvador - BA", True), ("Dev Python SP", "São Paulo - SP", False)]
    }
    
    ijr_results = {}
    for uf, jobs in matching_tests.items():
        ijr_results[uf] = []
        settings = {"level": "Todos", "location": uf, "contract": "Todos", "education": "Todos"}
        for title, loc, expected in jobs:
            dummy_job = {
                "title": title,
                "company": "Empresa Teste",
                "location": loc,
                "platform": "gupy",
                "requirements": "Desenvolvimento com Python e SQL bastante detalhado para passar no filtro de tamanho"
            }
            actual = bot.is_job_relevant(dummy_job, "Python", settings)
            passed = (actual == expected)
            ijr_results[uf].append({
                "title": title,
                "location": loc,
                "expected": expected,
                "actual": actual,
                "pass": passed
            })
            print(f"  [UF={uf}] Job: '{title}' @ '{loc}' -> Expected={expected}, Actual={actual} ({'PASS' if passed else 'FAIL'})")
            
    return ijr_results

async def main():
    trigger_results = await test_fastapi_trigger_endpoint_async()
    sig_results = test_scraper_signatures_and_kwargs()
    ijr_results = test_is_job_relevant_uf_matching()
    
    summary = {
        "ufs_tested": UFS,
        "trigger_endpoint": trigger_results,
        "scraper_signatures": sig_results,
        "is_job_relevant_matching": ijr_results
    }
    
    out_dir = os.path.abspath(".agents/teamwork_preview_challenger_state_2")
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "empirical_test_summary.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
        
    print(f"\nEmpirical verification complete! Output saved to: {out_file}")

if __name__ == "__main__":
    asyncio.run(main())
