import json
import urllib.parse
import hashlib
import asyncio
from typing import List, Dict, Any
import httpx
from scrapers.utils import construir_termo_busca, encode_param

try:
    from curl_cffi import requests as requests_cffi
except ImportError:
    requests_cffi = None

async def scrape(keyword: str = "", location: str = "", category: str = "", seniority: str = "", level: str = "Todos", max_pages: int = 10, country: str = "", **kwargs) -> List[Dict[str, Any]]:
    jobs = []
    
    loc_clean = (location or country or kwargs.get("location") or kwargs.get("country") or "").strip()
    if loc_clean.upper() in ["USA", "US", "UNITED STATES"]:
        return jobs

    termo = construir_termo_busca(keyword, category, seniority or level)
    if not termo:
        termo = "Vagas"

    is_remote = "remoto" in loc_clean.lower() or "remote" in loc_clean.lower()
    search_query = f"{termo} {loc_clean}".strip() if loc_clean and not is_remote else termo

    params = {
        "jobName": search_query,
        "limit": 50,
        "offset": 0
    }
    if is_remote:
        params["workplaceType"] = "remote"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json"
    }

    try:
        async with httpx.AsyncClient(timeout=10.0, headers=headers, follow_redirects=True) as client:
            response = await client.get("https://portal.api.gupy.io/api/v1/jobs", params=params)
            if response.status_code == 200:
                data = response.json()
                items = data.get("data", [])
                if isinstance(items, list):
                    for item in items:
                        career_page = item.get("careerPageName", "")
                        job_id_raw = str(item.get("id"))
                        job_id = f"gupy_{job_id_raw}"
                        url = item.get("jobUrl") or (
                            f"https://{career_page}.gupy.io/jobs/{job_id_raw}" if career_page else f"https://gupy.io/jobs/{job_id_raw}"
                        )
                        
                        cidade = item.get("city", "")
                        estado = item.get("state", "")
                        loc_str = "Remoto" if item.get("isRemote") else f"{cidade}, {estado}".strip(", ") or (loc_clean or "Brasil")

                        job_obj = {
                            "id": job_id,
                            "platform": "Gupy",
                            "source": "Gupy",
                            "title": item.get("name", "Sem título"),
                            "company": career_page or "Gupy",
                            "location": loc_str,
                            "url": url,
                            "link": url,
                            "job_type": "CLT/PJ",
                            "profession": keyword or category or "Gupy Vagas",
                            "level": seniority or level or "Todos",
                            "requirements": str(item.get("description", "")) or f"{item.get('name', '')} na empresa {career_page or 'Gupy'}"
                        }
                        try:
                            from bot import classify_job_profession
                            job_obj = classify_job_profession(job_obj)
                        except Exception:
                            pass
                        jobs.append(job_obj)
    except Exception as e:
        print(f"[Gupy Scraper] Erro ao buscar '{search_query}': {e}")

    return jobs
