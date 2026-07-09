import sys
sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright
import urllib.parse

keyword = "Python"
encoded_kw = urllib.parse.quote(keyword)
url = f"https://www.glassdoor.com.br/Job/jobs.htm?sc.keyword={encoded_kw}&locT=N&locId=0"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        viewport={"width": 1280, "height": 800},
        locale="pt-BR"
    )
    page = context.new_page()
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=45000)
        page.wait_for_timeout(3000)
        
        cards = page.query_selector_all('li[data-test="jobListing"]')
        print(f"Total cards: {len(cards)}")
        
        for idx, card in enumerate(cards[:5]):
            print(f"\n--- Card #{idx+1} ---")
            
            # Title
            title_sel = '[data-test="job-title"], a[data-test="job-link"], span[class*="job-title"], h3[class*="title"], h3'
            title_el = card.query_selector(title_sel)
            title = title_el.text_content().strip() if title_el else None
            print(f"  Title: {title}")
            
            # Company
            comp_sel = '[data-test="employer-name"], span[class*="employer-name"], div[class*="employerName"], span[class*="companyName"], p[class*="employer"]'
            comp_el = card.query_selector(comp_sel)
            company = comp_el.text_content().strip() if comp_el else None
            print(f"  Company: {company}")
            
            # Link
            link_el = card.query_selector('a[data-test="job-link"], a[href*="/Job/"], a[href*="/Vagas/"], a[href*="/partner/jobListing"], a')
            link = link_el.get_attribute("href") if link_el else None
            print(f"  Link: {link}")
            
            # Sibling tag or outer HTML of link
            if link_el:
                print(f"    Link HTML: <{link_el.evaluate('el => el.tagName')}> class=\"{link_el.get_attribute('class')}\" text=\"{link_el.text_content().strip()}\"")
                
    except Exception as e:
        print("Error:", e)
    finally:
        browser.close()
