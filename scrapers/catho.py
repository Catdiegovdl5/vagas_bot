import urllib.parse
import hashlib
from bs4 import BeautifulSoup
import asyncio

try:
    from curl_cffi import requests as requests_cffi
except ImportError:
    requests_cffi = None

async def scrape(keyword="Python", level="Todos", max_pages=10, location="", country="", **kwargs):
    jobs = []
    c_str = (country or "").lower()
    l_str = (location or "").lower()
    loc = location or country or kwargs.get("location") or kwargs.get("country") or ""
    if loc and loc.upper() in ["USA", "US", "UNITED STATES"]:
        return jobs
        
    try:
        catho_mapping = {
            "operações físicas":            "operador producao manutencao industrial",
            "operacoes fisicas":            "operador producao manutencao industrial",
            "indústria":                    "industrial fabrica",
            "industria":                    "industrial fabrica",
            "logística":                    "logistica estoque almoxarifado",
            "logistica":                    "logistica estoque almoxarifado",
            "administrativo":               "assistente administrativo escritorio",
            "criativos de performance":     "designer copywriter editor de video",
            "criativos":                    "designer copywriter editor de video",
            "inteligência de vendas":       "sdr bdr inside sales executivo de vendas",
            "inteligencia de vendas":       "sdr bdr inside sales executivo de vendas",
            "vendas":                       "executivo de vendas comercial",
            "engenharia de ia/dados":       "engenheiro de dados machine learning ia",
            "engenharia de ia dados":       "engenheiro de dados machine learning ia",
            "engenharia de dados":          "engenheiro de dados etl",
        }

        kw_str = keyword or "Python"
        kw_clean = kw_str.lower().strip()
        search_kw = catho_mapping.get(kw_clean, kw_str)
        lvl = level or "Todos"
        if lvl != "Todos": 
            search_kw += f" {lvl}"
        if loc and loc.lower() not in ["todos", "brasil", "brasil (remoto)", "remoto", "qualquer"]:
            search_kw += f" {loc}"
        encoded_kw = urllib.parse.quote(search_kw)
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        async def fetch_page(session, page):
            url = f"https://www.catho.com.br/vagas/{encoded_kw}/?q={encoded_kw}&page={page}"
            try:
                if session:
                    r = await session.get(url, headers=headers, impersonate="chrome110", timeout=10.0)
                else:
                    import httpx
                    async with httpx.AsyncClient(timeout=10.0) as client:
                        r = await client.get(url, headers=headers, timeout=10.0)
                if r.status_code == 200:
                    return r
            except Exception as e:
                print(f"Erro ao buscar página {page} no Catho: {e}")
            return None

        if requests_cffi and hasattr(requests_cffi, "AsyncSession"):
            async with requests_cffi.AsyncSession() as session:
                tasks = [fetch_page(session, page) for page in range(1, max_pages + 1)]
                responses = await asyncio.gather(*tasks)
        else:
            tasks = [fetch_page(None, page) for page in range(1, max_pages + 1)]
            responses = await asyncio.gather(*tasks)

        for r in responses:
            if not r:
                continue
            soup = BeautifulSoup(r.text, 'html.parser')
            job_cards = soup.find_all('article')
            
            for card in job_cards:
                try:
                    title_el = card.find('h2')
                    if not title_el:
                        continue
                        
                    title = title_el.text.strip() if (title_el and getattr(title_el, 'text', None)) else ""
                    if not title:
                        continue
                        
                    link_el = title_el.find('a', href=True) if title_el else None
                    if link_el:
                        link = link_el.get('href')
                        if link and not link.startswith('http'):
                            link = 'https://www.catho.com.br' + link
                    else:
                        link = f"https://www.catho.com.br/vagas/{encoded_kw}/?q={encoded_kw}"
                        
                    comp_el = card.find('p')
                    company = comp_el.text.strip() if (comp_el and getattr(comp_el, 'text', None)) else "Empresa Confidencial"
                    
                    salary_el = card.find('div', class_=lambda c: c and 'salary' in str(c).lower())
                    budget = salary_el.text.strip() if (salary_el and getattr(salary_el, 'text', None)) else "A Combinar"
                    
                    desc_el = card.find('span', class_=lambda c: c and 'description' in str(c).lower())
                    if not desc_el:
                        desc_el = card.find('div', class_=lambda c: c and 'description' in str(c).lower())
                    desc = desc_el.text.strip() if (desc_el and getattr(desc_el, 'text', None)) else f"Vaga para {title} na Catho."
                    
                    job_id = hashlib.md5(link.encode('utf-8')).hexdigest()[:16]
                    job_obj = {
                        "id": job_id,
                        "platform": "Catho",
                        "title": title,
                        "company": company,
                        "budget": budget,
                        "link": link,
                        "job_type": "CLT",
                        "profession": keyword,
                        "level": level,
                        "requirements": desc
                    }
                    try:
                        from bot import classify_job_profession
                        job_obj = classify_job_profession(job_obj)
                    except Exception:
                        pass
                    jobs.append(job_obj)
                except Exception as card_e:
                    continue
    except Exception as e:
        print("Erro Catho:", e)
        
    return jobs
