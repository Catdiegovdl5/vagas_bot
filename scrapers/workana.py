import json
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
        if level != "Todos": search_kw += f" {level}"
        search_kw = urllib.parse.quote(search_kw)
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'Accept-Language': 'pt-BR,pt;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        }
        
        for page in [1, 2]:
            if len(jobs) >= 30:
                break
                
            url = f"https://www.workana.com/jobs?query={search_kw}&page={page}"
            
            r = None
            if requests_cffi:
                try:
                    r = requests_cffi.get(url, headers=headers, impersonate="chrome110", timeout=15)
                except Exception:
                    r = None
            if r is None:
                import requests
                r = requests.get(url, headers=headers, timeout=15)
                
            soup = BeautifulSoup(r.text, 'html.parser')
            
            # A Workana agora usa Vue.js, e os dados estão em um payload JSON dentro da tag <search>
            search_tag = soup.find('search')
            if not search_tag or not search_tag.has_attr(':results-initials'):
                continue
                
            data = json.loads(search_tag[':results-initials'])
            results = data.get('results', [])
            
            for item in results:
                if len(jobs) >= 30:
                    break
                
                # Extrair o título puro usando bs4 porque ele vem com tags HTML
                title_html = item.get('title', '')
                title_soup = BeautifulSoup(title_html, 'html.parser')
                title = title_soup.text.strip()
                if not title:
                    continue
                    
                slug = item.get('slug', '')
                link = f"https://www.workana.com/job/{slug}" if slug else url
                
                req_text = item.get('description', '')
                req_text = BeautifulSoup(req_text, 'html.parser').text.strip() # limpar html da description também
                
                budget = item.get('budget', 'A Combinar')
                
                jobs.append({
                    "platform": "Workana",
                    "title": title,
                    "company": "Cliente Workana",
                    "budget": budget,
                    "link": link,
                    "job_type": "PJ",
                    "profession": keyword,
                    "level": level,
                    "requirements": req_text
                })
            

    except Exception as e:
        print("Erro Workana:", e)
        
    return jobs
