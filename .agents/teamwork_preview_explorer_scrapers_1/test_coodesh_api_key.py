import sys
sys.stdout.reconfigure(encoding='utf-8')
import requests

url = 'https://api.coodesh.com/v2/jobs?search=Python&pageSize=30'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json, text/plain, */*',
    'referer': 'https://coodesh.com/',
    'x-csh-key': 'coodesh-experts',
    'x-language': 'pt'
}

try:
    r = requests.get(url, headers=headers, timeout=15)
    print('Status:', r.status_code)
    print('Content-Type:', r.headers.get('Content-Type'))
    if r.status_code == 200:
        data = r.json()
        print('SUCCESS!')
        if isinstance(data, dict):
            print('Data keys:', data.keys())
            # Check if there is a jobs list, let's find list fields
            for k, v in data.items():
                if isinstance(v, list):
                    print(f"Key '{k}' length: {len(v)}")
                    if v:
                        print("Sample item keys:", v[0].keys() if hasattr(v[0], 'keys') else type(v[0]))
                        if hasattr(v[0], 'get'):
                            print("Sample title:", v[0].get('title'))
                            print("Sample company:", v[0].get('company', {}).get('name') if isinstance(v[0].get('company'), dict) else v[0].get('company'))
                            print("Sample link slug:", v[0].get('slug'))
    else:
        print('Response text:', r.text[:500])
except Exception as e:
    print('Error:', e)
