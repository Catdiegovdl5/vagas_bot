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
        print(f"Navigating to Glassdoor: {url}")
        page.goto(url, wait_until="domcontentloaded", timeout=45000)
        page.wait_for_timeout(5000)
        
        print("Page title:", page.title())
        content = page.content()
        print("Content length:", len(content))
        
        # Check for bot detection indicators
        if "captcha" in content.lower() or "security check" in content.lower() or "checking your browser" in content.lower() or "cloudflare" in content.lower():
            print("BOT DETECTION TRIGGERED!")
            # Print a snippet of the page text
            print("Page Text Snippet:", page.inner_text("body")[:1000])
        else:
            print("No obvious bot block. Inspecting cards...")
            # Let's find what list items or job cards are on the page
            # Dump all class names of 'li' tags
            lis = page.query_selector_all('li')
            print("Total 'li' tags:", len(lis))
            classes = set()
            for li in lis[:30]:
                cls = li.get_attribute("class")
                if cls:
                    classes.add(cls)
            print("Some 'li' classes found:", list(classes)[:10])
            
            # Print text of first 5 lis
            for idx, li in enumerate(lis[:5]):
                print(f"  li #{idx+1} text: {li.text_content().strip()[:100]}")
    except Exception as e:
        print("Error during execution:", e)
    finally:
        browser.close()
