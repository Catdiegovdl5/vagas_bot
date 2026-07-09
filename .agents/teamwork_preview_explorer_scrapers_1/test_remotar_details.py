import sys
sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('https://remotar.com.br/search/jobs?q=Python', wait_until='networkidle')
    page.wait_for_timeout(3000)
    
    headers = page.query_selector_all('div.card-header')
    print(f"Total card-headers found: {len(headers)}")
    for h in headers[:3]:
        print("---")
        # Dump inner HTML of this header
        print(h.inner_html().strip())
        
    browser.close()
