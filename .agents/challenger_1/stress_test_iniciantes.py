import sys
import os
import re

# Guarantee root directory is in sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from bot import is_job_relevant, normalize_str, match_exact_word, global_title_blacklist

def level_filter_iniciantes_tudo(job):
    """
    Direct extraction of the level filter logic for 'iniciantes tudo' from bot.py
    """
    title_norm = normalize_str(job.get('title', ''))
    reqs_norm = normalize_str(job.get('requirements', ''))
    full_text = title_norm + " " + reqs_norm
    
    aprendiz_terms = ['aprendiz', 'jovem aprendiz', 'menor aprendiz']
    is_aprendiz = any(match_exact_word(full_text, w) for w in aprendiz_terms)
    
    target_exp_terms = [
        "voluntario", "voluntariado", "ong", "projeto social",
        "open source", "codigo aberto",
        "sem experiencia", "nao exige experiencia", "primeiro emprego", "estagio inicial"
    ]
    has_target_exp = any(term in full_text for term in target_exp_terms)
    higher_terms = ["junior", "jr", "pleno", "pl", "senior", "sr"]
    has_higher_terms = any(match_exact_word(full_text, w) for w in higher_terms)
    is_ganhar_exp = has_target_exp and not has_higher_terms
    
    return (is_aprendiz or is_ganhar_exp), {
        "is_aprendiz": is_aprendiz,
        "has_target_exp": has_target_exp,
        "matched_target_terms": [t for t in target_exp_terms if t in full_text],
        "has_higher_terms": has_higher_terms,
        "matched_higher_terms": [w for w in higher_terms if match_exact_word(full_text, w)],
        "is_ganhar_exp": is_ganhar_exp,
    }

def run_suite():
    print("=" * 85)
    print(" COMPREHENSIVE EMPIRICAL STRESS SUITE: 'iniciantes tudo' LOGIC")
    print("=" * 85)

    settings = {
        "level": "iniciantes tudo",
        "location": "Brasil (Remoto)",
        "contract": "Todos",
        "education": "Todos",
        "platforms": {},
        "ai_filter": False
    }

    test_matrix = [
        # --- Category 1: Standard Valid Beginner Jobs ---
        {
            "id": "SUB-01",
            "category": "Standard Valid",
            "title": "Jovem Aprendiz de TI",
            "reqs": "Vaga para jovem aprendiz atuar no setor de TI.",
            "keyword": "TI",
            "expect_level_pass": True,
            "expect_full_pass": True,
            "reason": "Standard Jovem Aprendiz job."
        },
        {
            "id": "SUB-02",
            "category": "Standard Valid",
            "title": "Desenvolvedor Voluntário",
            "reqs": "Desenvolvimento voluntário para ONG de tecnologia.",
            "keyword": "Desenvolvedor",
            "expect_level_pass": True,
            "expect_full_pass": True,
            "reason": "Standard volunteer job (Ganhar Experiência)."
        },
        {
            "id": "SUB-03",
            "category": "Standard Valid",
            "title": "Projeto Open Source",
            "reqs": "Contribuição em código aberto sem experiência prévia.",
            "keyword": "Open Source",
            "expect_level_pass": True,
            "expect_full_pass": True,
            "reason": "Open source project without required experience."
        },

        # --- Category 2: Conflicting Seniority Keywords ---
        {
            "id": "CONF-01",
            "category": "Conflicting Level",
            "title": "Aprendiz Pleno",
            "reqs": "Atuação como jovem aprendiz nível pleno.",
            "keyword": "Aprendiz",
            "expect_level_pass": False, # SHOULD BE REJECTED: Pleno conflicts with beginner!
            "expect_full_pass": False,
            "reason": "'Aprendiz Pleno' combines beginner term with mid-level 'Pleno'."
        },
        {
            "id": "CONF-02",
            "category": "Conflicting Level",
            "title": "Jovem Aprendiz Sênior",
            "reqs": "Jovem aprendiz para apoiar equipe sênior.",
            "keyword": "Jovem Aprendiz",
            "expect_level_pass": False, # SHOULD BE REJECTED: Senior conflicts with beginner!
            "expect_full_pass": False,
            "reason": "'Jovem Aprendiz Sênior' combines beginner term with 'Sênior'."
        },
        {
            "id": "CONF-03",
            "category": "Conflicting Level",
            "title": "Voluntário Sênior",
            "reqs": "Trabalho voluntário para profissional sênior.",
            "keyword": "Voluntário",
            "expect_level_pass": False,
            "expect_full_pass": False,
            "reason": "Volunteer job specifically asking for Senior profile."
        },
        {
            "id": "CONF-04",
            "category": "Conflicting Level",
            "title": "Open Source Sênior",
            "reqs": "Projeto open source buscando desenvolvedores sênior.",
            "keyword": "Open Source",
            "expect_level_pass": False,
            "expect_full_pass": False,
            "reason": "Open source project requiring Senior level."
        },
        {
            "id": "CONF-05",
            "category": "Conflicting Level",
            "title": "Dev Júnior 1 ano de experiência",
            "reqs": "Desenvolvedor júnior exigindo 1 ano de experiência.",
            "keyword": "Desenvolvedor",
            "expect_level_pass": False,
            "expect_full_pass": False,
            "reason": "Junior job requiring experience is NOT for zero-experience beginners."
        },

        # --- Category 3: Substring Collisions (e.g. 'ong' in 'MongoDB') ---
        {
            "id": "SUBSTR-01",
            "category": "Substring Bug ('ong')",
            "title": "Desenvolvedor Python",
            "reqs": "Desenvolvimento backend com Python e MongoDB.",
            "keyword": "Python",
            "expect_level_pass": False, # SHOULD BE REJECTED: Regular job with MongoDB, not a volunteer/ONG job!
            "expect_full_pass": False,
            "reason": "'MongoDB' contains 'ong', causing false positive match as ONG/Volunteer job."
        },
        {
            "id": "SUBSTR-02",
            "category": "Substring Bug ('ong')",
            "title": "Engenheiro de Software",
            "reqs": "Contratação para projeto de longo prazo.",
            "keyword": "Engenheiro",
            "expect_level_pass": False, # Regular job with 'longo', not ONG!
            "expect_full_pass": False,
            "reason": "'longo' contains 'ong', causing false positive match."
        },
        {
            "id": "SUBSTR-03",
            "category": "Substring Bug ('ong')",
            "title": "Analista de Sistemas",
            "reqs": "Strong skills in system architecture and APIs.",
            "keyword": "Analista",
            "expect_level_pass": False, # Regular job with 'strong', not ONG!
            "expect_full_pass": False,
            "reason": "'strong' contains 'ong', causing false positive match."
        },

        # --- Category 4: Word Boundary Seniority False Rejection (e.g. 'PL/SQL') ---
        {
            "id": "BOUNDARY-01",
            "category": "Word Boundary ('pl' in PL/SQL)",
            "title": "Desenvolvedor Voluntário",
            "reqs": "Projeto social sem experiência exigida. Atuação com PL/SQL.",
            "keyword": "Desenvolvedor",
            "expect_level_pass": True, # SHOULD PASS: Legitimate volunteer job mentioning database PL/SQL!
            "expect_full_pass": True,
            "reason": "'PL/SQL' matches 'pl' via regex word boundary, falsely marking job as Pleno."
        },
        {
            "id": "BOUNDARY-02",
            "category": "Word Boundary ('pl' in PL/SQL)",
            "title": "Projeto Open Source",
            "reqs": "Código aberto sem experiência. Manutenção de stored procedures em PL/SQL.",
            "keyword": "Open Source",
            "expect_level_pass": True, # SHOULD PASS: Legitimate open source job mentioning PL/SQL!
            "expect_full_pass": True,
            "reason": "'PL/SQL' causes false rejection as 'Pleno'."
        },

        # --- Category 5: Accents and Case Sensitivity ---
        {
            "id": "CASE-01",
            "category": "Case & Accents",
            "title": "JOVEM APRENDIZ DE TI",
            "reqs": "VAGA PARA JOVEM APRENDIZ EM TECNOLOGIA.",
            "keyword": "TI",
            "expect_level_pass": True,
            "expect_full_pass": True,
            "reason": "Uppercase text handling."
        },
        {
            "id": "CASE-02",
            "category": "Case & Accents",
            "title": "DESENVOLVEDOR VOLUNTÁRIO",
            "reqs": "PROJETO DE CÓDIGO ABERTO SEM EXPERIÊNCIA",
            "keyword": "Desenvolvedor",
            "expect_level_pass": True,
            "expect_full_pass": True,
            "reason": "Uppercase text with accents."
        }
    ]

    summary_records = []

    for t in test_matrix:
        job = {
            "title": t["title"],
            "requirements": t["reqs"],
            "platform": "linkedin",
            "location": "Remoto"
        }
        
        # Direct level filter evaluation
        level_pass, level_meta = level_filter_iniciantes_tudo(job)
        
        # Full function evaluation
        full_pass = is_job_relevant(job, t["keyword"], settings)

        level_status = "PASS" if (level_pass == t["expect_level_pass"]) else "FAIL"
        full_status = "PASS" if (full_pass == t["expect_full_pass"]) else "FAIL"

        record = {
            "id": t["id"],
            "category": t["category"],
            "title": t["title"],
            "keyword": t["keyword"],
            "expect_level": t["expect_level_pass"],
            "got_level": level_pass,
            "level_status": level_status,
            "expect_full": t["expect_full_pass"],
            "got_full": full_pass,
            "full_status": full_status,
            "meta": level_meta,
            "reason": t["reason"]
        }
        summary_records.append(record)

        print(f"\n[{record['id']}] {t['category']} — {t['title']}")
        print(f"     Reason: {t['reason']}")
        print(f"     [Level Filter] Expected: {t['expect_level_pass']} | Got: {level_pass} => {level_status}")
        if level_status == "FAIL":
            print(f"     >>> LEVEL FILTER DISCREPANCY! Meta: {level_meta}")
        print(f"     [Full Function] Expected: {t['expect_full_pass']} | Got: {full_pass} => {full_status}")
        if full_status == "FAIL":
            print(f"     >>> FULL FUNCTION DISCREPANCY!")

    print("\n" + "=" * 85)
    print(" SUMMARY TABLE OF FINDINGS")
    print("=" * 85)
    print(f"{'ID':<12} | {'Category':<25} | {'Level Exp/Got':<15} | {'Level Status':<12} | {'Full Exp/Got':<15} | {'Full Status':<12}")
    print("-" * 105)
    for r in summary_records:
        level_str = f"{r['expect_level']}/{r['got_level']}"
        full_str = f"{r['expect_full']}/{r['got_full']}"
        print(f"{r['id']:<12} | {r['category']:<25} | {level_str:<15} | {r['level_status']:<12} | {full_str:<15} | {r['full_status']:<12}")

    return summary_records

if __name__ == '__main__':
    run_suite()
