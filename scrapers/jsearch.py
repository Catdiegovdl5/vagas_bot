import requests
import urllib.parse
import os

def scrape(keyword, level, country="Brasil"):
    jobs = []
    try:
        # JSearch requer uma API Key válida do RapidAPI
        # Configure JSEARCH_API_KEY no seu .env ou nas variáveis de ambiente
        api_key = os.environ.get("JSEARCH_API_KEY", "")
        if not api_key:
            print("JSearch: JSEARCH_API_KEY não configurada. Pulando scraper.")
            return jobs
        
        search_kw = f"{keyword}"
        if level != "Todos":
            search_kw += f" {level}"
            
        encoded_kw = urllib.parse.quote(search_kw)
        
        if "Brasil" in country:
            url = f"https://jsearch.p.rapidapi.com/search?query={encoded_kw}&page=1&num_pages=3&date_posted=month&country=br&language=pt"
        elif country == "USA":
            url = f"https://jsearch.p.rapidapi.com/search?query={encoded_kw}&page=1&num_pages=3&date_posted=month&country=us&language=en"
        else:
            url = f"https://jsearch.p.rapidapi.com/search?query={encoded_kw}&page=1&num_pages=3&date_posted=month"
        
        headers = {
            "x-rapidapi-key": api_key,
            "x-rapidapi-host": "jsearch.p.rapidapi.com"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
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
            
        data = response.json()
        if "message" in data:
            print(f"JSearch API mensagem: {data['message']}")
            return jobs
        
        if data.get("data"):
            for item in data["data"][:30]:
                title = item.get("job_title", "Sem título")
                j_type = "PJ" if "PJ" in title.upper() else "CLT"
                
                desc = item.get("job_description", "")
                if len(desc) > 150:
                    req_text = desc[:150].replace('\n', ' ') + "..."
                else:
                    req_text = desc.replace('\n', ' ')
                
                if not req_text.strip():
                    req_text = "Sem descrição disponível."
                
                link = item.get("job_apply_link") or item.get("job_google_link") or "https://google.com"
                
                jobs.append({
                    "platform": f"JSearch",
                    "title": title,
                    "company": item.get("employer_name", "Confidencial"),
                    "budget": "A Combinar",
                    "link": link,
                    "job_type": j_type,
                    "profession": keyword,
                    "level": level,
                    "requirements": req_text
                })
    except Exception as e:
        print("Erro JSearch:", e)
    
    return jobs
