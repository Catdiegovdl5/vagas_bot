import urllib.parse

try:
    from curl_cffi import requests as requests_cffi
except ImportError:
    requests_cffi = None

def scrape(keyword="Python", level="Todos", location="", country="", **kwargs):
    jobs = []
    c_str = (country or "").lower()
    l_str = (location or "").lower()
    loc = location or country or kwargs.get("location") or kwargs.get("country") or ""
    if loc and loc.upper() in ["USA", "US", "UNITED STATES"]:
        return jobs
        
    try:
        # Mapeamento: keyword padronizada → termo que a API da Coodesh entende
        coodesh_mapping = {
            # --- 6 NOVAS CATEGORIAS MACRO E SUB-PROFISSÕES ---
            "operações físicas":            "operador producao manutencao industrial",
            "operacoes fisicas":            "operador producao manutencao industrial",
            "indústria":                    "industrial fabrica operador",
            "industria":                    "industrial fabrica operador",
            "operador cnc":                 "operador cnc",
            "pintor industrial":            "pintor industrial",
            "mecânico industrial":          "mecanico industrial",
            "mecanico industrial":          "mecanico industrial",
            "soldador":                     "soldador caldeireiro",
            "soldador / caldeireiro":       "soldador caldeireiro",
            "eletricista":                  "eletricista industrial",
            "operador de produção":         "operador de producao",
            "operador de producao":         "operador de producao",
            "auxiliar de produção":         "auxiliar de producao",
            "auxiliar de producao":         "auxiliar de producao",
            "auxiliar de operações":        "auxiliar de operacoes",
            "auxiliar de operacoes":        "auxiliar de operacoes",
            "conferente":                   "conferente",

            "logística":                    "logistica estoque almoxarifado",
            "logistica":                    "logistica estoque almoxarifado",
            "assistente de logística":     "assistente logistica",
            "assistente de logistica":     "assistente logistica",
            "auxiliar de logística":        "auxiliar logistica",
            "auxiliar de logistica":        "auxiliar logistica",
            "auxiliar de almoxarifado":     "auxiliar almoxarifado",
            "operador de empilhadeira":     "operador empilhadeira",
            "auxiliar de expedição":        "auxiliar expedicao",
            "auxiliar de expedicao":        "auxiliar expedicao",
            "motorista":                    "motorista",
            "almoxarife":                   "almoxarife",

            "administrativo":               "assistente administrativo escritorio",
            "assistente administrativo":    "assistente administrativo",
            "auxiliar administrativo":      "auxiliar administrativo",
            "recepcionista":                "recepcionista",
            "auxiliar de escritório":       "auxiliar escritorio",
            "auxiliar de escritorio":       "auxiliar escritorio",
            "data entry":                   "data entry digitador",
            "digitador":                    "digitador",
            "assistente financeiro":        "assistente financeiro",

            "criativos de performance":     "designer performance copywriter editor video",
            "criativos":                    "designer copywriter editor video",
            "design":                       "designer grafico",
            "designer conversional":        "designer conversional",
            "copywriter":                   "copywriter",
            "criador de anúncios":          "criador de anuncios",
            "criador de anuncios":          "criador de anuncios",
            "motion designer":              "motion designer",
            "editor de vídeo":              "editor de video",
            "editor de video":              "editor de video",
            "gestor de tráfego":            "gestor trafego pago",
            "gestor de trafego":            "gestor trafego pago",
            "designer gráfico":             "designer grafico",
            "designer grafico":             "designer grafico",

            "inteligência de vendas":       "sdr bdr inside sales executivo vendas",
            "inteligencia de vendas":       "sdr bdr inside sales executivo vendas",
            "vendas":                       "executivo vendas comercial",
            "sdr":                          "sdr vendas",
            "bdr":                          "bdr prospeccao",
            "inside sales":                 "inside sales",
            "analista de sales ops":        "analista sales ops",
            "executivo de vendas":          "executivo vendas",
            "crm":                          "analista crm",
            "analista de crm":              "analista crm",
            "analista de vendas":           "analista vendas",

            "engenharia de ia/dados":       "engenheiro de dados ia machine learning",
            "engenharia de ia dados":       "engenheiro de dados ia machine learning",
            "engenharia de dados":          "data engineer etl",
            "engenheiro de dados":          "data engineer",
            "data engineer":                "data engineer",
            "engenheiro de ia":              "ai engineer",
            "machine learning":             "machine learning engineer",
            "cientista de dados":            "data scientist",
            "analista de dados":            "data analyst",

            # IA / AI
            "especialista em ia":            "inteligencia artificial",
            "especialista em ia generativa": "ia generativa",
            "desenvolvedor de agentes ia":   "ai agents",
            "prompt engineer":               "prompt engineer",
            "machine learning engineer":     "machine learning",
            # Desenvolvimento
            "desenvolvedor python":          "python developer",
            "desenvolvedor backend":         "backend developer",
            "desenvolvedor node":            "node.js developer",
            "desenvolvedor react":           "react developer",
            "desenvolvedor fullstack":       "fullstack developer",
            "desenvolvedor django":          "django developer",
            "desenvolvedor fastapi":         "fastapi developer",
            "desenvolvedor rpa":             "rpa developer",
            "desenvolvedor junior python":   "python junior",
            "desenvolvedor junior react":    "react junior",
            "desenvolvedor junior fullstack": "fullstack junior",
            "desenvolvedor pleno python":    "python pleno",
            "desenvolvedor pleno react":     "react pleno",
            "desenvolvedor pleno fullstack": "fullstack pleno",
            # Dados & Analytics
            "analista de analytics":        "analytics",
            "analista sql":                 "sql analyst",
            "analista de power bi":         "power bi",
            "analista de dados junior":     "data analyst junior",
            "analista de dados pleno":      "data analyst pleno",
            # Marketing & Growth
            "gestor de trafego pleno":      "gestor trafego pleno",
            "growth hacker":                "growth hacker",
            "analista de marketing digital": "marketing digital",
            "especialista em seo":          "seo",
            "analista de marketing junior": "marketing junior",
            # Design & Video
            "video maker":                  "videomaker",
            "social media":                 "social media",
            "ux designer":                  "ux designer",
            # Admin
            "analista de rh":               "analista rh",
            "suporte tecnico n1":           "suporte tecnico",
            "assistente de faturamento":    "faturamento",
        }

        kw_str = keyword or "Python"
        lvl_str = level or "Todos"
        kw_clean = kw_str.lower().strip()
        search_kw = coodesh_mapping.get(kw_clean, kw_str)
        if lvl_str != "Todos":
            search_kw += f" {lvl_str}"
        if loc and loc.lower() not in ["todos", "brasil", "brasil (remoto)", "remoto", "qualquer", ""]:
            search_kw += f" {loc}"
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
                
                job_obj = {
                    "platform": "Coodesh",
                    "title": title,
                    "company": company,
                    "budget": salary,
                    "link": link,
                    "job_type": job_type_formatted,
                    "profession": keyword,
                    "level": level,
                    "requirements": reqs
                }
                try:
                    from bot import classify_job_profession
                    job_obj = classify_job_profession(job_obj)
                except Exception:
                    pass
                jobs.append(job_obj)
    except Exception as e:
        print("Erro Coodesh:", e)
        
    return jobs
