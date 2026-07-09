import sys
sys.stdout.reconfigure(encoding='utf-8')
import urllib.parse
from playwright.sync_api import sync_playwright

try:
    from playwright_stealth import stealth_sync
except ImportError:
    stealth_sync = None

def scrape_with_trace(keyword, level="Todos", country="Brasil"):
    print("Starting trace...")
    jobs = []
    encoded_kw = urllib.parse.quote(keyword)
    
    urls_to_try = [
        f"https://www.glassdoor.com.br/Vagas/{urllib.parse.quote(keyword.replace(' ', '-'))}-vagas-SRCH_KO0,{len(keyword)}.htm",
        f"https://www.glassdoor.com.br/Job/jobs.htm?sc.keyword={encoded_kw}&locT=N&locId=0",
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
            print("Applying stealth sync...")
            stealth_sync(page)
        
        loaded = False
        for url in urls_to_try:
            try:
                print(f"Trying URL: {url}")
                page.goto(url, wait_until="domcontentloaded", timeout=45000)
                page.wait_for_timeout(3000)
                
                content = page.content()
                print(f"Content length: {len(content)}")
                # Check for blocking keywords
                if "captcha" in content.lower() or "security check" in content.lower() or "checking your browser" in content.lower():
                    print("Page contains block words (captcha/security check/checking browser)!")
                
                if ("glassdoor" in content.lower() or "mock" in content.lower()) and len(content) > 20:
                    loaded = True
                    print("Loaded successfully!")
                    break
            except Exception as e:
                print(f"Error loading URL: {e}")
                continue
        
        if not loaded:
            print("Not loaded. Exiting...")
            browser.close()
            return jobs
            
        try:
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
                    print(f"Checking selector '{sel}': found {len(found)}")
                    if found:
                        cards = found
                        break
                except Exception as sel_e:
                    print(f"Error querying selector '{sel}': {sel_e}")
                    continue
            
            if not cards:
                print("No cards found. Querying fallback...")
                cards = page.query_selector_all('a[href*="/Job/"], a[href*="/Vagas/"], a[href*="/partner/jobListing"]')
                print(f"Fallback found {len(cards)}")

            print(f"Looping over {len(cards)} cards...")
            for idx, card in enumerate(cards[:20]):
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
                    
                    comp_sel = ', '.join([
                        '[data-test="employer-name"]',
                        'span[class*="employer-name"]',
                        'div[class*="employerName"]',
                        'span[class*="companyName"]',
                        'p[class*="employer"]',
                    ])
                    comp_el = card.query_selector(comp_sel)
                    company = comp_el.text_content().strip() if comp_el else "Empresa Confidencial"
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

                    print(f"Card #{idx+1}: Title='{title}', Company='{company}', Link='{link}'")
                    if not link:
                        print("  Skipped due to empty link!")
                        continue
                    
                    # We print click logic to see if it causes any error
                    print("  Attempting to click card/title...")
                    try:
                        if title_el:
                            title_el.click(force=True)
                        else:
                            card.click(force=True)
                        page.wait_for_timeout(1000)
                        print("  Clicked!")
                    except Exception as click_e:
                        print(f"  Click failed: {click_e}")
                        
                except Exception as card_e:
                    print(f"  Error on card #{idx+1}: {card_e}")
                    continue
                    
        except Exception as e:
            print(f"Erro geral: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    scrape_with_trace("Python")
