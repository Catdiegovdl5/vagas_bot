import requests
import urllib.parse
import hashlib

def scrape(keyword="Python", level="Todos", location="", country="", **kwargs):
    c_str = (country or "").lower()
    l_str = (location or "").lower()
    loc = location or country or kwargs.get("location") or kwargs.get("country") or ""
    if loc and loc.upper() in ["USA", "US", "UNITED STATES"]:
        return []
        
    jobs = []
    try:
        kw = keyword or "Python"
        lvl = level or "Todos"
        repos = "repo:frontendbr/vagas repo:backend-br/vagas repo:react-brasil/vagas repo:qa-brasil/vagas"
        query = f"{repos} is:issue is:open {kw}"
        
        if lvl != "Todos":
            query += f" {lvl}"
        if loc and loc.lower() not in ["todos", "brasil", "brasil (remoto)", "remoto", "qualquer", ""]:
            query += f" {loc}"
            
        encoded_q = urllib.parse.quote(query)
        url = f"https://api.github.com/search/issues?q={encoded_q}&sort=created&order=desc&per_page=15"
        
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "SniperBot"
        }
        
        response = None
        try:
            response = requests.get(url, headers=headers, timeout=10.0)
        except Exception:
            response = None
            
        if response and response.status_code == 200:
            try:
                data = response.json()
            except Exception:
                data = {}
            if isinstance(data, dict):
                raw_items = data.get("items")
                items = raw_items if isinstance(raw_items, list) else []
                
                for item in items:
                    if not isinstance(item, dict):
                        continue
                    title = item.get("title", "Sem título")
                    html_url = item.get("html_url", "")
                    body = item.get("body", "Sem descrição")
                    
                    company = "Confidencial"
                    if " na " in title.lower():
                        parts = title.lower().split(" na ")
                        company = parts[-1].strip().title()
                    elif " @ " in title:
                        parts = title.split(" @ ")
                        company = parts[-1].strip()
                        
                    raw_labels = item.get("labels")
                    labels = [l.get("name", "") for l in raw_labels if isinstance(l, dict) and l.get("name")] if isinstance(raw_labels, list) else []
                    
                    job_type = "A Combinar"
                    labels_lower = [l.lower() for l in labels]
                    if "pj" in labels_lower: job_type = "PJ"
                    elif "clt" in labels_lower: job_type = "CLT"
                    else:
                        if "pj" in title.lower(): job_type = "PJ"
                        elif "clt" in title.lower(): job_type = "CLT"
                    
                    desc = body[:250] + "..." if body and len(body) > 250 else (body or "Sem descrição")
                    
                    job_id = hashlib.md5(html_url.encode('utf-8')).hexdigest()[:16]
                    job_obj = {
                        "id": job_id,
                        "platform": "GitHub Vagas",
                        "title": title,
                        "company": company,
                        "budget": "A Combinar",
                        "link": html_url,
                        "job_type": job_type,
                        "profession": keyword,
                        "level": level,
                        "requirements": f"Labels: {', '.join(labels)}\n\n{desc}" if labels else desc
                    }
                    try:
                        from bot import classify_job_profession
                        job_obj = classify_job_profession(job_obj)
                    except Exception:
                        pass
                    jobs.append(job_obj)
    except Exception as e:
        print("Erro GitHub Vagas:", e)
        
    return jobs

