import json
import urllib.parse
from bs4 import BeautifulSoup
import asyncio

try:
    from curl_cffi import requests as requests_cffi
except ImportError:
    requests_cffi = None

async def scrape(keyword="Python", level="Todos", max_pages=10, location="", country="", **kwargs):
    jobs = []
    c_str = (country or "").lower()
    l_str = (location or "").lower()
    loc = location or country or kwargs.get("location") or kwargs.get("country") or ""
    if loc and loc.upper() in ["USA", "US", "UNITED STATES"]:
        return jobs
        
    try:
        # Mapeamento completo: keyword padronizada → termo real indexado pelo Gupy
        gupy_mapping = {
            # --- 6 NOVAS CATEGORIAS MACRO E SUB-PROFISSÕES ---
            # 1. Operações Físicas
            "operações físicas":            "Operador Produção Manutenção Industrial",
            "operacoes fisicas":            "Operador Produção Manutenção Industrial",
            "indústria":                    "Industrial Fábrica Operador",
            "industria":                    "Industrial Fábrica Operador",
            "operador cnc":                 "Operador CNC",
            "pintor industrial":            "Pintor Industrial",
            "mecânico industrial":          "Mecânico Industrial",
            "mecanico industrial":          "Mecânico Industrial",
            "soldador":                     "Soldador Caldeireiro",
            "soldador / caldeireiro":       "Soldador Caldeireiro",
            "eletricista":                  "Eletricista Industrial",
            "operador de produção":         "Operador de Produção",
            "operador de producao":         "Operador de Produção",
            "auxiliar de produção":         "Auxiliar de Produção",
            "auxiliar de producao":         "Auxiliar de Produção",
            "auxiliar de operações":        "Auxiliar de Operações",
            "auxiliar de operacoes":        "Auxiliar de Operações",
            "conferente":                   "Conferente",

            # 2. Logística
            "logística":                    "Logística Almoxarifado Estoque",
            "logistica":                    "Logística Almoxarifado Estoque",
            "assistente de logística":     "Assistente de Logística",
            "assistente de logistica":     "Assistente de Logística",
            "auxiliar de logística":        "Auxiliar de Logística",
            "auxiliar de logistica":        "Auxiliar de Logística",
            "auxiliar de almoxarifado":     "Auxiliar de Almoxarifado",
            "operador de empilhadeira":     "Operador de Empilhadeira",
            "auxiliar de expedição":        "Auxiliar de Expedição",
            "auxiliar de expedicao":        "Auxiliar de Expedição",
            "motorista":                    "Motorista",
            "almoxarife":                   "Almoxarife Estoquista",

            # 3. Administrativo
            "administrativo":               "Assistente Administrativo Escritório",
            "assistente administrativo":    "Assistente Administrativo",
            "auxiliar administrativo":      "Auxiliar Administrativo",
            "recepcionista":                "Recepcionista",
            "auxiliar de escritório":       "Auxiliar de Escritório",
            "auxiliar de escritorio":       "Auxiliar de Escritório",
            "data entry":                   "Data Entry Digitador",
            "digitador":                    "Digitador Data Entry",
            "assistente financeiro":        "Assistente Financeiro",

            # 4. Criativos de Performance
            "criativos de performance":     "Designer Copywriter Editor de Vídeo",
            "criativos":                    "Designer Performance Copywriter",
            "design":                       "Designer Gráfico",
            "designer conversional":        "Designer Conversional",
            "copywriter":                   "Copywriter Redator",
            "criador de anúncios":          "Criador de Anúncios Performance",
            "criador de anuncios":          "Criador de Anúncios Performance",
            "motion designer":              "Motion Designer",
            "editor de vídeo":              "Editor de Vídeo",
            "editor de video":              "Editor de Vídeo",
            "gestor de tráfego":            "Gestor de Tráfego Pago",
            "gestor de trafego":            "Gestor de Tráfego Pago",
            "designer gráfico":             "Designer Gráfico",
            "designer grafico":             "Designer Gráfico",

            # 5. Inteligência de Vendas
            "inteligência de vendas":       "SDR BDR Inside Sales Vendas",
            "inteligencia de vendas":       "SDR BDR Inside Sales Vendas",
            "vendas":                       "Executivo de Vendas Comercial",
            "sdr":                          "SDR Vendas",
            "bdr":                          "BDR Prospecção",
            "inside sales":                 "Inside Sales",
            "analista de sales ops":        "Sales Ops Analista",
            "executivo de vendas":          "Executivo de Vendas",
            "crm":                          "CRM Analyst",
            "analista de crm":              "Analista CRM",
            "analista de vendas":           "Analista de Vendas",

            # 6. Engenharia de IA/Dados
            "engenharia de ia/dados":       "Engenheiro de Dados IA Machine Learning",
            "engenharia de ia dados":       "Engenheiro de Dados IA Machine Learning",
            "engenharia de dados":          "Data Engineer ETL",
            "engenheiro de dados":          "Data Engineer",
            "data engineer":                "Data Engineer",
            "engenheiro de ia":              "AI Engineer",
            "machine learning":             "Machine Learning Engineer",
            "cientista de dados":            "Data Scientist",
            "analista de dados":            "Analista de Dados",

            # --- IA / AI ---
            "especialista em ia":            "Inteligência Artificial",
            "especialista em ia generativa": "IA Generativa",
            "desenvolvedor de agentes ia":   "Agentes IA",
            "prompt engineer":               "Prompt Engineer",
            "machine learning engineer":     "Machine Learning",
            # Desenvolvimento
            "desenvolvedor python":          "Python",
            "desenvolvedor backend":         "Backend Developer",
            "desenvolvedor node":            "Node.js",
            "desenvolvedor react":           "React Developer",
            "desenvolvedor fullstack":       "Fullstack",
            "desenvolvedor django":          "Django Python",
            "desenvolvedor fastapi":         "FastAPI Python",
            "desenvolvedor rpa":             "RPA Automação",
            "desenvolvedor junior python":   "Desenvolvedor Python Jr",
            "desenvolvedor junior react":    "Frontend React Jr",
            "desenvolvedor junior fullstack": "Desenvolvedor Fullstack Jr",
            "desenvolvedor pleno python":    "Desenvolvedor Python Pleno",
            "desenvolvedor pleno react":     "Frontend React Pleno",
            "desenvolvedor pleno fullstack": "Fullstack Pleno",
            # Dados & Analytics
            "analista de analytics":        "Analytics",
            "analista sql":                 "SQL",
            "analista de power bi":         "Power BI",
            "analista de dados junior":     "Analista de Dados Jr",
            "analista de dados pleno":      "Analista de Dados Pleno",
            # Marketing & Growth
            "gestor de trafego pleno":      "gestor trafego pleno",
            "growth hacker":                "Growth Marketing",
            "analista de marketing digital": "Marketing Digital",
            "especialista em seo":          "SEO",
            "analista de marketing junior": "Analista de Marketing Jr",
            # Design & Video
            "video maker":                  "Videomaker Produtor",
            "social media":                 "Social Media",
            "ux designer":                  "UX UI Designer",
            # Admin
            "analista de rh":               "Analista RH Recursos Humanos",
            "suporte tecnico n1":           "Suporte Técnico Helpdesk",
            "assistente de faturamento":    "Faturamento",
        }
        
        kw_str = keyword or "Python"
        lvl_str = level or "Todos"
        kw_clean = kw_str.lower().strip()
        search_kw = gupy_mapping.get(kw_clean, kw_str)
        if lvl_str != "Todos":
            search_kw += f" {lvl_str}"
        if loc and loc.lower() not in ["todos", "brasil", "brasil (remoto)", "remoto", "qualquer", ""]:
            search_kw += f" {loc}"
        encoded_kw = urllib.parse.quote(search_kw)
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json, text/plain, */*",
            "Referer": "https://employability-portal.gupy.io/",
        }
        
        async def fetch_page(session, page):
            offset = (page - 1) * 30
            api_url = f"https://employability-portal.gupy.io/api/v1/jobs?jobName={encoded_kw}&limit=30&offset={offset}"
            try:
                if session:
                    r = await session.get(api_url, headers=headers, impersonate="chrome110", timeout=15)
                else:
                    import httpx
                    async with httpx.AsyncClient() as client:
                        r = await client.get(api_url, headers=headers, timeout=15)
                if r.status_code == 200:
                    return r
            except Exception as e:
                print(f"Erro ao buscar pagina {page} no Gupy: {e}")
            return None

        if requests_cffi and hasattr(requests_cffi, "AsyncSession"):
            async with requests_cffi.AsyncSession() as session:
                tasks = [fetch_page(session, page) for page in range(1, max_pages + 1)]
                responses = await asyncio.gather(*tasks)
        else:
            tasks = [fetch_page(None, page) for page in range(1, max_pages + 1)]
            responses = await asyncio.gather(*tasks)

        for r in responses:
            if not r:
                continue
            try:
                try:
                    if hasattr(r, "json") and callable(r.json):
                        api_data = r.json()
                    else:
                        api_data = json.loads(r.text)
                    job_list = api_data.get("data", []) or api_data.get("jobs", []) or []
                except Exception:
                    # Fallback: tentar __NEXT_DATA__ do HTML
                    soup = BeautifulSoup(r.text, 'html.parser')
                    script = soup.find('script', id='__NEXT_DATA__')
                    job_list = []
                    if script and script.string:
                        ndata = json.loads(script.string)
                        job_list = ndata.get("props", {}).get("pageProps", {}).get("initialData", {}).get("jobs", [])
                
                for item in job_list:
                    try:
                        title = item.get("name", "Sem Título")
                        company = item.get("careerPageName", "Empresa Confidencial")
                        link = item.get("jobUrl", "")
                        if not link:
                            continue
                        job_type = item.get("type", "CLT")
                        city = item.get("city", "")
                        state = item.get("state", "")
                        
                        desc = item.get("description", "")
                        if not desc:
                            desc = f"Vaga na empresa {company}. Local: {city} {state}."
                            
                        job_obj = {
                            "platform": "Gupy",
                            "title": title,
                            "company": company,
                            "budget": "A Combinar",
                            "link": link,
                            "job_type": job_type or "CLT",
                            "profession": keyword,
                            "level": level,
                            "requirements": desc
                        }
                        try:
                            from bot import classify_job_profession
                            job_obj = classify_job_profession(job_obj)
                        except Exception:
                            pass
                        jobs.append(job_obj)
                    except Exception:
                        continue
            except Exception as e:
                print("Erro ao decodificar JSON Gupy:", e)
    except Exception as e:
        print("Erro Gupy:", e)
        
    return jobs
