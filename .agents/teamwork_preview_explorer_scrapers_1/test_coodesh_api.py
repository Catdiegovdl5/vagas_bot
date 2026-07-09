import sys
sys.stdout.reconfigure(encoding='utf-8')
import requests

url = 'https://api.coodesh.com/v2/jobs?search=Python&pageSize=30'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json, text/plain, */*'
}

try:
    r = requests.get(url, headers=headers, timeout=15)
    print('Status:', r.status_code)
    if r.status_code == 200:
        data = r.json()
        print('Data keys:', data.keys() if hasattr(data, 'keys') else type(data))
        if isinstance(data, dict):
            # Print keys and some samples
            for k, v in data.items():
                if isinstance(v, list):
                    print(f"Key '{k}' is list of length {len(v)}")
                    if v:
                        print("  Sample element:", v[0])
                else:
                    print(f"Key '{k}': {type(v)} (value: {str(v)[:100]})")
        elif isinstance(data, list):
            print("Data is a list of length:", len(data))
            if data:
                print("Sample element:", data[0])
except Exception as e:
    print('Error:', e)
