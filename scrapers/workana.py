import urllib.parse
import asyncio
import unicodedata
import hashlib
from typing import List, Dict, Any
import httpx
from bs4 import BeautifulSoup
from scrapers.utils import construir_termo_busca, encode_param

try:
    from curl_cffi import requests as cffi_requests
except ImportError:
    cffi_requests = None

try:
    from playwright.async_api import async_playwright
except ImportError:
    async_playwright = None

def _scrape_curl_cffi(search_kw: str, keyword: str, level: str) -> List[Dict[str, Any]]:
    if not cffi_requests:
        return []
    jobs = []
    url = f"https://www.workana.com/jobs?query={encode_param(search_kw)}&language=en%2Cpt"
    try:
        response = cffi_requests.get(url, impersonate="chrome120", timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            cards = soup.select(".project-item, .project-card, div[id^='project-']")
            for card in cards:
                title_el = card.select_one(".project-title a, h2 a, a.project-title")
                desc_el = card.select_one(".project-details, .expander, .description")
                budget_el = card.select_one(".values, .budget")
                if title_el:
                    title = title_el.get_text(strip=True)
                    href = title_el.get("href", "")
                    link = href if href.startswith("http") else f"https://www.workana.com{href}"
                    req_text = desc_el.get_text(strip=True) if desc_el else card.get_text(strip=True)
                    budget = budget_el.get_text(strip=True) if budget_el else "A Combinar"
                    job_id = hashlib.md5(link.encode('utf-8')).hexdigest()[:16]

                    job_obj = {
                        "id": job_id,
                        "platform": "Workana",
                        "source": "Workana",
                        "title": title,
                        "company": "Cliente Workana",
                        "budget": budget,
                        "location": "Remoto",
                        "url": link,
                        "link": link,
                        "job_type": "PJ",
                        "profession": keyword or "Workana Vagas",
                        "level": level or "Todos",
                        "requirements": req_text
                    }
                    try:
                        from bot import classify_job_profession
                        job_obj = classify_job_profession(job_obj)
                    except Exception:
                        pass
                    jobs.append(job_obj)
    except Exception as e:
        print(f"[Workana curl_cffi Warning] {e}")
    return jobs

async def scrape(keyword: str = "", location: str = "", category: str = "", seniority: str = "", level: str = "Todos", max_pages: int = 10, country: str = "", **kwargs) -> List[Dict[str, Any]]:
    jobs = []
    termo = construir_termo_busca(keyword, category, seniority or level)
    if not termo:
        termo = "Python"

    search_kw = termo

    # 1. Tentar Playwright com renderização dinâmica segura
    if async_playwright is not None:
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
                page = await context.new_page()
                url = f"https://www.workana.com/jobs?query={encode_param(search_kw)}&language=en%2Cpt"
                await page.goto(url, timeout=15000, wait_until="domcontentloaded")
                await asyncio.sleep(3)

                links = await page.query_selector_all("a[href*='/job/']")
                seen_links = set()
                for l_el in links[:25]:
                    href = await l_el.get_attribute("href")
                    title = (await l_el.inner_text()).strip()
                    if href and title and len(title) > 5 and href not in seen_links:
                        seen_links.add(href)
                        link = href if href.startswith("http") else f"https://www.workana.com{href}"
                        job_id = hashlib.md5(link.encode('utf-8')).hexdigest()[:16]
                        job_obj = {
                            "id": job_id,
                            "platform": "Workana",
                            "source": "Workana",
                            "title": title,
                            "company": "Cliente Workana",
                            "budget": "A Combinar",
                            "location": "Remoto",
                            "url": link,
                            "link": link,
                            "job_type": "PJ",
                            "profession": keyword or category or "Workana Vagas",
                            "level": seniority or level or "Todos",
                            "requirements": f"Vaga de Freelance no Workana: {title}"
                        }
                        try:
                            from bot import classify_job_profession
                            job_obj = classify_job_profession(job_obj)
                        except Exception:
                            pass
                        jobs.append(job_obj)
                await browser.close()
                if jobs:
                    return jobs
        except Exception as e:
            print(f"[Workana Playwright Warning] {e}")

    # 2. Fallback via curl_cffi
    cffi_jobs = await asyncio.to_thread(_scrape_curl_cffi, search_kw, keyword, seniority or level)
    if cffi_jobs:
        return cffi_jobs

    return jobs
