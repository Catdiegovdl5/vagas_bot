import sys
import os

# Add repo root directory to sys.path
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from bot import is_job_relevant

def run_stress_tests():
    print("=" * 80)
    print("EMPIRICAL STRESS TEST SUITE: is_job_relevant ('ganhar experiência')")
    print("=" * 80)

    # Base settings with user_level = 'ganhar experiência'
    base_settings = {
        "level": "ganhar experiência",
        "location": "Brasil (Remoto)",
        "contract": "Todos",
        "education": "Todos",
        "platforms": {"linkedin": True}
    }
    
    keyword = "Desenvolvedor Python"

    test_cases = [
        # ---------------------------------------------------------------------
        # CATEGORY 1: Mixed case / accents
        # ---------------------------------------------------------------------
        {
            "category": "1. Mixed case / accents",
            "name": "PROJETO SOCIAL (Uppercase)",
            "title": "PROJETO SOCIAL - Desenvolvedor Python",
            "reqs": "Projeto social de TI focado em voluntariado para desenvolvedores Python.",
            "expected": True,
            "rationale": "Matches 'projeto social' regardless of uppercase."
        },
        {
            "category": "1. Mixed case / accents",
            "name": "Código Aberto (Mixed case & accents)",
            "title": "Código Aberto - Dev Python",
            "reqs": "Oportunidade para contribuir com Código Aberto e desenvolvimento Python.",
            "expected": True,
            "rationale": "Matches 'codigo aberto' after normalization."
        },
        {
            "category": "1. Mixed case / accents",
            "name": "Sem Experiência (Mixed case & accents)",
            "title": "Sem Experiência - Desenvolvedor Python",
            "reqs": "Vaga para desenvolvedor Python sem experiência prévia requerida.",
            "expected": True,
            "rationale": "Matches 'sem experiencia' after normalization."
        },

        # ---------------------------------------------------------------------
        # CATEGORY 2: Boundary terms
        # ---------------------------------------------------------------------
        {
            "category": "2. Boundary terms",
            "name": "voluntariado em ONG",
            "title": "voluntariado em ONG - Programador Python",
            "reqs": "Trabalho de voluntariado em ONG promovendo tecnologia e código Python.",
            "expected": True,
            "rationale": "Matches boundary target terms 'voluntariado' and 'ong'."
        },
        {
            "category": "2. Boundary terms",
            "name": "primeiro emprego de TI",
            "title": "primeiro emprego de TI - Desenvolvedor Python",
            "reqs": "Excelente oportunidade para o primeiro emprego de TI em projetos Python.",
            "expected": True,
            "rationale": "Matches boundary target term 'primeiro emprego'."
        },

        # ---------------------------------------------------------------------
        # CATEGORY 3: Conflicting seniority
        # ---------------------------------------------------------------------
        {
            "category": "3. Conflicting seniority",
            "name": "Voluntário Júnior",
            "title": "Voluntário Júnior - Desenvolvedor Python",
            "reqs": "Vaga de voluntário júnior para desenvolvedores Python.",
            "expected": False,
            "rationale": "Conflicting seniority 'Júnior' must be rejected for 'ganhar experiência'."
        },
        {
            "category": "3. Conflicting seniority",
            "name": "Projeto Open Source Pleno",
            "title": "Projeto Open Source Pleno - Dev Python",
            "reqs": "Projeto open source direcionado a desenvolvedores de nível pleno.",
            "expected": False,
            "rationale": "Conflicting seniority 'Pleno' must be rejected for 'ganhar experiência'."
        },
        {
            "category": "3. Conflicting seniority",
            "name": "Sênior Sem Experiência",
            "title": "Sênior Sem Experiência - Arquiteto Python",
            "reqs": "Vaga sênior sem experiência prévia em framework específico.",
            "expected": False,
            "rationale": "Conflicting seniority 'Sênior' must be rejected for 'ganhar experiência'."
        },

        # ---------------------------------------------------------------------
        # CATEGORY 4: Missing target terms
        # ---------------------------------------------------------------------
        {
            "category": "4. Missing target terms",
            "name": "Desenvolvedor Python Remote",
            "title": "Desenvolvedor Python Remote",
            "reqs": "Desenvolvedor Python com conhecimento em Django, FastAPI e Docker.",
            "expected": False,
            "rationale": "Lacks target experience terms ('voluntario', 'sem experiencia', etc.)."
        },
        {
            "category": "4. Missing target terms",
            "name": "Estágio em TI 2 anos exp",
            "title": "Estágio em TI 2 anos exp - Desenvolvedor Python",
            "reqs": "Vaga de estágio em TI exigindo 2 anos de experiência profissional prévia.",
            "expected": False,
            "rationale": "Lacks target terms like 'estagio inicial' or 'sem experiencia'."
        },

        # ---------------------------------------------------------------------
        # CATEGORY 5: Adversarial & Substring / Boundary Flaws
        # ---------------------------------------------------------------------
        {
            "category": "5. Adversarial / Flaws",
            "name": "False positive substring 'involuntario'",
            "title": "Desenvolvedor Python - Desligamento involuntario",
            "reqs": "Processo seletivo para programador Python em reestruturação.",
            "expected": False, # 'voluntario' in 'involuntario' is a false positive!
            "rationale": "'involuntario' contains 'voluntario' as substring. Should NOT pass if substring matching is flawed."
        },
        {
            "category": "5. Adversarial / Flaws",
            "name": "False positive substring 'congresso' ('ong')",
            "title": "Desenvolvedor Python em congresso de TI",
            "reqs": "Desenvolvimento de aplicativo Python para apresentação em congresso.",
            "expected": False, # 'ong' in 'congresso' is a false positive!
            "rationale": "'congresso' contains 'ong' as substring. Should NOT pass as an ONG job."
        },
        {
            "category": "5. Adversarial / Flaws",
            "name": "PL/SQL in Voluntário job",
            "title": "Desenvolvedor Python Voluntário - Conhecimento em PL/SQL",
            "reqs": "Trabalho voluntário em ONG para desenvolver scripts Python e banco de dados PL/SQL.",
            "expected": True, # Should pass because it's a valid volunteer Python job with PL/SQL
            "rationale": "Valid volunteer job. Tests if match_exact_word('pl/sql', 'pl') falsely triggers higher_term rejection."
        },
        {
            "category": "5. Adversarial / Flaws",
            "name": "Accented settings level: 'Ganhar Experiência'",
            "title": "PROJETO SOCIAL - Desenvolvedor Python",
            "reqs": "Projeto social voluntário em Python.",
            "expected": True,
            "settings": {
                "level": "Ganhar Experiência",
                "location": "Brasil (Remoto)",
                "contract": "Todos",
                "education": "Todos",
                "platforms": {"linkedin": True}
            },
            "rationale": "Tests if settings['level'] normalization handles accents ('Ganhar Experiência')."
        }
    ]

    results = []
    category_counts = {}

    for idx, test in enumerate(test_cases, 1):
        cat = test["category"]
        if cat not in category_counts:
            category_counts[cat] = {"total": 0, "passed": 0, "failed": 0}
        category_counts[cat]["total"] += 1

        curr_settings = test.get("settings", base_settings)
        job = {
            "title": test["title"],
            "requirements": test["reqs"],
            "location": "Remoto",
            "platform": "linkedin"
        }

        actual = is_job_relevant(job, keyword, curr_settings)
        passed = (actual == test["expected"])

        if passed:
            category_counts[cat]["passed"] += 1
            status_str = "PASS"
        else:
            category_counts[cat]["failed"] += 1
            status_str = "FAIL"

        results.append({
            "id": idx,
            "category": cat,
            "name": test["name"],
            "expected": test["expected"],
            "actual": actual,
            "passed": passed,
            "rationale": test["rationale"]
        })

        print(f"[{status_str}] Test #{idx}: {test['name']}")
        print(f"       Category: {cat}")
        print(f"       Expected: {test['expected']} | Actual: {actual}")
        print(f"       Rationale: {test['rationale']}\n")

    total_tests = len(test_cases)
    total_passed = sum(1 for r in results if r["passed"])
    total_failed = total_tests - total_passed
    pass_rate = (total_passed / total_tests) * 100.0

    print("=" * 80)
    print("SUMMARY BY CATEGORY")
    print("=" * 80)
    for cat, stats in category_counts.items():
        rate = (stats["passed"] / stats["total"]) * 100.0 if stats["total"] > 0 else 0
        print(f"  {cat}: {stats['passed']}/{stats['total']} Passed ({rate:.1f}%)")

    print("-" * 80)
    print(f"TOTAL: {total_passed}/{total_tests} Passed ({pass_rate:.1f}%) | Failed: {total_failed}")
    print("=" * 80)

    return results, category_counts, total_passed, total_failed, total_tests

if __name__ == "__main__":
    run_stress_tests()
