"""
test_location_state.py - Suíte de Teste Completa para Validação de Filtro de Localização / Estados (UF)

Testes cobertos:
1. End-to-end / Endpoint app.py (/api/trigger):
   Verifica que requisições enviadas ao endpoint com `location="SP"` repassam `location="SP"`
   corretamente para as funções de filtragem do backend (is_job_relevant).
2. Auditoria dos Dicionários de Mapeamento UF (Python & JS):
   Verifica que UF_MAP no Python (bot.py) e no Frontend (#state-select & UF_MAP em static/index.html)
   possuem as 27 UFs brasileiras completas com nomes de estado e principais cidades.
3. Lógica de Filtragem de Vagas e Preservação de Remoto:
   Verifica que vagas 100% remotas passam em qualquer estado selecionado,
   enquanto vagas presenciais casam apenas com a UF, nome por extenso do estado ou principal cidade.
"""

import sys
import os
import re
from unittest.mock import patch, MagicMock

# Ajusta path para importar arquivos do projeto
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from bot import is_job_relevant, normalize_str

errors = []

def assert_check(desc, result, expected):
    status = "[PASSOU]" if result == expected else "[FALHOU]"
    print(f"  {status} {desc}: obtido={result}, esperado={expected}")
    if result != expected:
        errors.append(f"{desc} (obtido={result}, esperado={expected})")


print("\n========================================================")
print(" 1. REPASSE DE PARÂMETRO 'location' NO APP.PY (/api/trigger)")
print("========================================================")

def test_app_trigger_location_passing():
    from app import app
    from fastapi.testclient import TestClient

    client = TestClient(app)

    captured_settings = []

    def mock_is_job_relevant(job, keyword, settings):
        captured_settings.append(settings)
        return True

    with patch("bot.is_job_relevant", side_effect=mock_is_job_relevant), \
         patch("importlib.import_module") as mock_import:

        mock_module = MagicMock()
        mock_module.scrape = MagicMock(return_value=[
            {"title": "Dev Python", "requirements": "Vaga Python SP", "location": "São Paulo - SP", "platform": "gupy"}
        ])
        mock_import.return_value = mock_module

        response = client.post("/api/trigger", json={
            "keyword": "Python",
            "level": "Júnior",
            "location": "SP",
            "platforms": ["gupy"]
        })

        assert_check("Status HTTP de /api/trigger é 200", response.status_code, 200)

        # Aguarda breve momento para execução assíncrona da task em background
        import time
        time.sleep(0.3)

        has_sp_location = any(s.get("location") == "SP" for s in captured_settings)
        assert_check("O parâmetro location='SP' foi repassado ao settings de is_job_relevant", has_sp_location, True)

test_app_trigger_location_passing()


print("\n========================================================")
print(" 2. AUDITORIA COMPLETA DAS 27 UFS (PYTHON UF_MAP & FRONTEND JS/HTML)")
print("========================================================")

ALL_27_UFS = {
    "ac", "al", "am", "ap", "ba", "ce", "df", "es", "go", "ma",
    "mg", "ms", "mt", "pa", "pb", "pe", "pi", "pr", "rj", "rn",
    "ro", "rr", "rs", "sc", "se", "sp", "to"
}

def test_uf_map_completeness():
    # Extrai o UF_MAP do bot.py usando inspeção dinâmica ou regex
    bot_path = os.path.join(PROJECT_ROOT, "bot.py")
    with open(bot_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Localiza o dicionário UF_MAP em bot.py
    match = re.search(r'UF_MAP\s*=\s*\{([^}]+)\}', content, re.DOTALL)
    assert_check("UF_MAP encontrado no arquivo bot.py", bool(match), True)

    if match:
        dict_text = match.group(1)
        found_ufs = set(re.findall(r'"([a-z]{2})":', dict_text))
        missing_ufs = ALL_27_UFS - found_ufs
        assert_check(f"UF_MAP no bot.py possui todas as 27 UFs brasileiras (Faltando: {missing_ufs})", len(found_ufs), 27)

def test_frontend_state_select():
    html_path = os.path.join(PROJECT_ROOT, "static", "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    match_select = re.search(r'<select id="state-select"[^>]*>(.*?)</select>', html_content, re.DOTALL)
    assert_check("<select id='state-select'> encontrado em static/index.html", bool(match_select), True)

    if match_select:
        options_text = match_select.group(1)
        option_ufs = set(val.lower() for val in re.findall(r'<option value="([A-Z]{2})">', options_text))
        missing_options = ALL_27_UFS - option_ufs
        assert_check(f"Dropdown de estados no HTML contém as 27 UFs (Faltando: {missing_options})", len(option_ufs), 27)

def test_frontend_js_uf_map():
    html_path = os.path.join(PROJECT_ROOT, "static", "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    match_js_uf = re.search(r'const (?:UF_MAP|UF_MAPPING)\s*=\s*\{([^;]+)\};', html_content, re.DOTALL)
    assert_check("UF_MAP em JavaScript encontrado em static/index.html", bool(match_js_uf), True)

    if match_js_uf:
        dict_text = match_js_uf.group(1)
        found_ufs = set(val.lower() for val in re.findall(r'"([a-zA-Z]{2})":', dict_text))
        missing_ufs = ALL_27_UFS - found_ufs
        assert_check(f"UF_MAP do JS em static/index.html possui as 27 UFs (Faltando: {missing_ufs})", len(found_ufs & ALL_27_UFS), 27)

test_uf_map_completeness()
test_frontend_state_select()
test_frontend_js_uf_map()


print("\n========================================================")
print(" 3. PRESERVAÇÃO DE 100% REMOTO & FILTRAGEM POR ESTADO/UF/CIDADE")
print("========================================================")

def make_job(title, reqs, loc="", platform="gupy"):
    return {"title": title, "requirements": reqs, "location": loc, "platform": platform}

def loc(state):
    return {"location": state, "level": "Todos", "contract": "Todos"}

# Testes com vagas remotas
vaga_remota_gupy = make_job("Dev Python", "Desenvolvedor Backend Python 100% remoto home office", "", "gupy")
vaga_remota_workana = make_job("Editor de Video", "Edicao de reels freelance projeto remoto", "", "workana")
vaga_remota_remotar = make_job("Analista de Dados", "Vaga analista de dados 100% home office", "Brasil (Remoto)", "remotar")

assert_check("Vaga Remota Gupy passa para filtro SP", is_job_relevant(vaga_remota_gupy, "Desenvolvedor Python", loc("sp")), True)
assert_check("Vaga Remota Gupy passa para filtro AM", is_job_relevant(vaga_remota_gupy, "Desenvolvedor Python", loc("am")), True)
assert_check("Vaga Workana passa para filtro RS", is_job_relevant(vaga_remota_workana, "Editor de Vídeo", loc("rs")), True)
assert_check("Vaga Remotar passa para filtro CE", is_job_relevant(vaga_remota_remotar, "Analista de Dados", loc("ce")), True)

# Testes com correspondência de UF, Nome Completo e Cidade Principal
vaga_sp_sigla = make_job("Analista de Dados", "SQL Python Power BI presencial em Sao Paulo", "São Paulo - SP")
vaga_mg_extenso = make_job("Engenheiro de Dados", "Pipeline ETL SQL Python presencial em Minas Gerais", "Belo Horizonte")
vaga_pr_cidade = make_job("Dev Backend", "Desenvolvedor backend em Curitiba presencial", "Curitiba - PR")
vaga_ba_cidade = make_job("Analista CRM", "Analista CRM Salesforce em Salvador presencial", "Salvador - BA")

assert_check("Vaga SP (Sigla SP) passa no filtro SP", is_job_relevant(vaga_sp_sigla, "Analista de Dados", loc("sp")), True)
assert_check("Vaga MG (Minas Gerais) passa no filtro MG", is_job_relevant(vaga_mg_extenso, "Engenheiro de Dados", loc("mg")), True)
assert_check("Vaga PR (Curitiba) passa no filtro PR", is_job_relevant(vaga_pr_cidade, "Desenvolvedor Backend", loc("pr")), True)
assert_check("Vaga BA (Salvador) passa no filtro BA", is_job_relevant(vaga_ba_cidade, "Analista de CRM", loc("ba")), True)

# Testes de rejeição cruzada (Vaga presencial de estado A rejeitada para estado B)
assert_check("Vaga presencial SP REJEITADA para filtro RJ", is_job_relevant(vaga_sp_sigla, "Analista de Dados", loc("rj")), False)
assert_check("Vaga presencial PR REJEITADA para filtro SC", is_job_relevant(vaga_pr_cidade, "Desenvolvedor Backend", loc("sc")), False)

# Testes Anti-Falso-Positivo (Palavras com siglas como substring)
vaga_esp = make_job("Especialista em Marketing", "Especialista responsavel por marketing digital no Rio de Janeiro presencial", "Rio de Janeiro - RJ")
assert_check("Palavra 'Especialista' (contendo 'sp') no RJ NAO passa no filtro SP", is_job_relevant(vaga_esp, "Analista de Marketing Digital", loc("sp")), False)


print("\n========================================================")
if errors:
    print(f"[FALHOU] {len(errors)} testes falharam:")
    for err in errors:
        print(f"  - {err}")
    sys.exit(1)
else:
    print("[PASSOU] TODOS OS TESTES DA SUÍTE DE LOCALIZAÇÃO PASSARAM COM SUCESSO!")
    print("========================================================\n")
