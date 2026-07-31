import urllib.parse
from bs4 import BeautifulSoup

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
        # Mapeamento: keyword padronizada → termo que aparece nos títulos de vagas no ProgramaThor
        programathor_mapping = {
            # --- 6 NOVAS CATEGORIAS MACRO E SUB-PROFISSÕES ---
            "operações físicas":            "Operacoes Fisicas Producao Manutencao",
            "operacoes fisicas":            "Operacoes Fisicas Producao Manutencao",
            "indústria":                    "Industrial Operador",
            "industria":                    "Industrial Operador",
            "operador cnc":                 "Operador CNC",
            "pintor industrial":            "Pintor Industrial",
            "mecânico industrial":          "Mecanico Industrial",
            "mecanico industrial":          "Mecanico Industrial",
            "soldador":                     "Soldador",
            "soldador / caldeireiro":       "Soldador",
            "eletricista":                  "Eletricista",
            "operador de produção":         "Operador Producao",
            "operador de producao":         "Operador Producao",
            "auxiliar de produção":         "Auxiliar Producao",
            "auxiliar de producao":         "Auxiliar Producao",
            "auxiliar de operações":        "Auxiliar Operacoes",
            "auxiliar de operacoes":        "Auxiliar Operacoes",
            "conferente":                   "Conferente",

            "logística":                    "Logistica Estoque Almoxarifado",
            "logistica":                    "Logistica Estoque Almoxarifado",
            "assistente de logística":     "Assistente Logistica",
            "assistente de logistica":     "Assistente Logistica",
            "auxiliar de logística":        "Auxiliar Logistica",
            "auxiliar de logistica":        "Auxiliar Logistica",
            "auxiliar de almoxarifado":     "Auxiliar Almoxarifado",
            "operador de empilhadeira":     "Operador Empilhadeira",
            "auxiliar de expedição":        "Auxiliar Expedicao",
            "auxiliar de expedicao":        "Auxiliar Expedicao",
            "motorista":                    "Motorista",
            "almoxarife":                   "Almoxarife",

            "administrativo":               "Administrativo",
            "assistente administrativo":    "Assistente Administrativo",
            "auxiliar administrativo":      "Auxiliar Administrativo",
            "recepcionista":                "Recepcionista",
            "auxiliar de escritório":       "Auxiliar Escritorio",
            "auxiliar de escritorio":       "Auxiliar Escritorio",
            "data entry":                   "Data Entry",
            "digitador":                    "Digitador",
            "assistente financeiro":        "Assistente Financeiro",

            "criativos de performance":     "Designer Copywriter Editor Video",
            "criativos":                    "Designer Copywriter Editor Video",
            "design":                       "Designer",
            "designer conversional":        "Designer Conversional",
            "copywriter":                   "Copywriter",
            "criador de anúncios":          "Criador Anuncios",
            "criador de anuncios":          "Criador Anuncios",
            "motion designer":              "Motion Designer",
            "editor de vídeo":              "Editor Video",
            "editor de video":              "Editor Video",
            "gestor de tráfego":            "Trafego Pago",
            "gestor de trafego":            "Trafego Pago",
            "designer gráfico":             "Designer",
            "designer grafico":             "Designer",

            "inteligência de vendas":       "SDR BDR Inside Sales Executivo Vendas",
            "inteligencia de vendas":       "SDR BDR Inside Sales Executivo Vendas",
            "vendas":                       "Executivo Vendas",
            "sdr":                          "SDR",
            "bdr":                          "BDR",
            "inside sales":                 "Inside Sales",
            "analista de sales ops":        "Sales Ops",
            "executivo de vendas":          "Executivo Vendas",
            "crm":                          "CRM",
            "analista de crm":              "Analista CRM",
            "analista de vendas":           "Analista Vendas",

            "engenharia de ia/dados":       "Engenheiro Dados IA Machine Learning",
            "engenharia de ia dados":       "Engenheiro Dados IA Machine Learning",
            "engenharia de dados":          "Engenheiro de Dados ETL",
            "engenheiro de dados":          "Engenheiro de Dados",
            "data engineer":                "Data Engineer",
            "engenheiro de ia":              "AI Engineer",
            "machine learning":             "Machine Learning",
            "cientista de dados":            "Cientista de Dados",
            "analista de dados":            "Analista de Dados",

            # IA / AI
            "especialista em ia":            "Inteligencia Artificial",
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
            "gestor de trafego pleno":      "Trafego Pago Pleno",
            "growth hacker":                "Growth Hacker",
            "analista de marketing digital": "Marketing Digital",
            "especialista em seo":          "SEO",
            "analista de marketing junior": "Marketing Junior",
            # Design & Video
            "video maker":                  "Videomaker",
            "social media":                 "Social Media",
            "ux designer":                  "UX Designer",
            # Admin
            "analista de rh":               "RH",
            "suporte tecnico n1":           "Suporte Tecnico",
            "assistente de faturamento":    "Faturamento",
        }

        kw_str = keyword or "Python"
        lvl_str = level or "Todos"
        kw_clean = kw_str.lower().strip()
        search_kw = programathor_mapping.get(kw_clean, kw_str)
        if lvl_str != "Todos": search_kw += f" {lvl_str}"
        if loc and loc.lower() not in ["todos", "brasil", "brasil (remoto)", "remoto", "qualquer", ""]:
            search_kw += f" {loc}"
        encoded_kw = urllib.parse.quote(search_kw)
        
        url = f"https://programathor.com.br/jobs?text={encoded_kw}"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        if not requests_cffi:
            import requests
            r = requests.get(url, headers=headers, timeout=15)
        else:
            r = requests_cffi.get(url, headers=headers, impersonate="chrome110", timeout=15)
            
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            job_cards = soup.find_all('div', class_=lambda c: c and 'cell-list' in str(c).lower())
            
            for card in job_cards:
                try:
                    title_el = card.find('h3') or card.find('h2')
                    if not title_el or not getattr(title_el, 'text', None):
                        continue
                    title = title_el.text.strip()
                    
                    link_el = card.find('a', href=True)
                    if link_el:
                        link = link_el.get('href')
                        if link and not link.startswith('http'):
                            link = 'https://programathor.com.br' + link
                    else:
                        link = url
                        
                    comp_el = card.find('div', class_=lambda c: c and 'logo' in str(c).lower())
                    company = comp_el.get('title', "Empresa Confidencial") if comp_el else "Empresa Confidencial"
                    
                    tags = card.find_all('span', class_=lambda c: c and 'tag' in str(c).lower())
                    tags_text = " | ".join([t.text.strip() for t in tags if getattr(t, 'text', None) and t.text.strip()])
                    
                    job_obj = {
                        "platform": "ProgramaThor",
                        "title": title,
                        "company": company,
                        "budget": "A Combinar",
                        "link": link,
                        "job_type": "CLT/PJ",
                        "profession": keyword,
                        "level": level,
                        "requirements": tags_text if tags_text else f"Vaga para {title} no ProgramaThor."
                    }
                    try:
                        from bot import classify_job_profession
                        job_obj = classify_job_profession(job_obj)
                    except Exception:
                        pass
                    jobs.append(job_obj)
                except Exception as card_e:
                    continue
    except Exception as e:
        print("Erro ProgramaThor:", e)
        
    return jobs
