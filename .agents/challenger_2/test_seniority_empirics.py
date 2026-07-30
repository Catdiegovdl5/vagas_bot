import sys
import os
import copy

# Ensure project root is in sys.path
sys.path.insert(0, r"C:/Users/99196/OneDrive/Documentos/vagas_bot")

from bot import is_job_relevant, get_user_settings, normalize_str

def run_empirical_tests():
    print("=================================================================")
    print("STARTING EMPIRICAL SENIORITY REGRESSION & ISOLATION TEST SUITE")
    print("=================================================================")

    base_settings = {
        "location": "Brasil (Remoto)",
        "contract": "Todos",
        "education": "Todos",
        "platforms": {},
        "ai_filter": False,
        "escudo_ptbr": True
    }

    # Define test jobs covering various categories
    test_jobs = [
        # --- APRENDIZ JOBS ---
        {
            "id": "A1",
            "category": "Aprendiz",
            "job": {
                "title": "Jovem Aprendiz de TI",
                "requirements": "Suporte básico a usuários e organização de equipamentos de TI. Vaga para jovem aprendiz.",
                "platform": "linkedin",
                "location": "Remoto"
            },
            "keyword": "suporte tecnico n1"
        },
        {
            "id": "A2",
            "category": "Aprendiz",
            "job": {
                "title": "Menor Aprendiz Administrativo",
                "requirements": "Auxílio no arquivo e digitação de documentos.",
                "platform": "catho",
                "location": "Remoto"
            },
            "keyword": "assistente administrativo"
        },
        {
            "id": "A3",
            "category": "Aprendiz",
            "job": {
                "title": "Aprendiz de Programação Python",
                "requirements": "Aprenda a programar em Python com nossa equipe. Programa de aprendizagem.",
                "platform": "indeed",
                "location": "Remoto"
            },
            "keyword": "desenvolvedor python"
        },

        # --- GANHAR EXPERIÊNCIA JOBS ---
        {
            "id": "G1",
            "category": "Ganhar Experiência",
            "job": {
                "title": "Desenvolvedor Python Voluntário",
                "requirements": "Projeto social sem fins lucrativos para desenvolvimento de software voluntário.",
                "platform": "linkedin",
                "location": "Remoto"
            },
            "keyword": "desenvolvedor python"
        },
        {
            "id": "G2",
            "category": "Ganhar Experiência",
            "job": {
                "title": "Analista de Dados sem experiência",
                "requirements": "Oportunidade para primeiro emprego. Não exige experiência prévia na área de dados.",
                "platform": "indeed",
                "location": "Remoto"
            },
            "keyword": "analista de dados"
        },
        {
            "id": "G3",
            "category": "Ganhar Experiência",
            "job": {
                "title": "Front-End Developer - Projeto Open Source ONG",
                "requirements": "Trabalho comunitário em código aberto para doar tempo e ganhar experiência.",
                "platform": "github_vagas",
                "location": "Remoto"
            },
            "keyword": "desenvolvedor react"
        },
        {
            "id": "G4",
            "category": "Ganhar Experiência",
            "job": {
                "title": "Estágio Inicial em Marketing Digital",
                "requirements": "Estágio inicial sem cobrança de conhecimentos prévios. Primeiro emprego.",
                "platform": "infojobs",
                "location": "Remoto"
            },
            "keyword": "analista de marketing digital"
        },

        # --- JÚNIOR JOBS ---
        {
            "id": "J1",
            "category": "Júnior",
            "job": {
                "title": "Desenvolvedor Junior Python",
                "requirements": "Conhecimentos em Python e Django. Mínimo 1 ano de experiência.",
                "platform": "linkedin",
                "location": "Remoto"
            },
            "keyword": "desenvolvedor python"
        },
        {
            "id": "J2",
            "category": "Júnior",
            "job": {
                "title": "Analista de Dados Jr",
                "requirements": "SQL intermediário e Power BI. Experiência prévia como analista junior.",
                "platform": "gupy",
                "location": "Remoto"
            },
            "keyword": "analista de dados"
        },
        {
            "id": "J3",
            "category": "Júnior",
            "job": {
                "title": "Assistente de Marketing Junior",
                "requirements": "Criação de posts para redes sociais e redação inbound.",
                "platform": "catho",
                "location": "Remoto"
            },
            "keyword": "analista de marketing digital"
        },

        # --- PLENO JOBS ---
        {
            "id": "P1",
            "category": "Pleno",
            "job": {
                "title": "Desenvolvedor Pleno Python",
                "requirements": "Experiência de 3+ anos com Python, FastAPI e Docker.",
                "platform": "linkedin",
                "location": "Remoto"
            },
            "keyword": "desenvolvedor python"
        },
        {
            "id": "P2",
            "category": "Pleno",
            "job": {
                "title": "Analista de Dados Pleno",
                "requirements": "Perfil pleno para atuacão em data warehouse e modelagem de dados.",
                "platform": "glassdoor",
                "location": "Remoto"
            },
            "keyword": "analista de dados"
        },

        # --- SÊNIOR JOBS ---
        {
            "id": "S1",
            "category": "Sênior",
            "job": {
                "title": "Desenvolvedor Senior Python",
                "requirements": "Liderança técnica, arquitetura de sistemas Python e microsserviços.",
                "platform": "linkedin",
                "location": "Remoto"
            },
            "keyword": "desenvolvedor python"
        },
        {
            "id": "S2",
            "category": "Sênior",
            "job": {
                "title": "Engenheiro de Dados Especialista",
                "requirements": "Experiência sênior com Spark, Databricks e Airflow.",
                "platform": "remotar",
                "location": "Remoto"
            },
            "keyword": "engenheiro de dados"
        },

        # --- MIXED / EDGE CASE JOBS ---
        {
            "id": "M1",
            "category": "Mixed",
            "job": {
                "title": "Jovem Aprendiz Junior de TI",
                "requirements": "Programa de jovem aprendiz para suporte junior em TI.",
                "platform": "linkedin",
                "location": "Remoto"
            },
            "keyword": "suporte tecnico n1"
        },
        {
            "id": "M2",
            "category": "Mixed",
            "job": {
                "title": "Voluntário Senior de Projetos",
                "requirements": "Procuramos um profissional senior para trabalho voluntário em ONG.",
                "platform": "linkedin",
                "location": "Remoto"
            },
            "keyword": "assistente administrativo"
        },
        {
            "id": "M3",
            "category": "Mixed",
            "job": {
                "title": "Desenvolvedor Python (Sem Experiência) Junior",
                "requirements": "Vaga sem experiência exigida para desenvolvedor junior.",
                "platform": "indeed",
                "location": "Remoto"
            },
            "keyword": "desenvolvedor python"
        },
        {
            "id": "M4",
            "category": "Mixed",
            "job": {
                "title": "Professor de Python Jovem Aprendiz",
                "requirements": "Lecionar aulas de python para jovens aprendizes.",
                "platform": "linkedin",
                "location": "Remoto"
            },
            "keyword": "desenvolvedor python"
        }
    ]

    levels_to_test = [
        "Todos",
        "Júnior",
        "Pleno",
        "Sênior",
        "Jovem Aprendiz",
        "Ganhar Experiência",
        "Iniciantes Tudo"
    ]

    results_matrix = []

    print(f"\nEvaluating {len(test_jobs)} job test cases across {len(levels_to_test)} seniority levels...\n")

    header = f"{'ID':<4} | {'Category':<18} | {'Title':<40} | " + " | ".join([f"{l:<16}" for l in levels_to_test])
    print(header)
    print("-" * len(header))

    union_discrepancies = []
    isolation_regressions = []

    for item in test_jobs:
        job_id = item["id"]
        cat = item["category"]
        job = item["job"]
        kw = item["keyword"]
        title = job["title"]

        row_results = {}
        for lvl in levels_to_test:
            s = copy.deepcopy(base_settings)
            s["level"] = lvl
            ans = is_job_relevant(job, kw, s)
            row_results[lvl] = ans

        # Check Union Property: Iniciantes Tudo == (Jovem Aprendiz OR Ganhar Experiência)
        iniciantes_res = row_results["Iniciantes Tudo"]
        aprendiz_res = row_results["Jovem Aprendiz"]
        ganhar_exp_res = row_results["Ganhar Experiência"]
        expected_union = aprendiz_res or ganhar_exp_res

        if iniciantes_res != expected_union:
            union_discrepancies.append({
                "id": job_id,
                "title": title,
                "iniciantes_tudo": iniciantes_res,
                "jovem_aprendiz": aprendiz_res,
                "ganhar_experiencia": ganhar_exp_res,
                "expected_union": expected_union
            })

        # Format output line
        res_str = " | ".join([f"{str(row_results[l]):<16}" for l in levels_to_test])
        print(f"{job_id:<4} | {cat:<18} | {title[:40]:<40} | {res_str}")

        results_matrix.append({
            "item": item,
            "results": row_results
        })

    print("\n" + "=" * 65)
    print("EMPIRICAL ANALYSIS OF FINDINGS")
    print("=" * 65)

    print(f"\n1. UNION IDENTITY TEST (Iniciantes Tudo == Jovem Aprendiz OR Ganhar Experiência):")
    if not union_discrepancies:
        print("   [PASS] 100% Match! 'Iniciantes Tudo' is EXACTLY identical to (Jovem Aprendiz OR Ganhar Experiência) across all test jobs.")
    else:
        print(f"   [DISCREPANCY DETECTED] Found {len(union_discrepancies)} cases where 'Iniciantes Tudo' != (Jovem Aprendiz OR Ganhar Experiência):")
        for d in union_discrepancies:
            print(f"   - Job {d['id']} ('{d['title']}'): Iniciantes Tudo={d['iniciantes_tudo']}, Jovem Aprendiz={d['jovem_aprendiz']}, Ganhar Exp={d['ganhar_experiencia']} (Expected Union={d['expected_union']})")

    # 2. ISOLATION & REGRESSION CHECK
    print(f"\n2. SENIORITY LEVEL ISOLATION CHECK:")
    # Check Junior: Should reject Sênior (S1, S2) and Pleno (P1, P2)
    junior_rejects_senior_pleno = not results_matrix[7]["results"]["Júnior"] and not results_matrix[9]["results"]["Júnior"] and not results_matrix[10]["results"]["Júnior"]
    print(f"   - Júnior rejects Pleno/Sênior: {'[PASS]' if junior_rejects_senior_pleno else '[FAIL]'}")

    # Check Pleno: Should reject Júnior (J1, J2) and Sênior (S1, S2)
    pleno_rejects_jr_sr = not results_matrix[6]["results"]["Pleno"] and not results_matrix[9]["results"]["Pleno"]
    print(f"   - Pleno rejects Júnior/Sênior: {'[PASS]' if pleno_rejects_jr_sr else '[FAIL]'}")

    # Check Sênior: Should reject Júnior (J1, J2) and Pleno (P1, P2)
    senior_rejects_jr_pl = not results_matrix[6]["results"]["Sênior"] and not results_matrix[7]["results"]["Sênior"]
    print(f"   - Sênior rejects Júnior/Pleno: {'[PASS]' if senior_rejects_jr_pl else '[FAIL]'}")

    # Check Jovem Aprendiz: Requires 'aprendiz' term
    aprendiz_strict = results_matrix[0]["results"]["Jovem Aprendiz"] and not results_matrix[6]["results"]["Jovem Aprendiz"]
    print(f"   - Jovem Aprendiz requires aprendiz terms strictly: {'[PASS]' if aprendiz_strict else '[FAIL]'}")

    # Check Ganhar Experiência: Requires target exp terms AND no higher terms
    ganhar_exp_strict = results_matrix[3]["results"]["Ganhar Experiência"] and not results_matrix[6]["results"]["Ganhar Experiência"]
    print(f"   - Ganhar Experiência requires target terms and excludes higher terms: {'[PASS]' if ganhar_exp_strict else '[FAIL]'}")

    return results_matrix, union_discrepancies

if __name__ == "__main__":
    run_empirical_tests()
