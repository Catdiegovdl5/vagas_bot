"""
Empirical Regression Test Harness for Milestone 3
Target: is_job_relevant in bot.py
Objective: Verify 100% behavior preservation for existing seniority levels:
           ["Todos", "Júnior", "Pleno", "Sênior", "Jovem Aprendiz"]
           after the addition of "ganhar experiência".
"""

import sys
import os
import re
import unicodedata
import json

# Add root directory to sys.path
ROOT_DIR = r"C:\Users\99196\OneDrive\Documentos\vagas_bot"
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from bot import is_job_relevant, normalize_str, match_exact_word, check_co_occurrence, global_title_blacklist, blacklist

def is_job_relevant_legacy(job, keyword, settings):
    """
    Reference implementation of is_job_relevant prior to adding 'ganhar experiencia'.
    """
    title_norm = normalize_str(job.get('title', ''))
    reqs_norm = normalize_str(job.get('requirements', ''))
    full_text = title_norm + " " + reqs_norm
    
    kw_norm = normalize_str(keyword)
    user_level = normalize_str(settings.get('level', 'Todos'))
    user_location = normalize_str(settings.get('location', 'Todos'))
    user_contract = normalize_str(settings.get('contract', 'Todos'))
    
    if 'banco de talentos' in title_norm or 'talent pool' in title_norm:
        return False
        
    job_platform = normalize_str(job.get('platform', ''))
    is_freelance_platform = any(p in job_platform for p in ['workana', '99freelas', 'freelancer', 'workana.com'])
    is_remote_default_platform = any(p in job_platform for p in ['remotar', 'coodesh', 'programathor', 'geekhunter'])
    
    job_loc = normalize_str(job.get('location', ''))
    
    is_remote_term = any(r in full_text or r in job_loc for r in ['remoto', 'remota', 'home office', 'remote', 'teletrabalho', 'anywhere', 'work from home'])
    is_presential_term = any(p in full_text or p in job_loc for p in ['presencial', 'hibrido', 'hybrid', 'on-site', 'onsite', 'modelo hibrido'])
 
    if not is_freelance_platform and len(reqs_norm) < 30 and job_platform not in ['linkedin', 'indeed']:
        return False
        
    if 'remoto' in user_location:
        if is_freelance_platform or is_remote_default_platform:
            pass
        elif is_remote_term:
            pass
        elif is_presential_term:
            return False
        elif len(job_loc) > 3 and 'brasil' not in job_loc and 'brazil' not in job_loc:
            return False
            
    elif 'londrina' in user_location or 'assai' in user_location:
        valid_cities = ['londrina', 'cambe', 'ibipora', 'jataizinho', 'rolandia', 'arapongas', 'maringa', 'apucarana', 'cornelio', 'parana', ' pr ', '- pr', '-pr']
        is_local = any(city in job_loc for city in valid_cities) or (not job_loc and any(city in full_text for city in valid_cities))
        if not (is_local or is_remote_term):
            return False
 
    if user_contract == 'clt':
        if (match_exact_word(full_text, 'pj') or 'freelancer' in full_text or 'pessoa juridica' in full_text) and 'clt' not in full_text:
            return False
    elif user_contract == 'pj':
        if ('clt' in full_text or 'carteira assinada' in full_text) and not match_exact_word(full_text, 'pj'):
            return False
 
    junior_terms = ['junior', 'jr', 'estagio', 'estagiario', 'trainee', 'assistente', 'auxiliar']
    senior_terms = ['senior', 'sr', 'especialista', 'coordenador', 'gerente', 'diretor', 'tech lead', 'head', 'lead', 'executivo', 'executive', 'architect', 'arquiteto', 'vp', 'manager', 'gestor']
    pleno_terms = ['pleno', 'pl']
    aprendiz_terms = ['aprendiz', 'jovem aprendiz', 'menor aprendiz']
    
    active_junior_terms = [t for t in junior_terms if not match_exact_word(kw_norm, t)]
    active_senior_terms = [t for t in senior_terms if not match_exact_word(kw_norm, t)]
    active_pleno_terms = [t for t in pleno_terms if not match_exact_word(kw_norm, t)]
    
    if user_level == 'junior':
        if any(match_exact_word(title_norm, w) for w in active_senior_terms + active_pleno_terms):
            return False
    elif user_level == 'pleno':
        if any(match_exact_word(title_norm, w) for w in active_junior_terms + active_senior_terms):
            return False
    elif user_level == 'senior':
        if any(match_exact_word(title_norm, w) for w in active_junior_terms + active_pleno_terms):
            return False
    elif user_level == 'jovem aprendiz':
        if not any(match_exact_word(full_text, w) for w in aprendiz_terms):
            return False

    if user_level in ['junior', 'pleno', 'senior']:
        title_has_level = any(match_exact_word(title_norm, w) for w in active_junior_terms + active_pleno_terms + active_senior_terms)
        if not title_has_level:
            regex_pattern = r'\b(nivel|perfil|profissional|cargo|vaga|experiencia como|experiencia)\s+(junior|jr|pleno|pl|senior|sr|especialista)\b'
            matches = re.findall(regex_pattern, reqs_norm)
            if matches:
                found_levels = [m[1] for m in matches]
                has_junior = any(t in found_levels for t in active_junior_terms)
                has_pleno = any(t in found_levels for t in active_pleno_terms)
                has_senior = any(t in found_levels for t in active_senior_terms)
                
                if user_level == 'junior' and (has_senior or has_pleno) and not has_junior:
                    return False
                elif user_level == 'pleno' and (has_junior or has_senior) and not has_pleno:
                    return False
                elif user_level == 'senior' and (has_junior or has_pleno) and not has_senior:
                    return False

    # 1. Global Title Blacklist check (legacy logic without ganar experiencia exception)
    active_global_blacklist = [term for term in global_title_blacklist if term not in kw_norm]
    if any(match_exact_word(title_norm, term) for term in active_global_blacklist):
        return False
        
    # 2. Local Niche-specific Blacklist check
    if kw_norm in blacklist:
        if any(match_exact_word(title_norm, w) for w in blacklist[kw_norm]):
            return False
 
    return check_co_occurrence(full_text, kw_norm, job=job)


def generate_test_jobs():
    """Generates a rich suite of synthetic jobs across various titles, requirements, platforms, and locations."""
    return [
        # Junior developer jobs
        {
            "id": "JOB_001",
            "title": "Desenvolvedor Python Júnior",
            "requirements": "Buscamos desenvolvedor python júnior com conhecimentos em FastAPI, Git e SQL. Trabalho 100% remoto.",
            "platform": "linkedin",
            "location": "Brasil (Remoto)"
        },
        {
            "id": "JOB_002",
            "title": "Desenvolvedor Python Jr",
            "requirements": "Vaga para Desenvolvedor Python Jr. Requisitos: Python 3, Django básico, PostgreSQL.",
            "platform": "gupy",
            "location": "Remoto"
        },
        # Pleno developer jobs
        {
            "id": "JOB_003",
            "title": "Desenvolvedor Python Pleno",
            "requirements": "Buscamos Desenvolvedor Python Pleno com 3 anos de experiência em Django, Celery e Docker.",
            "platform": "linkedin",
            "location": "Brasil (Remoto)"
        },
        {
            "id": "JOB_004",
            "title": "Analista de Dados Pleno",
            "requirements": "Analista de dados pleno para atuar com SQL, Power BI, Python e modelagem de dados.",
            "platform": "catho",
            "location": "Remoto"
        },
        # Senior developer jobs
        {
            "id": "JOB_005",
            "title": "Desenvolvedor Python Sênior",
            "requirements": "Engenheiro de Software Sênior / Dev Python Sr com forte experiência em arquitetura de microsserviços.",
            "platform": "linkedin",
            "location": "Brasil (Remoto)"
        },
        {
            "id": "JOB_006",
            "title": "Tech Lead Python",
            "requirements": "Liderança técnica para equipe Python. Requer experiência sênior e gestão de projetos.",
            "platform": "programathor",
            "location": "Brasil (Remoto)"
        },
        # Jovem Aprendiz jobs
        {
            "id": "JOB_007",
            "title": "Jovem Aprendiz Administrativo",
            "requirements": "Vaga de Jovem Aprendiz para apoiar rotinas de escritório e atendimento ao público.",
            "platform": "gupy",
            "location": "Londrina/PR"
        },
        {
            "id": "JOB_008",
            "title": "Menor Aprendiz TI",
            "requirements": "Programa Menor Aprendiz na área de tecnologia. Não exige experiência prévia.",
            "platform": "infojobs",
            "location": "Remoto"
        },
        # Volunteer / Open source / No experience jobs (the target for "ganhar experiência")
        {
            "id": "JOB_009",
            "title": "Desenvolvedor Python Voluntário ONG",
            "requirements": "Projeto social de código aberto em busca de desenvolvedor voluntário para criar soluções com Python.",
            "platform": "linkedin",
            "location": "Brasil (Remoto)"
        },
        {
            "id": "JOB_010",
            "title": "Assistente de Dados sem experiência",
            "requirements": "Oportunidade para primeiro emprego na área de dados. Não exige experiência prévia.",
            "platform": "gupy",
            "location": "Remoto"
        },
        # Blacklisted title jobs (e.g. Professor, Médico, Faxineiro)
        {
            "id": "JOB_011",
            "title": "Professor de Python",
            "requirements": "Lecionar aulas de linguagem Python para turmas de graduação e cursos livres.",
            "platform": "indeed",
            "location": "Remoto"
        },
        {
            "id": "JOB_012",
            "title": "Advogado Trabalhista",
            "requirements": "Atuação jurídica em contencioso e consultivo trabalhista.",
            "platform": "catho",
            "location": "Londrina/PR"
        },
        # Niche blacklist tests (e.g. Gestor de Tráfego with Logística term)
        {
            "id": "JOB_013",
            "title": "Controlador de Tráfego Aéreo",
            "requirements": "Gestão e controle de tráfego de frotas e veículos no pátio logístico.",
            "platform": "catho",
            "location": "Presencial"
        },
        # AI jobs
        {
            "id": "JOB_014",
            "title": "Especialista em IA",
            "requirements": "Consultor especialista em IA para implementação de agentes inteligentes e LLMs OpenAI.",
            "platform": "linkedin",
            "location": "Brasil (Remoto)"
        },
        # Freelance platform jobs
        {
            "id": "JOB_015",
            "title": "Desenvolvedor Python para Web Scraping",
            "requirements": "Preciso de um freela para criar script de scraping em Python com Playwright.",
            "platform": "workana",
            "location": "Remoto"
        },
        # Talent pool / Banco de talentos
        {
            "id": "JOB_016",
            "title": "Banco de Talentos - Desenvolvedor Python",
            "requirements": "Cadastre seu currículo em nosso banco de talentos para futuras oportunidades.",
            "platform": "gupy",
            "location": "Remoto"
        },
        # Short description edge cases
        {
            "id": "JOB_017",
            "title": "Desenvolvedor Python",
            "requirements": "Vaga curta de python.",
            "platform": "linkedin",
            "location": "Remoto"
        },
        # Ambiguous level in requirements
        {
            "id": "JOB_018",
            "title": "Desenvolvedor Python",
            "requirements": "Buscamos profissional nível sênior com experiência comprovada de 5 anos em Django.",
            "platform": "gupy",
            "location": "Remoto"
        },
        {
            "id": "JOB_019",
            "title": "Desenvolvedor Python",
            "requirements": "Buscamos perfil júnior para apoio ao time de desenvolvimento backend.",
            "platform": "gupy",
            "location": "Remoto"
        },
        {
            "id": "JOB_020",
            "title": "Desenvolvedor Python",
            "requirements": "Nível pleno exigido. Conhecimentos avançados de Python e SQL.",
            "platform": "gupy",
            "location": "Remoto"
        }
    ]


def run_regression_harness():
    existing_levels = ["Todos", "Júnior", "Pleno", "Sênior", "Jovem Aprendiz"]
    keywords = ["Desenvolvedor Python", "Analista de Dados", "Especialista em IA", "Gestor de Tráfego", "Jovem Aprendiz"]
    
    test_jobs = generate_test_jobs()
    
    total_tests = 0
    passed_tests = 0
    failed_tests = []
    
    print("======================================================================")
    print("STARTING EMPIRICAL REGRESSION TEST FOR EXISTING SENIORITY LEVELS")
    print("======================================================================")
    
    for level in existing_levels:
        for kw in keywords:
            for job in test_jobs:
                total_tests += 1
                settings = {"level": level, "location": "Brasil (Remoto)", "contract": "Todos"}
                
                res_current = is_job_relevant(job, kw, settings)
                res_legacy = is_job_relevant_legacy(job, kw, settings)
                
                if res_current == res_legacy:
                    passed_tests += 1
                else:
                    failed_tests.append({
                        "job_id": job["id"],
                        "job_title": job["title"],
                        "keyword": kw,
                        "level": level,
                        "expected_legacy": res_legacy,
                        "actual_current": res_current
                    })
                    
    print(f"Total Test Executions: {total_tests}")
    print(f"Passed Executions:     {passed_tests}")
    print(f"Failed Executions:     {len(failed_tests)}")
    
    if len(failed_tests) == 0:
        print("\nSUCCESS: 100% Behavioral Preservation Confirmed!")
        print("Existing seniority levels ('Todos', 'Júnior', 'Pleno', 'Sênior', 'Jovem Aprendiz') suffer ZERO regression.")
    else:
        print("\nFAILURE: Regressions Detected!")
        for fail in failed_tests:
            print(f"  - Job {fail['job_id']} ('{fail['job_title']}'), KW: '{fail['keyword']}', Level: '{fail['level']}': Expected {fail['expected_legacy']}, Got {fail['actual_current']}")
            
    # Also verify "ganhar experiência" standalone test
    print("\n----------------------------------------------------------------------")
    print("TESTING NEW LEVEL: 'ganhar experiência'")
    print("----------------------------------------------------------------------")
    exp_test_results = []
    exp_settings = {"level": "ganhar experiência", "location": "Brasil (Remoto)", "contract": "Todos"}
    for job in test_jobs:
        res = is_job_relevant(job, "Desenvolvedor Python", exp_settings)
        exp_test_results.append((job["id"], job["title"], res))
        print(f"  [{job['id']}] {job['title'][:40]:<40} -> Relevant: {res}")
        
    summary = {
        "total_tests": total_tests,
        "passed_tests": passed_tests,
        "failed_tests": failed_tests,
        "existing_levels_tested": existing_levels,
        "regression_free": len(failed_tests) == 0,
        "ganhar_experiencia_sample": exp_test_results
    }
    
    report_file = os.path.join(os.path.dirname(__file__), "regression_results.json")
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
        
    print(f"\nDetailed JSON report written to: {report_file}")
    return len(failed_tests) == 0

if __name__ == "__main__":
    run_regression_harness()
