import sys
sys.stdout.reconfigure(encoding='utf-8')
import requests
from bs4 import BeautifulSoup

try:
    from curl_cffi import requests as requests_cffi
except ImportError:
    requests_cffi = None

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# 1. Test Coodesh
coodesh_url = "https://coodesh.com/vagas?search=python"
print("=== TESTING COODESH ===")
try:
    r = requests.get(coodesh_url, headers=headers, timeout=15)
    print("Coodesh standard requests status:", r.status_code)
    print("Coodesh content length:", len(r.text))
    soup = BeautifulSoup(r.text, 'html.parser')
    
    # Check what job elements exist
    job_cards = soup.find_all('div', class_=lambda c: c and 'job-card' in str(c).lower())
    print("job-card divs found:", len(job_cards))
    
    links = soup.find_all('a', href=lambda h: h and '/vagas/' in h)
    print("Links with /vagas/ found:", len(links))
    if links:
        print("Sample link:", links[0].get('href'), "text:", links[0].text.strip())
        
except Exception as e:
    print("Coodesh error:", e)

# 2. Test Geekhunter
geek_url = "https://geekhunter.com.br/vagas?q=python"
print("\n=== TESTING GEEKHUNTER ===")
try:
    r = requests.get(geek_url, headers=headers, timeout=15)
    print("Geekhunter status:", r.status_code)
    print("Geekhunter length:", len(r.text))
    soup = BeautifulSoup(r.text, 'html.parser')
    job_cards = soup.find_all('div', class_=lambda c: c and 'job' in str(c).lower())
    print("Job class divs found:", len(job_cards))
    if len(r.text) < 1000:
        print("Body:", r.text)
except Exception as e:
    print("Geekhunter error:", e)
