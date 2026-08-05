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

async def scrape(keyword: str = "", location: str = "", category: str = "", seniority: str = "", level: str = "Todos", country: str = "", contract: str = "Todos", **kwargs) -> List[Dict[str, Any]]:
    jobs = []
    loc_clean = (location or country or kwargs.get("location") or kwargs.get("country") or "").strip()

    termo = construir_termo_busca(keyword, category, seniority or level)
    if not termo:
        termo = "Vagas"

    is_remote = "remoto" in loc_clean.lower() or "remote" in loc_clean.lower()

    url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={encode_param(termo)}"
    if is_remote:
        url += "&f_WT=2"
    elif loc_clean and loc_clean.lower() not in ["todos", "brasil", "remoto"]:
        url += f"&location={encode_param(loc_clean)}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7"
    }

    try:
        async with httpx.AsyncClient(timeout=12.0, headers=headers, follow_redirects=True) as client:
            response = await client.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                cards = soup.find_all("li")

                for card in cards:
                    title_el = card.find("h3", class_="base-search-card__title")
                    company_el = card.find("h4", class_="base-search-card__subtitle")
                    location_el = card.find("span", class_="job-search-card__location")
                    link_el = card.find("a", class_="base-card__full-link")

                    if title_el and link_el and link_el.get("href"):
                        job_url = link_el["href"].split("?")[0]
                        job_id_raw = job_url.split("-")[-1]
                        job_id = f"linkedin_{job_id_raw}" if job_id_raw else hashlib.md5(job_url.encode('utf-8')).hexdigest()[:16]

                        title_str = title_el.get_text(strip=True)
                        company_str = company_el.get_text(strip=True) if company_el else "LinkedIn"
                        loc_str = location_el.get_text(strip=True) if location_el else (loc_clean or "Brasil")

                        job_obj = {
                            "id": job_id,
                            "platform": "LinkedIn",
                            "source": "LinkedIn",
                            "title": title_str,
                            "company": company_str,
                            "location": loc_str,
                            "url": job_url,
                            "link": job_url,
                            "job_type": contract or "CLT/PJ",
                            "profession": keyword or category or "LinkedIn Vagas",
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
        print(f"[LinkedIn Scraper] Erro ao buscar '{termo}': {e}")

    return jobs
