import sys
sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    requests_logged = []
    page.on('request', lambda r: requests_logged.append(r.url))
    
    page.goto('https://coodesh.com/vagas?search=Python', wait_until='networkidle')
    page.wait_for_timeout(3000)
    
    print("Logged requests for Coodesh:")
    for url in requests_logged:
        if 'coodesh' in url and ('api' in url or 'json' in url or 'graphql' in url or 'query' in url or 'search' in url):
            print("  -", url)
            
    browser.close()
