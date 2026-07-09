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
        
        url = f"https://www.catho.com.br/vagas/{encoded_kw}/?q={encoded_kw}"
        
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
            job_cards = soup.find_all('article')
            
            for card in job_cards[:30]:
                try:
                    title_el = card.find('h2')
                    if not title_el:
                        continue
                        
                    title = title_el.text.strip()
                    
                    link_el = title_el.find('a', href=True)
                    if link_el:
                        link = link_el.get('href')
                        if link and not link.startswith('http'):
                            link = 'https://www.catho.com.br' + link
                    else:
                        link = url
                        
                    comp_el = card.find('p')
                    company = comp_el.text.strip() if comp_el else "Empresa Confidencial"
                    
                    salary_el = card.find('div', class_=lambda c: c and 'salary' in str(c).lower())
                    budget = salary_el.text.strip() if salary_el else "A Combinar"
                    
                    desc_el = card.find('span', class_=lambda c: c and 'description' in str(c).lower())
                    if not desc_el:
                        desc_el = card.find('div', class_=lambda c: c and 'description' in str(c).lower())
                    desc = desc_el.text.strip() if desc_el else f"Vaga para {title} na Catho."
                    
                    jobs.append({
                        "platform": "Catho",
                        "title": title,
                        "company": company,
                        "budget": budget,
                        "link": link,
                        "job_type": "CLT",
                        "profession": keyword,
                        "level": level,
                        "requirements": desc[:300] + "..." if len(desc) > 300 else desc
                    })
                except Exception as card_e:
                    continue
    except Exception as e:
        print("Erro Catho:", e)
        
    return jobs
