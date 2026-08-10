import sys
import os
import asyncio
import json
import glob

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from fastapi.testclient import TestClient
from prioriti.app import app

def test_error_reporter_and_self_healer():
    print("=" * 70)
    print("🧪 INICIANDO TESTE DO MIDDLEWARE ERROR REPORTER E AI SELF-HEALER")
    print("=" * 70)

    client = TestClient(app)
    
    # Executa GET na rota que dispara erro forçado
    response = client.get("/api/test_error_trigger")
    print(f"Status Code retornado: {response.status_code}")
    print(f"Resposta JSON: {response.json()}")

    assert response.status_code == 500
    assert response.json().get("status") == "error"

    # Verifica se os arquivos de log foram salvos em logs/
    logs_dir = os.path.join(PROJECT_ROOT, "logs")
    json_logs = glob.glob(os.path.join(logs_dir, "error_context_*.json"))
    md_logs = glob.glob(os.path.join(logs_dir, "error_context_*.md"))

    print(f"Total de arquivos JSON de erro criados: {len(json_logs)}")
    print(f"Total de arquivos MD de erro criados: {len(md_logs)}")

    assert len(json_logs) > 0
    assert len(md_logs) > 0

    latest_json = max(json_logs, key=os.path.getmtime)
    with open(latest_json, "r", encoding="utf-8") as f:
        err_data = json.load(f)

    print("\n🔍 Conteúdo do último log de erro registrado:")
    print(f"  - Endpoint: {err_data.get('endpoint')}")
    print(f"  - Método: {err_data.get('method')}")
    print(f"  - Exceção: {err_data.get('exception_type')}: {err_data.get('exception_message')}")
    print(f"  - Localização: {err_data.get('filepath')}:{err_data.get('line_number')}")

    print("\n" + "=" * 70)
    print("✅ TESTE DO MIDDLEWARE ERROR REPORTER CONCLUÍDO COM SUCESSO!")
    print("=" * 70)

if __name__ == "__main__":
    test_error_reporter_and_self_healer()
