import requests
import urllib.parse
from bs4 import BeautifulSoup

try:
    from curl_cffi import requests as requests_cffi
except ImportError:
    requests_cffi = None

def scrape(keyword="Python", level="Todos"):
    jobs = []
    try:
        search_kw = keyword
        if level != "Todos":
            search_kw += f" {level}"
        encoded_kw = urllib.parse.quote(search_kw)
        
        # Consome a API pública da Remotar
        url = f"https://api.remotar.com.br/jobs?search={encoded_kw}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'Referer': 'https://remotar.com.br/',
        }
        
        r = None
        if requests_cffi:
            try:
                r = requests_cffi.get(url, headers=headers, impersonate="chrome110", timeout=15)
            except Exception:
                r = None
        if r is None:
            r = requests.get(url, headers=headers, timeout=15)
            
        if r.status_code == 200:
            data = r.json()
            results = data.get('data', [])
            for item in results[:30]:
                title = item.get('title', '')
                if not title:
                    continue
                
                company = "Start-up Gringa"
                if item.get('company') and item.get('company').get('name'):
                    company = item.get('company').get('name')
                elif item.get('companyDisplayName'):
                    company = item.get('companyDisplayName')
                
                # Link original da vaga
                job_url = item.get('externalLink') or f"https://remotar.com.br/search?q={encoded_kw}"
                
                # Tipo de contratação
                title_upper = title.upper()
                j_type = "PJ" if "PJ" in title_upper or "FREELANCE" in title_upper else "CLT"
                
                # Salário/Budget
                budget = "A Combinar"
                salary_info = item.get('jobSalary')
                if salary_info and salary_info.get('type') != 'uninformed':
                    curr = salary_info.get('currency') or 'BRL'
                    val_from = salary_info.get('from')
                    val_to = salary_info.get('to')
                    if val_from or val_to:
                        budget = f"{curr} {val_from or 0} - {val_to or 0}"
                
                # Descrição limpa
                sub = item.get('subtitle') or ''
                desc_html = item.get('description') or ''
                more = item.get('moreInfos') or ''
                
                full_html = f"<p>{sub}</p> {desc_html} <p>{more}</p>"
                clean_text = BeautifulSoup(full_html, 'html.parser').get_text(separator=' ').strip()
                
                # Remover espaços extras
                req_text = " ".join(clean_text.split())
                if not req_text:
                    req_text = f"Vaga 100% Remota. Requisitos: proficiência em {keyword}."
                
                jobs.append({
                    "platform": "Remotar",
                    "title": title,
                    "company": company,
                    "budget": budget,
                    "link": job_url,
                    "job_type": j_type,
                    "profession": keyword,
                    "level": level,
                    "requirements": req_text
                })
                
    except Exception as e:
        print(f"Remotar Scraper Error: {e}")
    return jobs
