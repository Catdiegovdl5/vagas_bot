import requests
from bs4 import BeautifulSoup
import urllib.parse

def scrape(keyword="Python", level="Todos", location="", country="", **kwargs):
    jobs = []
    try:
        search_kw = keyword or "Python"
        lvl = level or "Todos"
        loc = location or country or kwargs.get("location") or kwargs.get("country") or ""
        
        if lvl != "Todos":
            search_kw += f" {lvl}"
        if loc and loc.lower() not in ["todos", "brasil", "brasil (remoto)", "remoto", "qualquer", ""]:
            search_kw += f" {loc}"
            
        encoded_kw = urllib.parse.quote(search_kw)
        url = f"https://www.99freelas.com.br/projects?q={encoded_kw}"
        
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Seleciona os links diretamente dos títulos da classe .title a ou .project-title a
            links = soup.select('.title a, .project-title a, .result-item a.title')
            
            for a_tag in links[:15]:
                title = a_tag.text.strip() if (a_tag and getattr(a_tag, 'text', None)) else ""
                href = a_tag.get('href', '') if a_tag else ""
                if not title or not href or '#' in href:
                    continue
                    
                link = "https://www.99freelas.com.br" + href if href.startswith('/') else href
                
                # Busca elemento pai ou container do item para extrair a descrição
                parent = a_tag.find_parent('li') or a_tag.find_parent('div') if a_tag else None
                desc = "Sem descrição"
                if parent:
                    desc_el = parent.select_one('.description, .project-description, .summary')
                    if desc_el and getattr(desc_el, 'text', None):
                        desc = desc_el.text.strip()
                
                jobs.append({
                    "platform": "99Freelas",
                    "title": title,
                    "company": "Cliente 99Freelas",
                    "budget": "PJ - A Combinar",
                    "link": link,
                    "job_type": "Freelance / PJ",
                    "profession": keyword,
                    "level": level,
                    "requirements": desc[:250] + "..." if len(desc) > 250 else desc
                })
    except Exception as e:
        print("Erro 99Freelas:", e)
        
    return jobs
