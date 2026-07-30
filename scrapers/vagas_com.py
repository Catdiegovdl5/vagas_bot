import urllib.parse
from bs4 import BeautifulSoup
import asyncio

try:
    from curl_cffi import requests as requests_cffi
except ImportError:
    requests_cffi = None

async def scrape(keyword="Python", level="Todos", max_pages=1, location="", country="", **kwargs):
    jobs = []
    c_str = (country or "").lower()
    l_str = (location or "").lower()
    loc = location or country or kwargs.get("location") or kwargs.get("country") or ""
    if loc and loc.upper() in ["USA", "US", "UNITED STATES"]:
        return jobs
        
    try:
        # Mapeamento: keyword padronizada → termo que o Vagas.com indexa na URL
        vagas_com_mapping = {
            # --- 6 NOVAS CATEGORIAS MACRO E SUB-PROFISSÕES ---
            # 1. Operações Físicas
            "operações físicas":            "operacao-industrial",
            "operacoes fisicas":            "operacao-industrial",
            "indústria":                    "industrial",
            "industria":                    "industrial",
            "operador cnc":                 "operador-cnc",
            "pintor industrial":            "pintor-industrial",
            "mecânico industrial":          "mecanico-industrial",
            "mecanico industrial":          "mecanico-industrial",
            "soldador":                     "soldador",
            "soldador / caldeireiro":       "soldador",
            "eletricista":                  "eletricista-industrial",
            "operador de produção":         "operador-de-producao",
            "operador de producao":         "operador-de-producao",
            "auxiliar de produção":         "auxiliar-de-producao",
            "auxiliar de producao":         "auxiliar-de-producao",
            "auxiliar de operações":        "auxiliar-de-operacoes",
            "auxiliar de operacoes":        "auxiliar-de-operacoes",
            "conferente":                   "conferente",

            # 2. Logística
            "logística":                    "logistica",
            "logistica":                    "logistica",
            "assistente de logística":     "assistente-de-logistica",
            "assistente de logistica":     "assistente-de-logistica",
            "auxiliar de logística":        "auxiliar-de-logistica",
            "auxiliar de logistica":        "auxiliar-de-logistica",
            "auxiliar de almoxarifado":     "auxiliar-de-almoxarifado",
            "operador de empilhadeira":     "operador-de-empilhadeira",
            "auxiliar de expedição":        "auxiliar-de-expedicao",
            "auxiliar de expedicao":        "auxiliar-de-expedicao",
            "motorista":                    "motorista",
            "almoxarife":                   "almoxarife",

            # 3. Administrativo
            "administrativo":               "administrativo",
            "assistente administrativo":    "assistente-administrativo",
            "auxiliar administrativo":      "auxiliar-administrativo",
            "recepcionista":                "recepcionista",
            "auxiliar de escritório":       "auxiliar-de-escritorio",
            "auxiliar de escritorio":       "auxiliar-de-escritorio",
            "data entry":                   "data-entry",
            "digitador":                    "digitador",
            "assistente financeiro":        "assistente-financeiro",

            # 4. Criativos de Performance
            "criativos de performance":     "design-performance",
            "criativos":                    "design",
            "design":                       "design",
            "designer conversional":        "designer-conversional",
            "copywriter":                   "copywriter",
            "criador de anúncios":          "criador-de-anuncios",
            "criador de anuncios":          "criador-de-anuncios",
            "motion designer":              "motion-designer",
            "editor de vídeo":              "editor-de-video",
            "editor de video":              "editor-de-video",
            "gestor de tráfego":            "gestor-de-trafego",
            "gestor de trafego":            "gestor-de-trafego",
            "designer gráfico":             "designer-grafico",
            "designer grafico":             "designer-grafico",

            # 5. Inteligência de Vendas
            "inteligência de vendas":       "vendas-b2b",
            "inteligencia de vendas":       "vendas-b2b",
            "vendas":                       "vendas",
            "sdr":                          "sdr",
            "bdr":                          "bdr",
            "inside sales":                 "inside-sales",
            "analista de sales ops":        "sales-ops",
            "executivo de vendas":          "executivo-de-vendas",
            "crm":                          "analista-crm",
            "analista de crm":              "analista-crm",
            "analista de vendas":           "analista-de-vendas",

            # 6. Engenharia de IA/Dados
            "engenharia de ia/dados":       "engenharia-de-dados",
            "engenharia de ia dados":       "engenharia-de-dados",
            "engenharia de dados":          "engenharia-de-dados",
            "engenheiro de dados":          "engenheiro-de-dados",
            "data engineer":                "data-engineer",
            "engenheiro de ia":              "engenheiro-ia",
            "machine learning":             "machine-learning",
            "cientista de dados":            "data-scientist",
            "analista de dados":            "analista-de-dados",

            # IA / AI
            "especialista em ia":            "inteligencia-artificial",
            "especialista em ia generativa": "ia-generativa",
            "desenvolvedor de agentes ia":   "agentes-ia",
            "prompt engineer":               "prompt-engineer",
            "machine learning engineer":     "machine-learning",
            # Desenvolvimento
            "desenvolvedor python":          "desenvolvedor-python",
            "desenvolvedor backend":         "desenvolvedor-backend",
            "desenvolvedor node":            "desenvolvedor-nodejs",
            "desenvolvedor react":           "desenvolvedor-react",
            "desenvolvedor fullstack":       "desenvolvedor-fullstack",
            "desenvolvedor django":          "desenvolvedor-django",
            "desenvolvedor fastapi":         "desenvolvedor-fastapi",
            "desenvolvedor rpa":             "desenvolvedor-rpa",
            "desenvolvedor junior python":   "desenvolvedor-python-junior",
            "desenvolvedor junior react":    "desenvolvedor-react-junior",
            "desenvolvedor junior fullstack": "desenvolvedor-fullstack-junior",
            "desenvolvedor pleno python":    "desenvolvedor-python-pleno",
            "desenvolvedor pleno react":     "desenvolvedor-react-pleno",
            "desenvolvedor pleno fullstack": "desenvolvedor-fullstack-pleno",
            # Dados
            "analista de analytics":        "analista-analytics",
            "analista sql":                 "analista-sql",
            "analista de power bi":         "analista-power-bi",
            "analista de dados junior":     "analista-de-dados-junior",
            "analista de dados pleno":      "analista-de-dados-pleno",
            # Marketing & Growth
            "gestor de trafego pleno":      "gestor-trafego-pleno",
            "growth hacker":                "growth-hacker",
            "analista de marketing digital": "analista-marketing-digital",
            "especialista em seo":          "especialista-seo",
            "analista de marketing junior": "analista-marketing-junior",
            # Design & Video
            "video maker":                  "videomaker",
            "social media":                 "social-media",
            "ux designer":                  "designer-ux",
            # Admin
            "analista de rh":               "analista-recursos-humanos",
            "suporte tecnico n1":           "suporte-tecnico",
            "assistente de faturamento":    "auxiliar-faturamento",
        }
        
        kw_str = keyword or "Python"
        lvl_str = level or "Todos"
        kw_clean = kw_str.lower().strip()
        search_kw = vagas_com_mapping.get(kw_clean, kw_str.replace(' ', '-'))
        if lvl_str != "Todos":
            search_kw += f"-{lvl_str.lower()}"
        if loc and loc.lower() not in ["todos", "brasil", "brasil (remoto)", "remoto", "qualquer", ""]:
            search_kw += f"-{loc.replace(' ', '-').lower()}"
        encoded_kw = urllib.parse.quote(search_kw)
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        async def fetch_page(session, page):
            url = f"https://www.vagas.com.br/vagas-de-{encoded_kw}?pagina={page}"
            try:
                if session:
                    r = await session.get(url, headers=headers, impersonate="chrome110", timeout=15)
                else:
                    import httpx
                    async with httpx.AsyncClient() as client:
                        r = await client.get(url, headers=headers, timeout=15)
                if r.status_code == 200:
                    return r
            except Exception as e:
                print(f"Erro ao buscar página {page} no Vagas.com: {e}")
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
            soup = BeautifulSoup(r.text, 'html.parser')
            job_cards = soup.find_all('li', class_=lambda c: c and 'vaga' in str(c).lower())
            
            for card in job_cards:
                try:
                    title_el = card.find('a', class_=lambda c: c and 'link-vaga' in str(c).lower())
                    if not title_el:
                        title_el = card.find('h2')
                    if not title_el:
                        continue
                        
                    title = title_el.text.strip()
                    link = title_el.get('href', '') if title_el.name == 'a' else ''
                    if link and not link.startswith('http'):
                        link = 'https://www.vagas.com.br' + link
                        
                    comp_el = card.find('span', class_=lambda c: c and 'empr' in str(c).lower())
                    company = comp_el.text.strip() if comp_el else "Empresa Confidencial"
                    
                    desc_el = card.find('div', class_=lambda c: c and 'detalhes' in str(c).lower())
                    desc = desc_el.text.strip() if desc_el else f"Vaga para {title} no Vagas.com.br."
                    
                    job_obj = {
                        "platform": "Vagas.com",
                        "title": title,
                        "company": company,
                        "budget": "A Combinar",
                        "link": link,
                        "job_type": "CLT",
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
                except Exception as card_e:
                    continue
    except Exception as e:
        print("Erro Vagas.com:", e)
        
    return jobs
