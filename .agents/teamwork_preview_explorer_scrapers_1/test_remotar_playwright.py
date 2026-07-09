import sys
sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('https://remotar.com.br/search/jobs?q=Python', wait_until='networkidle')
    page.wait_for_timeout(3000)
    
    elems = page.query_selector_all('text=Python')
    print('Elements with text Python:', len(elems))
    for el in elems[:10]:
        try:
            parent = el.evaluate_handle('el => el.parentElement')
            tag = parent.evaluate('el => el.tagName')
            cls = parent.evaluate('el => el.className')
            print(f'  Parent: <{tag}> class="{cls}" text="{el.text_content().strip()[:40]}"')
        except Exception as e:
            print('Error evaluating parent:', e)
        
    links = page.query_selector_all('a')
    print('Total links:', len(links))
    job_links = []
    for l in links:
        href = l.get_attribute('href')
        text = l.text_content().strip()
        if href and ('/vaga/' in href or '/vagas/' in href or 'job' in href):
            job_links.append((href, text))
    print('Total job links found:', len(job_links))
    for hl, text in job_links[:10]:
        print(f'  Link: {hl} -> {text}')
        
    # Let's inspect the actual HTML of the job elements or cards if they exist
    # Let's find any div that contains job postings
    job_cards = page.query_selector_all('div[class*="job"], div[class*="card"], li[class*="job"], a[class*="job"]')
    print('Total elements matching div/li/a with class containing job/card:', len(job_cards))
    for card in job_cards[:5]:
        cls = card.get_attribute('class')
        print(f'  Card tag: <{card.evaluate("el => el.tagName")}> class="{cls}" text="{card.text_content().strip()[:50]}"')
        
    browser.close()
