from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database import get_jobs, insert_jobs, init_db, mark_applied, mark_ignored, get_connection
import uvicorn
import os
import asyncio
import logging
import sqlite3
import unicodedata
from logging.handlers import RotatingFileHandler
from typing import Optional, List, Dict, Union
from dotenv import load_dotenv

load_dotenv()

def remover_acentos(texto: str) -> str:
    """Remove acentos e padroniza para caixa baixa."""
    if not texto:
        return ""
    nfkd = unicodedata.normalize('NFKD', texto)
    return "".join([c for c in nfkd if not unicodedata.combining(c)]).lower().strip()

# Configuração do Logger Segura (Limpa arquivos maiores que 1MB, guarda apenas 1 backup)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
log_path = os.path.join(BASE_DIR, "system.log")
logger = logging.getLogger("SniperBot")
logger.setLevel(logging.INFO)
handler = RotatingFileHandler(log_path, maxBytes=1000000, backupCount=1, encoding='utf-8')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)

logger.info("Sistema de Logs Iniciado com Sucesso.")

from normalizer import normalizar_banco_dados

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerenciador de Ciclo de Vida (Lifespan) assíncrono modernizado do FastAPI.
    Executa tarefas de inicialização, como checar se o banco tem vagas,
    normaliza a senioridade das vagas com precedência de título e dispara rotinas de background.
    """
    logger.info("FastAPI Server iniciado com sucesso via Lifespan Manager.")
    normalizar_banco_dados()
    jobs = get_jobs()
    if not jobs:
        logger.info("Banco de dados sem vagas. Disparando Varredura Inicial de População de Dados...")
        asyncio.create_task(run_initial_seed_search())
    
    # Inicia o loop de busca automática no background
    asyncio.create_task(background_periodic_hunt_loop())
    yield
    logger.info("FastAPI Server encerrando conexões...")

app = FastAPI(lifespan=lifespan)

import httpx
import time

_last_alert_time = 0

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    global _last_alert_time
    logger.exception(f"Unhandled Exception at {request.url.path}: {exc}")
    
    now = time.time()
    if now - _last_alert_time > 300:  # Rate limit: máximo 1 alerta a cada 5 minutos
        _last_alert_time = now
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        admin_id = os.getenv("ADMIN_TELEGRAM_ID", "43991652706")
        if bot_token:
            try:
                async with httpx.AsyncClient(timeout=5) as client:
                    msg = f"🚨 *CRITICAL UNHANDLED ERROR*\n📍 Rota: `{request.url.path}`\n❌ Exceção: `{str(exc)[:250]}`"
                    await client.post(
                        f"https://api.telegram.org/bot{bot_token}/sendMessage",
                        json={"chat_id": admin_id, "text": msg, "parse_mode": "Markdown"}
                    )
            except Exception as e:
                logger.error(f"Falha ao enviar alerta de erro via Telegram: {e}")
                
    return JSONResponse(status_code=500, content={"status": "error", "message": "Ocorreu um erro interno de servidor."})

# Middleware de Segurança e Hardening (Headers de Proteção Anti-Clickjacking & Anti-XSS)
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = "default-src 'self' 'unsafe-inline' 'unsafe-eval' https: data:;"
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Inicializa o banco de dados caso nao exista
init_db()

STATIC_DIR = os.path.join(BASE_DIR, "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/", response_class=HTMLResponse)
def serve_dashboard():
    """Rota principal: Serve o painel web (HTML) estático."""
    with open(os.path.join(STATIC_DIR, "index.html"), "r", encoding="utf-8") as f:
        return f.read()

@app.get("/tma/proposal", response_class=HTMLResponse)
def serve_tma_proposal():
    """Rota do Telegram Mini App (TMA): Serve a interface de geração de propostas via IA."""
    with open(os.path.join(STATIC_DIR, "index.html"), "r", encoding="utf-8") as f:
        return f.read()

@app.get("/api/jobs")
@app.get("/api/vagas")
def listar_vagas(
    estado: Optional[str] = "",
    cidade: Optional[str] = "",
    senioridade: Optional[str] = "todos",
    nivel: Optional[str] = None,
    modalidade: Optional[str] = "todos",
    categoria: Optional[str] = None,
    profession: Optional[str] = "",
    q: Optional[str] = None,
    lat: float = None,
    lon: float = None,
    radius: float = 50.0
):
    """
    Endpoint unificado de busca inteligente de vagas.
    - Usa jobs.db (via get_connection) com tabela 'jobs'
    - Suporta estado, cidade, senioridade (ou nivel), modalidade, categoria/profession e busca livre por palavra-chave (q)
    """
    base_query = """
        SELECT j.id, j.title, j.company, j.budget, j.link, j.platform,
               j.job_type, j.profession, j.level, j.requirements,
               j.location, j.lat, j.lon, j.lang, j.added_at,
               CASE
                   WHEN a.link IS NOT NULL THEN 'Aplicado'
                   WHEN i.link IS NOT NULL THEN 'Ignorado'
                   ELSE 'Disponível'
               END AS status
        FROM jobs j
        LEFT JOIN applied_jobs a ON j.link = a.link
        LEFT JOIN ignored_jobs i ON j.link = i.link
        WHERE 1=1
    """
    params = []

    # ── 1. Filtro por estado ────────────────────────────────────
    if estado and estado.lower() not in ("todos", "all", ""):
        uf = estado.strip().upper()
        base_query += " AND (UPPER(j.location) = ? OR UPPER(j.location) LIKE ?)"
        params.extend([uf, f"%{uf}%"])

    # ── 2. Filtro por cidade ────────────────────────────────────
    if cidade and cidade.strip():
        cid = remover_acentos(cidade)
        base_query += " AND (LOWER(j.location) LIKE ? OR LOWER(j.location) LIKE ?)"
        params.extend([f"%{cid}%", f"%{cidade.strip().lower()}%"])

    # ── 3. Filtro por modalidade (remoto, hibrido, presencial) ──
    if modalidade and modalidade.lower() not in ("todos", "all", ""):
        mod = remover_acentos(modalidade)
        if "remot" in mod:
            base_query += " AND (LOWER(j.location) LIKE '%remot%' OR LOWER(j.title) LIKE '%remot%' OR LOWER(j.title) LIKE '%home office%')"
        elif "hibrid" in mod:
            base_query += " AND (LOWER(j.location) LIKE '%hibrid%' OR LOWER(j.title) LIKE '%hibrid%')"
        elif "presenc" in mod:
            base_query += " AND (LOWER(j.location) LIKE '%presenc%' OR (LOWER(j.location) NOT LIKE '%remot%' AND LOWER(j.location) NOT LIKE '%hibrid%'))"

    # ── 4. Filtro Inteligente por Profissão / Categoria com Exclusão Visual ──
    cat_target = remover_acentos(categoria or profession or "")
    DESIGNER_EXCLUSIONS = [
        "designer", "design", "webdesigner", "ui/ux", "ux/ui", "criativo",
        "arte finalista", "grafico", "gr%fico", "motion", "videomaker", "editor de v%deo", "editor de video"
    ]
    TRAFFIC_CATEGORIES = [
        "gestor_trafego", "gestor_trafego_geral", "meta_ads", "google_ads",
        "media_buyer", "growth_performance", "especialista_ads", "growth_hacker", "trafego", "tr%fego"
    ]

    if cat_target and cat_target not in ("all", "todos", ""):
        if any(tc in cat_target for tc in TRAFFIC_CATEGORIES):
            if "meta" in cat_target:
                base_query += " AND (LOWER(j.title) LIKE '%meta ads%' OR LOWER(j.title) LIKE '%facebook ads%' OR LOWER(j.title) LIKE '%instagram ads%' OR LOWER(j.title) LIKE '%tiktok ads%' OR LOWER(j.title) LIKE '%social ads%')"
            elif "google" in cat_target:
                base_query += " AND (LOWER(j.title) LIKE '%google ads%' OR LOWER(j.title) LIKE '%youtube ads%' OR LOWER(j.title) LIKE '%sem%' OR LOWER(j.title) LIKE '%search ads%')"
            elif "buyer" in cat_target or "midia" in cat_target:
                base_query += " AND (LOWER(j.title) LIKE '%media buyer%' OR LOWER(j.title) LIKE '%m%dia paga%' OR LOWER(j.title) LIKE '%compra de m%dia%')"
            elif "growth" in cat_target or "performance" in cat_target:
                base_query += " AND (LOWER(j.title) LIKE '%growth%' OR LOWER(j.title) LIKE '%performance%' OR LOWER(j.title) LIKE '%cro%')"
            else:
                base_query += " AND (LOWER(j.title) LIKE '%tr%fego%' OR LOWER(j.title) LIKE '%media buyer%' OR LOWER(j.title) LIKE '%meta ads%' OR LOWER(j.title) LIKE '%google ads%' OR LOWER(j.title) LIKE '%facebook ads%' OR LOWER(j.title) LIKE '%trafficker%')"

            # EXCLUSÃO RIGOROSA: ignora vagas cujo TÍTULO seja estritamente de Designer/Criativo Visual
            for excl in DESIGNER_EXCLUSIONS:
                base_query += " AND LOWER(j.title) NOT LIKE ?"
                params.append(f"%{excl}%")

        elif any(dc in cat_target for dc in ["designer_grafico", "ui_ux", "motion_designer", "designer_performance", "design"]):
            if "ui" in cat_target or "ux" in cat_target:
                base_query += " AND (LOWER(j.title) LIKE '%ui%' OR LOWER(j.title) LIKE '%ux%' OR LOWER(j.title) LIKE '%product design%')"
            elif "motion" in cat_target:
                base_query += " AND (LOWER(j.title) LIKE '%motion%' OR LOWER(j.title) LIKE '%videomaker%' OR LOWER(j.title) LIKE '%editor%')"
            else:
                base_query += " AND (LOWER(j.title) LIKE '%design%' OR LOWER(j.profession) LIKE '%design%')"
        else:
            base_query += " AND (LOWER(j.profession) LIKE ? OR LOWER(j.title) LIKE ?)"
            params.extend([f"%{cat_target}%", f"%{cat_target}%"])

    # ── 5. Busca por palavra-chave livre (q) ──────────────────────
    if q and q.strip():
        termo = remover_acentos(q)
        base_query += " AND (LOWER(j.title) LIKE ? OR LOWER(j.company) LIKE ? OR LOWER(j.requirements) LIKE ?)"
        params.extend([f"%{termo}%", f"%{termo}%", f"%{termo}%"])

    # ── 6. Filtro Rigoroso de Senioridade Normalizada (Precedência de Título) ──
    sen_key = (nivel or senioridade or "todos").lower().strip()
    sen_map = {
        'junior': 'jr', 'jr': 'jr', 'júnior': 'jr',
        'pleno': 'pl', 'pl': 'pl',
        'senior': 'sr', 'sênior': 'sr', 'sr': 'sr',
        'lead': 'lead', 'especialista': 'lead', 'head': 'lead',
        'estagio': 'jr', 'trainee': 'jr'
    }
    sen_norm = sen_map.get(sen_key, sen_key)

    if sen_norm not in ("todos", "all", ""):
        base_query += " AND (j.senioridade_norm = ? OR j.level = ?)"
        params.extend([sen_norm, sen_norm])

    base_query += " ORDER BY j.added_at DESC LIMIT 300"

    try:
        conn = get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        rows = cursor.execute(base_query, params).fetchall()
        conn.close()
        jobs = []
        for r in rows:
            row_dict = dict(r)
            jobs.append({
                "id":           row_dict.get("id"),
                "title":        row_dict.get("title") or "Vaga Sem Título",
                "company":      row_dict.get("company") or "Empresa Confidencial",
                "location":     row_dict.get("location") or "Remoto/Brasil",
                "level":        row_dict.get("level") or "nao_informado",
                "link":         row_dict.get("link") or "#",
                "platform":     row_dict.get("platform") or "Geral",
                "requirements": row_dict.get("requirements") or "",
                "budget":       row_dict.get("budget") or "A combinar",
                "status":       row_dict.get("status") or "Disponível",
                "job_type":     row_dict.get("job_type") or "CLT",
                "profession":   row_dict.get("profession") or "Outros",
                "added_at":     row_dict.get("added_at") or "",
                "lang":         row_dict.get("lang") or "pt",
            })
        return {"jobs": jobs}
    except Exception as e:
        logger.error(f"Erro ao buscar vagas: {e}", exc_info=True)
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})




from pydantic import BaseModel
class JobActionRequest(BaseModel):
    link: str
    reason: str = None

@app.post("/api/apply_job")
async def api_apply_job(req: JobActionRequest):
    await asyncio.to_thread(mark_applied, req.link)
    return {"status": "success", "message": "Vaga marcada como candidatada!"}

@app.post("/api/ignore_job")
async def api_ignore_job(req: JobActionRequest):
    await asyncio.to_thread(mark_ignored, req.link, req.reason or "Outros")
    return {"status": "success", "message": "Vaga marcada como ignorada."}

class ProfileRequest(BaseModel):
    user_id: str = "web_user"
    full_name: str = None
    skills: str = None
    experience: str = None
    resume_text: str = None
    groq_api_key: str = None

@app.get("/api/profile")
def api_get_profile(user_id: str = "web_user", request: Request = None):
    auth_user = request.headers.get("X-User-ID", "web_user") if request else "web_user"
    if auth_user != user_id and auth_user != "admin":
        return JSONResponse(status_code=403, content={"status": "forbidden", "message": "Acesso negado: você não tem permissão para visualizar este perfil."})
    from database import get_user_profile
    return get_user_profile(user_id)

@app.post("/api/profile")
def api_save_profile(req: ProfileRequest, request: Request = None):
    auth_user = request.headers.get("X-User-ID", "web_user") if request else "web_user"
    if auth_user != req.user_id and auth_user != "admin":
        return JSONResponse(status_code=403, content={"status": "forbidden", "message": "Acesso negado: você não tem permissão para alterar este perfil."})
    from database import upsert_user_profile
    upsert_user_profile(
        req.user_id,
        full_name=req.full_name,
        skills=req.skills,
        experience=req.experience,
        resume_text=req.resume_text,
        groq_api_key=req.groq_api_key
    )
    return {"status": "success", "message": "Perfil atualizado com sucesso!"}

import importlib


@app.get("/health")
def health_check():
    from database import get_connection
    try:
        conn = get_connection()
        conn.execute("SELECT 1")
        conn.close()
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        return {"status": "error", "database": str(e)}

@app.get("/metrics")
def api_metrics():
    from database import get_connection
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM jobs")
    total_jobs = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM applied_jobs")
    total_applied = c.fetchone()[0]
    conn.close()
    return {
        "total_jobs": total_jobs,
        "total_applied": total_applied,
        "status": "online"
    }

import hmac

class PaymentWebhookPayload(BaseModel):
    event: str
    payment_id: str
    user_id: str
    amount: float = 39.90
    token: str = None

from fastapi.responses import HTMLResponse, JSONResponse

@app.post("/api/webhook/payment")
async def payment_webhook(req: PaymentWebhookPayload, request: Request):
    token_header = request.headers.get("X-Webhook-Secret") or req.token or ""
    expected_secret = os.getenv("PAYMENT_WEBHOOK_SECRET", "super_secret_webhook_key_2026")
    
    if not hmac.compare_digest(token_header, expected_secret):
        return JSONResponse(status_code=401, content={"status": "unauthorized", "message": "Assinatura do webhook inválida"})
        
    from database import register_payment_if_new, upsert_user_profile
    if not register_payment_if_new(req.payment_id, req.user_id, req.amount):
        return {"status": "ignored", "message": "Pagamento já processado (Idempotência Persistida em DB)"}
        
    upsert_user_profile(req.user_id, plan="PREMIUM")
    return {"status": "success", "message": f"Plano PREMIUM ativado para {req.user_id}"}

@app.post("/api/webhook/n8n")
async def n8n_webhook(request: Request):
    """ Webhook chamado pelo n8n a cada 24h contendo as vagas raspadas """
    data = await request.json()
    jobs = data.get("jobs", [])
    inserted = await asyncio.to_thread(insert_jobs, jobs)
    return {"status": "success", "inserted": inserted, "total_received": len(jobs)}

from fastapi.responses import HTMLResponse, Response
from database import get_jobs, insert_jobs, init_db, mark_applied, mark_ignored, get_user_profile
import inspect
import csv
import io

@app.get("/api/export_csv")
def api_export_csv():
    """Gera e retorna um arquivo CSV formatado com BOM para Excel."""
    jobs = get_jobs()
    output = io.StringIO()
    writer = csv.writer(output, delimiter=';')
    writer.writerow(['Título', 'Empresa', 'Plataforma', 'Status', 'Link', 'Requisitos'])
    for j in jobs:
        writer.writerow([
            j.get('title', ''),
            j.get('company', ''),
            j.get('platform', ''),
            j.get('status', 'Disponível'),
            j.get('link', ''),
            (j.get('requirements', '') or '')[:200].replace('\n', ' ')
        ])
    
    csv_bytes = ('\ufeff' + output.getvalue()).encode('utf-8')
    return Response(
        content=csv_bytes,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=vagas_sniper.csv"}
    )

@app.get("/api/models/available")
async def api_get_available_models(user_id: str = "web_user", request: Request = None):
    """Descoberta dinâmica BYOK estrita de modelos de IA baseada EXCLUSIVAMENTE nas chaves cadastradas pelo usuário."""
    auth_user = request.headers.get("X-User-ID", "web_user") if request else "web_user"
    effective_id = user_id if auth_user == "web_user" else auth_user
    
    from database import get_user_profile, get_connection, PostgresRLSTenantContext
    conn = get_connection()
    with PostgresRLSTenantContext(conn, effective_id):
        profile = get_user_profile(effective_id)

    # Ler chaves explicitamente cadastradas pelo usuário no seu perfil
    user_groq_key = profile.get("groq_api_key")
    user_gemini_key = profile.get("gemini_api_key")
    user_openrouter_key = profile.get("openrouter_api_key")

    # Fallbacks de sistema se o usuário não cadastrou nenhuma chave própria ainda
    sys_groq_key = os.getenv("GROQ_API_KEY_1") or os.getenv("GROQ_API_KEY")
    sys_gemini_key = os.getenv("GEMINI_API_KEY_1") or os.getenv("GEMINI_API_KEY")
    sys_openrouter_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")

    providers = []

    # Caso 1: Usuário cadastrou sua própria chave da Groq
    effective_groq = user_groq_key or (sys_groq_key if not user_gemini_key and not user_openrouter_key else None)
    if user_groq_key or (not user_gemini_key and not user_openrouter_key and sys_groq_key):
        groq_models = []
        if effective_groq:
            try:
                import requests
                def fetch_groq():
                    res = requests.get("https://api.groq.com/openai/v1/models", headers={"Authorization": f"Bearer {effective_groq}"}, timeout=4)
                    if res.status_code == 200:
                        return [m["id"] for m in res.json().get("data", [])]
                    return []
                raw_models = await asyncio.to_thread(fetch_groq)
                for m in raw_models:
                    if any(k in m for k in ["llama-3.3-70b", "llama-3.1-8b", "qwen", "gpt-oss"]):
                        tag = "🧠" if ("70b" in m or "120b" in m) else "⚡"
                        groq_models.append({"id": f"groq:{m}", "name": f"{tag} {m} (Groq LPU)", "provider": "Groq"})
            except Exception:
                pass
        
        if not groq_models:
            groq_models = [
                {"id": "groq:llama-3.3-70b-versatile", "name": "🧠 llama-3.3-70b-versatile (Groq LPU)", "provider": "Groq"},
                {"id": "groq:llama-3.1-8b-instant", "name": "⚡ llama-3.1-8b-instant (Groq LPU)", "provider": "Groq"}
            ]
        providers.append({"provider": "🚀 Groq Cloud API (Sua Chave)", "models": groq_models})

    # Caso 2: Usuário cadastrou sua própria chave da Google Gemini / OpenRouter
    if user_gemini_key or user_openrouter_key or (not user_groq_key and (sys_gemini_key or sys_openrouter_key)):
        gemini_models = [
            {"id": "google:gemini-3.1-flash-lite", "name": "⚡ Gemini 3.1 Flash-Lite (Google)", "provider": "Google"},
            {"id": "google:gemini-3.5-flash", "name": "🧠 Gemini 3.5 Flash (Google)", "provider": "Google"}
        ]
        providers.append({"provider": "⚡ Google Gemini AI (Sua Chave)", "models": gemini_models})

    has_user_keys = bool(user_groq_key or user_gemini_key or user_openrouter_key)
    return {
        "status": "success",
        "has_configured_keys": has_user_keys or bool(sys_groq_key or sys_gemini_key),
        "providers": providers
    }

# ─────────────────────────────────────────────────────────────
# ROTAS LGPD (Exportação de dados e Direito ao Esquecimento)
# ─────────────────────────────────────────────────────────────

@app.get("/api/lgpd/export")
async def api_lgpd_export(user_id: str = "web_user"):
    """Exporta todos os dados do titular em JSON (Portabilidade LGPD)."""
    from database import export_user_data_lgpd
    data = await asyncio.to_thread(export_user_data_lgpd, user_id)
    return JSONResponse(content=data)

@app.post("/api/lgpd/purge")
async def api_lgpd_purge(req: ProfileRequest):
    """Exclui de forma irreversível todos os dados do titular (Direito ao Esquecimento LGPD)."""
    from database import purge_user_data_lgpd
    success = await asyncio.to_thread(purge_user_data_lgpd, req.user_id)
    if success:
        return {"status": "success", "message": f"Todos os dados vinculados ao ID {req.user_id} foram excluídos permanentemente."}
    return JSONResponse(status_code=500, content={"status": "error", "message": "Falha na exclusão de dados."})

# ─────────────────────────────────────────────────────────────
# COPILOTO DE PROPOSTAS (TMA Telegram & Web Unificados)
# ─────────────────────────────────────────────────────────────

import hashlib
from urllib.parse import parse_qsl

def verify_telegram_init_data(init_data: str, bot_token: str) -> dict:
    """Valida a assinatura HMAC-SHA256 dos dados do Telegram Mini App."""
    if not init_data or not bot_token:
        return None
    try:
        parsed_data = dict(parse_qsl(init_data))
        hash_to_verify = parsed_data.pop("hash", None)
        if not hash_to_verify:
            return None
            
        data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(parsed_data.items()))
        secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
        calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
        
        if hmac.compare_digest(calculated_hash, hash_to_verify):
            user_json = parsed_data.get("user")
            if user_json:
                import json
                return json.loads(user_json)
            return parsed_data
        return None
    except Exception as e:
        logger.error(f"Erro na verificação initData Telegram: {e}")
        return None

from typing import Optional

class ProposalStartRequest(BaseModel):
    init_data: Optional[str] = None
    user_id: Optional[str] = "web_user"
    job_url: Optional[str] = ""
    job_title: Optional[str] = "Vaga Tech"
    job_requirements: Optional[str] = "Requisitos do projeto"
    platform: Optional[str] = "Workana"
    model_choice: Optional[str] = "gemini-3.1-flash-lite"
    length_choice: Optional[str] = "6-pilares"
    style_choice: Optional[str] = "alta-conversao"
    seniority_choice: Optional[str] = "Junior"
    custom_questions: Optional[str] = ""

class ProposalChatRequest(BaseModel):
    session_id: str
    user_message: str
    init_data: Optional[str] = None
    user_id: Optional[str] = "web_user"
    model_choice: Optional[str] = "gemini-3.1-flash-lite"

_proposal_sessions = {}

@app.post("/api/proposals/session/start")
async def api_proposal_start(req: ProposalStartRequest):
    """Inicia sessão de refinamento de proposta validando TMA initData ou sessão web."""
    plat_lower = str(req.platform or "").lower()
    if not any(p in plat_lower for p in ["workana", "99freelas", "novenove"]):
        return JSONResponse(status_code=400, content={"status": "error", "message": "Propostas por IA são permitidas apenas para vagas freelancer (Workana e 99Freelas)"})

    effective_user_id = req.user_id
    if req.init_data:
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        tg_user = verify_telegram_init_data(req.init_data, bot_token)
        if not tg_user:
            return JSONResponse(status_code=401, content={"status": "unauthorized", "message": "Assinatura do Telegram Mini App inválida"})
        effective_user_id = str(tg_user.get("id", req.user_id))

    from database import get_user_profile, get_connection, PostgresRLSTenantContext
    conn = get_connection()
    with PostgresRLSTenantContext(conn, effective_user_id):
        profile = get_user_profile(effective_user_id)
        resume_text = profile.get("resume_text", "Desenvolvedor Python & Growth Engineer com experiência em automações.")

    session_id = f"prop_sess_{effective_user_id}_{int(time.time())}"
    
    try:
        from scrapers.ai_filter import generate_custom_proposal, score_job_match
        initial_proposal = await generate_custom_proposal(
            resume_text,
            req.job_title,
            req.job_requirements,
            model_choice=req.model_choice,
            length_choice=req.length_choice,
            style_choice=req.style_choice,
            seniority_choice=req.seniority_choice,
            custom_questions=req.custom_questions
        )
        if not initial_proposal or len(initial_proposal) < 50:
            eval_res = await score_job_match(resume_text, {"title": req.job_title, "platform": req.platform, "requirements": req.job_requirements}, target_keyword=req.job_title, target_contract="Freelancer")
            initial_proposal = eval_res.get("proposal")
    except Exception as e:
        logger.error(f"Erro ao gerar proposta com IA: {e}")
        initial_proposal = f"""Olá! Tudo bem?
Analisei os detalhes do seu projeto de '{req.job_title}' e confesso que fiquei muito animado.

Por isso, proponho uma estratégia muito prática focada em 3 passos:

🎯 1. Mapeamento Estratégico: Análise completa do seu objetivo principal.
🚀 2. Implementação Ágil: Construção da solução sob medida com entregas rápidas.
📲 3. Acompanhamento Contínuo: Ajustes para garantir a máxima eficiência.

Podemos conversar por 5 minutos hoje para alinharmos os detalhes?"""

    _proposal_sessions[session_id] = {
        "user_id": effective_user_id,
        "job_title": req.job_title,
        "job_requirements": req.job_requirements,
        "resume_text": resume_text,
        "history": [
            {"role": "assistant", "content": initial_proposal}
        ]
    }

    from database import save_proposal_session
    await asyncio.to_thread(save_proposal_session, session_id, effective_user_id, req.job_title, req.job_requirements, _proposal_sessions[session_id]["history"])

    return {
        "status": "success",
        "session_id": session_id,
        "user_id": effective_user_id,
        "initial_proposal": initial_proposal,
        "job_title": req.job_title
    }

@app.post("/api/proposals/session/chat")
async def api_proposal_chat(req: ProposalChatRequest):
    """Refina a proposta de forma incremental via IA com contexto completo das instruções do usuário."""
    sess = _proposal_sessions.get(req.session_id)
    if not sess:
        return JSONResponse(status_code=404, content={"status": "not_found", "message": "Sessão de proposta não encontrada ou expirada"})

    effective_user_id = sess["user_id"]
    if req.init_data:
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        tg_user = verify_telegram_init_data(req.init_data, bot_token)
        if not tg_user or str(tg_user.get("id")) != effective_user_id:
            return JSONResponse(status_code=401, content={"status": "unauthorized", "message": "Assinatura de acesso negada"})

    from scrapers.ai_filter import budget_guard, generate_custom_proposal
    try:
        budget_guard.check_and_charge(0.0003)
    except Exception as e:
        return JSONResponse(status_code=429, content={"status": "rate_limited", "message": str(e)})

    sess["history"].append({"role": "user", "content": req.user_message})
    
    # Chama o gerador consultivo especializado passando a instrução digitada pelo usuário no chat e o modelo escolhido
    refined_proposal = await generate_custom_proposal(
        resume_text=sess["resume_text"],
        job_title=sess["job_title"],
        job_requirements=sess["job_requirements"],
        user_instruction=req.user_message,
        history=sess["history"],
        model_choice=req.model_choice
    )
    
    if not refined_proposal:
        refined_proposal = f"Versão Refinada ({req.user_message}):\n" + sess["history"][0]["content"]

    sess["history"].append({"role": "assistant", "content": refined_proposal})

    from database import save_proposal_session
    await asyncio.to_thread(save_proposal_session, req.session_id, effective_user_id, sess["job_title"], sess["job_requirements"], sess["history"])

    return {
        "status": "success",
        "refined_proposal": refined_proposal,
        "session_id": req.session_id
    }



PLATFORM_MODULE_MAP = {
    "workana": "workana",
    "gupy": "gupy",
    "catho": "catho",
    "infojobs": "infojobs",
    "linkedin": "linkedin",
    "vagas.com": "vagas_com",
    "vagas_com": "vagas_com",
    "vagas": "vagas_com",
    "99freelas": "novenove",
    "novenove": "novenove",
    "freelancer.com": "freelancer",
    "freelancer": "freelancer",
    "remotar": "remotar",
    "programathor": "programathor",
    "geekhunter": "geekhunter",
    "coodesh": "coodesh",
    "github vagas br": "github_vagas",
    "github_vagas": "github_vagas",
    "indeed": "indeed",
    "glassdoor": "glassdoor",
    "jooble": "jooble"
}

@app.post("/api/trigger")
async def trigger_hunt(request: Request):
    """ Dispara caçada assíncrona de vagas nas plataformas selecionadas """
    try:
        data = await request.json()
    except Exception:
        data = {}
        
    platforms = data.get("platforms", [])
    if not platforms:
        platforms = ["workana", "gupy", "catho", "infojobs"]
        
    keyword = data.get("keyword", "Python")
    level = data.get("level", "Todos")
    location = data.get("location", "Todos")
    
    logger.info(f"Recebida ordem de Varredura! Plataformas: {platforms} | Keyword: {keyword} | Nível: {level}")
    
    async def run_single_scraper(plat):
        plat_raw = str(plat).lower().strip()
        plat_clean = PLATFORM_MODULE_MAP.get(plat_raw, plat_raw.replace(".", "_").replace(" ", "_"))
        try:
            logger.info(f"[{plat_clean.upper()}] Inicializando Scraper (Até 10 páginas)...")
            module = importlib.import_module(f"scrapers.{plat_clean}")
            sig = inspect.signature(module.scrape)
            candidate_kwargs = {
                "keyword": keyword,
                "level": level,
                "location": location,
                "country": location,
                "max_pages": 10
            }
            has_kwargs = any(p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values())
            if has_kwargs:
                kwargs = candidate_kwargs
            else:
                kwargs = {k: v for k, v in candidate_kwargs.items() if k in sig.parameters}

            if inspect.iscoroutinefunction(module.scrape):
                jobs = await module.scrape(**kwargs)
            else:
                jobs = await asyncio.to_thread(module.scrape, **kwargs)
            logger.info(f"[{plat_clean.upper()}] Sucesso! {len(jobs) if jobs else 0} vagas capturadas.")
            return jobs if isinstance(jobs, list) else []
        except Exception as e:
            logger.error(f"[{plat_clean.upper()}] Erro no scraper: {str(e)}")
            return []

    async def run_hunt_background():
        results = await asyncio.gather(*(run_single_scraper(p) for p in platforms))
        all_jobs = []
        for r in results:
            all_jobs.extend(r)

        try:
            from bot import is_job_relevant
            settings = {
                "level": level,
                "location": location,
                "contract": "Todos",
                "education": "Todos"
            }
            filtered_jobs = [job for job in all_jobs if is_job_relevant(job, keyword, settings)]
            inserted = await asyncio.to_thread(insert_jobs, filtered_jobs if filtered_jobs else all_jobs)
            logger.info(f"Varredura Finalizada! {len(all_jobs)} vagas totais. {inserted} novas salvas.")
        except Exception as e:
            logger.error(f"Erro ao salvar vagas no banco: {str(e)}")

    asyncio.create_task(run_hunt_background())
    return {"status": "success", "inserted": 0, "total_found": 0, "message": f"Caçada disparada em segundo plano para {keyword} ({level})!"}

@app.api_route("/api/search", methods=["GET", "POST"])
async def api_search(request: Request):
    """ 
    Endpoint para busca síncrona/direta de vagas.
    Usado quando o usuário solicita uma pesquisa imediata pelo painel web.
    """
    if request.method == "POST":
        try:
            data = await request.json()
        except Exception:
            data = {}
    else:
        data = dict(request.query_params)

    platforms = data.get("platforms", ["workana", "gupy", "catho", "infojobs"])
    if isinstance(platforms, str):
        platforms = [p.strip() for p in platforms.split(",")]
    keyword = data.get("keyword", "Python")
    level = data.get("level", "Todos")
    location = data.get("location", "Todos")

    async def fetch_plat_search(plat):
        plat_raw = str(plat).lower().strip()
        plat_clean = PLATFORM_MODULE_MAP.get(plat_raw, plat_raw.replace(".", "_").replace(" ", "_"))
        try:
            module = importlib.import_module(f"scrapers.{plat_clean}")
            if inspect.iscoroutinefunction(module.scrape):
                jobs = await module.scrape(keyword=keyword, level=level, location=location, country=location, max_pages=10)
            else:
                jobs = await asyncio.to_thread(module.scrape, keyword=keyword, level=level, location=location, country=location, max_pages=10)
            return jobs if isinstance(jobs, list) else []
        except Exception as e:
            logger.error(f"[{plat_clean.upper()}] Erro no scraper search: {str(e)}")
            return []

    results = await asyncio.gather(*(fetch_plat_search(p) for p in platforms))
    all_jobs = []
    for r in results:
        all_jobs.extend(r)

    try:
        from bot import is_job_relevant
        settings = {"level": level, "location": location, "contract": "Todos", "education": "Todos"}
        filtered_jobs = [job for job in all_jobs if is_job_relevant(job, keyword, settings)]
        jobs_to_save = filtered_jobs if filtered_jobs else all_jobs
        inserted = await asyncio.to_thread(insert_jobs, jobs_to_save)
        return {"status": "success", "total": len(all_jobs), "inserted": inserted, "jobs": jobs_to_save}
    except Exception as e:
        logger.error(f"Erro em api_search: {e}")
        return {"status": "error", "message": str(e), "jobs": all_jobs}

@app.get("/api/logs")
def get_logs():
    """ Retorna as últimas 100 linhas de log """
    try:
        if not os.path.exists(log_path):
            return {"logs": ["Nenhum log encontrado ainda."]}
            
        with open(log_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        last_lines = lines[-100:]
        return {"logs": last_lines}
    except Exception as e:
        return {"logs": [f"Erro ao ler logs: {e}"]}



async def run_initial_seed_search():
    """Executa buscas iniciais para popular todas as categorias de vagas."""
    from bot import classify_job_profession
    seed_keywords = [
        "Indústria", "Logística", "Administrativo", "Design", "Vendas", 
        "Engenharia de Dados", "Python", "Analytics Engineer", "IA-Ops", 
        "Growth Engineer", "React"
    ]
    platforms = ["workana", "gupy", "catho", "infojobs"]
    for kw in seed_keywords:
        for plat in platforms:
            try:
                module = importlib.import_module(f"scrapers.{plat}")
                if inspect.iscoroutinefunction(module.scrape):
                    jobs = await module.scrape(keyword=kw, level="Todos", location="Todos", country="Todos")
                else:
                    jobs = await asyncio.to_thread(module.scrape, keyword=kw, level="Todos", location="Todos", country="Todos")
                if isinstance(jobs, list) and jobs:
                    classified_jobs = [classify_job_profession(j) for j in jobs]
                    await asyncio.to_thread(insert_jobs, classified_jobs)
            except Exception as e:
                logger.error(f"Seed search error [{plat} - {kw}]: {e}")

async def background_periodic_hunt_loop():
    """Loop continuo que busca novas vagas a cada 10 minutos (600 segundos)."""
    from bot import classify_job_profession
    while True:
        await asyncio.sleep(600)
        logger.info("[BACKGROUND AUTO-HUNT] Executando busca automatizada periódica...")
        try:
            macro_keywords = [
                "Indústria", "Logística", "Administrativo", "Design", "Vendas", 
                "Engenharia de Dados", "Python", "IA-Ops"
            ]
            for kw in macro_keywords:
                for plat in ["workana", "gupy", "catho", "infojobs"]:
                    module = importlib.import_module(f"scrapers.{plat}")
                    if inspect.iscoroutinefunction(module.scrape):
                        jobs = await module.scrape(keyword=kw, level="Todos", location="Todos", country="Todos")
                    else:
                        jobs = await asyncio.to_thread(module.scrape, keyword=kw, level="Todos", location="Todos", country="Todos")
                    if isinstance(jobs, list) and jobs:
                        classified_jobs = [classify_job_profession(j) for j in jobs]
                        await asyncio.to_thread(insert_jobs, classified_jobs)
        except Exception as e:
            logger.error(f"Erro no loop de busca periódica: {e}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)


