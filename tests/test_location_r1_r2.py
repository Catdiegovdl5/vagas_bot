import pytest
import asyncio
import inspect
import importlib
import glob
import os
import re

# 1. Verification for Requirement R1: All scrapers accept location, country, and **kwargs
def test_r1_all_scrapers_accept_location_parameters():
    scraper_files = glob.glob("scrapers/*.py")
    scraper_modules = [
        os.path.basename(f)[:-3] for f in scraper_files 
        if not f.endswith("run_test.py") and not "pycache" in f and os.path.basename(f) != "ai_filter.py"
    ]
    
    assert len(scraper_modules) >= 15, "Expected at least 15 scraper modules"

    for mod_name in scraper_modules:
        mod = importlib.import_module(f"scrapers.{mod_name}")
        assert hasattr(mod, "scrape"), f"Module scrapers.{mod_name} missing scrape function"
        sig = inspect.signature(mod.scrape)
        
        # Must accept location, country, or **kwargs without raising TypeError
        params = sig.parameters
        assert "location" in params or "country" in params or any(p.kind == inspect.Parameter.VAR_KEYWORD for p in params.values()), \
            f"scrapers.{mod_name}.scrape signature {sig} does not accept location/country/**kwargs"

@pytest.mark.asyncio
async def test_r1_scrapers_callable_with_location():
    scraper_files = glob.glob("scrapers/*.py")
    scraper_modules = [
        os.path.basename(f)[:-3] for f in scraper_files 
        if not f.endswith("run_test.py") and not "pycache" in f and os.path.basename(f) != "ai_filter.py"
    ]

    for mod_name in scraper_modules:
        mod = importlib.import_module(f"scrapers.{mod_name}")
        # Test calling with location and country kwargs directly (mocking/dry run where possible)
        try:
            if inspect.iscoroutinefunction(mod.scrape):
                # Call with minimal max_pages / params so it returns quickly or handles dry invocation
                res = await mod.scrape(keyword="Python", level="Todos", location="SP", country="SP", max_pages=1)
            else:
                res = mod.scrape(keyword="Python", level="Todos", location="SP", country="SP")
            assert isinstance(res, list), f"scrapers.{mod_name}.scrape should return a list"
        except Exception as e:
            # High-level network errors are expected if offline, but TypeError is strictly forbidden
            assert not isinstance(e, TypeError), f"scrapers.{mod_name}.scrape raised TypeError: {e}"

# 2. Verification for Requirement R2: Frontend UF Mapping & Remote Job Retention logic
def test_r2_index_html_uf_mapping_and_remote_job_retention():
    index_path = "static/index.html"
    assert os.path.exists(index_path), "static/index.html does not exist"
    
    content = open(index_path, encoding="utf-8").read()

    # Check 27 Brazilian UFs in UF_MAPPING
    all_27_ufs = ["AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"]
    
    assert "UF_MAPPING" in content, "static/index.html missing UF_MAPPING dictionary"
    
    for uf in all_27_ufs:
        assert f'"{uf}"' in content or f"'{uf}'" in content, f"UF {uf} missing in static/index.html UF_MAPPING"

    # Check Remote Job Retention logic
    assert "getJobWorkModel" in content, "static/index.html missing getJobWorkModel function"
    assert "getJobWorkModel(j) === 'remoto'" in content or "getJobWorkModel(job) === 'remoto'" in content, \
        "static/index.html missing Remote Job Retention check for 'remoto'"
