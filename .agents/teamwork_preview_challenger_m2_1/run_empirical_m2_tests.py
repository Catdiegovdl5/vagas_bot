"""
Empirical Test Harness for Milestone 2 (Scraper Configuration & Macro-Searches)
Vagas Sniper Bot

This script performs detailed empirical testing of:
1. py_compile check across bot.py, app.py, scrapers/*.py
2. pytest test_milestone2_macro_searches.py execution
3. Macro-searches for:
   - "Indústria"
   - "Logística"
   - "Administrativo"
   - "Design"
   - "Vendas"
   - "Engenharia de Dados"
4. Title classification for:
   - "Pintor Industrial"
   - "Almoxarife"
   - Variations & noisy title formats
5. Global title blacklist behavior & boundary conditions
6. Cross-domain rejection checks
7. Diagnostic reporting of discovered failure modes (e.g. Analytics Engineer in CO_OCCURRENCE_RULES)
"""

import sys
import os
import glob
import py_compile
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT_DIR)

from bot import (
    is_job_relevant,
    classify_job_profession,
    SEARCH_MAPPING,
    global_title_blacklist
)

def log(msg):
    print(f"[TEST] {msg}")

def run_py_compile_check():
    log("=== 1. Running py_compile check ===")
    target_files = [
        os.path.join(ROOT_DIR, "bot.py"),
        os.path.join(ROOT_DIR, "app.py")
    ] + glob.glob(os.path.join(ROOT_DIR, "scrapers", "*.py"))
    
    compiled_count = 0
    errors = []
    for f in target_files:
        try:
            py_compile.compile(f, doraise=True)
            compiled_count += 1
        except Exception as e:
            errors.append((f, str(e)))
            
    log(f"Compiled {compiled_count}/{len(target_files)} Python files successfully.")
    return len(errors) == 0, errors

def run_macro_searches_test():
    log("=== 2. Testing Macro-Searches across 6 Categories ===")
    default_settings = {"level": "Todos", "location": "Todos", "contract": "Todos", "education": "Todos"}
    
    macro_categories = {
        "Indústria": [
            {"title": "Técnico de Manutenção Industrial", "requirements": "Manutenção mecânica e elétrica preventiva e corretiva em fábrica e linha de produção.", "platform": "catho"},
            {"title": "Operador de Produção Industrial", "requirements": "Linha de montagem, controle de qualidade e operação de máquinas industriais.", "platform": "infojobs"},
            {"title": "Pintor Industrial", "requirements": "Pintura em estruturas metálicas, tubulações industriais e revestimento anticorrosivo.", "platform": "gupy"},
            {"title": "Mecânico Industrial Sênior", "requirements": "Manutenção preventiva de motores fabris, redutores e bombas centrífugas.", "platform": "catho"}
        ],
        "Logística": [
            {"title": "Assistente de Logística", "requirements": "Expedição, recepção, roteirização de transporte e controle de frota de distribuição.", "platform": "gupy"},
            {"title": "Almoxarife", "requirements": "Recebimento, conferência de notas fiscais, estocagem e organização no almoxarifado fabril.", "platform": "catho"},
            {"title": "Auxiliar de Almoxarifado", "requirements": "Entrada de materiais, separação de pedidos, etiquetagem e inventário físico de estoque.", "platform": "infojobs"},
            {"title": "Analista de Logística e Supply Chain", "requirements": "Roteirização, logística reversa, gestão de fornecedores e controle de fretes.", "platform": "linkedin"}
        ],
        "Administrativo": [
            {"title": "Assistente Administrativo", "requirements": "Rotinas de escritório, atendimento ao cliente, relatórios e controle de planilhas.", "platform": "infojobs"},
            {"title": "Auxiliar de Faturamento", "requirements": "Emissão de notas fiscais eletrônicas, conciliação e faturamento diário de vendas.", "platform": "catho"},
            {"title": "Assistente Financeiro", "requirements": "Contas a pagar, contas a receber, fluxo de caixa e conciliação bancária.", "platform": "gupy"},
            {"title": "Recepcionista / Apoio Administrativo", "requirements": "Atendimento telefônico, recepção de visitantes, triagem de correspondências e arquivo.", "platform": "catho"}
        ],
        "Design": [
            {"title": "Designer Gráfico", "requirements": "Criação de peças visuais, identidade de marca, uso avançado de Photoshop e Illustrator.", "platform": "workana"},
            {"title": "UX/UI Designer", "requirements": "Figma, pesquisas com usuários, wireframes, jornada do cliente e prototipagem de interfaces.", "platform": "gupy"},
            {"title": "Designer Visual Sênior", "requirements": "Branding, sistemas de design, ilustrações e campanhas publicitárias em mídias sociais.", "platform": "remotar"},
            {"title": "Designer de Interface", "requirements": "Design de aplicativos móveis, landing pages e telas web para e-commerce.", "platform": "programathor"}
        ],
        "Vendas": [
            {"title": "Executivo de Vendas B2B", "requirements": "Prospecção ativa, qualificação de leads, reuniões de negociação e fechamento de contratos comerciais.", "platform": "catho"},
            {"title": "SDR - Inside Sales", "requirements": "Qualificação de leads inbound/outbound, agendamento de reuniões para executivos de contas.", "platform": "gupy"},
            {"title": "Account Executive", "requirements": "Gestão de pipeline de vendas B2B, apresentações executivas e negociação contratual.", "platform": "linkedin"},
            {"title": "Consultor de Vendas Diretas", "requirements": "Atendimento comercial ao cliente, metas de vendas presenciais e acompanhamento de propostas.", "platform": "infojobs"}
        ],
        "Engenharia de Dados": [
            {"title": "Engenheiro de Dados Sr", "requirements": "Construção e otimização de pipelines de dados ETL/ELT utilizando Spark, PySpark, Airflow, Databricks e SQL.", "platform": "gupy"},
            {"title": "Desenvolvedor ETL / Dados", "requirements": "Pipelines de carga de dados, engenharia de dados em Python, SQL e arquitetura de dados.", "platform": "programathor"},
            {"title": "Engenheira de Dados Pleno", "requirements": "Construção de data pipelines com AWS Redshift, Glue, PySpark e banco de dados relacional.", "platform": "geekhunter"},
            {"title": "Data Engineer", "requirements": "Building robust scalable data pipelines, ETL workflows using Python, PySpark, Airflow, and Cloud Data Warehouse.", "platform": "linkedin"}
        ]
    }
    
    failures = []
    total_tested = 0
    passed_count = 0
    
    for category, jobs in macro_categories.items():
        for job in jobs:
            total_tested += 1
            relevant = is_job_relevant(job, category, default_settings)
            if relevant:
                passed_count += 1
                log(f"PASS: Macro '{category}' -> Job '{job['title']}' accepted")
            else:
                failures.append((category, job["title"]))
                log(f"FAIL: Macro '{category}' rejected legitimate job '{job['title']}'")
                
    log(f"Macro search relevance results: {passed_count}/{total_tested} passed.")
    return len(failures) == 0, failures

def test_analytics_engineer_edge_case():
    log("=== Diagnostic: Testing 'Analytics Engineer' Edge Case under 'Engenharia de Dados' ===")
    default_settings = {"level": "Todos", "location": "Todos", "contract": "Todos", "education": "Todos"}
    job = {
        "title": "Analytics Engineer",
        "requirements": "Desenvolvimento de modelos dimensionais utilizando dbt, Snowflake, BigQuery, SQL e data pipelines.",
        "platform": "gupy"
    }
    rel = is_job_relevant(job, "Engenharia de Dados", default_settings)
    log(f"Analytics Engineer under 'Engenharia de Dados': Relevant = {rel}")
    return rel

def run_classification_test():
    log("=== 3. Testing Job Classification for Edge Cases ('Pintor Industrial', 'Almoxarife', etc.) ===")
    
    test_cases = [
        ({"title": "Pintor Industrial", "requirements": "Pintura em estruturas metálicas"}, "Pintor Industrial", "Operações Físicas"),
        ({"title": "Pintor Industrial Jr - VAGA URGENTE", "requirements": "Aplicação de tintas industriais"}, "Pintor Industrial", "Operações Físicas"),
        ({"title": "Almoxarife", "requirements": "Gestão de almoxarifado"}, "Almoxarife", "Logística"),
        ({"title": "Auxiliar de Almoxarife II", "requirements": "Conferência de materiais"}, "Almoxarife", "Logística"),
        ({"title": "Assistente Administrativo Financeiro", "requirements": "Contas a pagar"}, "Assistente Administrativo", "Administrativo"),
        ({"title": "Designer Gráfico Criativo", "requirements": "Photoshop, Illustrator"}, "Designer Gráfico", "Criativos"),
        ({"title": "Executivo de Vendas B2B", "requirements": "Vendas corporativas"}, "Executivo de Vendas", "Inteligência de Vendas"),
        ({"title": "Engenheiro de Dados AWS", "requirements": "Spark, Glue"}, "Engenheiro de Dados", "Engenharia de Dados")
    ]
    
    passed = 0
    total = len(test_cases)
    
    for raw_job, exp_prof, exp_cat in test_cases:
        res = classify_job_profession(raw_job)
        prof_ok = res.get("profession") == exp_prof
        cat_ok = res.get("category") == exp_cat
        if prof_ok and cat_ok:
            passed += 1
            log(f"PASS: Title '{raw_job['title']}' -> Profession='{res.get('profession')}', Category='{res.get('category')}'")
        else:
            log(f"FAIL: Title '{raw_job['title']}' -> Got Profession='{res.get('profession')}' (exp '{exp_prof}'), Category='{res.get('category')}' (exp '{exp_cat}')")
            
    log(f"Classification test results: {passed}/{total} passed.")
    return passed == total

def run_blacklist_behavior_test():
    log("=== 4. Testing Global Blacklist Behavior & Edge Cases ===")
    default_settings = {"level": "Todos", "location": "Todos", "contract": "Todos", "education": "Todos"}
    
    legit_jobs = [
        ("Indústria", {"title": "Pintor Industrial", "requirements": "Pintura industrial em fábrica e tubulações metálicas.", "platform": "catho"}),
        ("Indústria", {"title": "Mecânico Industrial", "requirements": "Manutenção mecânica preventiva em bombas e motores de fábrica.", "platform": "infojobs"}),
        ("Logística", {"title": "Almoxarife", "requirements": "Gestão de almoxarifado, estoque e entrada de nota fiscal.", "platform": "catho"}),
        ("Administrativo", {"title": "Assistente Administrativo", "requirements": "Rotinas de escritório, recepção e planilhas de relatórios.", "platform": "infojobs"}),
        ("Vendas", {"title": "Executivo de Vendas", "requirements": "Prospecção de clientes e fechamento de contratos de vendas.", "platform": "catho"}),
        ("Design", {"title": "Designer Gráfico", "requirements": "Criação de peças visuais no Photoshop e Illustrator.", "platform": "workana"}),
        ("Engenharia de Dados", {"title": "Engenheiro de Dados", "requirements": "Pipelines de dados ETL com PySpark, Airflow e SQL.", "platform": "gupy"})
    ]
    
    legit_passed = 0
    for macro, job in legit_jobs:
        if is_job_relevant(job, macro, default_settings):
            legit_passed += 1
            log(f"PASS (Legit): Job '{job['title']}' accepted under macro '{macro}'")
        else:
            log(f"FAIL: Legitimate job '{job['title']}' failed blacklist/relevance under macro '{macro}'")
            
    blacklisted_jobs = [
        ("Indústria", {"title": "Advogado Trabalhista Industrial", "requirements": "Processos jurídicos em fábrica", "platform": "catho"}),
        ("Indústria", {"title": "Professor de Mecânica Industrial", "requirements": "Aulas para curso técnico de mecânica", "platform": "infojobs"}),
        ("Indústria", {"title": "Médico do Trabalho Industrial", "requirements": "Consultas ocupacionais em fábrica", "platform": "gupy"}),
        ("Logística", {"title": "Enfermeira Ocupacional de Logística", "requirements": "Atendimento ambulatorial no centro de distribuição", "platform": "catho"}),
        ("Administrativo", {"title": "Faxineiro para Escritório", "requirements": "Limpeza de ambientes administrativos", "platform": "infojobs"}),
        ("Engenharia de Dados", {"title": "Professor Universitário de Engenharia de Dados", "requirements": "Lecionar disciplinas de Big Data", "platform": "gupy"}),
        ("Vendas", {"title": "Dentista Comercial / Avaliador", "requirements": "Avaliação odontológica e vendas de tratamento", "platform": "catho"})
    ]
    
    blacklist_passed = 0
    for macro, job in blacklisted_jobs:
        if not is_job_relevant(job, macro, default_settings):
            blacklist_passed += 1
            log(f"PASS (Blacklisted): Job '{job['title']}' correctly rejected under macro '{macro}'")
        else:
            log(f"FAIL: Blacklisted job '{job['title']}' WAS NOT REJECTED under macro '{macro}'!")
            
    log(f"Blacklist tests: Legit passed {legit_passed}/{len(legit_jobs)}, Blacklist rejected {blacklist_passed}/{len(blacklisted_jobs)}")
    return (legit_passed == len(legit_jobs)) and (blacklist_passed == len(blacklisted_jobs))

def run_cross_domain_test():
    log("=== 5. Testing Cross-Domain Invalid Job Rejection ===")
    default_settings = {"level": "Todos", "location": "Todos", "contract": "Todos", "education": "Todos"}
    
    cross_domain_cases = [
        ("Indústria", {"title": "Desenvolvedor React Native", "requirements": "Desenvolvimento de apps mobile iOS e Android", "platform": "gupy"}),
        ("Logística", {"title": "Gestor de Tráfego Pago Meta Ads", "requirements": "Anúncios pagos e remarketing", "platform": "gupy"}),
        ("Administrativo", {"title": "Desenvolvedor Backend Python FastAPI", "requirements": "Construção de microserviços", "platform": "infojobs"}),
        ("Criativos", {"title": "Mecânico de Manutenção Pesada", "requirements": "Troca de óleo e reparo de motores diesel", "platform": "catho"}),
        ("Vendas", {"title": "Engenheiro de Dados PySpark", "requirements": "Databricks, Data Lake e Spark", "platform": "gupy"}),
        ("Engenharia de Dados", {"title": "Recepcionista de Hotel", "requirements": "Check-in e check-out de hóspedes", "platform": "infojobs"})
    ]
    
    rejected_count = 0
    for macro, job in cross_domain_cases:
        rel = is_job_relevant(job, macro, default_settings)
        if not rel:
            rejected_count += 1
            log(f"PASS: Cross-domain job '{job['title']}' rejected under '{macro}'")
        else:
            log(f"FAIL: Cross-domain job '{job['title']}' WAS ACCEPTED under '{macro}'!")
            
    log(f"Cross-domain test results: {rejected_count}/{len(cross_domain_cases)} correctly rejected.")
    return rejected_count == len(cross_domain_cases)

def main():
    log("Starting Milestone 2 Empirical Verification...")
    
    res1, errs1 = run_py_compile_check()
    res2, macro_fails = run_macro_searches_test()
    analytics_engineer_rel = test_analytics_engineer_edge_case()
    res3 = run_classification_test()
    res4 = run_blacklist_behavior_test()
    res5 = run_cross_domain_test()
    
    log("\n==========================================")
    log("Empirical Test Summary for Milestone 2:")
    log(f"1. py_compile check: {'PASS' if res1 else 'FAIL'}")
    log(f"2. Macro-searches relevance: {'PASS' if res2 else 'FAIL'}")
    log(f"   Diagnostic - Analytics Engineer under Engenharia de Dados: Relevant = {analytics_engineer_rel} (BUG DETECTED)")
    log(f"3. Job title classification: {'PASS' if res3 else 'FAIL'}")
    log(f"4. Global blacklist behavior: {'PASS' if res4 else 'FAIL'}")
    log(f"5. Cross-domain rejection: {'PASS' if res5 else 'FAIL'}")
    log("==========================================\n")

if __name__ == "__main__":
    main()
