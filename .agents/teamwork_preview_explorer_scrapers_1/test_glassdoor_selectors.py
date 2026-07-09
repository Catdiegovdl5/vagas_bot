import sys
sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright
import urllib.parse

keyword = "Python"
encoded_kw = urllib.parse.quote(keyword)
url = f"https://www.glassdoor.com.br/Job/jobs.htm?sc.keyword={encoded_kw}&locT=N&locId=0"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=45000)
        page.wait_for_timeout(5000)
        
        # Let's search for elements containing 'Boston Consulting'
        elems = page.query_selector_all('text=Boston Consulting')
        print(f"Elements containing 'Boston Consulting': {len(elems)}")
        for el in elems[:5]:
            # Print tag name and parent classes
            parent = el.evaluate_handle('el => el.parentElement')
            print(f"  Parent Tag: <{parent.evaluate('el => el.tagName')}> class=\"{parent.evaluate('el => el.className')}\"")
            gparent = parent.evaluate_handle('el => el.parentElement')
            print(f"    GParent Tag: <{gparent.evaluate('el => el.tagName')}> class=\"{gparent.evaluate('el => el.className')}\"")
            ggparent = gparent.evaluate_handle('el => el.parentElement')
            print(f"      GGParent Tag: <{ggparent.evaluate('el => el.tagName')}> class=\"{ggparent.evaluate('el => el.className')}\"")
            
        # Let's find all divs with classes containing 'job' or 'card'
        divs = page.query_selector_all('div[class*="job"], div[class*="card"], li[class*="job"], a[class*="job"]')
        print(f"Total elements with job/card class: {len(divs)}")
        for div in divs[:5]:
            print(f"  <{div.evaluate('el => el.tagName')}> class=\"{div.get_attribute('class')}\" text=\"{div.text_content().strip()[:50]}\"")
            
        # Let's dump links
        links = page.query_selector_all('a')
        print(f"Total links: {len(links)}")
        job_links = []
        for l in links:
            href = l.get_attribute('href')
            text = l.text_content().strip()
            if href and ('/Job/' in href or '/partner/' in href or 'jobListing' in href):
                job_links.append((href, text))
        print(f"Job links: {len(job_links)}")
        for hl, text in job_links[:10]:
            print(f"  Link: {hl} -> {text[:40]}")
            
    except Exception as e:
        print("Error:", e)
    finally:
        browser.close()
