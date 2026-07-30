"""
dashboard.py — Painel Web Admin do Sniper Bot SaaS
Interface web acessível via navegador com:
  - Estatísticas da plataforma (usuários, vagas, candidaturas)
  - Gráficos dinâmicos (Chart.js)
  - Gerenciamento de usuários (Free/Premium)
  - Status do sistema

Execute com: python dashboard.py
Acesse em: http://localhost:8080/dashboard
Senha padrão: sniper2025 (configurável via DASHBOARD_PASSWORD env var)
"""
import os
import json
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets

from database import (
    get_dashboard_stats, get_user_profile, set_user_plan,
    get_user_applications, init_db, get_connection
)

# ── Config ───────────────────────────────────────────────
DASHBOARD_PASSWORD = os.environ.get("DASHBOARD_PASSWORD", "sniper2025")
DASHBOARD_USER     = os.environ.get("DASHBOARD_USER", "admin")
DASHBOARD_PORT     = int(os.environ.get("DASHBOARD_PORT", "8080"))

app = FastAPI(title="Sniper Bot Admin", docs_url=None, redoc_url=None)
security = HTTPBasic()

init_db()

def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    correct_user = secrets.compare_digest(credentials.username.encode(), DASHBOARD_USER.encode())
    correct_pass = secrets.compare_digest(credentials.password.encode(), DASHBOARD_PASSWORD.encode())
    if not (correct_user and correct_pass):
        raise HTTPException(status_code=401, detail="Acesso negado",
                            headers={"WWW-Authenticate": "Basic"})
    return credentials.username


# ── API de Dados ─────────────────────────────────────────

@app.get("/api/stats")
def api_stats(user=Depends(verify_credentials)):
    return get_dashboard_stats()

@app.get("/api/users")
def api_users(user=Depends(verify_credentials)):
    conn = get_connection()
    try:
        c = conn.cursor()
        c.execute('''
            SELECT user_id, full_name, email, plan, daily_hunts, created_at
            FROM user_profiles ORDER BY created_at DESC LIMIT 100
        ''')
        cols = ['user_id', 'full_name', 'email', 'plan', 'daily_hunts', 'created_at']
        return [dict(zip(cols, row)) for row in c.fetchall()]
    finally:
        conn.close()

@app.post("/api/users/{user_id}/plan")
def api_set_plan(user_id: str, request_data: dict, user=Depends(verify_credentials)):
    plan = request_data.get("plan", "free")
    if plan not in ("free", "premium"):
        raise HTTPException(status_code=400, detail="Plano inválido. Use 'free' ou 'premium'.")
    set_user_plan(user_id, plan)
    return {"success": True, "user_id": user_id, "plan": plan}

@app.get("/api/applications")
def api_applications(user=Depends(verify_credentials)):
    conn = get_connection()
    try:
        c = conn.cursor()
        c.execute('''
            SELECT user_id, job_title, company, platform, applied_at, method, status
            FROM job_applications ORDER BY applied_at DESC LIMIT 200
        ''')
        cols = ['user_id', 'job_title', 'company', 'platform', 'applied_at', 'method', 'status']
        return [dict(zip(cols, row)) for row in c.fetchall()]
    finally:
        conn.close()


# ── Painel HTML ──────────────────────────────────────────

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(user=Depends(verify_credentials)):
    stats = get_dashboard_stats()

    jobs_by_platform_labels = json.dumps([d['platform'] for d in stats.get('jobs_by_platform', [])])
    jobs_by_platform_data   = json.dumps([d['count'] for d in stats.get('jobs_by_platform', [])])
    daily_labels = json.dumps([d['day'] for d in stats.get('daily_searches', [])])
    daily_data   = json.dumps([d['jobs_found'] for d in stats.get('daily_searches', [])])

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Sniper Bot — Admin Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;900&display=swap" rel="stylesheet">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'Inter', sans-serif; background: #0a0a14; color: #e2e8f0; min-height: 100vh; }}

  .header {{ background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
             border-bottom: 1px solid #2d3748; padding: 20px 40px;
             display: flex; align-items: center; gap: 16px; }}
  .header h1 {{ font-size: 24px; font-weight: 700; color: #fff; }}
  .header span {{ font-size: 28px; }}
  .badge {{ background: #4ade80; color: #052e16; padding: 4px 12px;
            border-radius: 20px; font-size: 12px; font-weight: 600; }}
  .timestamp {{ margin-left: auto; font-size: 13px; color: #718096; }}

  .container {{ max-width: 1400px; margin: 0 auto; padding: 30px 40px; }}

  .kpi-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 30px; }}
  .kpi-card {{ background: linear-gradient(135deg, #1a1a2e, #16213e);
               border: 1px solid #2d3748; border-radius: 16px; padding: 24px;
               transition: transform 0.2s; }}
  .kpi-card:hover {{ transform: translateY(-3px); }}
  .kpi-card .label {{ font-size: 13px; color: #718096; text-transform: uppercase;
                      letter-spacing: 0.5px; margin-bottom: 8px; }}
  .kpi-card .value {{ font-size: 36px; font-weight: 900; color: #fff; }}
  .kpi-card .sub   {{ font-size: 12px; color: #68d391; margin-top: 4px; }}
  .kpi-card.premium .value {{ color: #fbbf24; }}
  .kpi-card.apps .value {{ color: #60a5fa; }}
  .kpi-card.vagas .value {{ color: #a78bfa; }}

  .charts-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 30px; }}
  .chart-card {{ background: linear-gradient(135deg, #1a1a2e, #16213e);
                 border: 1px solid #2d3748; border-radius: 16px; padding: 24px; }}
  .chart-card h3 {{ font-size: 16px; font-weight: 600; margin-bottom: 20px; color: #e2e8f0; }}

  .users-card {{ background: linear-gradient(135deg, #1a1a2e, #16213e);
                 border: 1px solid #2d3748; border-radius: 16px; padding: 24px; }}
  .users-card h3 {{ font-size: 16px; font-weight: 600; margin-bottom: 20px; color: #e2e8f0;
                    display: flex; align-items: center; gap: 10px; }}
  table {{ width: 100%; border-collapse: collapse; }}
  th {{ text-align: left; padding: 10px 16px; font-size: 12px; color: #718096;
        text-transform: uppercase; border-bottom: 1px solid #2d3748; }}
  td {{ padding: 12px 16px; font-size: 14px; border-bottom: 1px solid #1e2d3d; }}
  tr:hover td {{ background: rgba(255,255,255,0.03); }}
  .plan-badge {{ padding: 3px 10px; border-radius: 12px; font-size: 11px; font-weight: 600; }}
  .plan-free {{ background: #1e3a2f; color: #68d391; }}
  .plan-premium {{ background: #3b2a10; color: #fbbf24; }}
  .upgrade-btn {{ background: linear-gradient(135deg, #667eea, #764ba2);
                  color: white; border: none; padding: 4px 12px; border-radius: 8px;
                  cursor: pointer; font-size: 12px; transition: opacity 0.2s; }}
  .upgrade-btn:hover {{ opacity: 0.8; }}

  @media (max-width: 900px) {{
    .kpi-grid {{ grid-template-columns: repeat(2, 1fr); }}
    .charts-grid {{ grid-template-columns: 1fr; }}
    .container {{ padding: 20px; }}
  }}
</style>
</head>
<body>
<div class="header">
  <span>🎯</span>
  <div>
    <h1>Sniper Bot SaaS — Admin Dashboard</h1>
    <div style="font-size:13px;color:#718096;">Painel de controle da plataforma</div>
  </div>
  <span class="badge">LIVE</span>
  <div class="timestamp">Atualizado: {datetime.now().strftime('%d/%m/%Y %H:%M')}</div>
</div>

<div class="container">

  <!-- KPIs -->
  <div class="kpi-grid">
    <div class="kpi-card">
      <div class="label">👥 Usuários Totais</div>
      <div class="value">{stats.get('total_users', 0)}</div>
      <div class="sub">Cadastrados na plataforma</div>
    </div>
    <div class="kpi-card premium">
      <div class="label">⭐ Usuários Premium</div>
      <div class="value">{stats.get('premium_users', 0)}</div>
      <div class="sub">Plano pago ativo</div>
    </div>
    <div class="kpi-card vagas">
      <div class="label">💼 Vagas no Banco</div>
      <div class="value">{stats.get('total_jobs', 0)}</div>
      <div class="sub">Total coletado</div>
    </div>
    <div class="kpi-card apps">
      <div class="label">✅ Candidaturas</div>
      <div class="value">{stats.get('total_applications', 0)}</div>
      <div class="sub">Registradas pelos usuários</div>
    </div>
  </div>

  <!-- Gráficos -->
  <div class="charts-grid">
    <div class="chart-card">
      <h3>📊 Vagas por Plataforma</h3>
      <canvas id="platformChart" height="200"></canvas>
    </div>
    <div class="chart-card">
      <h3>📈 Buscas nos Últimos 7 Dias</h3>
      <canvas id="dailyChart" height="200"></canvas>
    </div>
  </div>

  <!-- Tabela de Usuários -->
  <div class="users-card">
    <h3>👥 Gerenciar Usuários <span style="font-size:13px;color:#718096;font-weight:400;">(últimos 100)</span></h3>
    <div id="users-table">Carregando...</div>
  </div>

</div>

<script>
// Gráfico de plataformas
const platformCtx = document.getElementById('platformChart').getContext('2d');
new Chart(platformCtx, {{
  type: 'doughnut',
  data: {{
    labels: {jobs_by_platform_labels},
    datasets: [{{
      data: {jobs_by_platform_data},
      backgroundColor: ['#667eea','#764ba2','#f093fb','#4facfe','#43e97b','#fa709a','#fee140','#a18cd1','#fda085','#f5576c']
    }}]
  }},
  options: {{ responsive: true, plugins: {{ legend: {{ position: 'bottom', labels: {{ color: '#e2e8f0', padding: 10 }} }} }} }}
}});

// Gráfico de buscas diárias
const dailyCtx = document.getElementById('dailyChart').getContext('2d');
new Chart(dailyCtx, {{
  type: 'bar',
  data: {{
    labels: {daily_labels},
    datasets: [{{
      label: 'Vagas Encontradas',
      data: {daily_data},
      backgroundColor: 'rgba(102, 126, 234, 0.7)',
      borderColor: '#667eea',
      borderWidth: 1,
      borderRadius: 6
    }}]
  }},
  options: {{
    responsive: true,
    plugins: {{ legend: {{ labels: {{ color: '#e2e8f0' }} }} }},
    scales: {{
      x: {{ ticks: {{ color: '#718096' }}, grid: {{ color: '#2d3748' }} }},
      y: {{ ticks: {{ color: '#718096' }}, grid: {{ color: '#2d3748' }} }}
    }}
  }}
}});

// Carrega tabela de usuários
fetch('/api/users').then(r => r.json()).then(users => {{
  if (!users.length) {{ document.getElementById('users-table').innerHTML = '<p style="color:#718096;padding:20px;">Nenhum usuário cadastrado ainda.</p>'; return; }}
  let html = '<table><thead><tr><th>Telegram ID</th><th>Nome</th><th>E-mail</th><th>Plano</th><th>Buscas Hoje</th><th>Cadastro</th><th>Ação</th></tr></thead><tbody>';
  users.forEach(u => {{
    const planBadge = u.plan === 'premium' ? '<span class="plan-badge plan-premium">⭐ Premium</span>' : '<span class="plan-badge plan-free">Free</span>';
    const btn = u.plan === 'premium'
      ? `<button class="upgrade-btn" onclick="setplan('${{u.user_id}}','free')" style="background:linear-gradient(135deg,#4a5568,#2d3748)">↓ Rebaixar</button>`
      : `<button class="upgrade-btn" onclick="setplan('${{u.user_id}}','premium')">↑ Ativar Premium</button>`;
    html += `<tr><td style="font-family:monospace;font-size:12px;">${{u.user_id}}</td><td>${{u.full_name || '—'}}</td><td>${{u.email || '—'}}</td><td>${{planBadge}}</td><td>${{u.daily_hunts || 0}}</td><td>${{(u.created_at||'').split(' ')[0]}}</td><td>${{btn}}</td></tr>`;
  }});
  html += '</tbody></table>';
  document.getElementById('users-table').innerHTML = html;
}}).catch(() => {{ document.getElementById('users-table').innerHTML = '<p style="color:#f56565;padding:20px;">Erro ao carregar usuários.</p>'; }});

function setplan(userId, plan) {{
  if (!confirm(`Alterar plano de ${{userId}} para "${{plan}}"?`)) return;
  fetch(`/api/users/${{userId}}/plan`, {{method:'POST', headers:{{'Content-Type':'application/json'}}, body: JSON.stringify({{plan}})}})
    .then(r => r.json()).then(() => location.reload());
}}
</script>
</body>
</html>"""
    return HTMLResponse(content=html)

@app.get("/")
def root():
    return RedirectResponse(url="/dashboard")


if __name__ == "__main__":
    import uvicorn
    print(f"🌐 Dashboard iniciando em http://localhost:{DASHBOARD_PORT}/dashboard")
    print(f"🔑 Login: {DASHBOARD_USER} / {DASHBOARD_PASSWORD}")
    uvicorn.run(app, host="0.0.0.0", port=DASHBOARD_PORT)
