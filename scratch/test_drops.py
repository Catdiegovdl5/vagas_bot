import asyncio
from scrapers import workana
from bot import is_job_relevant, normalize_str

async def test():
    jobs = workana.scrape('Especialista em IA', 'Todos', 10)
    print(f'Workana encontrou: {len(jobs)} vagas brutas')
    
    unique_jobs = {}
    for job in jobs:
        link = job.get('link', '')
        if link not in unique_jobs:
            unique_jobs[link] = job
            
    print(f'Vagas unicas brutas: {len(unique_jobs)}')
    
    settings = {'level': 'Todos', 'location': 'Todos', 'contract': 'Todos'}
    relevant = []
    for job in unique_jobs.values():
        if is_job_relevant(job, 'Especialista em IA', settings):
            relevant.append(job)
            
    print(f'Vagas relevantes (is_job_relevant): {len(relevant)}')
    
    print('Filtro supremo local:')
    unique_supreme = {}
    for job in relevant:
        comp_norm = normalize_str(job.get('company', ''))
        link_norm = job.get('link', '')
        k = link_norm if link_norm else f"{normalize_str(job.get('title', ''))}|{comp_norm}"
        if k not in unique_supreme:
            unique_supreme[k] = job
    print(f'Vagas aps supreme deduplication: {len(unique_supreme)}')
    
    vagas_br = []
    for job in unique_supreme.values():
        plat_lower = job.get('platform', '').lower()
        is_freela_plat = any(p in plat_lower for p in ['workana', '99freelas', 'freelancer'])
        
        # Passa direto se for freelance
        if is_freela_plat:
            vagas_br.append(job)
            
    print(f'Vagas aps escudo: {len(vagas_br)}')

asyncio.run(test())
