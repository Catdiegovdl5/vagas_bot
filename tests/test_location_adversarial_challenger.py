"""
test_location_adversarial_challenger.py - Comprehensive Adversarial Stress Test Suite
Empirical verification of R1 & R2 fixes, state search edge cases, accents, word boundaries,
preposition collisions, cross-state collisions, and frontend artifacts.
"""
import sys
import os
import re

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

from bot import is_job_relevant, normalize_str

passed_tests = 0
failed_tests = 0
errors = []
findings = []

def assert_check(test_name, category, result, expected, context=""):
    global passed_tests, failed_tests
    if result == expected:
        passed_tests += 1
        print(f"  [PASSOU] [{category}] {test_name}")
    else:
        failed_tests += 1
        msg = f"[{category}] {test_name}: obtido={result}, esperado={expected}. Context: {context}"
        print(f"  [FALHOU] {msg}")
        errors.append(msg)

def make_job(title, reqs, loc="", platform="gupy"):
    return {
        "title": title,
        "requirements": reqs,
        "location": loc,
        "platform": platform
    }

def make_settings(location="Todos", level="Todos", contract="Todos"):
    return {
        "location": location,
        "level": level,
        "contract": contract
    }

print("\n========================================================")
print(" ADVERSARIAL STRESS SUITE: LOCATION & UF SEARCH")
print("========================================================\n")

# -------------------------------------------------------------------
# CATEGORY 1: ACCENTS & DIACRITICS NORMALIZATION IN STATE NAMES & CITIES
# -------------------------------------------------------------------
print("--- 1. Accents & Diacritics Normalization ---")

accent_cases = [
    ("São Paulo", "São Paulo - SP", "Desenvolvedor Backend em São Paulo", True),
    ("sao paulo", "São Paulo - SP", "Desenvolvedor Backend em São Paulo", True),
    ("SãO PaULo", "sao paulo - sp", "Desenvolvedor Backend em sao paulo", True),
    ("SP", "São Paulo", "Vaga presencial na capital", True),
    ("Ceará", "Fortaleza - CE", "Vaga presencial no Ceará", True),
    ("ceara", "Fortaleza - CE", "Vaga presencial no Ceara", True),
    ("Amapá", "Macapá - AP", "Vaga presencial no Amapá", True),
    ("amapa", "Macapá - AP", "Vaga presencial no Amapa", True),
    ("Paraná", "Curitiba - PR", "Vaga presencial no Paraná", True),
    ("parana", "Curitiba - PR", "Vaga presencial no Parana", True),
    ("Espírito Santo", "Vitória - ES", "Vaga presencial no Espírito Santo", True),
    ("espirito santo", "Vitória - ES", "Vaga presencial no Espirito Santo", True),
    ("Maranhão", "São Luís - MA", "Vaga presencial no Maranhão", True),
    ("maranhao", "São Luís - MA", "Vaga presencial no Maranhao", True),
    ("Piauí", "Teresina - PI", "Vaga presencial no Piauí", True),
    ("piaui", "Teresina - PI", "Vaga presencial no Piaui", True),
    ("Rondônia", "Porto Velho - RO", "Vaga presencial em Rondônia", True),
    ("rondonia", "Porto Velho - RO", "Vaga presencial em Rondonia", True),
    ("Goiás", "Goiânia - GO", "Vaga presencial em Goiás", True),
    ("goias", "Goiânia - GO", "Vaga presencial em Goias", True),
    ("Pará", "Belém - PA", "Vaga presencial em Belém Pará", True),
    ("para", "Belém - PA", "Vaga presencial no estado do Para", True),
]

for s_filter, j_loc, j_req, exp in accent_cases:
    job = make_job("Engenheiro de Software", j_req, j_loc)
    res = is_job_relevant(job, "Engenheiro de Software", make_settings(location=s_filter))
    assert_check(f"Filtro '{s_filter}' x Loc '{j_loc}'", "Accents", res, exp, f"Reqs: {j_req}")


# -------------------------------------------------------------------
# CATEGORY 2: ANTI-FALSE-POSITIVO WORD BOUNDARY STRESS TEST FOR ALL 27 UFS
# -------------------------------------------------------------------
print("\n--- 2. Anti-False-Positivo Substring & Word Boundary ---")

word_boundary_negative_tests = [
    ("ac", "Engenheiro de Software ACesso a banco de dados em Vitoria ES", "Vitória - ES"),
    ("al", "Engenheiro ALto nivel de conhecimento presencial em Sao Paulo", "São Paulo - SP"),
    ("am", "Analista AMbiente de producao em Belo Horizonte MG", "Belo Horizonte - MG"),
    ("ap", "Dev APlicacao mobile presencial em Curitiba PR", "Curitiba - PR"),
    ("ba", "Dev BAckend Python presencial em Florianopolis SC", "Florianópolis - SC"),
    ("ce", "Vaga CEntro de inovacao presencial em Porto Alegre RS", "Porto Alegre - RS"),
    ("df", "Engenheiro geracao de pDFs presencial no Rio de Janeiro", "Rio de Janeiro - RJ"),
    ("es", "ESpecialista em marketing presencial em Sao Paulo SP", "São Paulo - SP"),
    ("go", "Dev GOol ou Golang presencial em Salvador BA", "Salvador - BA"),
    ("ma", "Analista MAssivo de dados presencial em Recife PE", "Recife - PE"),
    ("mg", "Engenheiro MGram sistemas presencial em Belem PA", "Belém - PA"),
    ("ms", "Desenvolvedor cMS WordPress presencial em Fortaleza CE", "Fortaleza - CE"),
    ("mt", "Desenvolvedor htMT5 CSS3 presencial em Manaus AM", "Manaus - AM"),
    ("pb", "Engenheiro PBx telefonia presencial em Goiania GO", "Goiânia - GO"),
    ("pe", "Analista PErfil pleno presencial em Cuiaba MT", "Cuiabá - MT"),
    ("pi", "Engenheiro PIpeline ETL presencial em Joao Pessoa PB", "João Pessoa - PB"),
    ("pr", "Gerente PRojeto presencial em Maceio AL", "Maceió - AL"),
    ("rj", "Analista de dados presencial em Natal RN", "Natal - RN"),
    ("rn", "Dev Python presencial em Aracaju SE", "Aracaju - SE"),
    ("rr", "Dev eRRor handling presencial em Palmas TO", "Palmas - TO"),
    ("rs", "Analista RSs feeds presencial em Rio Branco AC", "Rio Branco - AC"),
    ("sc", "Dev SCript Python presencial em Macapa AP", "Macapá - AP"),
    ("se", "Analista SEguranca da informacao presencial em Boa Vista RR", "Boa Vista - RR"),
    ("sp", "reSPonsavel por projetos presenciais no Rio de Janeiro", "Rio de Janeiro - RJ"),
    ("to", "Analista TOdo o Brasil presencial em Belo Horizonte MG", "Belo Horizonte - MG"),
]

for target_uf, req_text, loc_text in word_boundary_negative_tests:
    job = make_job("Analista de Sistemas", req_text, loc_text)
    res = is_job_relevant(job, "Analista de Sistemas", make_settings(location=target_uf))
    assert_check(f"Substring '{target_uf.upper()}' inside word -> False", "Anti-False-Pos", res, False, f"Req: '{req_text}' | Loc: '{loc_text}'")

punctuation_positive_tests = [
    ("sp", "Analista de Dados", "Desenvolvedor em SP.", "SP."),
    ("sp", "Analista de Dados", "Desenvolvedor em SP,", "SP,"),
    ("sp", "Analista de Dados", "Desenvolvedor em SP-Brasil", "SP-Brasil"),
    ("sp", "Analista de Dados", "Desenvolvedor em (SP)", "(SP)"),
    ("sp", "Analista de Dados", "Desenvolvedor em SP/RJ", "SP/RJ"),
    ("rj", "Analista de Dados", "Desenvolvedor em SP/RJ", "SP/RJ"),
]

for target_uf, title, req_text, loc_text in punctuation_positive_tests:
    job = make_job(title, req_text, loc_text)
    res = is_job_relevant(job, title, make_settings(location=target_uf))
    assert_check(f"Punctuation match UF '{target_uf.upper()}' in '{loc_text}' -> True", "Punctuation-Boundary", res, True)


# -------------------------------------------------------------------
# CATEGORY 3: COLLISION & PREPOSITION VULNERABILITY INVESTIGATION
# -------------------------------------------------------------------
print("\n--- 3. Collision & Preposition Vulnerability Checks ---")

# Bug 1: Pará (PA) expanded keyword "para" matches Portuguese preposition "para"
job_rj_preposition = make_job("Dev Python", "Vaga presencial para trabalhar no Rio de Janeiro RJ", "Rio de Janeiro - RJ")
res_pa_bug = is_job_relevant(job_rj_preposition, "Dev Python", make_settings(location="pa"))
assert_check("Preposition 'para' in RJ job matches PA filter (EXPECTED False, CURRENT BUG True)", "Vulnerability-Preposition-PA", res_pa_bug, False, "Job in RJ using preposition 'para'")

# Bug 2: Mato Grosso (MT) keyword "mato grosso" matches Mato Grosso do Sul (MS) job
job_ms_state = make_job("Dev Python", "Vaga presencial em Campo Grande no estado de Mato Grosso do Sul MS", "Campo Grande - MS")
res_mt_bug = is_job_relevant(job_ms_state, "Dev Python", make_settings(location="mt"))
assert_check("MT filter matches MS job (EXPECTED False, CURRENT BUG True)", "Vulnerability-State-Collision-MT-MS", res_mt_bug, False, "Job in MS containing 'Mato Grosso do Sul'")


# -------------------------------------------------------------------
# CATEGORY 4: REMOTE & STATE FILTER COMBINATIONS
# -------------------------------------------------------------------
print("\n--- 4. Remote & State Filter Combinations ---")

remote_combos = [
    ("Dev Python", "Desenvolvedor Python 100% remoto home office", "", "gupy", "sp", True, "100% remoto Gupy para filtro SP"),
    ("Dev Python", "Desenvolvedor Python 100% remoto home office", "", "gupy", "am", True, "100% remoto Gupy para filtro AM"),
    ("Dev Python", "Desenvolvedor Python 100% remoto home office", "", "gupy", "rs", True, "100% remoto Gupy para filtro RS"),
    ("Dev Python", "Vaga presencial em Sao Paulo SP", "São Paulo - SP", "gupy", "sp", True, "Presencial SP para filtro SP"),
    ("Dev Python", "Vaga presencial em Sao Paulo SP", "São Paulo - SP", "gupy", "rj", False, "Presencial SP para filtro RJ"),
    ("Dev Python", "Vaga presencial em Sao Paulo SP", "São Paulo - SP", "gupy", "remoto", False, "Presencial SP para filtro 'remoto'"),
    ("Dev Python", "Vaga 100% home office remota no Rio de Janeiro", "Rio de Janeiro - RJ", "gupy", "remoto", True, "Vaga remota RJ para filtro 'remoto'"),
    ("Dev Python", "Vaga presencial em Curitiba PR", "Curitiba - PR", "remotar", "sp", True, "Plataforma Remotar pass-through para filtro SP"),
    ("Editor de Video", "Edicao de video projeto freelance", "Sao Paulo", "workana", "ce", True, "Workana freelance pass-through para filtro CE"),
    ("Dev Frontend", "Desenvolvedor React 100% home office teletrabalho anywhere", "Brasil", "catho", "mg", True, "Keywords teletrabalho/anywhere para filtro MG"),
]

for title, reqs, loc_str, plat, s_filter, exp, desc in remote_combos:
    job = make_job(title, reqs, loc_str, plat)
    res = is_job_relevant(job, title, make_settings(location=s_filter))
    assert_check(desc, "Remote-State-Combos", res, exp, f"Plat: {plat}, Loc: '{loc_str}'")


# -------------------------------------------------------------------
# CATEGORY 5: ALL 27 BRAZILIAN UFS POSITIVE & CROSS-STATE REJECTION
# -------------------------------------------------------------------
print("\n--- 5. All 27 Brazilian UFs Verification & Cross-Rejection ---")

ALL_27 = {
    "ac": ("Acre", "Rio Branco"),
    "al": ("Alagoas", "Maceió"),
    "am": ("Amazonas", "Manaus"),
    "ap": ("Amapá", "Macapá"),
    "ba": ("Bahia", "Salvador"),
    "ce": ("Ceará", "Fortaleza"),
    "df": ("Distrito Federal", "Brasília"),
    "es": ("Espírito Santo", "Vitória"),
    "go": ("Goiás", "Goiânia"),
    "ma": ("Maranhão", "São Luís"),
    "mg": ("Minas Gerais", "Belo Horizonte"),
    "ms": ("Mato Grosso do Sul", "Campo Grande"),
    "mt": ("Mato Grosso", "Cuiabá"),
    "pa": ("Pará", "Belém"),
    "pb": ("Paraíba", "João Pessoa"),
    "pe": ("Pernambuco", "Recife"),
    "pi": ("Piauí", "Teresina"),
    "pr": ("Paraná", "Curitiba"),
    "rj": ("Rio de Janeiro", "Rio de Janeiro"),
    "rn": ("Rio Grande do Norte", "Natal"),
    "ro": ("Rondônia", "Porto Velho"),
    "rr": ("Roraima", "Boa Vista"),
    "rs": ("Rio Grande do Sul", "Porto Alegre"),
    "sc": ("Santa Catarina", "Florianópolis"),
    "se": ("Sergipe", "Aracaju"),
    "sp": ("São Paulo", "São Paulo"),
    "to": ("Tocantins", "Palmas"),
}

for uf, (state_fullname, capital) in ALL_27.items():
    job_uf = make_job("Analista de Dados", f"Vaga presencial em {capital} {uf.upper()}", f"{capital} - {uf.upper()}")
    res_uf = is_job_relevant(job_uf, "Analista de Dados", make_settings(location=uf))
    assert_check(f"UF {uf.upper()} match por sigla", "27-UFs", res_uf, True)

    job_full = make_job("Analista de Dados", f"Vaga presencial no estado de {state_fullname}", f"{capital}")
    res_full = is_job_relevant(job_full, "Analista de Dados", make_settings(location=uf))
    assert_check(f"UF {uf.upper()} match por nome por extenso ({state_fullname})", "27-UFs", res_full, True)

    target_wrong_uf = "rj" if uf != "rj" else "sp"
    res_wrong = is_job_relevant(job_uf, "Analista de Dados", make_settings(location=target_wrong_uf))
    assert_check(f"Vaga em {uf.upper()} rejeitada para filtro {target_wrong_uf.upper()}", "27-UFs-CrossRejection", res_wrong, False)


# -------------------------------------------------------------------
# CATEGORY 6: WILDCARD / NO-FILTER / EDGE CASES IN LOCATION SETTINGS
# -------------------------------------------------------------------
print("\n--- 6. Wildcard & Edge Cases in Location Settings ---")

edge_settings = [
    ("Todos", True, "Filtro 'Todos' aceita qualquer vaga presencial"),
    ("todas", True, "Filtro 'todas' aceita qualquer vaga presencial"),
    ("qualquer", True, "Filtro 'qualquer' aceita qualquer vaga presencial"),
    ("all", True, "Filtro 'all' aceita qualquer vaga presencial"),
    ("", True, "Filtro vazio '' aceita qualquer vaga presencial"),
    ("  SP  ", True, "Filtro '  SP  ' com espacos aceita vaga SP"),
]

sample_job = make_job("Analista de Dados", "Vaga presencial em Porto Alegre RS", "Porto Alegre - RS")

for loc_setting, exp, desc in edge_settings:
    target_job = sample_job if loc_setting.strip().lower() != "sp" else make_job("Analista de Dados", "Vaga presencial SP", "São Paulo - SP")
    res = is_job_relevant(target_job, "Analista de Dados", make_settings(location=loc_setting))
    assert_check(desc, "Settings-EdgeCases", res, exp)

print("\n========================================================")
print(f" RESUMO DA SUÍTE ADVERSARIAL:")
print(f" TOTAL DE TESTES: {passed_tests + failed_tests}")
print(f" PASSOU: {passed_tests}")
print(f" FALHOU: {failed_tests}")
print("========================================================\n")

if errors:
    print("FALHAS / REPRODUÇÃO EMPÍRICA DE BUGS:")
    for err in errors:
        print(f" - {err}")
else:
    print("Todos os testes passaram sem erros.")
