import sys
sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('https://remotar.com.br/search/jobs?q=Python', wait_until='networkidle')
    page.wait_for_timeout(3000)
    
    # Let's find links containing '/job/' and not 'company' or other irrelevant paths
    links = page.query_selector_all('a[href*="/job/"]')
    print(f"Total /job/ links: {len(links)}")
    for l in links[:5]:
        href = l.get_attribute('href')
        text = l.text_content().strip()
        print(f"  Link: {href} -> Text: {text}")
        
        # Walk up parents to see where the card is
        parent = l
        for depth in range(1, 4):
            parent = parent.evaluate_handle('el => el.parentElement')
            tag = parent.evaluate('el => el.tagName')
            cls = parent.evaluate('el => el.className')
            print(f"    Parent at depth {depth}: <{tag}> class=\"{cls}\"")
            
    browser.close()
