import json
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
        
        # Usa a nova API pública JSON da Gupy
        api_url = f"https://employability-portal.gupy.io/api/v1/jobs?jobName={encoded_kw}&limit=30"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json, text/plain, */*",
            "Referer": "https://employability-portal.gupy.io/",
        }
        
        r = None
        if requests_cffi:
            try:
                r = requests_cffi.get(api_url, headers=headers, impersonate="chrome110", timeout=15)
            except Exception:
                r = None
        if r is None:
            import requests as req_std
            r = req_std.get(api_url, headers=headers, timeout=15)
        
        if r.status_code == 200:
            try:
                api_data = r.json()
                job_list = api_data.get("data", []) or api_data.get("jobs", []) or []
            except Exception:
                # Fallback: tentar __NEXT_DATA__ do HTML
                soup = BeautifulSoup(r.text, 'html.parser')
                script = soup.find('script', id='__NEXT_DATA__')
                job_list = []
                if script and script.string:
                    ndata = json.loads(script.string)
                    job_list = ndata.get("props", {}).get("pageProps", {}).get("initialData", {}).get("jobs", [])
            
            for item in job_list[:30]:
                try:
                    title = item.get("name", "Sem Título")
                    company = item.get("careerPageName", "Empresa Confidencial")
                    link = item.get("jobUrl", api_url)
                    job_type = item.get("type", "CLT")
                    city = item.get("city", "")
                    state = item.get("state", "")
                    
                    desc = item.get("description", "")
                    if not desc:
                        desc = f"Vaga na empresa {company}. Local: {city} {state}."
                        
                    jobs.append({
                        "platform": "Gupy",
                        "title": title,
                        "company": company,
                        "budget": "A Combinar",
                        "link": link,
                        "job_type": job_type,
                        "profession": keyword,
                        "level": level,
                        "requirements": desc[:300] + "..." if len(desc) > 300 else desc
                    })
                except Exception:
                    continue
    except Exception as e:
        print("Erro Gupy:", e)
        
    return jobs
