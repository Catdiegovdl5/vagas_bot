import sys
import os

print("=== STARTING M3_2 DETAILED VERIFICATION SCRIPT ===")

from bot import (
    SEARCH_MAPPING, 
    CO_OCCURRENCE_RULES, 
    global_title_blacklist, 
    classify_job_profession, 
    is_job_relevant, 
    check_co_occurrence
)

# 1. SEARCH_MAPPING Macro Keywords
print("\n--- 1. Testing SEARCH_MAPPING Macro Keywords ---")
macro_keys = ["Indústria", "Logística", "Administrativo", "Vendas", "Design", "Engenharia de Dados"]
for key in macro_keys:
    mapped = SEARCH_MAPPING.get(key)
    print(f"  '{key}' -> '{mapped}'")
    assert mapped is not None, f"Missing SEARCH_MAPPING for '{key}'"

print("  Checking optional 'Dados' macro key...")
dados_mapped = SEARCH_MAPPING.get("Dados")
print(f"  'Dados' -> '{dados_mapped}'")
if dados_mapped is None:
    print("  [NOTE] 'Dados' is not explicitly mapped in SEARCH_MAPPING; 'Engenharia de Dados' is used instead.")

# 2. Blue Collar Exemptions in global_title_blacklist
print("\n--- 2. Testing global_title_blacklist Blue Collar Exemptions ---")
blue_collar_roles = ["operador", "pintor", "ajudante", "mecanico", "motorista", "almoxarife"]
for role in blue_collar_roles:
    is_blacklisted = role in global_title_blacklist
    print(f"  '{role}' in global_title_blacklist: {is_blacklisted}")
    assert not is_blacklisted, f"Role '{role}' is wrongfully in global_title_blacklist!"

# 3. classify_job_profession logic
print("\n--- 3. Testing classify_job_profession Logic ---")
test_cases = [
    ({"title": "Pintor Industrial de Estrutura", "requirements": "Experiência em fábrica"}, "Pintor Industrial", "Operações Físicas"),
    ({"title": "Mecânico Industrial Sr", "requirements": "Manutenção preventiva em máquinas"}, "Mecânico Industrial", "Operações Físicas"),
    ({"title": "Operador de Produção I", "requirements": "Operação de linha de montagem"}, "Operador de Produção", "Operações Físicas"),
    ({"title": "Almoxarife Pleno", "requirements": "Recebimento e controle de estoque"}, "Almoxarife", "Logística"),
    ({"title": "Assistente de Logística", "requirements": "Rastreamento de frotas e fretes"}, "Assistente de Logística", "Logística"),
    ({"title": "Assistente Financeiro", "requirements": "Conciliação bancária e contas a pagar"}, "Assistente Financeiro", "Administrativo"),
    ({"title": "Assistente Administrativo", "requirements": "Suporte a escritório e recepção"}, "Assistente Administrativo", "Administrativo"),
    ({"title": "Editor de Vídeo", "requirements": "Premiere, After Effects, cortes"}, "Editor de Vídeo", "Criativos"),
    ({"title": "Executivo de Vendas B2B", "requirements": "Prospecção ativa e fechamento de contratos"}, "Executivo de Vendas", "Inteligência de Vendas"),
    ({"title": "Engenheiro de Dados", "requirements": "Pipelines ETL, PySpark, Airflow"}, "Engenheiro de Dados", "Engenharia de Dados"),
]

for job_dict, exp_prof, exp_cat in test_cases:
    classified = classify_job_profession(job_dict.copy())
    prof = classified.get("profession")
    cat = classified.get("category")
    print(f"  Title: '{job_dict['title']}' -> Profession: '{prof}' (Expected: '{exp_prof}'), Category: '{cat}' (Expected: '{exp_cat}')")
    assert prof == exp_prof, f"Expected profession '{exp_prof}', got '{prof}'"
    assert cat == exp_cat, f"Expected category '{exp_cat}', got '{cat}'"

# 4. CO_OCCURRENCE_RULES for macro keywords & sub-professions
print("\n--- 4. Testing CO_OCCURRENCE_RULES ---")
required_rules = [
    "operacoes fisicas", "industria", "logistica", "administrativo", 
    "criativos", "design", "inteligencia de vendas", "vendas", 
    "engenharia de dados", "pintor industrial", "mecanico industrial", 
    "almoxarife", "executivo de vendas"
]
for rule_key in required_rules:
    assert rule_key in CO_OCCURRENCE_RULES, f"Missing CO_OCCURRENCE_RULE for '{rule_key}'"
    groups = CO_OCCURRENCE_RULES[rule_key]
    assert len(groups) == 2, f"Rule '{rule_key}' does not have 2 co-occurrence groups"
    print(f"  Rule '{rule_key}': Group 1 size={len(groups[0])}, Group 2 size={len(groups[1])}")

# Test relevance filtering with co-occurrence
print("\n--- 5. Testing is_job_relevant with CO_OCCURRENCE_RULES ---")
settings = {"level": "Todos", "location": "Todos", "contract": "Todos"}

# Valid job for "Indústria": has industrial terms + production role
job_ind_valid = {"title": "Operador de Produção Industrial", "requirements": "Trabalho em linha de fábrica metalúrgica", "platform": "catho"}
rel_ind = is_job_relevant(job_ind_valid, "Indústria", settings)
print(f"  Job 'Operador de Produção Industrial' for 'Indústria': {rel_ind}")
assert rel_ind is True, "Valid industrial job was rejected by relevance filter!"

# Irrelevant job for "Indústria": generic sales job with no industrial context
job_ind_invalid = {"title": "Vendedor de Loja de Roupas", "requirements": "Atendimento no balcão do shopping", "platform": "catho"}
rel_ind_inv = is_job_relevant(job_ind_invalid, "Indústria", settings)
print(f"  Job 'Vendedor de Loja de Roupas' for 'Indústria': {rel_ind_inv}")
assert rel_ind_inv is False, "Irrelevant sales job was falsely accepted for 'Indústria'!"

# 6. app.py Seed and Periodic Loop Verification
print("\n--- 6. Testing app.py Seed and Periodic Hunt Integration ---")
import app
assert hasattr(app, 'run_initial_seed_search'), "app.py missing run_initial_seed_search!"
assert hasattr(app, 'background_periodic_hunt_loop'), "app.py missing background_periodic_hunt_loop!"

import inspect
assert inspect.iscoroutinefunction(app.run_initial_seed_search), "run_initial_seed_search must be async!"
assert inspect.iscoroutinefunction(app.background_periodic_hunt_loop), "background_periodic_hunt_loop must be async!"

# Check seed keywords in app.py
print("  Checking seed keywords and periodic hunt keywords in app.py...")
import re
with open("app.py", "r", encoding="utf-8") as f:
    app_src = f.read()

assert "run_initial_seed_search" in app_src, "run_initial_seed_search definition missing"
assert "background_periodic_hunt_loop" in app_src, "background_periodic_hunt_loop definition missing"
assert "Indústria" in app_src and "Logística" in app_src and "Administrativo" in app_src, "Macro keywords missing in app.py"

print("\n=== ALL M3_2 VERIFICATION TESTS PASSED SUCCESSFULLY ===")
