import sys
sys.stdout.reconfigure(encoding='utf-8')
import requests

url = 'https://api.coodesh.com/v2/jobs?search=Python&pageSize=30'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Referer': 'https://coodesh.com/',
    'Origin': 'https://coodesh.com'
}

try:
    r = requests.get(url, headers=headers, timeout=15)
    print('Status:', r.status_code)
    print('Content-Type:', r.headers.get('Content-Type'))
    if r.status_code == 200:
        data = r.json()
        # It might be a list or a dict
        if isinstance(data, dict):
            print('Data keys:', data.keys())
            # Let's print some properties of data
            for k, v in data.items():
                if isinstance(v, list):
                    print(f"Key '{k}' is list of length {len(v)}")
                    if v:
                        print("  Sample item:", v[0])
                else:
                    print(f"Key '{k}': {type(v)} (value snippet: {str(v)[:100]})")
        elif isinstance(data, list):
            print('Data list length:', len(data))
            if data:
                print('Sample job:', data[0])
    else:
        print('Response Text:', r.text[:500])
except Exception as e:
    print('Error:', e)
