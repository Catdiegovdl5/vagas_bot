import sys
sys.stdout.reconfigure(encoding='utf-8')
import requests

url = 'https://api.coodesh.com/v2/jobs?search=Python&pageSize=5'
headers = {
    'User-Agent': 'Mozilla/5.0',
    'Accept': 'application/json',
    'referer': 'https://coodesh.com/',
    'x-csh-key': 'coodesh-experts',
    'x-language': 'pt'
}

try:
    r = requests.get(url, headers=headers, timeout=15)
    if r.status_code == 200:
        docs = r.json().get('docs', [])
        for idx, doc in enumerate(docs):
            print(f"\n=== Job #{idx+1} ===")
            print("Title:", doc.get('title'))
            print("Slug:", doc.get('slug'))
            company = doc.get('company')
            print("Company field type:", type(company))
            print("Company content:", company)
            # Check other fields we need: link, budget, requirements, type
            print("Home office:", doc.get('home_office'))
            print("Job Type:", doc.get('job_type'))
            print("Skills:", doc.get('skills'))
except Exception as e:
    print('Error:', e)
