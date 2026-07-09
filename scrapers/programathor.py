import urllib.parse
from bs4 import BeautifulSoup

try:
    from curl_cffi import requests as requests_cffi
except ImportError:
    requests_cffi = None

def scrape(keyword, level="Todos", country="Brasil"):
    jobs = []
    if "Brasil" not in country:
        return jobs
        
    try:
        search_kw = keyword
        if level != "Todos": search_kw += f" {level}"
        encoded_kw = urllib.parse.quote(search_kw)
        
        url = f"https://programathor.com.br/jobs?text={encoded_kw}"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        if not requests_cffi:
            import requests
            r = requests.get(url, headers=headers, timeout=15)
        else:
            r = requests_cffi.get(url, headers=headers, impersonate="chrome110", timeout=15)
            
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            job_cards = soup.find_all('div', class_=lambda c: c and 'cell-list' in str(c).lower())
            
            for card in job_cards[:30]:
                try:
                    title_el = card.find('h3')
                    if not title_el:
                        continue
                        
                    title = title_el.text.strip()
                    
                    link_el = card.find('a', href=True)
                    if link_el:
                        link = link_el.get('href')
                        if link and not link.startswith('http'):
                            link = 'https://programathor.com.br' + link
                    else:
                        link = url
                        
                    comp_el = card.find('div', class_=lambda c: c and 'logo' in str(c).lower())
                    company = comp_el.get('title', "Empresa Confidencial") if comp_el else "Empresa Confidencial"
                    
                    tags = card.find_all('span', class_=lambda c: c and 'tag' in str(c).lower())
                    tags_text = " | ".join([t.text.strip() for t in tags])
                    
                    jobs.append({
                        "platform": "ProgramaThor",
                        "title": title,
                        "company": company,
                        "budget": "A Combinar",
                        "link": link,
                        "job_type": "CLT/PJ",
                        "profession": keyword,
                        "level": level,
                        "requirements": tags_text if tags_text else f"Vaga para {title} no ProgramaThor."
                    })
                except Exception as card_e:
                    continue
    except Exception as e:
        print("Erro ProgramaThor:", e)
        
    return jobs
