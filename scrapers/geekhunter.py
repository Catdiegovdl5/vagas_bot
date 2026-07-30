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
        # Mapeamento: keyword padronizada → termo que aparece nos títulos das vagas na GeekHunter
        geekhunter_mapping = {
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

            "administrativo":               "Assistente Administrativo",
            "assistente administrativo":    "Assistente Administrativo",
            "auxiliar administrativo":      "Auxiliar Administrativo",
            "recepcionista":                "Recepcionista",
            "auxiliar de escritório":       "Auxiliar Escritorio",
            "auxiliar de escritorio":       "Auxiliar Escritorio",
            "data entry":                   "Data Entry",
            "digitador":                    "Digitador",
            "assistente financeiro":        "Assistente Financeiro",

            "criativos de performance":     "Designer Performance Copywriter Editor Video",
            "criativos":                    "Designer Performance Copywriter Editor Video",
            "design":                       "Designer Grafico",
            "designer conversional":        "Designer Conversional",
            "copywriter":                   "Copywriter",
            "criador de anúncios":          "Criador Anuncios",
            "criador de anuncios":          "Criador Anuncios",
            "motion designer":              "Motion Designer",
            "editor de vídeo":              "Editor Video",
            "editor de video":              "Editor Video",
            "gestor de tráfego":            "Gestor Trafego",
            "gestor de trafego":            "Gestor Trafego",
            "designer gráfico":             "Designer Grafico",
            "designer grafico":             "Designer Grafico",

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
            "engenharia de dados":          "Data Engineer ETL",
            "engenheiro de dados":          "Data Engineer",
            "data engineer":                "Data Engineer",
            "engenheiro de ia":              "AI Engineer",
            "machine learning":             "Machine Learning",
            "cientista de dados":            "Data Scientist",
            "analista de dados":            "Data Analyst",

            # IA / AI
            "especialista em ia":            "Inteligencia Artificial",
            "especialista em ia generativa": "IA Generativa",
            "desenvolvedor de agentes ia":   "AI Agents",
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
            "analista de dados junior":     "Data Analyst Junior",
            "analista de dados pleno":      "Data Analyst Pleno",
            # Marketing & Growth
            "gestor de trafego pleno":      "Gestor Trafego Pleno",
            "growth hacker":                "Growth Hacker",
            "analista de marketing digital": "Marketing Digital",
            "especialista em seo":          "SEO",
            "analista de marketing junior": "Marketing Junior",
            # Design & Video
            "video maker":                  "Videomaker",
            "social media":                 "Social Media",
            "ux designer":                  "UX Designer",
            # Admin
            "analista de rh":               "Analista RH",
            "suporte tecnico n1":           "Suporte Tecnico",
            "assistente de faturamento":    "Faturamento",
        }

        kw_str = keyword or "Python"
        lvl_str = level or "Todos"
        kw_clean = kw_str.lower().strip()
        search_kw = geekhunter_mapping.get(kw_clean, kw_str)
        if lvl_str != "Todos":
            search_kw += f" {lvl_str}"
        if loc and loc.lower() not in ["todos", "brasil", "brasil (remoto)", "remoto", "qualquer", ""]:
            search_kw += f" {loc}"
        encoded_kw = urllib.parse.quote(search_kw)
        
        # URL atualizada com subdomínio e rota pt/vagas
        url = f"https://www.geekhunter.com/pt/vagas?q={encoded_kw}"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            "Referer": "https://www.geekhunter.com/pt/vagas",
        }
        
        r = None
        if requests_cffi:
            try:
                r = requests_cffi.get(url, headers=headers, impersonate="chrome110", timeout=15)
            except Exception:
                r = None
        if r is None:
            import requests as req_std
            r = req_std.get(url, headers=headers, timeout=15)
            
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            
            # Encontra todos os links de vaga pré-renderizados no HTML
            links = soup.find_all('a', href=lambda h: h and '/jobs/' in h)
            
            for card in links[:30]:
                try:
                    href = card.get('href') or ''
                    if not href.startswith('http'):
                        job_url = urllib.parse.urljoin("https://www.geekhunter.com", href)
                    else:
                        job_url = href
                        
                    # Extrai a empresa a partir do slug no path da URL
                    parts = job_url.split('/')
                    company = "Empresa via GeekHunter"
                    if 'pt' in parts:
                        pt_idx = parts.index('pt')
                        if pt_idx + 1 < len(parts):
                            company_slug = parts[pt_idx + 1]
                            if company_slug != 'jobs' and company_slug != 'vagas':
                                company = company_slug.replace('-', ' ').title()
                    
                    # Título
                    title_el = card.find('p', class_=lambda c: c and 'q4uo1b' in c) or card.find('p')
                    if not title_el:
                        continue
                    title = title_el.text.strip()
                    # Limpa prefixos de oportunidade
                    if "Oportunidade |" in title:
                        title = title.replace("Oportunidade |", "").strip()
                    elif "Oportunidade" in title and "|" in title:
                        title = title.split("|", 1)[1].strip()
                        
                    if not title:
                        continue
                        
                    # Salário/Budget
                    budget = "A Combinar"
                    salary_el = card.find('p', class_=lambda c: c and 'o118sj' in c)
                    if salary_el:
                        budget = salary_el.text.strip()
                    else:
                        # Fallback: procura por textos de salário
                        p_tags = card.find_all('p')
                        for p in p_tags:
                            p_text = p.text.strip()
                            if "R$" in p_text or "$" in p_text:
                                budget = p_text
                                break
                    
                    # Tipo de contratação
                    j_type = "CLT/PJ"
                    type_el = card.find('p', class_=lambda c: c and '2fkfcz' in c)
                    if type_el:
                        j_type = type_el.text.strip()
                    
                    # Skills/Requirements
                    skill_elements = card.find_all('div', class_=lambda c: c and 'dqhvn' in c)
                    skills = [s.text.strip() for s in skill_elements if s.text.strip()]
                    if skills:
                        reqs = ", ".join(skills)
                    else:
                        reqs = f"Vaga para {title} na GeekHunter."
                        
                    job_obj = {
                        "platform": "GeekHunter",
                        "title": title,
                        "company": company,
                        "budget": budget,
                        "link": job_url,
                        "job_type": j_type,
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
                except Exception as card_e:
                    continue
    except Exception as e:
        print("Erro GeekHunter:", e)
        
    return jobs
