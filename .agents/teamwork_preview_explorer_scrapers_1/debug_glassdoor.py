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
        print("Loading Glassdoor...")
        page.goto(url, wait_until="domcontentloaded", timeout=45000)
        page.wait_for_timeout(3000)
        
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
            found = page.query_selector_all(sel)
            print(f"Selector '{sel}' found: {len(found)} elements")
            if found:
                cards = found
                break
                
        if not cards:
            fallback_sel = 'a[href*="/Job/"], a[href*="/Vagas/"], a[href*="/partner/jobListing"]'
            found = page.query_selector_all(fallback_sel)
            print(f"Fallback selector '{fallback_sel}' found: {len(found)} elements")
            cards = found
            
        print("Total cards picked:", len(cards))
        for idx, card in enumerate(cards[:5]):
            print(f"Card #{idx+1} Tag: <{card.evaluate('el => el.tagName')}> Class: \"{card.get_attribute('class')}\"")
            # Try to query title
            title_sel = '[data-test="job-title"], a[data-test="job-link"], span[class*="job-title"], h3[class*="title"], h3'
            title_el = card.query_selector(title_sel)
            title_text = title_el.text_content().strip() if title_el else "NOT FOUND"
            print(f"  Title: {title_text}")
            
    except Exception as e:
        print("Error:", e)
    finally:
        browser.close()
