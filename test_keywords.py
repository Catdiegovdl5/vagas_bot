import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from bot import is_job_relevant, normalize_str
    print("Successfully imported is_job_relevant and normalize_str from bot.py")
except Exception as e:
    print(f"Error importing from bot.py: {e}")
    sys.exit(1)

# Default settings for testing
test_settings = {
    "level": "Todos",
    "location": "Brasil (Remoto)",
    "contract": "Todos",
    "education": "Todos",
    "platforms": {},
    "ai_filter": False
}

# 5 approved cases: (Title, Keyword, Expected Result)
approved_cases = [
    # 1. "Desenvolvedor Python" under "Backend Python" or "Engenheiro de Software Python"
    ("Desenvolvedor Python", "Backend Python", True),
    # 2. "Especialista em IA Generativa" under "Especialista em IA Generativa"
    ("Especialista em IA Generativa", "Especialista em IA Generativa", True),
    # 3. "Estagiário de Programação" under "Estagiário de TI / Programação"
    ("Estagiário de Programação", "Estagiário de TI / Programação", True),
    # 4. "Auxiliar Administrativo" under "Auxiliar Administrativo"
    ("Auxiliar Administrativo", "Auxiliar Administrativo", True),
    # 5. "Gestor de Tráfego Pago" under "Gestor de Tráfego / Performance"
    ("Gestor de Tráfego Pago", "Gestor de Tráfego / Performance", True)
]

# 5 rejected cases: (Title, Keyword, Expected Result)
rejected_cases = [
    # 1. "Professor de Python" under "Backend Python"
    ("Professor de Python", "Backend Python", False),
    # 2. "Tutor de IA" under "Especialista em IA"
    ("Tutor de IA", "Especialista em IA", False),
    # 3. "Estagiário de Direito" under "Desenvolvedor Júnior / Estagiário"
    ("Estagiário de Direito", "Desenvolvedor Júnior / Estagiário", False),
    # 4. "Auxiliar de Limpeza" under "Auxiliar Administrativo"
    ("Auxiliar de Limpeza", "Auxiliar Administrativo", False),
    # 5. "Faxineiro" under "Auxiliar Administrativo"
    ("Faxineiro", "Auxiliar Administrativo", False)
]

# Boundary and regression cases: (Title, Keyword, Expected Result, Custom Settings)
boundary_cases = [
    # 1. Global blacklist term "professor" at the end of the string
    ("Desenvolvedor Python Professor", "Backend Python", False, {**test_settings}),
    # 2. Global blacklist term at the beginning of the string
    ("Professor de Desenvolvedor Python", "Backend Python", False, {**test_settings}),
    # 3. Seniority level conflict at the beginning of the string (for junior candidate)
    ("Senior Python Developer", "Backend Python", False, {**test_settings, "level": "junior"}),
    # 4. Seniority level conflict at the end of the string (for junior candidate)
    ("Desenvolvedor Python Pleno", "Backend Python", False, {**test_settings, "level": "junior"}),
    # 5. Contract conflict at the end of the string (for CLT candidate)
    ("Desenvolvedor Python PJ", "Backend Python", False, {**test_settings, "contract": "clt"}),
    # 6. Contract conflict with punctuation like "Desenvolvedor Python - PJ" (for CLT candidate)
    ("Desenvolvedor Python - PJ", "Backend Python", False, {**test_settings, "contract": "clt"}),
    # 7. Junior candidate seeking junior role (should pass)
    ("Junior Python Developer", "Backend Python", True, {**test_settings, "level": "junior"}),
    # 8. PJ candidate matching PJ job (should pass)
    ("Desenvolvedor Python PJ", "Backend Python", True, {**test_settings, "contract": "pj"}),
    # 9. CLT candidate matching job without PJ (should pass)
    ("Desenvolvedor Python", "Backend Python", True, {**test_settings, "contract": "clt"}),
    # 10. Local blacklist boundary case (should fail because "aereo" is blacklisted for "gestor de trafego / performance")
    ("Gestor de Tráfego Aéreo", "Gestor de Tráfego / Performance", False, {**test_settings}),
]

failed = False

print("\n--- Running Approved Cases ---")
for title, keyword, expected in approved_cases:
    job = {"title": title, "requirements": "Requisitos da vaga.", "location": "Remoto"}
    res = is_job_relevant(job, keyword, test_settings)
    print(f"Title: '{title}' | Keyword: '{keyword}' -> Got: {res} | Expected: {expected}")
    if res != expected:
        print("FAIL!")
        failed = True
    else:
        print("PASS")

print("\n--- Running Rejected Cases ---")
for title, keyword, expected in rejected_cases:
    job = {"title": title, "requirements": "Requisitos da vaga.", "location": "Remoto"}
    res = is_job_relevant(job, keyword, test_settings)
    print(f"Title: '{title}' | Keyword: '{keyword}' -> Got: {res} | Expected: {expected}")
    if res != expected:
        print("FAIL!")
        failed = True
    else:
        print("PASS")

print("\n--- Running Boundary Cases ---")
for title, keyword, expected, custom_settings in boundary_cases:
    job = {"title": title, "requirements": "Requisitos da vaga.", "location": "Remoto"}
    res = is_job_relevant(job, keyword, custom_settings)
    print(f"Title: '{title}' | Keyword: '{keyword}' | Settings: {custom_settings} -> Got: {res} | Expected: {expected}")
    if res != expected:
        print("FAIL!")
        failed = True
    else:
        print("PASS")

if __name__ == "__main__":
    if failed:
        print("\nSome tests FAILED!")
        sys.exit(1)
    else:
        print("\nAll tests PASSED successfully!")
        sys.exit(0)
