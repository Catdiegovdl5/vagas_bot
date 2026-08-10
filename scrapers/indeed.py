import urllib.parse
import hashlib
from playwright.sync_api import sync_playwright
import re
import json
import time
from bs4 import BeautifulSoup

try:
    from curl_cffi import requests as requests_cffi
except ImportError:
    requests_cffi = None

try:
    from playwright_stealth import stealth_sync
except ImportError:
    stealth_sync = None

def scrape(keyword="Python", level="Todos", location="", country="", **kwargs):
    c_str = (country or "").lower()
    l_str = (location or "").lower()
    loc = location or country or kwargs.get("location") or kwargs.get("country") or ""
    if "Londrina" in loc:
        loc_param = "&l=Londrina%2C+PR&radius=15"
    elif "Assaí" in loc:
        loc_param = "&l=Assa%C3%AD%2C+PR&radius=15"
    elif loc and loc.lower() not in ["todos", "brasil", "brasil (remoto)", "remoto", "qualquer", ""]:
        loc_param = f"&l={urllib.parse.quote(loc)}"
    else:
        loc_param = ""
        
    jobs = []

    # Mapeamento: keyword padronizada → termo de busca no Indeed
    indeed_mapping = {
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
        "prompt engineer":               "prompt engineer ia",
        "machine learning engineer":     "machine learning engineer",
        # Desenvolvimento
        "desenvolvedor python":          "desenvolvedor python",
        "desenvolvedor backend":         "desenvolvedor backend",
        "desenvolvedor node":            "desenvolvedor node.js",
        "desenvolvedor react":           "desenvolvedor react",
        "desenvolvedor fullstack":       "desenvolvedor fullstack",
        "desenvolvedor django":          "desenvolvedor django",
        "desenvolvedor fastapi":         "desenvolvedor fastapi",
        "desenvolvedor rpa":             "desenvolvedor rpa automacao",
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
        "growth hacker":                "growth hacker marketing",
        "analista de marketing digital": "analista marketing digital",
        "especialista em seo":          "especialista seo",
        "analista de marketing junior": "analista marketing junior",
        # Design & Video
        "video maker":                  "videomaker",
        "social media":                 "social media",
        "ux designer":                  "ux designer",
        # Admin
        "analista de rh":               "analista rh",
        "suporte tecnico n1":           "suporte tecnico",
        "assistente de faturamento":    "assistente faturamento",
    }

    kw_str = keyword or "Python"
    lvl_str = level or "Todos"
    kw_clean = kw_str.lower().strip()
    search_term = indeed_mapping.get(kw_clean, kw_str)
    if lvl_str != "Todos":
        search_term += f" {lvl_str}"
    encoded_kw = urllib.parse.quote(search_term)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        if stealth_sync:
            stealth_sync(page)
        
        for start in [0, 10]:
            url = f"https://br.indeed.com/jobs?q={encoded_kw}{loc_param}&start={start}"
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=60000)
                content = page.content()
                
                # Cloudflare check
                if "Cloudflare" in content or "Please wait..." in content:
                    page.wait_for_timeout(5000)
                    content = page.content()
                
                match = re.search(r'window\.mosaic\.providerData\[[\'"]mosaic-provider-jobcards[\'"]\]\s*=\s*(\{.*?\});', content, re.DOTALL | re.IGNORECASE)
                if not match:
                    match = re.search(r'window\._initialData\s*=\s*(\{.*?\});', content, re.DOTALL)
                
                if match:
                    try:
                        data = json.loads(match.group(1))
                    except Exception:
                        data = {}
                    
                    meta_data = data.get("metaData") if isinstance(data, dict) else {}
                    mosaic_model = meta_data.get("mosaicProviderJobCardsModel") if isinstance(meta_data, dict) else {}
                    raw_results = mosaic_model.get("results") if isinstance(mosaic_model, dict) else []
                    results = raw_results if isinstance(raw_results, list) else []
                    
                    detail_count = 0  # Limite de páginas de detalhe por execução
                    for r in results:
                        if not isinstance(r, dict):
                            continue
                        title = r.get("title", "Sem Título")
                        company = r.get("company", "Empresa Confidencial")
                        jobkey = r.get("jobkey", "")
                        link = f"https://br.indeed.com/viewjob?jk={jobkey}" if jobkey else ""
                        snippet = r.get("snippet", "")
                        clean_snippet = re.sub('<[^<]+>', '', snippet) if snippet else ""
                        location_val = r.get("formattedLocation", "Remoto/Brasil")
                        salary_obj = r.get("salarySnippet")
                        salary = salary_obj.get("text", "A Combinar") if isinstance(salary_obj, dict) else "A Combinar"
                        
                        if title != "Sem Título" and link:
                            description = ""
                            fetched_by_cffi = False
                            
                            # Buscar detalhe apenas para as 5 primeiras vagas (evita lentidão de 116s)
                            if detail_count < 5:
                                # 1. Try curl_cffi
                                if jobkey and requests_cffi:
                                    try:
                                        headers = {
                                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                                            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                                            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
                                            "Referer": "https://br.indeed.com/"
                                        }
                                        detail_url = f"https://br.indeed.com/viewjob?jk={jobkey}"
                                        resp = requests_cffi.get(detail_url, impersonate="chrome110", headers=headers, timeout=10.0)
                                        if resp.status_code == 200 and "Cloudflare" not in resp.text and "Please wait..." not in resp.text:
                                            soup = BeautifulSoup(resp.text, "html.parser")
                                            desc_el = (
                                                soup.find(id="jobDescriptionText") or
                                                soup.find(attrs={"data-testid": "jobDescriptionText"}) or
                                                soup.find(attrs={"data-testid": "job-description"}) or
                                                soup.find(class_=lambda c: c and "jobsearch-jobDescriptionText" in str(c)) or
                                                soup.find(class_=lambda c: c and "job-description" in str(c)) or
                                                soup.find(class_=lambda c: c and "jobDescription" in str(c))
                                            )
                                            if desc_el:
                                                description = desc_el.get_text(separator="\n").strip()
                                                fetched_by_cffi = True
                                    except Exception as cffi_e:
                                        print(f"curl_cffi failed for Indeed job {jobkey}: {cffi_e}")
                                
                                # 2. Fallback to Playwright (reuse existing context)
                                if jobkey and (not fetched_by_cffi or not description or len(description) < 100):
                                    detail_page = None
                                    try:
                                        detail_page = context.new_page()
                                        if stealth_sync:
                                            stealth_sync(detail_page)
                                        detail_page.goto(f"https://br.indeed.com/viewjob?jk={jobkey}", wait_until="domcontentloaded", timeout=30000)
                                        
                                        SELECTORS = [
                                            "#jobDescriptionText",
                                            "[data-testid='jobDescriptionText']",
                                            "[data-testid='job-description']",
                                            ".jobsearch-jobDescriptionText",
                                            ".job-description",
                                            "[class*='jobDescription']",
                                            "[class*='JobDescription']",
                                        ]
                                        sel_string = ", ".join(SELECTORS)
                                        try:
                                            detail_page.wait_for_selector(sel_string, timeout=10000)
                                            desc_el = detail_page.query_selector(sel_string)
                                            if desc_el:
                                                description = desc_el.text_content().strip()
                                        except Exception:
                                            pass
                                    except Exception as pw_e:
                                        print(f"Playwright fallback failed for Indeed job {jobkey}: {pw_e}")
                                    finally:
                                        if detail_page:
                                            detail_page.close()
                                
                                detail_count += 1
                                         
                            if not description:
                                description = f"Local: {location_val}. Resumo: {clean_snippet}"
                                
                            job_id = hashlib.md5(link.encode('utf-8')).hexdigest()[:16]
                            job_obj = {
                                "id": job_id,
                                "platform": "Indeed",
                                "title": title,
                                "company": company,
                                "budget": salary,
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

            except Exception as e:
                print(f"Erro no scraper Indeed Playwright na página {start}: {e}")
                
        browser.close()
            
    return jobs

