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

def test_iniciantes_voluntario():
    settings = {
        "level": "iniciantes tudo",
        "location": "Brasil (Remoto)",
        "contract": "Todos",
        "education": "Todos",
        "platforms": {},
        "ai_filter": False
    }
    job_voluntario = {
        "title": "Dev Voluntário",
        "requirements": "Desenvolvimento de software voluntário para causa social",
        "platform": "linkedin",
        "location": "Remoto"
    }
    assert is_job_relevant(job_voluntario, "Dev", settings) is True

def test_iniciantes_aprendiz():
    settings = {
        "level": "iniciantes tudo",
        "location": "Brasil (Remoto)",
        "contract": "Todos",
        "education": "Todos",
        "platforms": {},
        "ai_filter": False
    }
    job_aprendiz = {
        "title": "Jovem Aprendiz de TI",
        "requirements": "Vaga de jovem aprendiz para atuar na área de TI",
        "platform": "linkedin",
        "location": "Remoto"
    }
    assert is_job_relevant(job_aprendiz, "TI", settings) is True

def test_iniciantes_junior_blocked():
    settings = {
        "level": "iniciantes tudo",
        "location": "Brasil (Remoto)",
        "contract": "Todos",
        "education": "Todos",
        "platforms": {},
        "ai_filter": False
    }
    job_junior = {
        "title": "Dev Júnior 1 ano de experiência",
        "requirements": "Desenvolvedor júnior com 1 ano de experiência prévia",
        "platform": "linkedin",
        "location": "Remoto"
    }
    assert is_job_relevant(job_junior, "Dev", settings) is False

def main():
    print("=" * 60)
    print("RUNNING TEST SUITE: test_iniciantes.py ('Iniciantes Tudo')")
    print("=" * 60)

    try:
        test_iniciantes_voluntario()
        print("[PASS] Vaga 'Dev Voluntário' (Ganhar Experiência) -> True")
        test_iniciantes_aprendiz()
        print("[PASS] Vaga 'Jovem Aprendiz de TI' (Aprendiz) -> True")
        test_iniciantes_junior_blocked()
        print("[PASS] Vaga 'Dev Júnior 1 ano de experiência' -> False")
        print("=" * 60)
        print("ALL INICIANTES TUDO TEST CASES PASSED SUCCESSFULLY! Exit code 0.")
        sys.stdout.flush()
        sys.exit(0)
    except AssertionError as e:
        print(f"[FAIL] Assertion failed: {e}")
        sys.stdout.flush()
        sys.exit(1)
    except Exception as e:
        print(f"[FAIL] Unexpected error: {e}")
        sys.stdout.flush()
        sys.exit(1)

if __name__ == '__main__':
    main()
