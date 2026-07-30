import requests
from bs4 import BeautifulSoup
import re
import urllib.parse

try:
    from curl_cffi import requests as requests_cffi
except ImportError:
    requests_cffi = None

def scrape(keyword="Python", level="Todos", location="", country="", **kwargs):
    jobs = []
    c_str = (country or "").lower()
    l_str = (location or "").lower()
    target_loc = location or country or kwargs.get("location") or kwargs.get("country") or ""
    try:
        kw = keyword or "Python"
        lvl = level or "Todos"
        search_kw = f"{kw}"
        if lvl != "Todos":
            search_kw += f" {lvl}"
            
        base_url = "br.jooble.org"
        loc = "Brazil"
        if "Londrina" in target_loc:
            loc = "Londrina"
        elif "Assaí" in target_loc:
            loc = "Assaí"
        elif target_loc and target_loc.upper() in ["USA", "US", "UNITED STATES"]:
            base_url = "jooble.org"
            loc = "United States"
        elif target_loc and target_loc.lower() not in ["todos", "brasil", "brasil (remoto)", "remoto", "qualquer", ""]:
            loc = target_loc
            
        url = f"https://{base_url}/api/0031603e-bd0a-4505-ad10-383c420d804f"
        
        payload = {
            "keywords": search_kw,
            "location": loc,
            "page": "1"
        }
        
        headers = {
            "Content-type": "application/json"
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        data = response.json()
        
        if data.get("jobs"):
            for item in data["jobs"][:30]:
                title = item.get("title", "Sem título")
                j_type = "PJ" if "PJ" in title.upper() else "CLT"
                
                link = item.get("link", "#")
                description = ""
                final_url = link
                
                if link and link != "#":
                    try:
                        redirect_headers = {
                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7"
                        }
                        
                        if requests_cffi:
                            r = requests_cffi.get(link, headers=redirect_headers, allow_redirects=True, timeout=12, impersonate="chrome110")
                        else:
                            r = requests.get(link, headers=redirect_headers, allow_redirects=True, timeout=12)
                            
                        final_url = r.url
                        html_content = r.text
                        
                        if r.status_code == 200:
                            soup = BeautifulSoup(html_content, "html.parser")
                            
                            if "gupy.io" in final_url:
                                desc_el = (soup.find(attrs={"data-testid": "vacancy-description-text"}) or 
                                           soup.find(attrs={"data-testid": "text-description"}) or
                                           soup.find(class_=re.compile(r"description|vacancy", re.I)))
                            elif "indeed.com" in final_url:
                                desc_el = soup.find(id="jobDescriptionText")
                            elif "jooble" in final_url:
                                desc_el = (soup.find("div", class_="job-description_description") or 
                                           soup.find("div", class_="description") or
                                           soup.find(class_=re.compile(r"description|desc", re.I)))
                            else:
                                desc_el = (soup.find(id="jobDescriptionText") or 
                                           soup.find("div", class_=re.compile(r"description|jobDescription|job-desc|vaga-desc|vacancy-desc", re.I)) or
                                           soup.find(attrs={"data-testid": re.compile(r"description|vacancy", re.I)}) or
                                           soup.find("article") or
                                           soup.find("main"))
                                           
                            if desc_el:
                                description = desc_el.get_text(separator="\n").strip()
                    except Exception as redirect_e:
                        print(f"Error following redirect for Jooble job {link}: {redirect_e}")
                
                if not description or len(description) < 150:
                    api_snippet = item.get("snippet", "")
                    description = api_snippet.replace('<b>', '').replace('</b>', '').replace('\n', ' ').strip()
                    
                # Guard: descartar vagas com link inválido ou sem título
                if not title or not final_url or final_url == '#':
                    continue

                jobs.append({
                    "platform": "Jooble",
                    "title": title,
                    "company": item.get("company", "Confidencial"),
                    "budget": item.get("salary") or "A Combinar",
                    "link": final_url,
                    "job_type": j_type,
                    "profession": keyword,
                    "level": level,
                    "requirements": description
                })
    except Exception:
        pass
        
    return jobs
