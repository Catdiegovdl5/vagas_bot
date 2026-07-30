from bot import normalize_str, global_title_blacklist, blacklist

def debug_is_job_relevant(job, keyword, settings):
    title_norm = normalize_str(job.get('title', ''))
    reqs_norm = normalize_str(job.get('requirements', ''))
    full_text = title_norm + " " + reqs_norm
    
    kw_norm = normalize_str(keyword)
    user_level = normalize_str(settings.get('level', 'Todos'))
    user_location = normalize_str(settings.get('location', 'Todos'))
    user_contract = normalize_str(settings.get('contract', 'Todos'))
    
    print("--- Debugging is_job_relevant ---")
    print(f"Title Norm: '{title_norm}'")
    print(f"Reqs Norm: '{reqs_norm}'")
    print(f"Kw Norm: '{kw_norm}'")
    print(f"User Level: '{user_level}'")
    print(f"User Location: '{user_location}'")
    print(f"User Contract: '{user_contract}'")
    
    if 'banco de talentos' in title_norm or 'talent pool' in title_norm:
        print("Rejected: banco de talentos")
        return False
        
    # Filtro de Localização Estrito
    job_loc = normalize_str(job.get('location', ''))
    has_remote_kw = any(r in full_text or r in job_loc for r in ['remoto', 'home office', 'remote', 'teletrabalho', 'anywhere', 'work from home'])
    has_fake_remote = any(f in full_text for f in ['não é remoto', 'nao e remoto', 'sem home office', 'vaga presencial', '100% presencial', 'nao tem home office', 'modelo presencial', 'not remote'])
    is_remote_term = has_remote_kw and not has_fake_remote
    
    if 'remoto' in user_location:
        if not is_remote_term:
            print("Rejected: remote check")
            return False
            
    # Location cambe etc checks...
    # Level checks:
    junior_terms = ['junior', 'jr', 'estagio', 'estagiario', 'trainee', 'aprendiz', 'assistente', 'auxiliar']
    senior_terms = ['senior', 'sr', 'especialista', 'coordenador', 'gerente', 'diretor', 'tech lead', 'head', 'lead', 'executivo', 'executive', 'architect', 'arquiteto', 'vp', 'manager', 'gestor']
    pleno_terms = ['pleno', 'pl']
    strict_senior_text = ['senior', 'sênior', 'pleno', 'diretor', 'gerente', 'coordenador', 'especialista']
    
    if user_level == 'junior':
        pass
    elif user_level == 'pleno':
        pass
    elif user_level == 'senior':
        print("Running senior checks...")
        import re
        if any(re.search(rf'\b{w}\b', title_norm) for w in junior_terms + pleno_terms):
            print("Rejected senior check 1 (junior/pleno term in title)")
            return False
        if any(re.search(rf'\b{w}\b', full_text) for w in ['junior', 'jr', 'estagio', 'estagiario', 'pleno']):
            print("Rejected senior check 2 (junior/pleno term in full_text)")
            return False

    import re
    # 1. Global Title Blacklist check (excluding terms in user search keyword)
    active_global_blacklist = [term for term in global_title_blacklist if term not in kw_norm]
    for term in active_global_blacklist:
        if re.search(rf'\b{re.escape(term)}\b', title_norm):
            print(f"Rejected: Global blacklist term '{term}'")
            return False
        
    # 2. Local Niche-specific Blacklist check
    if kw_norm in blacklist:
        for w in blacklist[kw_norm]:
            if re.search(rf'\b{re.escape(w)}\b', title_norm):
                print(f"Rejected: Local blacklist term '{w}'")
                return False

    if kw_norm in title_norm:
        print("Accepted: kw_norm in title_norm")
        return True
        
    def has_any(words):
        for w in words:
            if w.endswith('*'):
                pattern = rf'\b{re.escape(w[:-1])}\w*'
                if re.search(pattern, title_norm):
                    print(f"has_any match wildcard: {w} -> {pattern} matches")
                    return True
            else:
                pattern = rf'\b{re.escape(w)}\b'
                if re.search(pattern, title_norm):
                    print(f"has_any match exact: {w} -> {pattern} matches")
                    return True
        return False

    rules = {
        "especialista em ia generativa": [
            [
                "chatgpt", "gpt", "claude", "gemini", "llm", "genai", "generativa", "deepseek", "anthropic", "copilot", "ia", "ai", "artificial", "prompt"
            ], 
            [
                "imagem", "video", "audiovisual", "criacao", "design", "arte", "conteudo", "multimodal", "avatar", "animacao", "motion",
                "ilustracao", "3d", "render", "modelagem", "catalogo", "fotorrealista", "voz", "locutor", "voice", "audio", "narracao",
                "texto", "copy", "redacao", "marketing", "mkt", "redator", "writer", "copywriter", "social media", "midia", "media",
                "trafego", "ads", "anuncios", "performance", "generativa", "synthetic", "solucoes", "videomaker", "filmmaker", "creator", "criador", "influencer"
            ]
        ],
    }
    
    if kw_norm in rules:
        groups = rules[kw_norm]
        res = all(has_any(group) for group in groups)
        print(f"Rule match result: {res}")
        return res
        
    kw_words = [w for w in re.split(r'\W+', kw_norm) if len(w) > 3]
    if kw_words:
        res = any(w in title_norm for w in kw_words)
        print(f"Fallback match result: {res}")
        return res
    return True

job1 = {
    "title": "Copywriter ChatGPT",
    "requirements": "Criação de textos usando inteligência artificial."
}
test_settings = {
    "level": "Todos",
    "location": "Brasil (Remoto)",
    "contract": "Todos",
    "education": "Todos",
    "platforms": {},
    "ai_filter": False
}
debug_is_job_relevant(job1, "Especialista em IA Generativa", test_settings)

job2 = {
    "platform": "InfoJobs",
    "title": "Python Developer",
    "company": "Test Company",
    "budget": "A Combinar",
    "link": "https://example.com/job/test-1",
    "job_type": "CLT",
    "profession": "Python",
    "level": "Sênior",
    "requirements": "Procura-se desenvolvedor Python Sênior experiente com conhecimentos de Django e APIs REST.",
    "location": "Remoto"
}
settings_senior = {
    "level": "Sênior",
    "location": "Brasil (Remoto)",
    "contract": "Todos",
    "education": "Todos",
    "platforms": {},
    "ai_filter": False
}
debug_is_job_relevant(job2, "Python", settings_senior)
