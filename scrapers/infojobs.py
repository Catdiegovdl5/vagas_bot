import asyncio
import hashlib
import urllib.parse
from typing import List, Dict, Any
import httpx
from bs4 import BeautifulSoup
from scrapers.utils import construir_termo_busca, encode_param

try:
    from curl_cffi import requests as requests_cffi
except ImportError:
    requests_cffi = None

async def scrape(keyword: str = "", location: str = "", category: str = "", seniority: str = "", level: str = "Todos", country: str = "", **kwargs) -> List[Dict[str, Any]]:
    jobs = []
    loc_clean = (location or country or kwargs.get("location") or kwargs.get("country") or "").strip()

    termo = construir_termo_busca(keyword, category, seniority or level)
    if not termo:
        termo = "vagas"

    search_query = f"{termo} {loc_clean}".strip() if loc_clean else termo
    url = f"https://www.infojobs.com.br/vagas-de-emprego-{encode_param(search_query)}.aspx"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }

    try:
        async with httpx.AsyncClient(timeout=10.0, headers=headers, follow_redirects=True) as client:
            response = await client.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                containers = soup.select("div.element-vaga, div.js_rowVaga")

                for container in containers:
                    title_el = container.select_one("h2.h3, a[js-title-vaga], a.text-decoration-none")
                    company_el = container.select_one(".container-vaga-company, .company-name, div.text-subtle")
                    location_el = container.select_one(".container-vaga-location, .location, span.text-subtle")

                    if title_el:
                        href = title_el.get("href", "")
                        if href:
                            full_url = href if href.startswith("http") else f"https://www.infojobs.com.br{href}"
                            job_id_raw = full_url.split("/")[-1].replace(".aspx", "")
                            job_id = f"infojobs_{job_id_raw}" if job_id_raw else hashlib.md5(full_url.encode('utf-8')).hexdigest()[:16]

                            title_str = title_el.get_text(strip=True)
                            company_str = company_el.get_text(strip=True) if company_el else "InfoJobs"
                            loc_str = location_el.get_text(strip=True) if location_el else (loc_clean or "Brasil")

                            job_obj = {
                                "id": job_id,
                                "platform": "InfoJobs",
                                "source": "InfoJobs",
                                "title": title_str,
                                "company": company_str,
                                "location": loc_str,
                                "url": full_url,
                                "link": full_url,
                                "job_type": "CLT/PJ",
                                "profession": keyword or category or "InfoJobs Vagas",
                                "level": seniority or level or "Todos",
                                "requirements": f"{title_str} na empresa {company_str} ({loc_str})."
                            }
                            try:
                                from bot import classify_job_profession
                                job_obj = classify_job_profession(job_obj)
                            except Exception:
                                pass
                            jobs.append(job_obj)
    except Exception as e:
        print(f"[InfoJobs Scraper] Erro ao buscar '{search_query}': {e}")

    return jobs
