import urllib.parse
from playwright.sync_api import sync_playwright

try:
    from playwright_stealth import stealth_sync
except ImportError:
    stealth_sync = None

def scrape(keyword, level="Todos", country="Brasil"):
    jobs = []
    encoded_kw = urllib.parse.quote(keyword)
    
    # Glassdoor BR redireciona para /vagas/ com parâmetro sc.keyword
    urls_to_try = [
        f"https://www.glassdoor.com.br/Job/jobs.htm?sc.keyword={encoded_kw}&locT=N&locId=0",
        f"https://www.glassdoor.com.br/Vagas/{urllib.parse.quote(keyword.replace(' ', '-'))}-vagas-SRCH_KO0,{len(keyword)}.htm",
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
                            description = desc_el.text_content().strip()
                    except Exception:
                        pass
                    
                    if not description:
                        description = f"Vaga de {title} na empresa {company}. Acesse o link para mais detalhes e candidatura."

                    jobs.append({
                        "platform": "Glassdoor",
                        "title": title,
                        "company": company,
                        "budget": budget,
                        "link": link,
                        "job_type": "CLT",
                        "profession": keyword,
                        "level": level,
                        "requirements": description
                    })
                except Exception:
                    continue
                    
        except Exception as e:
            print(f"Erro geral no scraper Glassdoor: {e}")
        finally:
            browser.close()
            
    return jobs
