import requests
import urllib.parse
import hashlib

def scrape(keyword="Python", level="Todos", location="", country="", **kwargs):
    jobs = []
    c_str = (country or "").lower()
    l_str = (location or "").lower()
    loc = location or country or kwargs.get("location") or kwargs.get("country") or ""
    try:
        search_kw = keyword or "Python"
        lvl = level or "Todos"
        if lvl != "Todos":
            search_kw += f" {lvl}"
        if loc and loc.lower() not in ["todos", "brasil", "brasil (remoto)", "remoto", "qualquer", ""]:
            search_kw += f" {loc}"
        encoded_kw = urllib.parse.quote(search_kw)
        url = f"https://www.freelancer.com/api/projects/0.1/projects/active/?query={encoded_kw}&limit=15"
        
        headers = {"User-Agent": "Mozilla/5.0"}
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
                res_obj = data.get("result")
                if isinstance(res_obj, dict):
                    projects = res_obj.get("projects")
                    if isinstance(projects, list):
                        for item in projects:
                            if not isinstance(item, dict):
                                continue
                            title = item.get("title") or "Sem título"
                            desc = item.get("description") or "Sem descrição"
                            
                            seo_url = item.get("seo_url", "")
                            link = f"https://www.freelancer.com/projects/{seo_url}" if seo_url else "https://www.freelancer.com"
                            
                            b_obj = item.get("budget")
                            b_dict = b_obj if isinstance(b_obj, dict) else {}
                            budget_min = b_dict.get("minimum") or 0
                            budget_max = b_dict.get("maximum") or 0
                            
                            c_obj = item.get("currency")
                            c_dict = c_obj if isinstance(c_obj, dict) else {}
                            currency = c_dict.get("code", "USD")
                            budget_str = f"{currency} {budget_min} - {budget_max}" if budget_max > 0 else "A Combinar"
                            
                            job_id = hashlib.md5(link.encode('utf-8')).hexdigest()[:16]
                            job_obj = {
                                "id": job_id,
                                "platform": "Freelancer.com",
                                "title": title,
                                "company": "Cliente Freelancer.com",
                                "budget": f"PJ - {budget_str}",
                                "link": link,
                                "job_type": "Freelance / PJ",
                                "profession": keyword,
                                "level": level,
                                "requirements": desc[:250] + "..." if len(desc) > 250 else desc
                            }
                            try:
                                from bot import classify_job_profession
                                job_obj = classify_job_profession(job_obj)
                            except Exception:
                                pass
                            jobs.append(job_obj)
    except Exception as e:
        print("Erro Freelancer.com:", e)
        
    return jobs

