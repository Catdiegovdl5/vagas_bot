import pytest
from bot import is_job_relevant, DEFAULT_SETTINGS, check_ia_validity

def test_verb_ia_vs_acronym_ia():
    keyword = "Especialista em IA"
    settings = DEFAULT_SETTINGS.copy()
    settings["location"] = "Todos"
    settings["level"] = "Todos"
    settings["contract"] = "Todos"

    # --- VERB CASES (Should return False because "ia" is a verb and there is no other IA keyword) ---
    # Case A: "ia" followed by infinitive verb ending in 'r'
    job_verb_infinitive_r = {
        "title": "Especialista que ia gerenciar a equipe",
        "requirements": "Profissional que ia planejar e executar a integração das APIs.",
        "location": "remoto",
        "platform": "linkedin"
    }
    assert not is_job_relevant(job_verb_infinitive_r, keyword, settings), "Failed: Verb 'ia' followed by infinitive ending in 'r' should be rejected"

    # Case B: "ia" followed by specific infinitive verbs (e.g. fazer, ser, ter)
    job_verb_specific = {
        "title": "Especialista que ia fazer o deploy",
        "requirements": "Procuramos quem ia ser o responsável pela infraestrutura.",
        "location": "remoto",
        "platform": "linkedin"
    }
    assert not is_job_relevant(job_verb_specific, keyword, settings), "Failed: Verb 'ia' followed by specific infinitive verb should be rejected"

    # Case C: "ia" preceded by verb-related words (que, se, ele, ela, etc.)
    job_verb_preceding = {
        "title": "Especialista que ia apoiar",
        "requirements": "Disse que se ia aventurar na área.",
        "location": "remoto",
        "platform": "linkedin"
    }
    assert not is_job_relevant(job_verb_preceding, keyword, settings), "Failed: Verb 'ia' preceded by verb-related word should be rejected"

    # --- ACRONYM CASES (Should return True) ---
    # Case D: Uppercase "IA"
    job_acronym_upper = {
        "title": "Especialista de IA",
        "requirements": "Experiência prática em modelos de linguagem grande.",
        "location": "remoto",
        "platform": "linkedin"
    }
    assert is_job_relevant(job_acronym_upper, keyword, settings), "Failed: Uppercase IA acronym should be approved"

    # Case E: "I.A." with dots
    job_acronym_dots = {
        "title": "Especialista de I.A.",
        "requirements": "Trabalhar com redes neurais artificiais.",
        "location": "remoto",
        "platform": "linkedin"
    }
    assert is_job_relevant(job_acronym_dots, keyword, settings), "Failed: Dotted I.A. acronym should be approved"

    # Case F: CamelCase/Lowercase "Ia" or "ia" in non-verb context
    job_acronym_non_verb = {
        "title": "Consultor com foco em Ia",
        "requirements": "Ter atuado com modelos de machine learning e processamento de linguagem de ia.",
        "location": "remoto",
        "platform": "linkedin"
    }
    assert is_job_relevant(job_acronym_non_verb, keyword, settings), "Failed: 'Ia' / 'ia' in non-verb context should be approved"

    # --- MIXED CASES (Should return True because a valid IA acronym is present) ---
    # Case G: Verb "ia" and Acronym "IA" in the same description
    job_mixed = {
        "title": "Especialista que ia programar soluções de IA",
        "requirements": "O candidato ideal ia atuar na implementação de modelos avançados de IA Generativa.",
        "location": "remoto",
        "platform": "linkedin"
    }
    assert is_job_relevant(job_mixed, keyword, settings), "Failed: Mixed case containing valid IA acronym should be approved"


def test_blacklist_filtering():
    keyword = "Especialista em IA"
    settings = DEFAULT_SETTINGS.copy()
    settings["location"] = "Todos"
    settings["level"] = "Todos"
    settings["contract"] = "Todos"

    # Niche commercial_sales: "vendas", "vendedor", etc.
    job_sales = {
        "title": "Especialista de Vendas de IA",
        "requirements": "Profissional focado em vender soluções de IA.",
        "location": "remoto",
        "platform": "linkedin"
    }
    assert not is_job_relevant(job_sales, keyword, settings), "Failed: Blacklisted sales title should be rejected"

    # Niche marketing_ads: "marketing", "ads", etc.
    job_mkt = {
        "title": "Especialista em Tráfego Pago e Marketing de IA",
        "requirements": "Gerenciar anúncios nas redes sociais.",
        "location": "remoto",
        "platform": "linkedin"
    }
    assert not is_job_relevant(job_mkt, keyword, settings), "Failed: Blacklisted marketing title should be rejected"

    # Niche creative_video: "video", "editor", "vsl", etc.
    job_video = {
        "title": "Especialista / Editor de Vídeo e VSL com Inteligência Artificial",
        "requirements": "Cortar e renderizar vídeos integrados com IA.",
        "location": "remoto",
        "platform": "linkedin"
    }
    assert not is_job_relevant(job_video, keyword, settings), "Failed: Blacklisted video editor title should be rejected"

    # Niche customer_service: "atendimento", "suporte", etc.
    job_support = {
        "title": "Especialista de Suporte de IA",
        "requirements": "Prestar atendimento e ajudar usuários com a plataforma de IA.",
        "location": "remoto",
        "platform": "linkedin"
    }
    assert not is_job_relevant(job_support, keyword, settings), "Failed: Blacklisted support title should be rejected"


def test_location_and_contract_and_level_filtering():
    keyword = "Especialista em IA"
    
    # 1. Location filtering
    settings_remote = DEFAULT_SETTINGS.copy()
    settings_remote["location"] = "Brasil (Remoto)"
    settings_remote["level"] = "Todos"
    settings_remote["contract"] = "Todos"

    job_presential = {
        "title": "Especialista em IA",
        "requirements": "Vaga 100% presencial em São Paulo.",
        "location": "São Paulo, SP",
        "platform": "linkedin"
    }
    assert not is_job_relevant(job_presential, keyword, settings_remote), "Failed: Presential job when remote is required should be rejected"

    # 2. Contract filtering
    settings_clt = DEFAULT_SETTINGS.copy()
    settings_clt["location"] = "Todos"
    settings_clt["level"] = "Todos"
    settings_clt["contract"] = "CLT"

    job_pj_only = {
        "title": "Especialista em IA (PJ)",
        "requirements": "Contratação estrita como Pessoa Jurídica (PJ).",
        "location": "remoto",
        "platform": "linkedin"
    }
    assert not is_job_relevant(job_pj_only, keyword, settings_clt), "Failed: PJ-only job when CLT is required should be rejected"

    # 3. Level filtering
    settings_junior = DEFAULT_SETTINGS.copy()
    settings_junior["location"] = "Todos"
    settings_junior["level"] = "Júnior"
    settings_junior["contract"] = "Todos"

    job_senior_title = {
        "title": "Sênior Especialista em IA",
        "requirements": "Atuar na liderança técnica da equipe.",
        "location": "remoto",
        "platform": "linkedin"
    }
    assert not is_job_relevant(job_senior_title, keyword, settings_junior), "Failed: Senior job when Junior is required should be rejected"
