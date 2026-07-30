import urllib.parse
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import asyncio
import re

try:
    from curl_cffi import requests as requests_cffi
except ImportError:
    requests_cffi = None

try:
    from playwright_stealth import Stealth
    async def apply_stealth(page):
        try:
            await Stealth().apply_stealth_async(page)
        except Exception as e:
            print("Erro ao aplicar stealth:", e)
except ImportError:
    apply_stealth = None

async def scrape(keyword="Python", level="Todos", max_pages=10, location="", country="", **kwargs):
    jobs = []
    c_str = (country or "").lower()
    l_str = (location or "").lower()
    loc = location or country or kwargs.get("location") or kwargs.get("country") or ""
    if loc and loc.upper() in ["USA", "US", "UNITED STATES"]:
        return jobs

    # Mapeamento: keyword padronizada → termo de busca no InfoJobs
    infojobs_mapping = {
        # --- 6 NOVAS CATEGORIAS MACRO E SUB-PROFISSÕES ---
        # 1. Operações Físicas
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

        # 2. Logística
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

        # 3. Administrativo
        "administrativo":               "assistente administrativo escritorio",
        "assistente administrativo":    "assistente administrativo",
        "auxiliar administrativo":      "auxiliar administrativo",
        "recepcionista":                "recepcionista",
        "auxiliar de escritório":       "auxiliar escritorio",
        "auxiliar de escritorio":       "auxiliar escritorio",
        "data entry":                   "data entry digitador",
        "digitador":                    "digitador",
        "assistente financeiro":        "assistente financeiro",

        # 4. Criativos de Performance
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

        # 5. Inteligência de Vendas
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

        # 6. Engenharia de IA/Dados
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
        "especialista em ia":            "inteligencia artificial",
        "especialista em ia generativa": "ia generativa",
        "desenvolvedor de agentes ia":   "desenvolvedor ia",
        "prompt engineer":               "prompt engineer",
        "machine learning engineer":     "machine learning",
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
        "analista de rh":               "analista rh",
        "suporte tecnico n1":           "suporte tecnico",
        "assistente de faturamento":    "assistente faturamento",
    }

    kw_str = keyword or "Python"
    lvl_str = level or "Todos"
    kw_clean = kw_str.lower().strip()
    search_term = infojobs_mapping.get(kw_clean, kw_str)
    if lvl_str != "Todos":
        search_term += f" {lvl_str}"
    if loc and loc.lower() not in ["todos", "brasil", "brasil (remoto)", "remoto", "qualquer", ""]:
        search_term += f" {loc}"
    encoded_kw = urllib.parse.quote(search_term)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7"
    }

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
            locale="pt-BR"
        )
        
        raw_cards_info = []
        
        for page_num in range(1, max_pages + 1):
            url = f"https://www.infojobs.com.br/vagas-de-emprego.aspx?palavra={encoded_kw}&page={page_num}"
            page = await context.new_page()
            if apply_stealth:
                await apply_stealth(page)
            
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=60000)
                await page.wait_for_timeout(3000)
                
                cards = await page.query_selector_all('div.element-vaga, div[class*="js_vacancyCard"], div[class*="vacancyCard"], [data-type="vacancy"]')
                if not cards:
                    cards = await page.query_selector_all('a[href*="vaga-de-"], a[href*="/vaga-"]')
                
                for card in cards[:15]:
                    try:
                        link_el = await card.query_selector('a[href*="vaga-de-"], a[href*="/vaga-"], a')
                        link = await link_el.get_attribute("href") if link_el else ""
                        if not link:
                            card_href = await card.get_attribute("href")
                            if card_href:
                                link = card_href
                                
                        if not link:
                            continue
                            
                        if not link.startswith("http"):
                            link = urllib.parse.urljoin("https://www.infojobs.com.br", link)
                            
                        title_el = (await card.query_selector('h3') or 
                                    await card.query_selector('h2') or 
                                    await card.query_selector('div[class*="title"]') or 
                                    link_el)
                        title = await title_el.text_content() if title_el else "Sem Título"
                        title = title.strip()
                        if not title or title == "Sem Título":
                            title = await card.text_content()
                            title = title.strip()
                            
                        if "\n" in title:
                            title = title.split("\n")[0].strip()
                            
                        comp_el = (await card.query_selector('div.companyName') or 
                                   await card.query_selector('.company') or 
                                   await card.query_selector('div[class*="company"]') or
                                   await card.query_selector('a[href*="empresa"]'))
                        company = await comp_el.text_content() if comp_el else "Empresa Confidencial"
                        company = company.strip()
                        if "\n" in company:
                            company = company.split("\n")[0].strip()
                            
                        salary_el = (await card.query_selector('div.salary') or 
                                     await card.query_selector('span[class*="salary"]') or 
                                     await card.query_selector('.val-salary') or
                                     await card.query_selector('span[class*="valor"]'))
                        budget = await salary_el.text_content() if salary_el else "A Combinar"
                        budget = budget.strip()
                        
                        if title == "Sem Título" or not link:
                            continue
                            
                        raw_cards_info.append({
                            "title": title,
                            "company": company,
                            "budget": budget,
                            "link": link
                        })
                    except Exception as card_e:
                        print(f"Erro ao processar card Infojobs: {card_e}")
            except Exception as page_e:
                print(f"Erro ao acessar pagina {page_num} do Infojobs: {page_e}")
            finally:
                await page.close()

        # Deduplicate
        seen_links = set()
        unique_cards = []
        for c in raw_cards_info:
            if c["link"] not in seen_links:
                seen_links.add(c["link"])
                unique_cards.append(c)

        async def get_description(session, card_info):
            link = card_info["link"]
            title = card_info["title"]
            company = card_info["company"]
            description = ""
            fetched_by_cffi = False
            
            if session:
                try:
                    resp = await session.get(link, impersonate="chrome110", headers=headers, timeout=10)
                    if resp.status_code == 200 and "Cloudflare" not in resp.text:
                        soup = BeautifulSoup(resp.text, "html.parser")
                        desc_container = (soup.find("div", class_="description") or 
                                          soup.find("div", class_="vaga-desc") or 
                                          soup.find("div", class_=re.compile(r"description|vaga-desc|job-desc")))
                        if desc_container:
                            description = desc_container.get_text(separator="\n").strip()
                            fetched_by_cffi = True
                except Exception as cffi_e:
                    print(f"curl_cffi timeout infojobs: {cffi_e}")
            
            if not fetched_by_cffi or not description or len(description) < 100:
                detail_page = None
                try:
                    detail_page = await context.new_page()
                    if apply_stealth:
                        await apply_stealth(detail_page)
                    await detail_page.goto(link, wait_until="domcontentloaded", timeout=30000)
                    await detail_page.wait_for_timeout(1000)
                    
                    desc_el = (await detail_page.query_selector('div.description') or 
                               await detail_page.query_selector('div.vaga-desc') or 
                               await detail_page.query_selector('div[class*="description"]') or
                               await detail_page.query_selector('div[class*="vaga-desc"]') or
                               await detail_page.query_selector('section[class*="description"]'))
                    if desc_el:
                        description = await desc_el.text_content()
                        description = description.strip()
                except Exception as pw_detail_e:
                    print(f"Playwright fallback timeout infojobs: {pw_detail_e}")
                finally:
                    if detail_page:
                        await detail_page.close()
            
            if not description:
                description = f"Informações adicionais para a oportunidade de {title} na empresa {company}. Para consultar os requisitos completos e instruções de candidatura, acesse a página oficial através do link fornecido."
                
            return {
                "platform": "Infojobs",
                "title": title,
                "company": company,
                "budget": card_info["budget"],
                "link": link,
                "job_type": "CLT",
                "profession": keyword,
                "level": level,
                "requirements": description
            }

        sem = asyncio.Semaphore(3)
        async def sem_get_desc(session, card_info):
            async with sem:
                return await get_description(session, card_info)

        if requests_cffi and hasattr(requests_cffi, "AsyncSession"):
            async with requests_cffi.AsyncSession() as session:
                tasks = [sem_get_desc(session, card) for card in unique_cards]
                jobs = await asyncio.gather(*tasks)
        else:
            tasks = [sem_get_desc(None, card) for card in unique_cards]
            jobs = await asyncio.gather(*tasks)
            
        await browser.close()
        
    return list(jobs)
