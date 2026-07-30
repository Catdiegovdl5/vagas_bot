import pytest
import asyncio
import inspect
import importlib
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch

from app import app, PLATFORM_MODULE_MAP
import bot

UFS = ["SP", "RJ", "MG", "PR", "RS", "SC", "BA"]
ALL_PLATFORMS = [
    "workana", "gupy", "catho", "infojobs", "linkedin", "vagas_com",
    "novenove", "freelancer", "remotar", "programathor", "geekhunter",
    "coodesh", "github_vagas", "indeed", "glassdoor", "jooble"
]

@pytest.mark.asyncio
@pytest.mark.parametrize("uf", UFS)
async def test_api_trigger_location_propagation(uf):
    captured_ijr_settings = []
    captured_scraper_kwargs = {}
    
    patchers = []
    for plat in ALL_PLATFORMS:
        plat_clean = PLATFORM_MODULE_MAP.get(plat, plat)
        mod = importlib.import_module(f"scrapers.{plat_clean}")
        if hasattr(mod, "scrape"):
            dummy_job = {
                "title": f"Desenvolvedor Python {uf}",
                "company": f"Empresa {uf}",
                "location": f"Cidade - {uf}",
                "platform": plat_clean,
                "requirements": "Requisitos em Python e SQL com tamanho suficiente para o filtro de qualidade"
            }
            if inspect.iscoroutinefunction(mod.scrape):
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

    for p in patchers:
        p.start()

    real_ijr = bot.is_job_relevant
    def spy_ijr(job, keyword, settings):
        captured_ijr_settings.append(dict(settings))
        return real_ijr(job, keyword, settings)

    try:
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
                assert response.status_code == 200
                assert response.json()["status"] == "success"
                
                pending = [t for t in asyncio.all_tasks() if t != asyncio.current_task()]
                if pending:
                    await asyncio.gather(*pending, return_exceptions=True)

            # Assertions
            assert len(captured_scraper_kwargs) == len(ALL_PLATFORMS)
            for plat_clean, kwargs in captured_scraper_kwargs.items():
                assert kwargs.get("location") == uf or kwargs.get("country") == uf
                
            assert len(captured_ijr_settings) > 0
            for settings in captured_ijr_settings:
                assert settings.get("location") == uf
    finally:
        for p in patchers:
            p.stop()
