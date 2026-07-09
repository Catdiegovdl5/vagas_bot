import sys
sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('https://www.geekhunter.com/pt/vagas?q=Python', wait_until='networkidle')
    page.wait_for_timeout(3000)
    
    # Check if there is any link containing 'vaga'
    links = page.query_selector_all('a')
    print("Total links on Geekhunter:", len(links))
    job_links = []
    for l in links:
        href = l.get_attribute('href')
        text = l.text_content().strip()
        if href and ('vaga' in href or 'job' in href):
            job_links.append((href, text))
    print("Job-like links found:", len(job_links))
    for href, text in job_links[:10]:
        print(f"  Link: {href} -> Text: {text}")
        
    # Let's check text content of the page to see if we can see job titles
    body_text = page.inner_text('body')
    print("Does body contain 'vaga'?", 'vaga' in body_text.lower())
    print("Does body contain 'python'?", 'python' in body_text.lower())
    
    # Print the first few headings
    headings = page.query_selector_all('h1, h2, h3, h4')
    print("Total headings:", len(headings))
    for h in headings[:10]:
        print(f"  <{h.evaluate('el => el.tagName')}>: {h.text_content().strip()}")
        
    browser.close()
