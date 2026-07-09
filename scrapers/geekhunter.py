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
        if level != "Todos":
            search_kw += f" {level}"
        encoded_kw = urllib.parse.quote(search_kw)
        
        # URL atualizada com subdomínio e rota pt/vagas
        url = f"https://www.geekhunter.com/pt/vagas?q={encoded_kw}"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            "Referer": "https://www.geekhunter.com/pt/vagas",
        }
        
        r = None
        if requests_cffi:
            try:
                r = requests_cffi.get(url, headers=headers, impersonate="chrome110", timeout=15)
            except Exception:
                r = None
        if r is None:
            import requests as req_std
            r = req_std.get(url, headers=headers, timeout=15)
            
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            
            # Encontra todos os links de vaga pré-renderizados no HTML
            links = soup.find_all('a', href=lambda h: h and '/jobs/' in h)
            
            for card in links[:30]:
                try:
                    href = card.get('href') or ''
                    if not href.startswith('http'):
                        job_url = urllib.parse.urljoin("https://www.geekhunter.com", href)
                    else:
                        job_url = href
                        
                    # Extrai a empresa a partir do slug no path da URL
                    parts = job_url.split('/')
                    company = "Empresa via GeekHunter"
                    if 'pt' in parts:
                        pt_idx = parts.index('pt')
                        if pt_idx + 1 < len(parts):
                            company_slug = parts[pt_idx + 1]
                            if company_slug != 'jobs' and company_slug != 'vagas':
                                company = company_slug.replace('-', ' ').title()
                    
                    # Título
                    title_el = card.find('p', class_=lambda c: c and 'q4uo1b' in c) or card.find('p')
                    if not title_el:
                        continue
                    title = title_el.text.strip()
                    # Limpa prefixos de oportunidade
                    if "Oportunidade |" in title:
                        title = title.replace("Oportunidade |", "").strip()
                    elif "Oportunidade" in title and "|" in title:
                        title = title.split("|", 1)[1].strip()
                        
                    if not title:
                        continue
                        
                    # Salário/Budget
                    budget = "A Combinar"
                    salary_el = card.find('p', class_=lambda c: c and 'o118sj' in c)
                    if salary_el:
                        budget = salary_el.text.strip()
                    else:
                        # Fallback: procura por textos de salário
                        p_tags = card.find_all('p')
                        for p in p_tags:
                            p_text = p.text.strip()
                            if "R$" in p_text or "$" in p_text:
                                budget = p_text
                                break
                    
                    # Tipo de contratação
                    j_type = "CLT/PJ"
                    type_el = card.find('p', class_=lambda c: c and '2fkfcz' in c)
                    if type_el:
                        j_type = type_el.text.strip()
                    
                    # Skills/Requirements
                    skill_elements = card.find_all('div', class_=lambda c: c and 'dqhvn' in c)
                    skills = [s.text.strip() for s in skill_elements if s.text.strip()]
                    if skills:
                        reqs = ", ".join(skills)
                    else:
                        reqs = f"Vaga para {title} na GeekHunter."
                        
                    jobs.append({
                        "platform": "GeekHunter",
                        "title": title,
                        "company": company,
                        "budget": budget,
                        "link": job_url,
                        "job_type": j_type,
                        "profession": keyword,
                        "level": level,
                        "requirements": reqs
                    })
                except Exception as card_e:
                    continue
    except Exception as e:
        print("Erro GeekHunter:", e)
        
    return jobs
