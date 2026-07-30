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

def check_scraper_signatures():
    """Inspects signatures of all scraper modules to verify parameter compatibility."""
    info = {}
    for plat in ALL_PLATFORMS:
        plat_clean = PLATFORM_MODULE_MAP.get(plat, plat)
        try:
            mod = importlib.import_module(f"scrapers.{plat_clean}")
            if hasattr(mod, "scrape"):
                sig = inspect.signature(mod.scrape)
                params = list(sig.parameters.keys())
                has_kwargs = any(p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values())
                accepts_location = "location" in params or has_kwargs
                accepts_country = "country" in params or has_kwargs
                info[plat_clean] = {
                    "has_scrape": True,
                    "parameters": params,
                    "has_var_keyword": has_kwargs,
                    "accepts_location": accepts_location,
                    "accepts_country": accepts_country,
                    "is_coroutine": inspect.iscoroutinefunction(mod.scrape)
                }
            else:
                info[plat_clean] = {"has_scrape": False}
        except Exception as e:
            info[plat_clean] = {"error": str(e)}
    return info

async def test_scraper_invocation_with_location():
    """Empirically tests invocation of scraper modules with location parameter without network hanging."""
    results = {}
    
    # We patch requests.get, httpx, and Playwright / BeautifulSoup network layers to avoid network delays/hangs
    # while running the actual scraper code structure
    with patch("requests.get") as mock_req_get, \
         patch("httpx.AsyncClient.get") as mock_httpx_get, \
         patch("httpx.get") as mock_httpx_sync_get:
        
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = "<html><body><div class='job'>Job Title</div></body></html>"
        mock_resp.json.return_value = []
        mock_req_get.return_value = mock_resp
        mock_httpx_get.return_value = mock_resp
        mock_httpx_sync_get.return_value = mock_resp
        
        for uf in UFS:
            results[uf] = {}
            for plat in ALL_PLATFORMS:
                plat_clean = PLATFORM_MODULE_MAP.get(plat, plat)
                try:
                    mod = importlib.import_module(f"scrapers.{plat_clean}")
                    if not hasattr(mod, "scrape"):
                        results[uf][plat_clean] = {"status": "SKIPPED", "reason": "No scrape function"}
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
                    
                    if inspect.iscoroutinefunction(mod.scrape):
                        res = await mod.scrape(**kwargs)
                    else:
                        res = await asyncio.to_thread(mod.scrape, **kwargs)
                        
                    results[uf][plat_clean] = {
                        "status": "PASS",
                        "kwargs_sent": kwargs,
                        "exception": None
                    }
                except Exception as e:
                    results[uf][plat_clean] = {
                        "status": "FAIL",
                        "kwargs_sent": kwargs if 'kwargs' in locals() else {},
                        "exception": f"{type(e).__name__}: {str(e)}"
                    }
    return results

async def test_fastapi_trigger_endpoint_payloads():
    """Empirically tests /api/trigger endpoint for all UFs and verifies is_job_relevant settings."""
    trigger_results = {}
    
    with patch("app.insert_jobs", return_value=1) as mock_db:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
            for uf in UFS:
                captured_is_job_relevant_calls = []
                captured_scraper_calls = {}
                
                # Setup scraper mocks to capture kwargs passed by app.py
                mock_scrapers = {}
                for plat in ALL_PLATFORMS:
                    plat_clean = PLATFORM_MODULE_MAP.get(plat, plat)
                    try:
                        mod = importlib.import_module(f"scrapers.{plat_clean}")
                        orig_scrape = getattr(mod, "scrape", None)
                        if orig_scrape:
                            dummy_job = {
                                "title": f"Desenvolvedor Python {uf}",
                                "company": "Empresa Teste",
                                "location": f"Cidade - {uf}",
                                "platform": plat_clean,
                                "requirements": f"Requisitos Python {uf}"
                            }
                            
                            if inspect.iscoroutinefunction(orig_scrape):
                                async def mock_async_scrape(p_clean=plat_clean, **kwargs):
                                    captured_scraper_calls[p_clean] = kwargs
                                    return [dummy_job]
                                mock_scrapers[plat_clean] = patch.object(mod, "scrape", side_effect=mock_async_scrape)
                            else:
                                def mock_sync_scrape(p_clean=plat_clean, **kwargs):
                                    captured_scraper_calls[p_clean] = kwargs
                                    return [dummy_job]
                                mock_scrapers[plat_clean] = patch.object(mod, "scrape", side_effect=mock_sync_scrape)
                    except Exception:
                        pass
                
                # Start scraper patches
                for p_patch in mock_scrapers.values():
                    p_patch.start()
                    
                # Spy bot.is_job_relevant
                real_ijr = bot.is_job_relevant
                def spy_ijr(job, keyword, settings):
                    captured_is_job_relevant_calls.append({
                        "job": job,
                        "keyword": keyword,
                        "settings": dict(settings)
                    })
                    return real_ijr(job, keyword, settings)
                
                with patch("bot.is_job_relevant", side_effect=spy_ijr):
                    payload = {
                        "platforms": ALL_PLATFORMS,
                        "keyword": "Python",
                        "level": "Pleno",
                        "location": uf
                    }
                    
                    response = await client.post("/api/trigger", json=payload)
                    status_code = response.status_code
                    resp_data = response.json()
                    
                    # Wait for background task run_hunt_background to complete
                    await asyncio.sleep(0.5)
                    
                    # Stop scraper patches
                    for p_patch in mock_scrapers.values():
                        p_patch.stop()
                    
                    # Evaluate assertions
                    settings_locations = [c["settings"].get("location") for c in captured_is_job_relevant_calls]
                    exact_location_passed = all(loc == uf for loc in settings_locations) if settings_locations else False
                    
                    trigger_results[uf] = {
                        "status_code": status_code,
                        "response_status": resp_data.get("status"),
                        "response_message": resp_data.get("message"),
                        "scrapers_called_count": len(captured_scraper_calls),
                        "captured_scraper_kwargs": captured_scraper_calls,
                        "is_job_relevant_calls_count": len(captured_is_job_relevant_calls),
                        "settings_locations_received": list(set(settings_locations)),
                        "exact_uf_in_settings_verified": exact_location_passed
                    }
                    
    return trigger_results

def test_is_job_relevant_location_filtering():
    """Empirically tests is_job_relevant filtering behavior for each UF against matching vs non-matching jobs."""
    uf_filtering_results = {}
    
    test_cases_by_uf = {
        "SP": [("Dev Python SP", "São Paulo - SP", True), ("Dev Python RJ", "Rio de Janeiro - RJ", False)],
        "RJ": [("Dev Python RJ", "Rio de Janeiro - RJ", True), ("Dev Python SP", "São Paulo - SP", False)],
        "MG": [("Dev Python BH", "Belo Horizonte - MG", True), ("Dev Python PR", "Curitiba - PR", False)],
        "PR": [("Dev Python CWB", "Curitiba - PR", True), ("Dev Python RS", "Porto Alegre - RS", False)],
        "RS": [("Dev Python POA", "Porto Alegre - RS", True), ("Dev Python SC", "Florianópolis - SC", False)],
        "SC": [("Dev Python Floripa", "Florianópolis - SC", True), ("Dev Python BA", "Salvador - BA", False)],
        "BA": [("Dev Python SSA", "Salvador - BA", True), ("Dev Python SP", "São Paulo - SP", False)]
    }
    
    for uf, test_jobs in test_cases_by_uf.items():
        uf_filtering_results[uf] = []
        settings = {"level": "Todos", "location": uf, "contract": "Todos", "education": "Todos"}
        for title, job_loc, expected_relevant in test_jobs:
            job = {
                "title": title,
                "company": "Empresa Teste",
                "location": job_loc,
                "platform": "gupy",
                "requirements": "Requisitos mínimos com Python e SQL bastante detalhados para passar no filtro de tamanho"
            }
            res = bot.is_job_relevant(job, "Python", settings)
            passed_test = (res == expected_relevant)
            uf_filtering_results[uf].append({
                "job_title": title,
                "job_location": job_loc,
                "expected": expected_relevant,
                "actual": res,
                "pass": passed_test
            })
            
    return uf_filtering_results

async def main():
    print("Executing Scraper Signature Check...")
    sig_info = check_scraper_signatures()
    
    print("Executing Scraper Direct Location Test...")
    scraper_direct_res = await test_scraper_invocation_with_location()
    
    print("Executing FastAPI /api/trigger Endpoint Test...")
    trigger_endpoint_res = await test_fastapi_trigger_endpoint_payloads()
    
    print("Executing is_job_relevant Location Filtering Test...")
    ijr_filter_res = test_is_job_relevant_location_filtering()
    
    summary = {
        "scraper_signatures": sig_info,
        "scraper_direct_invocation": scraper_direct_res,
        "trigger_endpoint": trigger_endpoint_res,
        "is_job_relevant_filtering": ijr_filter_res
    }
    
    out_path = os.path.abspath(".agents/teamwork_preview_challenger_state_2/empirical_results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
        
    print(f"\nEmpirical verification finished! Saved full details to: {out_path}")

if __name__ == "__main__":
    asyncio.run(main())
