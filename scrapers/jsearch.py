import requests
import urllib.parse
import os
import hashlib

def scrape(keyword="Python", level="Todos", location="", country="", **kwargs):
    jobs = []
    c_str = (country or "").lower()
    l_str = (location or "").lower()
    target_loc = location or country or kwargs.get("location") or kwargs.get("country") or ""
    try:
        api_key = os.environ.get("JSEARCH_API_KEY", "")
        if not api_key:
            print("JSearch: JSEARCH_API_KEY não configurada. Pulando scraper.")
            return jobs
        
        kw = keyword or "Python"
        lvl = level or "Todos"
        search_kw = f"{kw}"
        if lvl != "Todos":
            search_kw += f" {lvl}"
        if target_loc and target_loc.lower() not in ["todos", "brasil", "brasil (remoto)", "remoto", "qualquer", ""] and target_loc.upper() not in ["USA", "US"]:
            search_kw += f" {target_loc}"
            
        encoded_kw = urllib.parse.quote(search_kw)
        
        if target_loc and target_loc.upper() in ["USA", "US"]:
            url = f"https://jsearch.p.rapidapi.com/search?query={encoded_kw}&page=1&num_pages=3&date_posted=month&country=us&language=en"
        else:
            url = f"https://jsearch.p.rapidapi.com/search?query={encoded_kw}&page=1&num_pages=3&date_posted=month&country=br&language=pt"
        
        headers = {
            "x-rapidapi-key": api_key,
            "x-rapidapi-host": "jsearch.p.rapidapi.com"
        }
        
        response = None
        try:
            response = requests.get(url, headers=headers, timeout=10.0)
        except Exception:
            response = None
            
        if not response:
            return jobs
        
        if response.status_code == 404:
            print("JSearch: Endpoint não encontrado (404). Verifique se sua API Key é válida e está ativa no RapidAPI.")
            return jobs
        elif response.status_code == 403:
            print("JSearch: Acesso negado (403). Verifique se sua API Key do RapidAPI está correta.")
            return jobs
        elif response.status_code == 429:
            print("JSearch: Limite de requisições atingido (429). Aguarde antes de tentar novamente.")
            return jobs
        elif response.status_code != 200:
            print(f"JSearch: Erro HTTP {response.status_code}.")
            return jobs
            
        try:
            data = response.json()
        except Exception:
            data = {}
            
        if isinstance(data, dict):
            if "message" in data:
                print(f"JSearch API mensagem: {data['message']}")
                return jobs
            
            raw_data = data.get("data")
            if isinstance(raw_data, list):
                for item in raw_data[:30]:
                    if not isinstance(item, dict):
                        continue
                    title = item.get("job_title", "Sem título")
                    j_type = "PJ" if "PJ" in title.upper() else "CLT"
                    
                    desc = item.get("job_description", "")
                    if len(desc) > 150:
                        req_text = desc[:150].replace('\n', ' ') + "..."
                    else:
                        req_text = desc.replace('\n', ' ')
                    
                    if not req_text.strip():
                        req_text = "Sem descrição disponível."
                    
                    link = item.get("job_apply_link") or item.get("job_google_link") or ""
                    
                    # Guard: descartar vagas sem link válido ou sem título real
                    if not title or not link or link == "#":
                        continue
                    
                    jsearch_id = item.get("job_id") or link
                    job_id = hashlib.md5(str(jsearch_id).encode('utf-8')).hexdigest()[:16]
                    job_obj = {
                        "id": job_id,
                        "platform": f"JSearch",
                        "title": title,
                        "company": item.get("employer_name", "Confidencial"),
                        "budget": "A Combinar",
                        "link": link,
                        "job_type": j_type,
                        "profession": keyword,
                        "level": level,
                        "requirements": req_text
                    }
                    try:
                        from bot import classify_job_profession
                        job_obj = classify_job_profession(job_obj)
                    except Exception:
                        pass
                    jobs.append(job_obj)
    except Exception as e:
        print("Erro JSearch:", e)
    
    return jobs

