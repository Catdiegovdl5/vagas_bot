import urllib.parse
from playwright.sync_api import sync_playwright

try:
    from playwright_stealth import stealth_sync
except ImportError:
    stealth_sync = None

def scrape(keyword="Python", level="Todos", location="", country="", **kwargs):
    jobs = []
    c_str = (country or "").lower()
    l_str = (location or "").lower()
    loc = location or country or kwargs.get("location") or kwargs.get("country") or ""

    # Mapeamento: keyword padronizada → termo de busca no Glassdoor
    glassdoor_mapping = {
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
        "engenharia de dados":          "engenheiro de dados etl",
        "engenheiro de dados":          "engenheiro de dados",
        "data engineer":                "data engineer",
        "engenheiro de ia":              "engenheiro ia",
        "machine learning":             "machine learning engineer",
        "cientista de dados":            "cientista de dados",
        "analista de dados":            "analista de dados",

        # IA / AI
        "especialista em ia":            "especialista inteligencia artificial",
        "especialista em ia generativa": "ia generativa",
        "desenvolvedor de agentes ia":   "desenvolvedor agentes ia",
        "prompt engineer":               "prompt engineer",
        "machine learning engineer":     "machine learning engineer",
        # Desenvolvimento
        "desenvolvedor python":          "desenvolvedor python",
        "desenvolvedor backend":         "desenvolvedor backend",
        "desenvolvedor node":            "desenvolvedor node",
        "desenvolvedor react":           "desenvolvedor react",
        "desenvolvedor fullstack":       "desenvolvedor fullstack",
        "desenvolvedor django":          "desenvolvedor django",
        "desenvolvedor fastapi":         "desenvolvedor fastapi",
        "desenvolvedor rpa":             "desenvolvedor rpa",
        "desenvolvedor junior python":   "desenvolvedor python junior",
        "desenvolvedor junior react":    "desenvolvedor react junior",
        "desenvolvedor junior fullstack": "desenvolvedor fullstack junior",
        "desenvolvedor pleno python":    "desenvolvedor python pleno",
        "desenvolvedor pleno react":     "desenvolvedor react pleno",
        "desenvolvedor pleno fullstack": "desenvolvedor fullstack pleno",
        # Dados & Analytics
        "analista de analytics":        "analista analytics",
        "analista sql":                 "analista sql",
        "analista de power bi":         "analista power bi",
        "analista de dados junior":     "analista dados junior",
        "analista de dados pleno":      "analista dados pleno",
        # Marketing & Growth
        "gestor de trafego pleno":      "gestor trafego pago pleno",
        "growth hacker":                "growth hacker",
        "analista de marketing digital": "analista marketing digital",
        "especialista em seo":          "especialista seo",
        "analista de marketing junior": "analista marketing junior",
        # Design & Video
        "video maker":                  "videomaker",
        "social media":                 "social media",
        "ux designer":                  "ux designer",
        # Admin
        "analista de rh":               "analista recursos humanos",
        "suporte tecnico n1":           "suporte tecnico",
        "assistente de faturamento":    "assistente faturamento",
    }

    kw_str = keyword or "Python"
    lvl_str = level or "Todos"
    kw_clean = kw_str.lower().strip()
    search_term = glassdoor_mapping.get(kw_clean, kw_str)
    if lvl_str != "Todos":
        search_term += f" {lvl_str}"
    if loc and loc.lower() not in ["todos", "brasil", "brasil (remoto)", "remoto", "qualquer", ""]:
        search_term += f" {loc}"
    encoded_kw = urllib.parse.quote(search_term)
    
    # Glassdoor BR redireciona para /vagas/ com parâmetro sc.keyword
    urls_to_try = [
        f"https://www.glassdoor.com.br/Job/jobs.htm?sc.keyword={encoded_kw}&locT=N&locId=0",
        f"https://www.glassdoor.com.br/Vagas/{urllib.parse.quote(search_term.replace(' ', '-'))}-vagas-SRCH_KO0,{len(search_term)}.htm",
    ]
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
            locale="pt-BR",
            extra_http_headers={
                "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7"
            }
        )
        page = context.new_page()
        if stealth_sync:
            stealth_sync(page)
        
        loaded = False
        for url in urls_to_try:
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=45000)
                page.wait_for_timeout(3000)
                
                # Verificar se carregou algo útil
                content = page.content()
                content_lower = content.lower()
                
                is_blocked = (
                    "cloudflare" in content_lower or 
                    "security check" in content_lower or 
                    "checking your browser" in content_lower or 
                    "turnstile" in content_lower or 
                    "captcha" in content_lower or
                    "please enable js" in content_lower
                )
                
                if ("glassdoor" in content_lower or "mock" in content_lower) and len(content) > 20 and not is_blocked:
                    loaded = True
                    break
            except Exception:
                continue
        
        if not loaded:
            browser.close()
            return jobs
            
        try:
            # Seletores amplos para capturar cards de vagas
            CARD_SELECTORS = [
                'li[data-test="jobListing"]',
                'li[class*="JobsList_jobListItem"]',
                'li[class*="jobListItem"]',
                'article[class*="jobCard"]',
                'div[class*="jobCard"]',
                'li[data-jobid]',
                'a[data-test="job-link"]',
            ]
            
            cards = []
            for sel in CARD_SELECTORS:
                try:
                    found = page.query_selector_all(sel)
                    if found:
                        cards = found
                        break
                except Exception:
                    continue
            
            # Fallback: procurar por links de vagas
            if not cards:
                cards = page.query_selector_all('a[href*="/Job/"], a[href*="/Vagas/"], a[href*="/partner/jobListing"]')

            for card in cards[:20]:
                try:
                    title_sel = ', '.join([
                        '[data-test="job-title"]',
                        'a[data-test="job-link"]',
                        'span[class*="job-title"]',
                        'h3[class*="title"]',
                        'h3',
                    ])
                    title_el = card.query_selector(title_sel)
                    title = title_el.text_content().strip() if title_el else ""
                    if not title:
                        continue

                    comp_sel = ', '.join([
                        '[data-test="employer-name"]',
                        'span[class*="employer-name"]',
                        'div[class*="employerName"]',
                        'span[class*="companyName"]',
                        'p[class*="employer"]',
                    ])
                    comp_el = card.query_selector(comp_sel)
                    company = comp_el.text_content().strip() if comp_el else "Empresa Confidencial"
                    # Limpar rating (ex: "Empresa ★ 4.2")
                    if " ★" in company:
                        company = company.split(" ★")[0].strip()
                    if "\n" in company:
                        company = company.split("\n")[0].strip()
                    
                    link_el = card.query_selector('a[data-test="job-link"], a[href*="/Job/"], a[href*="/Vagas/"], a[href*="/partner/jobListing"], a')
                    link = ""
                    if link_el:
                        link = link_el.get_attribute("href") or ""
                    if link and not link.startswith("http"):
                        link = urllib.parse.urljoin("https://www.glassdoor.com.br", link)

                    if not link:
                        continue

                    salary_el = card.query_selector('[data-test="detailSalary"], span[class*="salary"], div[class*="salary"]')
                    budget = salary_el.text_content().strip() if salary_el else "A Combinar"
                    
                    # Tenta buscar descrição clicando na vaga (painel lateral)
                    description = ""
                    try:
                        if title_el:
                            title_el.click(force=True)
                        else:
                            card.click(force=True)
                        page.wait_for_timeout(1200)
                        
                        desc_sel = ', '.join([
                            '[data-test="jobDescription"]',
                            'div[class*="jobDescription"]',
                            'div.jobDescriptionContent',
                            '#JobDescriptionContainer',
                            '.desc.module',
                        ])
                        try:
                            page.wait_for_selector(desc_sel, timeout=5000)
                        except Exception:
                            pass
                        desc_el = page.query_selector(desc_sel)
                        if desc_el:
                            raw_desc = desc_el.text_content()
                            description = raw_desc.strip() if raw_desc else ""
                    except Exception:
                        pass
                    
                    if not description:
                        description = f"Vaga de {title} na empresa {company}. Acesse o link para mais detalhes e candidatura."

                    job_obj = {
                        "platform": "Glassdoor",
                        "title": title,
                        "company": company,
                        "budget": budget,
                        "link": link,
                        "job_type": "CLT",
                        "profession": keyword,
                        "level": level,
                        "requirements": description
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
            print(f"Erro geral no scraper Glassdoor: {e}")
        finally:
            browser.close()
            
    return jobs
