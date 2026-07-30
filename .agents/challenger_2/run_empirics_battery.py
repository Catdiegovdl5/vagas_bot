import sys
import os
import copy
import json
import itertools

# Ensure project root is in sys.path
sys.path.insert(0, r"C:/Users/99196/OneDrive/Documentos/vagas_bot")

from bot import is_job_relevant, get_user_settings, normalize_str

def generate_test_dataset():
    """Generates 500+ synthetic job combinations to empirically challenge seniority filtering."""
    
    titles = [
        # Pure Apprentice
        "Jovem Aprendiz de TI",
        "Menor Aprendiz em Desenvolvimento",
        "Aprendiz de Suporte Técnico",
        "Jovem Aprendiz Administrativo",
        
        # Pure Experience Building
        "Desenvolvedor Python Voluntário",
        "Analista de Dados Sem Experiência",
        "Desenvolvedor Frontend - Projeto Social ONG",
        "Estágio Inicial Sem Experiência Prévia",
        "Programador Open Source Código Aberto",
        "Primeiro Emprego Tecnologia",
        
        # Combined Beginner (Aprendiz + Ganhar Exp)
        "Jovem Aprendiz Sem Experiência em TI",
        "Menor Aprendiz Voluntário ONG",
        
        # Junior
        "Desenvolvedor Junior Python",
        "Desenvolvedor Jr React",
        "Analista de Dados Junior",
        "Assistente de Marketing Junior",
        "Estagiário de TI",
        "Desenvolvedor Junior 1 ano experiência",
        
        # Pleno
        "Desenvolvedor Pleno Python",
        "Desenvolvedor Pl Python",
        "Analista de Dados Pleno",
        "Gestor de Tráfego Pleno",
        "Fullstack Developer Mid Level",
        
        # Senior
        "Desenvolvedor Senior Python",
        "Desenvolvedor Sr Backend",
        "Engenheiro de Dados Especialista",
        "Tech Lead Python",
        "Arquiteto de Software Senior",
        
        # Ambiguous / Edge Cases
        "Jovem Aprendiz Junior de TI",
        "Voluntário Senior de Projetos",
        "Desenvolvedor Junior Pleno",
        "Desenvolvedor Python (Sem Experiência) Junior",
        "Desenvolvedor Python", # Generic title
        "Analista de Dados",  # Generic title
        
        # Blacklisted titles
        "Professor de Python Jovem Aprendiz",
        "Advogado Voluntário",
        "Médico Junior"
    ]

    req_snippets = [
        "Conhecimentos básicos de programação. Vaga presencial.",
        "Desenvolvimento em Python, Django, FastAPI e SQL. Vaga 100% remota.",
        "Buscamos perfil junior para atuar em projetos de IA.",
        "Experiência sênior comprovada de pelo menos 5 anos com arquitetura.",
        "Perfil pleno com vivência em metodologias ágeis.",
        "Trabalho voluntário em código aberto para doar tempo e ganhar experiência.",
        "Não exige experiência prévia. Oportunidade para primeiro emprego.",
        "Você atuará em uma equipe com engenheiros sênior e plenos.",
        "Cargo sênior responsável pela liderança técnica do time."
    ]

    platforms = ["linkedin", "indeed", "gupy", "catho", "workana", "github_vagas"]
    keywords = ["desenvolvedor python", "analista de dados", "suporte tecnico n1"]

    jobs = []
    job_id = 1

    # Generate combinatorial combinations
    for t, r, p, kw in itertools.product(titles, req_snippets, platforms, keywords):
        # Filter combinations to keep size around 600
        if (job_id % 7) != 0 and len(jobs) >= 600:
            continue
        jobs.append({
            "id": f"JOB_{job_id:04d}",
            "job": {
                "title": t,
                "requirements": r,
                "platform": p,
                "location": "Remoto"
            },
            "keyword": kw
        })
        job_id += 1

    return jobs

def test_alias_normalization():
    print("\n--- TEST: ALIAS & CASE NORMALIZATION ---")
    base_settings = {
        "location": "Brasil (Remoto)",
        "contract": "Todos",
        "education": "Todos",
        "platforms": {},
        "ai_filter": False,
        "escudo_ptbr": True
    }
    
    test_job = {
        "title": "Desenvolvedor Python Voluntário",
        "requirements": "Projeto social sem fins lucrativos para ganhar experiência.",
        "platform": "linkedin",
        "location": "Remoto"
    }

    aliases = {
        "iniciantes tudo": ["iniciantes tudo", "Iniciantes Tudo", "INICIANTES TUDO", "iniciantes stuff"],
        "jovem aprendiz": ["jovem aprendiz", "Jovem Aprendiz", "JOVEM APRENDIZ"],
        "ganhar experiencia": ["ganhar experiencia", "ganhar experiência", "Ganhar Experiência", "GANHAR EXPERIÊNCIA"],
        "junior": ["junior", "júnior", "Júnior", "JUNIOR"],
        "pleno": ["pleno", "Pleno", "PLENO"],
        "senior": ["senior", "sênior", "Sênior", "SENIOR"]
    }

    passed_all = True
    for canonical, alias_list in aliases.items():
        base_res = None
        for alias in alias_list:
            s = copy.deepcopy(base_settings)
            s["level"] = alias
            res = is_job_relevant(test_job, "desenvolvedor python", s)
            if base_res is None:
                base_res = res
            elif res != base_res:
                print(f"[FAIL] Alias mismatch for {canonical}: '{alias}' gave {res}, expected {base_res}")
                passed_all = False
    
    if passed_all:
        print("[PASS] All level aliases and case variants behave 100% identically!")
    return passed_all

def test_union_property_and_isolation(dataset):
    print(f"\n--- TEST: UNION PROPERTY & ISOLATION MATRIX ({len(dataset)} JOBS) ---")
    
    base_settings = {
        "location": "Brasil (Remoto)",
        "contract": "Todos",
        "education": "Todos",
        "platforms": {},
        "ai_filter": False,
        "escudo_ptbr": True
    }

    union_matches = 0
    union_discrepancies = []

    level_accept_counts = {
        "Todos": 0,
        "Júnior": 0,
        "Pleno": 0,
        "Sênior": 0,
        "Jovem Aprendiz": 0,
        "Ganhar Experiência": 0,
        "Iniciantes Tudo": 0
    }

    isolation_failures = []

    for item in dataset:
        job = item["job"]
        kw = item["keyword"]
        j_id = item["id"]
        title = job["title"]
        title_norm = normalize_str(title)

        res = {}
        for lvl in level_accept_counts.keys():
            s = copy.deepcopy(base_settings)
            s["level"] = lvl
            ans = is_job_relevant(job, kw, s)
            res[lvl] = ans
            if ans:
                level_accept_counts[lvl] += 1

        # 1. Union Property Verification
        iniciantes_res = res["Iniciantes Tudo"]
        aprendiz_res = res["Jovem Aprendiz"]
        ganhar_exp_res = res["Ganhar Experiência"]
        expected_union = aprendiz_res or ganhar_exp_res

        if iniciantes_res == expected_union:
            union_matches += 1
        else:
            union_discrepancies.append({
                "id": j_id,
                "title": title,
                "requirements": job["requirements"],
                "iniciantes_tudo": iniciantes_res,
                "jovem_aprendiz": aprendiz_res,
                "ganhar_experiencia": ganhar_exp_res,
                "expected_union": expected_union
            })

        # 2. Isolation Verification
        # Rule: A pure Sênior title job must NOT be accepted by Júnior or Pleno or Aprendiz or Ganhar Exp
        if "senior" in title_norm or "sr" in title_norm:
            if res["Júnior"]:
                isolation_failures.append(f"{j_id}: Senior job '{title}' accepted by Júnior")
            if res["Pleno"]:
                isolation_failures.append(f"{j_id}: Senior job '{title}' accepted by Pleno")
            if res["Jovem Aprendiz"]:
                isolation_failures.append(f"{j_id}: Senior job '{title}' accepted by Jovem Aprendiz")
            if res["Ganhar Experiência"]:
                isolation_failures.append(f"{j_id}: Senior job '{title}' accepted by Ganhar Experiência")

        # Rule: A pure Pleno title job must NOT be accepted by Júnior or Sênior or Aprendiz or Ganhar Exp
        if "pleno" in title_norm or " pl " in title_norm:
            if res["Júnior"]:
                isolation_failures.append(f"{j_id}: Pleno job '{title}' accepted by Júnior")
            if res["Sênior"]:
                isolation_failures.append(f"{j_id}: Pleno job '{title}' accepted by Sênior")
            if res["Jovem Aprendiz"]:
                isolation_failures.append(f"{j_id}: Pleno job '{title}' accepted by Jovem Aprendiz")

        # Rule: A pure Junior title job must NOT be accepted by Pleno or Sênior or Aprendiz or Ganhar Exp
        if ("junior" in title_norm or " jr" in title_norm) and "aprendiz" not in title_norm and "voluntario" not in title_norm:
            if res["Pleno"]:
                isolation_failures.append(f"{j_id}: Junior job '{title}' accepted by Pleno")
            if res["Sênior"]:
                isolation_failures.append(f"{j_id}: Junior job '{title}' accepted by Sênior")

    union_pass_rate = (union_matches / len(dataset)) * 100
    print(f"\nResults Summary:")
    print(f"- Total Jobs Evaluated: {len(dataset)}")
    print(f"- Union Property Match: {union_matches}/{len(dataset)} ({union_pass_rate:.2f}%)")
    print(f"- Discrepancies Count: {len(union_discrepancies)}")
    print(f"- Isolation Violations: {len(isolation_failures)}")

    print("\nAcceptance Counts By Seniority Level:")
    for lvl, count in level_accept_counts.items():
        pct = (count / len(dataset)) * 100
        print(f"  * {lvl:<18}: {count:<5} ({pct:.1f}%)")

    if union_discrepancies:
        print("\n--- Discrepancy Sample Analysis ---")
        for d in union_discrepancies[:10]:
            print(f"ID: {d['id']} | Title: '{d['title']}'")
            print(f"   Iniciantes Tudo: {d['iniciantes_tudo']} | Jovem Aprendiz: {d['jovem_aprendiz']} | Ganhar Exp: {d['ganhar_experiencia']}")
            print(f"   Requirements: '{d['requirements'][:80]}...'")

    if isolation_failures:
        print("\n--- Isolation Failures Sample ---")
        for f in isolation_failures[:10]:
            print(f"   - {f}")

    return {
        "dataset_size": len(dataset),
        "union_matches": union_matches,
        "union_pass_rate": union_pass_rate,
        "discrepancies": union_discrepancies,
        "isolation_failures": isolation_failures,
        "level_counts": level_accept_counts
    }

def main():
    print("=================================================================")
    print("EMPIRICAL TEST BATTERY FOR BOT SENIORITY FILTERING")
    print("=================================================================")
    
    test_alias_normalization()
    
    dataset = generate_test_dataset()
    results = test_union_property_and_isolation(dataset)

    report_data = {
        "summary": results,
    }
    
    with open(r"C:/Users/99196/OneDrive/Documentos/vagas_bot/.agents/challenger_2/empirics_results.json", "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)
        
    print("\nResults exported to empirics_results.json successfully.")

if __name__ == "__main__":
    main()
