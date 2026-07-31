import urllib.request
import json

for sen in ['jr', 'pl', 'sr', 'lead']:
    url = f'http://localhost:8000/api/vagas?senioridade={sen}'
    req = urllib.request.urlopen(url)
    data = json.loads(req.read().decode('utf-8'))
    jobs = data.get('jobs', [])
    print(f"\n=== SENIORIDADE: {sen.upper()} ({len(jobs)} vagas) ===")
    for j in jobs[:5]:
        print(f"  - [{j.get('level')}] {j.get('title')} ({j.get('company')})")
