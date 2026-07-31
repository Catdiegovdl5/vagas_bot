"""
test_location_uf.py - Teste Completo do Filtro de Localização por UF
Verifica que o word boundary regex impede falsos positivos de siglas de estado.
Vagas simuladas com descrições realistas para passar no co-occurrence check.
"""
import sys
sys.path.insert(0, '.')
from bot import is_job_relevant

errors = []

def check(desc, result, expected):
    status = "[PASSOU]" if result == expected else "[FALHOU]"
    print(f"  {status}  {desc}: got={result}, expected={expected}")
    if result != expected:
        errors.append(desc)

def make_job(title, requirements, location, platform="gupy"):
    return {"title": title, "requirements": requirements, "location": location, "platform": platform}

def loc(state):
    return {"location": state, "level": "Todos", "contract": "Todos"}

# Vagas com descrições realistas por estado
VAGA_SP = make_job(
    "Analista de Dados Senior",
    "Analista de dados com experiencia em SQL, Python, Power BI. Vaga presencial em Sao Paulo SP. Analise de dados, dashboard e relatorios.",
    "São Paulo - SP"
)
VAGA_RJ = make_job(
    "Analista de Dados Pleno",
    "Analista de dados com SQL, Python e Power BI. Presencial no Rio de Janeiro RJ. Analise de dados e metricas.",
    "Rio de Janeiro - RJ"
)
VAGA_MG = make_job(
    "Engenheiro de Dados",
    "Engenheiro de dados pipeline ETL databricks spark SQL. Belo Horizonte Minas Gerais presencial.",
    "Belo Horizonte - MG"
)
VAGA_PR = make_job(
    "Analista de Dados Junior",
    "Analista de dados SQL Python Power BI dashboards Curitiba Parana PR presencial.",
    "Curitiba - PR"
)
VAGA_RS = make_job(
    "Engenheiro de Dados",
    "Engenheiro de dados pipeline ETL SQL Python databricks Porto Alegre Rio Grande do Sul RS.",
    "Porto Alegre - RS"
)
VAGA_SC = make_job(
    "Dev Python Backend",
    "Desenvolvedor Python Django FastAPI backend Florianopolis Santa Catarina SC.",
    "Florianópolis - SC"
)
VAGA_BA = make_job(
    "Analista de Dados",
    "Analista de dados SQL Python Power BI dashboards Salvador Bahia BA presencial.",
    "Salvador - BA"
)
VAGA_DF = make_job(
    "Analista de CRM",
    "Analista CRM Hubspot Salesforce automacao email marketing Brasilia Distrito Federal DF.",
    "Brasília - DF"
)
VAGA_REMOTO = make_job(
    "Dev Backend Python",
    "Desenvolvedor backend Python Django FastAPI 100% remoto home office qualquer estado Brasil.",
    "",
    "gupy"
)
VAGA_FREELANCE = make_job(
    "Gestor de Trafego",
    "Gestor de trafego pago Google Ads Meta Ads Facebook Ads media buyer performance ROAS.",
    "",
    "workana"
)

print("\n=== 1. ANTI-FALSO-POSITIVO: Palavras com UF como substring ===")
# Palavras: 'eSpeCialista' contem 'sp', 'reSPonsavel' contem 'sp' — deve ser False p/ SP
job_esp_rj = make_job(
    "Especialista em Marketing",
    "Especialista em marketing digital responsavel por campanhas no Rio de Janeiro presencial. Especialista sênior.",
    "Rio de Janeiro - RJ"
)
check("Especialista(sp) em RJ p/ filtro SP (False)", is_job_relevant(job_esp_rj, "Analista de Marketing Digital", loc("sp")), False)

job_rj_no_mg = make_job(
    "Analista de CRM Pleno",
    "Analista CRM HubSpot Salesforce automacao presencial Rio de Janeiro RJ. Gestão de relacionamento.",
    "Rio de Janeiro - RJ"
)
check("Analista CRM RJ p/ filtro MG (False)", is_job_relevant(job_rj_no_mg, "Analista de CRM", loc("mg")), False)

print("\n=== 2. MATCH CORRETO: Vaga do estado certo aceita ===")
check("Analista de Dados SP p/ filtro SP (True)", is_job_relevant(VAGA_SP, "Analista de Dados", loc("sp")), True)
check("Analista de Dados RJ p/ filtro RJ (True)", is_job_relevant(VAGA_RJ, "Analista de Dados", loc("rj")), True)
check("Engenheiro de Dados MG p/ filtro MG (True)", is_job_relevant(VAGA_MG, "Engenheiro de Dados", loc("mg")), True)
check("Analista de Dados PR p/ filtro PR (True)", is_job_relevant(VAGA_PR, "Analista de Dados", loc("pr")), True)
check("Engenheiro de Dados RS p/ filtro RS (True)", is_job_relevant(VAGA_RS, "Engenheiro de Dados", loc("rs")), True)
check("Dev Python SC p/ filtro SC (True)", is_job_relevant(VAGA_SC, "Desenvolvedor Python", loc("sc")), True)
check("Analista de Dados BA p/ filtro BA (True)", is_job_relevant(VAGA_BA, "Analista de Dados", loc("ba")), True)
check("Analista de CRM DF p/ filtro DF (True)", is_job_relevant(VAGA_DF, "Analista de CRM", loc("df")), True)

print("\n=== 3. VAGAS REMOTAS: Passam em qualquer estado ===")
check("Dev Remoto p/ filtro SP (True)", is_job_relevant(VAGA_REMOTO, "Desenvolvedor Python", loc("sp")), True)
check("Dev Remoto p/ filtro RJ (True)", is_job_relevant(VAGA_REMOTO, "Desenvolvedor Python", loc("rj")), True)
check("Dev Remoto p/ filtro AM (True)", is_job_relevant(VAGA_REMOTO, "Desenvolvedor Python", loc("am")), True)
check("Freelance Workana p/ filtro SP (True)", is_job_relevant(VAGA_FREELANCE, "Gestor de Trafego", loc("sp")), True)
check("Freelance Workana p/ filtro RR (True)", is_job_relevant(VAGA_FREELANCE, "Gestor de Trafego", loc("rr")), True)

print("\n=== 4. CRUZAMENTO: Vaga de estado A rejeitada em estado B ===")
check("Vaga SP p/ filtro RJ (False)", is_job_relevant(VAGA_SP, "Analista de Dados", loc("rj")), False)
check("Vaga RJ p/ filtro MG (False)", is_job_relevant(VAGA_RJ, "Analista de Dados", loc("mg")), False)
check("Vaga MG p/ filtro RS (False)", is_job_relevant(VAGA_MG, "Engenheiro de Dados", loc("rs")), False)
check("Vaga BA p/ filtro CE (False)", is_job_relevant(VAGA_BA, "Analista de Dados", loc("ce")), False)
check("Vaga PR p/ filtro RJ (False)", is_job_relevant(VAGA_PR, "Analista de Dados", loc("rj")), False)

print("\n=== 5. SEM FILTRO: Aceitar tudo ===")
check("Sem filtro p/ SP (True)", is_job_relevant(VAGA_SP, "Analista de Dados", {"location": "Todos", "level": "Todos", "contract": "Todos"}), True)
check("Sem filtro p/ RJ (True)", is_job_relevant(VAGA_RJ, "Analista de Dados", {"location": "Todos", "level": "Todos", "contract": "Todos"}), True)

print()
total = 21
if errors:
    print(f"\n[FALHOU] {len(errors)} de {total} testes falharam:")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)
else:
    print(f"[PASSOU] TODOS OS {total} TESTES PASSARAM! Filtro de UF por word boundary funcionando 100%.")
