import urllib.parse

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
        
        # Consome a API pública da Coodesh
        api_url = f"https://api.coodesh.com/v2/jobs?search={encoded_kw}&pageSize=30"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'referer': 'https://coodesh.com/',
            'x-csh-key': 'coodesh-experts',
            'x-language': 'pt'
        }
        
        r = None
        if requests_cffi:
            try:
                r = requests_cffi.get(api_url, headers=headers, impersonate="chrome110", timeout=15)
            except Exception:
                r = None
        if r is None:
            import requests
            r = requests.get(api_url, headers=headers, timeout=15)
            
        if r.status_code == 200:
            data = r.json()
            docs = data.get('docs', [])
            for item in docs:
                title = item.get('title', '')
                if not title:
                    continue
                
                slug = item.get('slug', '')
                link = f"https://coodesh.com/vagas/{slug}" if slug else "https://coodesh.com/vagas"
                
                company_info = item.get('company')
                company = company_info.get('company_name') if company_info else "Tech Startup (Coodesh)"
                if not company:
                    company = "Tech Startup (Coodesh)"
                
                # Trata salário/budget
                salary = item.get('salary_range_formatted') or "A Combinar"
                if "negoci" in salary.lower():
                    salary = "A Combinar"
                
                # Trata skills/requirements
                skills_list = [s.get('name') for s in item.get('skills', []) if s.get('name')]
                if skills_list:
                    reqs = ", ".join(skills_list)
                else:
                    reqs = f"Vaga para {title} na Coodesh."
                
                # Tipo de contratação
                job_type_formatted = item.get('job_type_formatted') or "CLT/PJ"
                
                jobs.append({
                    "platform": "Coodesh",
                    "title": title,
                    "company": company,
                    "budget": salary,
                    "link": link,
                    "job_type": job_type_formatted,
                    "profession": keyword,
                    "level": level,
                    "requirements": reqs
                })
    except Exception as e:
        print("Erro Coodesh:", e)
        
    return jobs
