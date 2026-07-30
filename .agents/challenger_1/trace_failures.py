import sys
import os

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from bot import is_job_relevant, normalize_str, match_exact_word, global_title_blacklist, CO_OCCURRENCE_RULES, check_co_occurrence

settings = {
    "level": "iniciantes tudo",
    "location": "Brasil (Remoto)",
    "contract": "Todos",
    "education": "Todos",
    "platforms": {},
    "ai_filter": False
}

def debug_job(job, keyword, name):
    print(f"\n=== DEBUGGING: {name} ===")
    clean_kw = keyword
    title_norm = normalize_str(job.get('title', ''))
    reqs_norm = normalize_str(job.get('requirements', ''))
    full_text = title_norm + " " + reqs_norm
    kw_norm = normalize_str(clean_kw)
    user_level = normalize_str(settings.get('level', 'Todos'))

    aprendiz_terms = ['aprendiz', 'jovem aprendiz', 'menor aprendiz']
    is_aprendiz = any(match_exact_word(full_text, w) for w in aprendiz_terms)

    target_exp_terms = [
        "voluntario", "voluntariado", "ong", "projeto social",
        "open source", "codigo aberto",
        "sem experiencia", "nao exige experiencia", "primeiro emprego", "estagio inicial"
    ]
    has_target_exp = any(term in full_text for term in target_exp_terms)
    matching_target_terms = [term for term in target_exp_terms if term in full_text]

    higher_terms = ["junior", "jr", "pleno", "pl", "senior", "sr"]
    has_higher_terms = any(match_exact_word(full_text, w) for w in higher_terms)
    matching_higher_terms = [w for w in higher_terms if match_exact_word(full_text, w)]

    is_ganhar_exp = has_target_exp and not has_higher_terms

    print(f"full_text: '{full_text}'")
    print(f"is_aprendiz: {is_aprendiz}")
    print(f"has_target_exp: {has_target_exp} (matched: {matching_target_terms})")
    print(f"has_higher_terms: {has_higher_terms} (matched: {matching_higher_terms})")
    print(f"is_ganhar_exp: {is_ganhar_exp}")
    print(f"Passed level filter (is_aprendiz or is_ganhar_exp): {is_aprendiz or is_ganhar_exp}")

    active_global_blacklist = [term for term in global_title_blacklist if term not in kw_norm and not (user_level in ("ganhar experiencia", "iniciantes tudo", "iniciantes stuff") and term in ("voluntario", "voluntary"))]
    blacklisted_in_title = [term for term in active_global_blacklist if match_exact_word(title_norm, term)]
    print(f"Blacklisted in title: {blacklisted_in_title}")

    co_occ = check_co_occurrence(full_text, kw_norm, job=job)
    print(f"check_co_occurrence(kw='{kw_norm}'): {co_occ}")

    final_res = is_job_relevant(job, keyword, settings)
    print(f"FINAL RESULT: {final_res}")

debug_job({
    "title": "Desenvolvedor Open Source",
    "requirements": "Projeto de código aberto sem experiência necessária.",
    "platform": "github_vagas",
    "location": "Remoto"
}, "Dev", "TC02 - Standard Volunteer / Open Source")

debug_job({
    "title": "Desenvolvedor Backend Python",
    "requirements": "Desenvolvimento com Python, FastAPI e MongoDB.",
    "platform": "linkedin",
    "location": "Remoto"
}, "Python", "TC04 - MongoDB Substring")

debug_job({
    "title": "Aprendiz Pleno de TI",
    "requirements": "Programa de jovem aprendiz nível pleno.",
    "platform": "linkedin",
    "location": "Remoto"
}, "TI", "TC07 - Aprendiz Pleno")

debug_job({
    "title": "Desenvolvedor Voluntário SQL",
    "requirements": "Projeto social sem experiência, manutenção de consultas em PL/SQL.",
    "platform": "linkedin",
    "location": "Remoto"
}, "SQL", "TC10 - PL/SQL")

debug_job({
    "title": "DESENVOLVEDOR VOLUNTÁRIO",
    "requirements": "PROJETO DE CÓDIGO ABERTO PARA INICIANTES",
    "platform": "linkedin",
    "location": "REMOTO"
}, "Dev", "TC12 - Uppercase / Accents")
