import urllib.parse
import asyncio
import unicodedata
import hashlib
from typing import List, Dict, Any
import httpx
from bs4 import BeautifulSoup
from scrapers.utils import construir_termo_busca, encode_param

try:
    from playwright.async_api import async_playwright
except ImportError:
    async_playwright = None

async def _scrape_httpx_fallback(search_kw: str, keyword: str, level: str) -> List[Dict[str, Any]]:
    jobs = []
    url = f"https://www.workana.com/jobs?query={encode_param(search_kw)}&language=pt"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }
    try:
        async with httpx.AsyncClient(timeout=10.0, headers=headers, follow_redirects=True) as client:
            response = await client.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                cards = soup.select(".project-item, .project-card, div[id^='project-']")
                for card in cards:
                    title_el = card.select_one(".project-title a, h2 a, a.project-title")
                    desc_el = card.select_one(".project-details, .expander, .description")
                    if title_el:
                        title = title_el.get_text(strip=True)
                        href = title_el.get("href", "")
                        link = href if href.startswith("http") else f"https://www.workana.com{href}"
                        req_text = desc_el.get_text(strip=True) if desc_el else card.get_text(strip=True)
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
        print(f"[Workana HTTP Fallback] Erro ao buscar '{search_kw}': {e}")
    return jobs

async def scrape(keyword: str = "", location: str = "", category: str = "", seniority: str = "", level: str = "Todos", max_pages: int = 10, country: str = "", **kwargs) -> List[Dict[str, Any]]:
    jobs = []
    termo = construir_termo_busca(keyword, category, seniority or level)
    if not termo:
        termo = "Python"

    search_kw = termo

    # 1. Tentar Playwright se disponível
    if async_playwright is not None:
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                url = f"https://www.workana.com/jobs?query={encode_param(search_kw)}&language=pt"
                await page.goto(url, timeout=15000, wait_until="domcontentloaded")
                await page.wait_for_selector(".project-item, .project-card", timeout=5000)

                cards = await page.query_selector_all(".project-item, .project-card")
                for card in cards[:20]:
                    title_el = await card.query_selector(".project-title a, h2 a")
                    if title_el:
                        title = await title_el.inner_text()
                        link = await title_el.get_attribute("href")
                        if link and not link.startswith("http"):
                            link = f"https://www.workana.com{link}"
                        
                        desc_el = await card.query_selector(".project-details, .expander")
                        req_text = await desc_el.inner_text() if desc_el else title

                        job_id = hashlib.md5(link.encode('utf-8')).hexdigest()[:16]
                        job_obj = {
                            "id": job_id,
                            "platform": "Workana",
                            "source": "Workana",
                            "title": title.strip(),
                            "company": "Cliente Workana",
                            "budget": "A Combinar",
                            "location": "Remoto",
                            "url": link,
                            "link": link,
                            "job_type": "PJ",
                            "profession": keyword or category or "Workana Vagas",
                            "level": seniority or level or "Todos",
                            "requirements": req_text.strip()
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
            print(f"[Workana Playwright Warning] {e}. Alternando para fallback HTTP...")

    # 2. Fallback seguro via HTTP / BeautifulSoup (funciona sem Playwright e sem erros de asyncio)
    return await _scrape_httpx_fallback(search_kw, keyword, seniority or level)
