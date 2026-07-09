import sys
sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    requests_logged = []
    page.on('request', lambda r: requests_logged.append(r.url))
    
    # Go to the new Geekhunter search URL directly
    url = 'https://www.geekhunter.com/pt/vagas?q=Python'
    page.goto(url, wait_until='networkidle')
    page.wait_for_timeout(3000)
    
    print("Geekhunter page title:", page.title())
    print("Geekhunter final URL:", page.url)
    
    # Print all logged requests that are not google/analytics/ads
    print("\nLogged non-ad requests:")
    for r_url in requests_logged:
        if not any(k in r_url for k in ['google', 'analytics', 'doubleclick', 'privacytools', 'facebook', 'hotjar', 'linkedin']):
            print("  -", r_url)
            
    browser.close()
