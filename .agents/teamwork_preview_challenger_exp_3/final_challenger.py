import sys
import os
import unicodedata
import re

# Guarantee current directory (and parent dir for bot) is in sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, BASE_DIR)

# Set stdout encoding to UTF-8 for Windows console output
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

try:
    from bot import is_job_relevant, normalize_str
    print("✅ Successfully imported is_job_relevant from bot.py")
except Exception as e:
    print(f"❌ Error importing from bot.py: {e}")
    sys.exit(1)

def run_suite(suite_name, test_cases):
    print("\n" + "=" * 70)
    print(f"RUNNING SUITE: {suite_name}")
    print("=" * 70)

    passed_count = 0
    failed_count = 0
    failures = []

    for idx, case in enumerate(test_cases, 1):
        job, keyword, settings, expected, desc = case
        
        actual = is_job_relevant(job, keyword, settings)
        status = "PASS" if actual == expected else "FAIL"
        
        if actual == expected:
            passed_count += 1
            print(f"  [PASS] #{idx:02d}: {desc}")
        else:
            failed_count += 1
            explanation = "ALLOWED (expected BLOCK)" if actual else "BLOCKED (expected ALLOW)"
            print(f"  [FAIL] #{idx:02d}: {desc} -> Got: {actual} | Expected: {expected} ({explanation})")
            failures.append({
                "index": idx,
                "desc": desc,
                "job": job,
                "keyword": keyword,
                "settings": settings,
                "got": actual,
                "expected": expected
            })

    total = len(test_cases)
    pass_rate = (passed_count / total * 100) if total > 0 else 0
    print("-" * 70)
    print(f"  Summary for {suite_name}: {passed_count}/{total} Passed ({pass_rate:.1f}%) | {failed_count} Failed")
    
    return passed_count, failed_count, failures


def main():
    print("======================================================================")
    print("       POST-REMEDIATION EMPIRICAL TEST HARNESS (final_challenger.py)   ")
    print("======================================================================")

    # Default settings template
    base_settings = {
        "level": "Todos",
        "location": "Brasil (Remoto)",
        "contract": "Todos",
        "education": "Todos",
        "platforms": {},
        "ai_filter": False
    }

    # -------------------------------------------------------------------------
    # SUITE 1: user_level = 'ganhar experiência' Target Terms & Higher Terms Blocklist
    # -------------------------------------------------------------------------
    exp_settings = {**base_settings, "level": "ganhar experiência"}

    suite1_cases = [
        # (Job, Keyword, Settings, Expected, Description)
        # --- Target Terms (Should PASS) ---
        (
            {"title": "Dev Voluntário em ONG", "requirements": "Desenvolvimento de software voluntário para causa social.", "platform": "linkedin", "location": "Remoto"},
            "Dev", exp_settings, True,
            "Target term 'voluntario' + 'ong' -> PASS (Global title blacklist exempted)"
        ),
        (
            {"title": "Dev - Estágio Inicial Sem Experiência", "requirements": "Vaga para aprender desenvolvimento sem exigir experiência prévia.", "platform": "linkedin", "location": "Remoto"},
            "Dev", exp_settings, True,
            "Target term 'estagio inicial' + 'sem experiencia' -> PASS"
        ),
        (
            {"title": "Dev - Projeto Open Source para Iniciantes", "requirements": "Contribuição para código aberto e auxílio a novos desenvolvedores.", "platform": "linkedin", "location": "Remoto"},
            "Dev", exp_settings, True,
            "Target term 'open source' + 'codigo aberto' -> PASS"
        ),
        (
            {"title": "Desenvolvedor Sem Experiência", "requirements": "Primeiro emprego para quem não exige experiência prévia.", "platform": "linkedin", "location": "Remoto"},
            "Desenvolvedor", exp_settings, True,
            "Target term 'sem experiencia' + 'primeiro emprego' -> PASS"
        ),
        (
            {"title": "Desenvolvedor Voluntary Project", "requirements": "Open source voluntary project for beginners and learners.", "platform": "linkedin", "location": "Remoto"},
            "Desenvolvedor", exp_settings, True,
            "Target term 'voluntary' + 'open source' -> PASS"
        ),
        (
            {"title": "Dev Voluntariado em TI", "requirements": "Trabalho de voluntariado em desenvolvimento de software.", "platform": "linkedin", "location": "Remoto"},
            "Dev", exp_settings, True,
            "Target term 'voluntariado' -> PASS"
        ),
        (
            {"title": "Desenvolvedor - Projeto Social", "requirements": "Projeto social de inclusão digital.", "platform": "linkedin", "location": "Remoto"},
            "Desenvolvedor", exp_settings, True,
            "Target term 'projeto social' -> PASS"
        ),

        # --- Higher Terms Blocklist (Should FAIL / BLOCK) ---
        (
            {"title": "Dev Júnior 1 ano de experiência", "requirements": "Buscamos desenvolvedor júnior voluntário.", "platform": "linkedin", "location": "Remoto"},
            "Dev", exp_settings, False,
            "Blocked by higher term 'júnior' in title"
        ),
        (
            {"title": "Dev Jr Voluntário", "requirements": "Projeto de voluntariado para dev jr.", "platform": "linkedin", "location": "Remoto"},
            "Dev", exp_settings, False,
            "Blocked by higher term 'jr' in title"
        ),
        (
            {"title": "Dev Pleno", "requirements": "Desenvolvedor voluntário pleno.", "platform": "linkedin", "location": "Remoto"},
            "Dev", exp_settings, False,
            "Blocked by higher term 'pleno' in title"
        ),
        (
            {"title": "Dev Sênior", "requirements": "Desenvolvedor voluntário sênior com liderança.", "platform": "linkedin", "location": "Remoto"},
            "Dev", exp_settings, False,
            "Blocked by higher term 'sênior' in title"
        ),
        (
            {"title": "Dev Voluntário Pleno", "requirements": "Projeto voluntário para profissional nível pleno.", "platform": "linkedin", "location": "Remoto"},
            "Dev", exp_settings, False,
            "Target term present but blocked by higher term 'pleno'"
        ),
        (
            {"title": "Dev Voluntário Sr", "requirements": "Projeto voluntário para engenheiro sr.", "platform": "linkedin", "location": "Remoto"},
            "Dev", exp_settings, False,
            "Target term present but blocked by higher term 'sr'"
        ),

        # --- Lack of Target Terms (Should FAIL / BLOCK) ---
        (
            {"title": "Dev Python", "requirements": "Desenvolvimento de APIs com FastAPI e Python backend.", "platform": "linkedin", "location": "Remoto"},
            "Dev", exp_settings, False,
            "Generic job without target experience terms -> BLOCK"
        ),
        (
            {"title": "Professor Voluntário em ONG", "requirements": "Aulas voluntárias de informática.", "platform": "linkedin", "location": "Remoto"},
            "Dev", exp_settings, False,
            "Blocked by global title blacklist term 'professor'"
        ),
    ]

    # -------------------------------------------------------------------------
    # SUITE 2: All Other Seniority Levels ("Todos", "Júnior", "Pleno", "Sênior", "Jovem Aprendiz")
    # -------------------------------------------------------------------------
    suite2_cases = [
        # --- Nível: "Todos" ---
        (
            {"title": "Desenvolvedor Python Júnior", "requirements": "Python, Django backend.", "platform": "linkedin", "location": "Remoto"},
            "Desenvolvedor Python", {**base_settings, "level": "Todos"}, True,
            "Level 'Todos': Junior job -> PASS"
        ),
        (
            {"title": "Desenvolvedor Python Pleno", "requirements": "Python, FastAPI, microsserviços.", "platform": "linkedin", "location": "Remoto"},
            "Desenvolvedor Python", {**base_settings, "level": "Todos"}, True,
            "Level 'Todos': Pleno job -> PASS"
        ),
        (
            {"title": "Desenvolvedor Python Sênior", "requirements": "Arquitetura Python, liderança.", "platform": "linkedin", "location": "Remoto"},
            "Desenvolvedor Python", {**base_settings, "level": "Todos"}, True,
            "Level 'Todos': Senior job -> PASS"
        ),

        # --- Nível: "Júnior" ---
        (
            {"title": "Desenvolvedor Python Júnior", "requirements": "Conhecimento básico de Python e SQL.", "platform": "linkedin", "location": "Remoto"},
            "Desenvolvedor Python", {**base_settings, "level": "Júnior"}, True,
            "Level 'Júnior': Junior title -> PASS"
        ),
        (
            {"title": "Junior Python Developer", "requirements": "Entry level Python backend.", "platform": "linkedin", "location": "Remoto"},
            "Desenvolvedor Python", {**base_settings, "level": "Júnior"}, True,
            "Level 'Júnior': English Junior title -> PASS"
        ),
        (
            {"title": "Estagiário de Programação", "requirements": "Estágio em desenvolvimento de software Python.", "platform": "linkedin", "location": "Remoto"},
            "Estagiário de TI / Programação", {**base_settings, "level": "Júnior"}, True,
            "Level 'Júnior': Estagiário title -> PASS"
        ),
        (
            {"title": "Desenvolvedor Júnior", "requirements": "Desenvolvimento Python com Django. Você será mentorado por um engenheiro sênior.", "platform": "linkedin", "location": "Remoto"},
            "Desenvolvedor Python", {**base_settings, "level": "Júnior"}, True,
            "Level 'Júnior': Junior title with casual senior mention in reqs -> PASS"
        ),
        (
            {"title": "Desenvolvedor Python Pleno", "requirements": "Python backend pleno.", "platform": "linkedin", "location": "Remoto"},
            "Desenvolvedor Python", {**base_settings, "level": "Júnior"}, False,
            "Level 'Júnior': Pleno in title -> BLOCK"
        ),
        (
            {"title": "Senior Python Developer", "requirements": "Python backend sênior.", "platform": "linkedin", "location": "Remoto"},
            "Desenvolvedor Python", {**base_settings, "level": "Júnior"}, False,
            "Level 'Júnior': Senior in title -> BLOCK"
        ),
        (
            {"title": "Desenvolvedor", "requirements": "Buscamos profissional com nível experiência sênior.", "platform": "linkedin", "location": "Remoto"},
            "Desenvolvedor Python", {**base_settings, "level": "Júnior"}, False,
            "Level 'Júnior': Generic title, explicit sênior requirement in desc -> BLOCK"
        ),

        # --- Nível: "Pleno" ---
        (
            {"title": "Desenvolvedor Python Pleno", "requirements": "Experiência com Python, FastAPI e Docker.", "platform": "linkedin", "location": "Remoto"},
            "Desenvolvedor Python", {**base_settings, "level": "Pleno"}, True,
            "Level 'Pleno': Pleno title -> PASS"
        ),
        (
            {"title": "Analista de Dados Pleno", "requirements": "SQL, Python, Power BI nível pleno.", "platform": "linkedin", "location": "Remoto"},
            "Analista de Dados", {**base_settings, "level": "Pleno"}, True,
            "Level 'Pleno': Analista de dados pleno -> PASS"
        ),
        (
            {"title": "Desenvolvedor Python Júnior", "requirements": "Python para iniciantes.", "platform": "linkedin", "location": "Remoto"},
            "Desenvolvedor Python", {**base_settings, "level": "Pleno"}, False,
            "Level 'Pleno': Junior in title -> BLOCK"
        ),
        (
            {"title": "Desenvolvedor Python Sênior", "requirements": "Arquitetura e liderança sênior.", "platform": "linkedin", "location": "Remoto"},
            "Desenvolvedor Python", {**base_settings, "level": "Pleno"}, False,
            "Level 'Pleno': Senior in title -> BLOCK"
        ),

        # --- Nível: "Sênior" ---
        (
            {"title": "Desenvolvedor Python Sênior", "requirements": "Liderança técnica e arquitetura de microsserviços.", "platform": "linkedin", "location": "Remoto"},
            "Desenvolvedor Python", {**base_settings, "level": "Sênior"}, True,
            "Level 'Sênior': Senior title -> PASS"
        ),
        (
            {"title": "Senior Python Engineer", "requirements": "Senior backend development.", "platform": "linkedin", "location": "Remoto"},
            "Desenvolvedor Python", {**base_settings, "level": "Sênior"}, True,
            "Level 'Sênior': English Senior title -> PASS"
        ),
        (
            {"title": "Desenvolvedor Python Júnior", "requirements": "Vaga júnior.", "platform": "linkedin", "location": "Remoto"},
            "Desenvolvedor Python", {**base_settings, "level": "Sênior"}, False,
            "Level 'Sênior': Junior in title -> BLOCK"
        ),
        (
            {"title": "Desenvolvedor Python Pleno", "requirements": "Vaga pleno.", "platform": "linkedin", "location": "Remoto"},
            "Desenvolvedor Python", {**base_settings, "level": "Sênior"}, False,
            "Level 'Sênior': Pleno in title -> BLOCK"
        ),

        # --- Nível: "Jovem Aprendiz" ---
        (
            {"title": "Jovem Aprendiz em TI", "requirements": "Suporte e apoio em tarefas de informática e escritório.", "platform": "linkedin", "location": "Remoto"},
            "Suporte Técnico N1", {**base_settings, "level": "Jovem Aprendiz"}, True,
            "Level 'Jovem Aprendiz': Title has 'Jovem Aprendiz' -> PASS"
        ),
        (
            {"title": "Auxiliar de Escritório (Menor Aprendiz)", "requirements": "Atendimento e rotinas de escritório.", "platform": "linkedin", "location": "Remoto"},
            "Assistente Administrativo", {**base_settings, "level": "Jovem Aprendiz"}, True,
            "Level 'Jovem Aprendiz': Reqs has 'Menor Aprendiz' -> PASS"
        ),
        (
            {"title": "Desenvolvedor Python Júnior", "requirements": "Desenvolvimento Python com Django.", "platform": "linkedin", "location": "Remoto"},
            "Desenvolvedor Python", {**base_settings, "level": "Jovem Aprendiz"}, False,
            "Level 'Jovem Aprendiz': Missing aprendiz keyword -> BLOCK"
        ),
    ]

    # -------------------------------------------------------------------------
    # SUITE 3: Motor Rule Matching & Co-Occurrence & Blacklists
    # -------------------------------------------------------------------------
    suite3_cases = [
        # --- True Positives (Domain Relevant IT Roles) ---
        (
            {"title": "Desenvolvedor Python Backend", "requirements": "Precisa saber Django e FastAPI.", "platform": "linkedin", "location": "Remoto"},
            "Desenvolvedor Python", base_settings, True,
            "VP: Dev Python Backend com Django e FastAPI -> PASS"
        ),
        (
            {"title": "Analista de Dados Python", "requirements": "SQL, pandas, python, engenharia de dados.", "platform": "linkedin", "location": "Remoto"},
            "Analista de Dados", base_settings, True,
            "VP: Analista de Dados Python -> PASS"
        ),
        (
            {"title": "Especialista em IA Generativa", "requirements": "Experiência com Midjourney, ChatGPT, geração de conteúdo com LLM.", "platform": "linkedin", "location": "Remoto"},
            "Especialista em IA Generativa", base_settings, True,
            "VP: Especialista em IA Generativa com ChatGPT/LLM -> PASS"
        ),
        (
            {"title": "Desenvolvedor React Frontend", "requirements": "Vaga para desenvolvedor react, nextjs, typescript.", "platform": "linkedin", "location": "Remoto"},
            "Desenvolvedor React", base_settings, True,
            "VP: Dev React Frontend -> PASS"
        ),
        (
            {"title": "Desenvolvedor RPA Automação", "requirements": "UiPath, Power Automate, automação de processos, developer.", "platform": "linkedin", "location": "Remoto"},
            "Desenvolvedor RPA", base_settings, True,
            "VP: Desenvolvedor RPA -> PASS"
        ),
        (
            {"title": "Analista de Power BI", "requirements": "Criação de dashboards em Power BI, DAX e SQL.", "platform": "linkedin", "location": "Remoto"},
            "Analista de Power BI", base_settings, True,
            "VP: Analista de Power BI -> PASS"
        ),
        (
            {"title": "Auxiliar Administrativo", "requirements": "Rotinas de escritório, atendimento e planilhas adm.", "platform": "catho", "location": "Remoto"},
            "Assistente Administrativo", base_settings, True,
            "VP: Auxiliar Administrativo -> PASS"
        ),
        (
            {"title": "Gestor de Tráfego Pago", "requirements": "Gestão de Meta Ads, Google Ads e performance.", "platform": "linkedin", "location": "Remoto"},
            "Gestor de Tráfego", base_settings, True,
            "VP: Gestor de Tráfego Pago -> PASS"
        ),

        # --- False Positives (Must be BLOCKED by motor rules/blacklists) ---
        (
            {"title": "Enfermeira com conhecimento em TI", "requirements": "Buscamos enfermeira que saiba python para análises de saúde.", "platform": "linkedin", "location": "Remoto"},
            "Desenvolvedor Python", base_settings, False,
            "FP: Enfermeira com python -> BLOCK"
        ),
        (
            {"title": "Médico Veterinário Autônomo", "requirements": "Clínica veterinária, atendimento, python para controle de estoque.", "platform": "linkedin", "location": "Remoto"},
            "Desenvolvedor Python", base_settings, False,
            "FP: Médico Veterinário com python -> BLOCK"
        ),
        (
            {"title": "Motorista de Aplicativo Python", "requirements": "Motorista parceiro, CNH categoria B, conhecimento básico em python.", "platform": "linkedin", "location": "Remoto"},
            "Desenvolvedor Python", base_settings, False,
            "FP: Motorista com python -> BLOCK"
        ),
        (
            {"title": "Atendente de Lanchonete IA", "requirements": "Funcionário para atendimento ao balcão, IA é nossa empresa.", "platform": "linkedin", "location": "Remoto"},
            "Especialista em IA", base_settings, False,
            "FP: Atendente onde 'IA' é nome da empresa -> BLOCK"
        ),
        (
            {"title": "Costureira para Confecção", "requirements": "Máquina de costura, ia para agulha.", "platform": "linkedin", "location": "Remoto"},
            "Especialista em IA Generativa", base_settings, False,
            "FP: Costureira sem IA generativa -> BLOCK"
        ),
        (
            {"title": "Balconista de Farmácia React", "requirements": "Atendimento ao cliente, caixa registradora, sistema chama React.", "platform": "linkedin", "location": "Remoto"},
            "Desenvolvedor React", base_settings, False,
            "FP: Balconista onde 'React' é nome do sistema -> BLOCK"
        ),
        (
            {"title": "Repositor de Estoque com PowerBI", "requirements": "Repositor para supermercado, organização de gôndolas, relatórios em Power BI.", "platform": "linkedin", "location": "Remoto"},
            "Analista de Power BI", base_settings, False,
            "FP: Repositor com Power BI -> BLOCK"
        ),
        (
            {"title": "Recepcionista Machine Learning Center", "requirements": "Atendimento presencial na recepção do Machine Learning Center.", "platform": "linkedin", "location": "Remoto"},
            "Machine Learning Engineer", base_settings, False,
            "FP: Recepcionista em empresa ML -> BLOCK"
        ),
        (
            {"title": "Professor de Python", "requirements": "Aulas de python para iniciantes.", "platform": "linkedin", "location": "Remoto"},
            "Desenvolvedor Python", base_settings, False,
            "FP: Professor de Python -> BLOCK (Global title blacklist)"
        ),
        (
            {"title": "Auxiliar de Limpeza RPA Clean", "requirements": "Limpeza de ambientes, empresa chamada RPA Clean.", "platform": "linkedin", "location": "Remoto"},
            "Desenvolvedor RPA", base_settings, False,
            "FP: Auxiliar de limpeza da empresa RPA Clean -> BLOCK"
        ),
        (
            {"title": "Gestor de Tráfego Aéreo", "requirements": "Controle de tráfego aéreo e aeronaves.", "platform": "linkedin", "location": "Remoto"},
            "Gestor de Tráfego", base_settings, False,
            "FP: Gestor de tráfego aéreo -> BLOCK (Local blacklist 'aereo')"
        ),
        (
            {"title": "Faxineiro", "requirements": "Limpeza geral de escritórios.", "platform": "catho", "location": "Remoto"},
            "Assistente Administrativo", base_settings, False,
            "FP: Faxineiro -> BLOCK (Global title blacklist)"
        ),

        # --- Contract & Location Boundary Checks ---
        (
            {"title": "Desenvolvedor Python PJ", "requirements": "Vaga exclusiva para contratação PJ.", "platform": "linkedin", "location": "Remoto"},
            "Desenvolvedor Python", {**base_settings, "contract": "clt"}, False,
            "Contract mismatch: PJ job for candidate requiring CLT -> BLOCK"
        ),
        (
            {"title": "Desenvolvedor Python PJ", "requirements": "Vaga PJ sem CLT.", "platform": "linkedin", "location": "Remoto"},
            "Desenvolvedor Python", {**base_settings, "contract": "pj"}, True,
            "Contract match: PJ job for PJ candidate -> PASS"
        ),
        (
            {"title": "Desenvolvedor Python Presencial em SP", "requirements": "Trabalho 100% presencial em escritório de SP.", "platform": "catho", "location": "São Paulo"},
            "Desenvolvedor Python", {**base_settings, "location": "Brasil (Remoto)"}, False,
            "Location mismatch: Presential SP job for remote candidate -> BLOCK"
        ),
        (
            {"title": "Desenvolvedor Python Remoto", "requirements": "Trabalho 100% home office.", "platform": "remotar", "location": "Remoto"},
            "Desenvolvedor Python", {**base_settings, "location": "Brasil (Remoto)"}, True,
            "Location match: Remote job for remote candidate -> PASS"
        ),
    ]

    # -------------------------------------------------------------------------
    # Execute All Test Suites
    # -------------------------------------------------------------------------
    p1, f1, fail1 = run_suite("Suite 1: 'Ganhar Experiência' Level & Target/Higher Terms", suite1_cases)
    p2, f2, fail2 = run_suite("Suite 2: All Other Seniority Levels (Todos, Júnior, Pleno, Sênior, Jovem Aprendiz)", suite2_cases)
    p3, f3, fail3 = run_suite("Suite 3: Motor Rule Matching & Co-Occurrence & Blacklists", suite3_cases)

    total_passed = p1 + p2 + p3
    total_failed = f1 + f2 + f3
    total_tests = len(suite1_cases) + len(suite2_cases) + len(suite3_cases)
    overall_pass_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0

    print("\n" + "=" * 70)
    print("                      FINAL HARNESS SUMMARY                       ")
    print("=" * 70)
    print(f"  Total Evaluations Run : {total_tests}")
    print(f"  Total Passed          : {total_passed} ({overall_pass_rate:.2f}%)")
    print(f"  Total Failed          : {total_failed}")
    print(f"  Regressions Detected  : {total_failed}")
    print("=" * 70)

    if total_failed == 0:
        print("\n🎉 ALL TEST EVALUATIONS PASSED SUCCESSFULLY! 0 REGRESSIONS DETECTED.")
        print("Exit code: 0")
        sys.exit(0)
    else:
        print(f"\n❌ TEST HARNESS FAILED WITH {total_failed} FAILURE(S)/REGRESSION(S):")
        all_failures = fail1 + fail2 + fail3
        for item in all_failures:
            print(f"   -> #{item['index']}: {item['desc']} | Got {item['got']}, Expected {item['expected']}")
        print("\nExit code: 1")
        sys.exit(1)

if __name__ == '__main__':
    main()
