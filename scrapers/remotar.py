import requests
import urllib.parse
import hashlib
from bs4 import BeautifulSoup

try:
    from curl_cffi import requests as requests_cffi
except ImportError:
    requests_cffi = None

def scrape(keyword="Python", level="Todos", contract="Todos", location="", country="", **kwargs):
    jobs = []
    c_str = (country or "").lower()
    l_str = (location or "").lower()
    loc = location or country or kwargs.get("location") or kwargs.get("country") or ""
    try:
        # Mapeamento completo: termo generico → query otimizada para Remotar
        remotar_mapping = {
            # --- 6 NOVAS CATEGORIAS MACRO E SUB-PROFISSÕES ---
            "operações físicas":            "Operações Físicas Produção Manutenção",
            "operacoes fisicas":            "Operações Físicas Produção Manutenção",
            "indústria":                    "Indústria Operador",
            "industria":                    "Indústria Operador",
            "operador cnc":                 "Operador CNC",
            "pintor industrial":            "Pintor Industrial",
            "mecânico industrial":          "Mecânico Industrial",
            "mecanico industrial":          "Mecânico Industrial",
            "soldador":                     "Soldador",
            "soldador / caldeireiro":       "Soldador",
            "eletricista":                  "Eletricista",
            "operador de produção":         "Operador de Produção",
            "operador de producao":         "Operador de Produção",
            "auxiliar de produção":         "Auxiliar de Produção",
            "auxiliar de producao":         "Auxiliar de Produção",
            "auxiliar de operações":        "Auxiliar de Operações",
            "auxiliar de operacoes":        "Auxiliar de Operações",
            "conferente":                   "Conferente",

            "logística":                    "Logística Estoque Almoxarifado",
            "logistica":                    "Logística Estoque Almoxarifado",
            "assistente de logística":     "Assistente de Logística",
            "assistente de logistica":     "Assistente de Logística",
            "auxiliar de logística":        "Auxiliar de Logística",
            "auxiliar de logistica":        "Auxiliar de Logística",
            "auxiliar de almoxarifado":     "Auxiliar de Almoxarifado",
            "operador de empilhadeira":     "Operador de Empilhadeira",
            "auxiliar de expedição":        "Auxiliar de Expedição",
            "auxiliar de expedicao":        "Auxiliar de Expedição",
            "motorista":                    "Motorista",
            "almoxarife":                   "Almoxarife",

            "administrativo":               "Assistente Administrativo",
            "assistente administrativo":    "Assistente Administrativo",
            "auxiliar administrativo":      "Auxiliar Administrativo",
            "recepcionista":                "Recepcionista",
            "auxiliar de escritório":       "Auxiliar de Escritório",
            "auxiliar de escritorio":       "Auxiliar de Escritório",
            "data entry":                   "Data Entry",
            "digitador":                    "Digitador",
            "assistente financeiro":        "Assistente Financeiro",

            "criativos de performance":     "Designer Copywriter Editor Vídeo",
            "criativos":                    "Designer Copywriter Editor Vídeo",
            "design":                       "Designer Gráfico",
            "designer conversional":        "Designer Conversional",
            "copywriter":                   "Copywriter",
            "criador de anúncios":          "Criador de Anúncios",
            "criador de anuncios":          "Criador de Anúncios",
            "motion designer":              "Motion Designer",
            "editor de vídeo":              "Editor de Vídeo",
            "editor de video":              "Editor de Vídeo",
            "gestor de tráfego":            "Gestor de Tráfego",
            "gestor de trafego":            "Gestor de Tráfego",
            "designer gráfico":             "Designer Gráfico",
            "designer grafico":             "Designer Gráfico",

            "inteligência de vendas":       "SDR BDR Inside Sales Executivo Vendas",
            "inteligencia de vendas":       "SDR BDR Inside Sales Executivo Vendas",
            "vendas":                       "Executivo de Vendas",
            "sdr":                          "SDR",
            "bdr":                          "BDR",
            "inside sales":                 "Inside Sales",
            "analista de sales ops":        "Sales Ops",
            "executivo de vendas":          "Executivo de Vendas",
            "crm":                          "CRM",
            "analista de crm":              "Analista CRM",
            "analista de vendas":           "Analista de Vendas",

            "engenharia de ia/dados":       "Engenheiro de Dados IA Machine Learning",
            "engenharia de ia dados":       "Engenheiro de Dados IA Machine Learning",
            "engenharia de dados":          "Data Engineer",
            "engenheiro de dados":          "Data Engineer",
            "data engineer":                "Data Engineer",
            "engenheiro de ia":              "AI Engineer",
            "machine learning":             "Machine Learning",
            "cientista de dados":            "Data Science",
            "analista de dados":            "Data Analyst",

            # IA / AI
            "especialista em ia":            "Inteligência Artificial",
            "especialista em ia generativa": "IA Generativa",
            "desenvolvedor de agentes ia":   "Agentes IA",
            "prompt engineer":               "Prompt Engineer",
            "machine learning engineer":     "Machine Learning",
            # Desenvolvimento
            "desenvolvedor python":          "Python",
            "desenvolvedor backend":         "Backend",
            "desenvolvedor node":            "Node.js",
            "desenvolvedor react":           "React",
            "desenvolvedor fullstack":       "Fullstack",
            "desenvolvedor django":          "Django",
            "desenvolvedor fastapi":         "FastAPI",
            "desenvolvedor rpa":             "RPA",
            "desenvolvedor junior python":   "Python Junior",
            "desenvolvedor junior react":    "React Junior",
            "desenvolvedor junior fullstack": "Fullstack Junior",
            "desenvolvedor pleno python":    "Python Pleno",
            "desenvolvedor pleno react":     "React Pleno",
            "desenvolvedor pleno fullstack": "Fullstack Pleno",
            # Dados & Analytics
            "analista de analytics":        "Analytics",
            "analista sql":                 "SQL",
            "analista de power bi":         "Power BI",
            "analista de dados junior":     "Analista de Dados Junior",
            "analista de dados pleno":      "Analista de Dados Pleno",
            # Marketing & Growth
            "gestor de trafego pleno":      "Tráfego Pago Pleno",
            "growth hacker":                "Growth",
            "analista de marketing digital": "Marketing Digital",
            "especialista em seo":          "SEO",
            "analista de marketing junior": "Marketing Junior",
            # Design & Video
            "editor de video":              "Editor de Vídeo",
            "video maker":                  "Videomaker",
            "social media":                 "Social Media",
            "designer grafico":             "Designer Gráfico",
            "ux designer":                  "UX Designer",
            # Administrativo
            "analista de rh":               "Recursos Humanos",
            "suporte tecnico n1":           "Suporte N1",
            "assistente administrativo":    "Assistente Administrativo",
            "assistente financeiro":        "Financeiro",
            "assistente de faturamento":    "Faturamento",
            "assistente de logistica":      "Logística",
            "recepcionista":                "Recepcionista",
        }
        
        kw_str = keyword or "Python"
        lvl_str = level or "Todos"
        contract_str = contract or "Todos"
        kw_clean = kw_str.lower().strip()
        search_kw = remotar_mapping.get(kw_clean, kw_str)
        
        if lvl_str != "Todos":
            search_kw += f" {lvl_str}"
            
        if contract_str.upper() == "PJ":
            search_kw += " PJ"
        elif contract_str.upper() == "CLT":
            search_kw += " CLT"
            
        if loc and loc.lower() not in ["todos", "brasil", "brasil (remoto)", "remoto", "qualquer", ""]:
            search_kw += f" {loc}"
            
        encoded_kw = urllib.parse.quote(search_kw)
        
        # API da Remotar — por padrão já lista vagas 100% remotas
        url = f"https://api.remotar.com.br/jobs?search={encoded_kw}"
        print(f"[Remotar Scraper] Final request URL: {url}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'Referer': 'https://remotar.com.br/',
        }
        
        r = None
        if requests_cffi:
            try:
                r = requests_cffi.get(url, headers=headers, impersonate="chrome110", timeout=10.0)
            except Exception:
                r = None
        if r is None:
            try:
                r = requests.get(url, headers=headers, timeout=10.0)
            except Exception:
                r = None
            
        if r and getattr(r, "status_code", None) == 200:
            try:
                data = r.json()
            except Exception:
                data = {}
            if isinstance(data, dict):
                raw_results = data.get('data')
                results = raw_results if isinstance(raw_results, list) else []
                for item in results[:30]:
                    if not isinstance(item, dict):
                        continue
                    title = item.get('title', '')
                    if not title:
                        continue
                    
                    company = "Start-up Gringa"
                    comp_obj = item.get('company')
                    if isinstance(comp_obj, dict) and comp_obj.get('name'):
                        company = comp_obj.get('name')
                    elif item.get('companyDisplayName'):
                        company = item.get('companyDisplayName')
                    
                    # Link individual da vaga na Remotar
                    job_url = item.get('externalLink') or item.get('url')
                    if not job_url and item.get('slug'):
                        job_url = f"https://remotar.com.br/job/{item.get('slug')}"
                    if not job_url:
                        job_url = f"https://remotar.com.br/search?q={encoded_kw}"
                    
                    # Tipo de contratação
                    title_upper = title.upper()
                    j_type = "PJ" if "PJ" in title_upper or "FREELANCE" in title_upper else "CLT"
                    
                    # Salário/Budget
                    budget = "A Combinar"
                    salary_info = item.get('jobSalary')
                    if isinstance(salary_info, dict) and salary_info.get('type') != 'uninformed':
                        curr = salary_info.get('currency') or 'BRL'
                        val_from = salary_info.get('from')
                        val_to = salary_info.get('to')
                        if val_from or val_to:
                            budget = f"{curr} {val_from or 0} - {val_to or 0}"
                    
                    # Descrição limpa
                    sub = item.get('subtitle') or ''
                    desc_html = item.get('description') or ''
                    more = item.get('moreInfos') or ''
                    
                    full_html = f"<p>{sub}</p> {desc_html} <p>{more}</p>"
                    clean_text = BeautifulSoup(full_html, 'html.parser').get_text(separator=' ').strip()
                    
                    # Remover espaços extras
                    req_text = " ".join(clean_text.split())
                    if not req_text:
                        req_text = f"Vaga 100% Remota. Requisitos: proficiência em {keyword}."
                    
                    job_id = hashlib.md5(job_url.encode('utf-8')).hexdigest()[:16]
                    job_obj = {
                        "id": job_id,
                        "platform": "Remotar",
                        "title": title,
                        "company": company,
                        "budget": budget,
                        "link": job_url,
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
        print(f"Remotar Scraper Error: {e}")
    return jobs

