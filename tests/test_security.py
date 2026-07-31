"""
test_security.py — Suite Completa de Testes de Segurança, Health Check, Métricas e Webhook
Valida Headers HTTP, Endpoints /health e /metrics, Validação e Idempotência de Webhook.
"""
import sys
sys.path.insert(0, '.')
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)
PASS = "[PASSOU]"
FAIL = "[FALHOU]"
errors = []

def check(desc, condition):
    status = PASS if condition else FAIL
    print(f"  {status}  {desc}")
    if not condition:
        errors.append(desc)

print("\n=== 1. TESTE DE HEADERS DE SEGURANÇA HTTP ===")
res = client.get("/")
check("Status Code da Página Principal 200 OK", res.status_code == 200)
check("Header X-Frame-Options (Anti-Clickjacking)", res.headers.get("X-Frame-Options") == "DENY")
check("Header X-Content-Type-Options (Anti-MIME Sniffing)", res.headers.get("X-Content-Type-Options") == "nosniff")
check("Header Content-Security-Policy Ativo", "Content-Security-Policy" in res.headers)
check("Header X-XSS-Protection Ativo", res.headers.get("X-XSS-Protection") == "1; mode=block")

print("\n=== 2. TESTE DE HEALTH CHECK E MÉTRICAS ===")
res_health = client.get("/health")
check("GET /health responde 200 OK", res_health.status_code == 200)
check("GET /health confirma banco conectado", res_health.json().get("status") == "ok")

res_metrics = client.get("/metrics")
check("GET /metrics responde 200 OK", res_metrics.status_code == 200)
check("GET /metrics contém contagem total_jobs", "total_jobs" in res_metrics.json())

print("\n=== 3. TESTE DE WEBHOOK DE PAGAMENTO (SEGURANÇA & IDEMPOTÊNCIA) ===")
import time
unique_pay_id = f"pay_test_{int(time.time() * 1000)}"

# 3.1 Webhook sem token secreto deve ser rejeitado
res_unauth = client.post("/api/webhook/payment", json={
    "event": "PAYMENT_RECEIVED",
    "payment_id": f"{unique_pay_id}_unauth",
    "user_id": "test_user_01",
    "amount": 39.90,
    "token": "token_invalido"
})
check("Webhook não autorizado rejeitado (401)", res_unauth.status_code == 401)

# 3.2 Webhook com token correto deve aprovar pagamento
secret = "super_secret_webhook_key_2026"
res_auth = client.post("/api/webhook/payment", json={
    "event": "PAYMENT_RECEIVED",
    "payment_id": unique_pay_id,
    "user_id": "test_user_01",
    "amount": 39.90,
    "token": secret
})
check("Webhook com token válido aprovado (200)", res_auth.status_code == 200)
check("Plano PREMIUM ativado para o usuário", res_auth.json().get("status") == "success")

# 3.3 Teste de Idempotência: Envio de Webhook com payment_id duplicado
res_dup = client.post("/api/webhook/payment", json={
    "event": "PAYMENT_RECEIVED",
    "payment_id": unique_pay_id,
    "user_id": "test_user_01",
    "amount": 39.90,
    "token": secret
})
check("Webhook duplicado identificado e ignorado (Idempotência)", res_dup.json().get("status") == "ignored")

print("\n=== 4. TESTE DE PROTEÇÃO CONTRA MÉTODOS NÃO PERMITIDOS (CORS/HTTP) ===")
res_delete = client.delete("/api/jobs")
check("Método DELETE rejeitado (405 Method Not Allowed)", res_delete.status_code == 405)

res_put = client.put("/api/jobs")
check("Método PUT rejeitado (405 Method Not Allowed)", res_put.status_code == 405)

print()
if errors:
    print(f"[FALHOU] {len(errors)} teste(s) de segurança falharam:")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)
else:
    print("[PASSOU] TODOS OS TESTES DE SEGURANÇA E AUDITORIA PASSARAM COM SUCESSO!")
