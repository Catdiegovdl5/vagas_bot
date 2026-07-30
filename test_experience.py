import sys
import os

# Set stdout encoding to UTF-8 for Windows console support
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Guarantee current directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bot import is_job_relevant

def main():
    test_settings = {
        "level": "ganhar experiência",
        "location": "Brasil (Remoto)",
        "contract": "Todos",
        "education": "Todos",
        "platforms": {},
        "ai_filter": False
    }

    test_cases = [
        # (Title, Requirements, Keyword, Expected Result, Description)
        (
            "Dev Voluntário em ONG",
            "Desenvolvimento de software voluntário para causa social com requisitos.",
            "Dev",
            True,
            "1. Vaga 'Dev Voluntário em ONG' -> True"
        ),
        (
            "Dev - Estágio Inicial Sem Experiência",
            "Vaga para aprender desenvolvimento sem exigir experiência prévia no projeto.",
            "Dev",
            True,
            "2. Vaga 'Dev - Estágio Inicial Sem Experiência' -> True"
        ),
        (
            "Dev Júnior 1 ano de experiência",
            "Buscamos desenvolvedor júnior com 1 ano de experiência prévia.",
            "Dev",
            False,
            "3. Vaga 'Dev Júnior 1 ano de experiência' -> False (blocked by 'júnior')"
        ),
        (
            "Dev - Projeto Open Source para Iniciantes",
            "Contribuição para código aberto e auxílio a novos desenvolvedores.",
            "Dev",
            True,
            "4. Vaga 'Dev - Projeto Open Source para Iniciantes' -> True"
        ),
        (
            "Dev Pleno",
            "Desenvolvedor com experiência intermediária no projeto.",
            "Dev",
            False,
            "5a. Vaga 'Dev Pleno' -> False (blocked by 'pleno')"
        ),
        (
            "Dev Sênior",
            "Desenvolvedor sênior com liderança técnica e arquitetura.",
            "Dev",
            False,
            "5b. Vaga 'Dev Sênior' -> False (blocked by 'sênior')"
        ),
        (
            "Dev Python",
            "Desenvolvimento de APIs com FastAPI e Python backend.",
            "Dev",
            False,
            "5c. Vaga 'Dev Python' sem termos de experiência -> False"
        ),
        (
            "Dev Voluntário Pleno",
            "Projeto voluntário para profissional nível pleno com requisitos.",
            "Dev",
            False,
            "5d. Vaga 'Dev Voluntário Pleno' -> False (has target term but blocked by 'pleno')"
        ),
        (
            "Desenvolvedor Sem Experiência",
            "Primeiro emprego para quem não exige experiência prévia.",
            "Desenvolvedor",
            True,
            "5e. Vaga 'Desenvolvedor Sem Experiência' -> True"
        ),
        (
            "Desenvolvedor Voluntary Project",
            "Open source voluntary project for beginners and learners.",
            "Desenvolvedor",
            True,
            "5f. Vaga 'Desenvolvedor Voluntary Project' -> True (voluntary exempted)"
        )
    ]

    failed_count = 0
    print("=" * 60)
    print("RUNNING TEST SUITE: test_experience.py ('Ganhar Experiência')")
    print("=" * 60)

    for title, reqs, keyword, expected, desc in test_cases:
        job = {
            "title": title,
            "requirements": reqs,
            "platform": "linkedin",
            "location": "Remoto"
        }
        result = is_job_relevant(job, keyword, test_settings)
        status = "PASS" if result == expected else "FAIL"
        if result != expected:
            failed_count += 1
            print(f"[FAIL] {desc}")
            print(f"   Got: {result} | Expected: {expected} | Job: {title}")
        else:
            print(f"[PASS] {desc}")

    print("=" * 60)
    if failed_count == 0:
        print("ALL EXPERIENCE LEVEL TEST CASES PASSED SUCCESSFULLY! Exit code 0.")
        sys.stdout.flush()
        os._exit(0)
    else:
        print(f"TEST SUITE FAILED WITH {failed_count} ERRORS! Exit code 1.")
        sys.stdout.flush()
        os._exit(1)

if __name__ == '__main__':
    main()
