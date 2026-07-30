import asyncio
from bot import get_user_settings, is_job_relevant, _do_hunt

# Define dummy job data to test the strict filter
dummy_jobs = [
    {
        "title": "Suporte Técnico Nível 1 - Londrina",
        "company": "Tech Corp",
        "location": "Londrina - PR",
        "requirements": "Precisa ter conhecimento em redes. Não exige experiência.",
        "link": "http://example.com/1",
        "platform": "infojobs"
    },
    {
        "title": "Analista de Suporte Júnior - Remoto",
        "company": "Cloud Inc",
        "location": "Trabalho Remoto",
        "requirements": "Conhecimento em Linux.",
        "link": "http://example.com/2",
        "platform": "remotar"
    },
    {
        "title": "Assistente Administrativo - Presencial",
        "company": "Local Ltda",
        "location": "Apucarana",
        "requirements": "Organização e pacote Office.",
        "link": "http://example.com/3",
        "platform": "catho"
    }
]

def debug_filter(job, keyword, settings):
    from bot import normalize_str, match_exact_word
    
    title_norm = normalize_str(job.get('title', ''))
    reqs_norm = normalize_str(job.get('requirements', ''))
    full_text = f"{title_norm} {reqs_norm}"
    kw_norm = normalize_str(keyword)
    user_location = normalize_str(settings.get('location', 'Todos'))
    job_loc = normalize_str(job.get('location', ''))
    job_platform = job.get('platform', '').lower()
    user_level = normalize_str(settings.get('level', 'Todos'))
    
    print(f"[{job['title']}] kw_norm='{kw_norm}', title_norm='{title_norm}'")
    is_exact_kw = kw_norm in title_norm
    print(f"is_exact_kw: {is_exact_kw}")
    
    valid_cities = ['londrina', 'cambe', 'ibipora', 'jataizinho', 'rolandia', 'arapongas', 'maringa', 'apucarana', 'cornelio', 'parana', ' pr ', '- pr', '-pr']
    is_local = any(city in job_loc for city in valid_cities) or (not job_loc and any(city in full_text for city in valid_cities))
    print(f"is_local: {is_local}")
    
    if is_freelance_platform := (job_platform in ['workana', '99freelas', 'freelancer']):
        pass
    
    print(f"Checking level: {user_level}")
    
    junior_terms = ['junior', 'jr', 'estagio', 'estagiario', 'trainee', 'assistente', 'auxiliar']
    is_junior = any(match_exact_word(title_norm, w) for w in junior_terms)
    print(f"is_junior: {is_junior}")
    
    return "done"

def test_filters():
    settings_londrina = {
        "location": "Londrina/PR",
        "level": "iniciantes tudo",
        "contract": "Todos",
        "platforms": {"infojobs": True, "catho": True, "remotar": True}
    }
    
    settings_remoto = {
        "location": "Brasil (Remoto)",
        "level": "iniciantes tudo",
        "contract": "Todos",
        "platforms": {"infojobs": True, "catho": True, "remotar": True}
    }
    
    print("--- Testando filtro LONDRINA ---")
    for job in dummy_jobs:
        # Pass a keyword that matches one of the jobs to see is_exact_kw in action
        res = is_job_relevant(job, "Suporte Técnico", settings_londrina)
        print(f"Vaga: {job['title']} -> Passou: {res}")
        
    print("\n--- Testando filtro REMOTO ---")
    for job in dummy_jobs:
        res = is_job_relevant(job, "Analista", settings_remoto)
        print(f"Vaga: {job['title']} -> Passou: {res}")

if __name__ == "__main__":
    test_filters()

