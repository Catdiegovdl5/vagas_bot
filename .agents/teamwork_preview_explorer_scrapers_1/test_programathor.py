import sys
sys.stdout.reconfigure(encoding='utf-8')
import requests
from bs4 import BeautifulSoup

try:
    from curl_cffi import requests as requests_cffi
except ImportError:
    requests_cffi = None

url = "https://programathor.com.br/jobs-python"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

print("--- Testing standard requests ---")
try:
    r = requests.get(url, headers=headers, timeout=15)
    print("Status:", r.status_code)
    print("Content length:", len(r.text))
    soup = BeautifulSoup(r.text, 'html.parser')
    cards = soup.find_all('div', class_=lambda c: c and 'cell-list' in str(c).lower())
    print("Cards found (requests):", len(cards))
    if len(r.text) < 1000:
        print("Body:", r.text)
except Exception as e:
    print("Error requests:", e)

if requests_cffi:
    print("\n--- Testing curl_cffi ---")
    try:
        r2 = requests_cffi.get(url, headers=headers, impersonate="chrome110", timeout=15)
        print("Status (cffi):", r2.status_code)
        print("Content length (cffi):", len(r2.text))
        soup2 = BeautifulSoup(r2.text, 'html.parser')
        cards2 = soup2.find_all('div', class_=lambda c: c and 'cell-list' in str(c).lower())
        print("Cards found (cffi):", len(cards2))
        if len(r2.text) < 1000:
            print("Body (cffi):", r2.text)
    except Exception as e:
        print("Error cffi:", e)
else:
    print("\ncurl_cffi is NOT installed")
