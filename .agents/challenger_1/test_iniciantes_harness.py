import sys
import os

# Guarantee root directory is in sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from bot import is_job_relevant, normalize_str, match_exact_word

def run_tests():
    print("=" * 80)
    print("EMPIRICAL STRESS TEST HARNESS FOR 'iniciantes tudo'")
    print("=" * 80)
    
    settings = {
        "level": "iniciantes tudo",
        "location": "Brasil (Remoto)",
        "contract": "Todos",
        "education": "Todos",
        "platforms": {},
        "ai_filter": False
    }

    test_cases = [
        # --- Standard Expected Cases ---
        {
            "id": "TC01",
            "name": "Standard Jovem Aprendiz",
            "job": {
                "title": "Jovem Aprendiz de TI",
                "requirements": "Atuação com suporte básico e aprendizado em tecnologia.",
                "platform": "linkedin",
                "location": "Remoto"
            },
            "keyword": "TI",
            "expected": True,
            "category": "Jovem Aprendiz"
        },
        {
            "id": "TC02",
            "name": "Standard Volunteer / Open Source",
            "job": {
                "title": "Desenvolvedor Open Source",
                "requirements": "Projeto de código aberto sem experiência necessária.",
                "platform": "github_vagas",
                "location": "Remoto"
            },
            "keyword": "Dev",
            "expected": True,
            "category": "Ganhar Experiência"
        },
        {
            "id": "TC03",
            "name": "Standard Junior Job (Requires Experience)",
            "job": {
                "title": "Dev Júnior 1 ano de experiência",
                "requirements": "Desenvolvedor júnior com 1 ano de experiência prévia.",
                "platform": "linkedin",
                "location": "Remoto"
            },
            "keyword": "Dev",
            "expected": False,
            "category": "Standard Junior"
        },

        # --- Substring Collision ('ong' inside 'MongoDB', 'longo', etc.) ---
        {
            "id": "TC04",
            "name": "Substring False Positive: MongoDB in requirements",
            "job": {
                "title": "Desenvolvedor Backend Python",
                "requirements": "Desenvolvimento com Python, FastAPI e MongoDB.",
                "platform": "linkedin",
                "location": "Remoto"
            },
            "keyword": "Python",
            "expected": False, # Regular dev job requiring MongoDB; NOT a volunteer/ONG/aprendiz job!
            "category": "Substring Bug ('ong')"
        },
        {
            "id": "TC05",
            "name": "Substring False Positive: 'longo prazo' in description",
            "job": {
                "title": "Desenvolvedor Software",
                "requirements": "Projeto de longo prazo utilizando Python e SQL.",
                "platform": "linkedin",
                "location": "Remoto"
            },
            "keyword": "Python",
            "expected": False,
            "category": "Substring Bug ('ong')"
        },
        {
            "id": "TC06",
            "name": "Substring False Positive: 'strong' in description",
            "job": {
                "title": "Software Engineer",
                "requirements": "Strong knowledge in Python and cloud services.",
                "platform": "linkedin",
                "location": "Remoto"
            },
            "keyword": "Python",
            "expected": False,
            "category": "Substring Bug ('ong')"
        },

        # --- Conflicting Level Keywords ---
        {
            "id": "TC07",
            "name": "Conflicting Keywords: Aprendiz Pleno",
            "job": {
                "title": "Aprendiz Pleno de TI",
                "requirements": "Programa de jovem aprendiz nível pleno.",
                "platform": "linkedin",
                "location": "Remoto"
            },
            "keyword": "TI",
            "expected": False, # 'Pleno' should disqualify for beginner level!
            "category": "Conflicting Level"
        },
        {
            "id": "TC08",
            "name": "Conflicting Keywords: Voluntário Sênior",
            "job": {
                "title": "Dev Voluntário Sênior",
                "requirements": "Atuação voluntária para perfil sênior em arquitetura.",
                "platform": "linkedin",
                "location": "Remoto"
            },
            "keyword": "Dev",
            "expected": False, # Sênior should disqualify
            "category": "Conflicting Level"
        },
        {
            "id": "TC09",
            "name": "Conflicting Keywords: Open Source Sênior",
            "job": {
                "title": "Desenvolvedor Open Source Sr",
                "requirements": "Projeto open source buscando liderança sênior.",
                "platform": "github_vagas",
                "location": "Remoto"
            },
            "keyword": "Dev",
            "expected": False, # Sr should disqualify
            "category": "Conflicting Level"
        },

        # --- False Seniority Block due to 'PL/SQL' ('pl' inside 'PL/SQL') ---
        {
            "id": "TC10",
            "name": "False Seniority Rejection: Volunteer job mentioning PL/SQL",
            "job": {
                "title": "Desenvolvedor Voluntário SQL",
                "requirements": "Projeto social sem experiência, manutenção de consultas em PL/SQL.",
                "platform": "linkedin",
                "location": "Remoto"
            },
            "keyword": "SQL",
            "expected": True, # Valid volunteer job, PL/SQL is a database language, not 'Pleno'!
            "category": "Word Boundary Bug ('pl' in PL/SQL)"
        },
        {
            "id": "TC11",
            "name": "False Seniority Rejection: Open Source project mentioning PL/SQL",
            "job": {
                "title": "Projeto Open Source Database",
                "requirements": "Código aberto sem experiência exigida. Atribuição em scripts PL/SQL.",
                "platform": "github_vagas",
                "location": "Remoto"
            },
            "keyword": "Database",
            "expected": True, # Valid open source job, PL/SQL is a language!
            "category": "Word Boundary Bug ('pl' in PL/SQL)"
        },

        # --- Accents & Case Sensitivity ---
        {
            "id": "TC12",
            "name": "Uppercase / Accents: VOLUNTÁRIO / CÓDIGO ABERTO",
            "job": {
                "title": "DESENVOLVEDOR VOLUNTÁRIO",
                "requirements": "PROJETO DE CÓDIGO ABERTO PARA INICIANTES",
                "platform": "linkedin",
                "location": "REMOTO"
            },
            "keyword": "Dev",
            "expected": True,
            "category": "Case & Accents"
        },
        {
            "id": "TC13",
            "name": "Uppercase: JOVEM APRENDIZ DE TI",
            "job": {
                "title": "JOVEM APRENDIZ DE TI",
                "requirements": "VAGA PARA MENOR APRENDIZ E JOVEM APRENDIZ",
                "platform": "linkedin",
                "location": "REMOTO"
            },
            "keyword": "TI",
            "expected": True,
            "category": "Case & Accents"
        },

        # --- Substring / Boundary on 'jr' / 'sr' / 'pl' ---
        {
            "id": "TC14",
            "name": "Exact word check on 'sr' in words like 'SRV' / 'SRA'",
            "job": {
                "title": "Voluntário Servidor SRV",
                "requirements": "Projeto social de código aberto sem experiência prévia.",
                "platform": "linkedin",
                "location": "Remoto"
            },
            "keyword": "Voluntário",
            "expected": True,
            "category": "Word Boundary"
        }
    ]

    results = []
    passed_count = 0
    failed_count = 0

    for tc in test_cases:
        res = is_job_relevant(tc["job"], tc["keyword"], settings)
        passed = (res == tc["expected"])
        if passed:
            passed_count += 1
            status = "PASS"
        else:
            failed_count += 1
            status = "FAIL"
            
        results.append({
            "id": tc["id"],
            "name": tc["name"],
            "category": tc["category"],
            "expected": tc["expected"],
            "got": res,
            "status": status,
            "job": tc["job"]
        })
        print(f"[{status}] {tc['id']} - {tc['name']} (Category: {tc['category']})")
        print(f"       Expected: {tc['expected']} | Got: {res}")
        if not passed:
            print(f"       >>> DISCREPANCY DISCOVERED! <<<")
        print("-" * 60)

    print("\n" + "=" * 80)
    print(f"SUMMARY: Total: {len(test_cases)} | Passed: {passed_count} | Failed: {failed_count}")
    print("=" * 80)
    return results

if __name__ == '__main__':
    run_tests()
