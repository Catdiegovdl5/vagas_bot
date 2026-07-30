import sys
import os

# Guarantee root directory is in sys.path
sys.path.insert(0, r"C:\Users\99196\OneDrive\Documentos\vagas_bot")

from bot import is_job_relevant

def test_unseen_cases():
    settings = {
        "level": "ganhar experiencia",
        "location": "Brasil (Remoto)",
        "contract": "Todos",
        "education": "Todos",
        "platforms": {},
        "ai_filter": False
    }

    # Custom unseen cases
    test_data = [
        # (title, reqs, kw, expected)
        ("Programador C# para Projeto Social", "Vaga para atuar em projeto social de ONG", "Programador", True),
        ("Desenvolvedor Frontend Código Aberto", "Participe de projeto open source comunitário", "Desenvolvedor", True),
        ("Estagiário Sem Experiência", "Não exige experiência prévia", "Estagiário", False), # "estagiário" has "jr/estagio" -> wait! "estágio" in higher_terms? No, "estagio" is not in higher_terms ["junior", "jr", "pleno", "pl", "senior", "sr"]. Wait, let's check!
        ("Engenheiro de Software Sênior em ONG", "Atuação em ONG social para engenheiro sênior", "Engenheiro", False), # Blocked by sênior
        ("Auxiliar Técnico sem qualquer termo de exp", "Atividades de TI", "Auxiliar", False), # No target_exp_terms -> False
        ("Desenvolvedor Python Primeiro Emprego", "Vaga de primeiro emprego sem exigências", "Desenvolvedor", True),
    ]

    print("--- UNSEEN STRESS TEST RESULTS ---")
    all_passed = True
    for title, reqs, kw, expected in test_data:
        job = {
            "title": title,
            "requirements": reqs,
            "platform": "linkedin",
            "location": "Remoto"
        }
        res = is_job_relevant(job, kw, settings)
        status = "PASS" if res == expected else "FAIL"
        print(f"[{status}] Title: '{title}' | Got: {res} | Expected: {expected}")
        if res != expected:
            all_passed = False

    if all_passed:
        print("ALL UNSEEN STRESS TESTS PASSED!")
    else:
        print("SOME STRESS TESTS FAILED!")

if __name__ == "__main__":
    test_unseen_cases()
