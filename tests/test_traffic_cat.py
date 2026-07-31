import urllib.request
import json

url = 'http://localhost:8000/api/vagas?categoria=gestor_trafego'
req = urllib.request.urlopen(url)
data = json.loads(req.read().decode('utf-8'))
jobs = data.get('jobs', [])

print(f"Total vagas encontradas em Gestor de Tráfego: {len(jobs)}")
for j in jobs[:10]:
    print(f"  - Vaga: {j.get('title')} ({j.get('company')})")
