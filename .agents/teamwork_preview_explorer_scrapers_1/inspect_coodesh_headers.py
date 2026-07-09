import sys
sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    # We will log headers for Coodesh API requests
    def handle_request(request):
        if 'api.coodesh.com' in request.url:
            print(f"API Request: {request.url}")
            print("Headers:")
            headers = request.headers
            for k, v in headers.items():
                # Print non-sensitive or typical headers
                if k.lower() in ['authorization', 'x-api-key', 'referer', 'origin', 'content-type']:
                    print(f"  {k}: {v}")
                    
    page.on('request', handle_request)
    
    page.goto('https://coodesh.com/vagas?search=Python', wait_until='networkidle')
    page.wait_for_timeout(4000)
    
    browser.close()
