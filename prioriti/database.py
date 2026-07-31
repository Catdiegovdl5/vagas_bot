import sqlite3
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
DB_PATH = os.path.join(PROJECT_ROOT, "jobs.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH, timeout=15)
    conn.execute('PRAGMA journal_mode=WAL')
    conn.execute('PRAGMA synchronous=NORMAL')
    conn.execute('PRAGMA busy_timeout=5000')
    return conn

def normalizar_senioridade(texto: str) -> str:
    """Mapeia textos brutos das vagas para os códigos padronizados do filtro: estagio, jr, pl, sr, lead."""
    if not texto:
        return 'nao_informado'
    import re
    t = str(texto).lower()
    if re.search(r'\b(estag|estág|trainee|intern)\b', t):
        return 'estagio'
    elif re.search(r'\b(jun|jún|jr|junior|júnior)\b', t):
        return 'jr'
    elif re.search(r'\b(plen|pl|pleno)\b', t):
        return 'pl'
    elif re.search(r'\b(sen|sên|sr|senior|sênior)\b', t):
        return 'sr'
    elif re.search(r'\b(lead|especialista|head|principal|coordenador|gerente)\b', t):
        return 'lead'
    return 'nao_informado'

# =====================================================================
# 🗄️ ABSTRAÇÃO DE MULTI-TENANCY PARA FUTURA TRANSIÇÃO POSTGRESQL RLS
# =====================================================================
class PostgresRLSTenantContext:
    """
    Gerenciador de contexto para PostgreSQL Row-Level Security (RLS).
    Executa `SET LOCAL app.current_tenant = tenant_id` dentro de uma transação.
    Ao fazer COMMIT/ROLLBACK, o PostgreSQL limpa o valor da variável de sessão automaticamente,
    evitando vazamento de contexto em conexões recicladas (PgBouncer/RDS Proxy).
    Se a conexão for SQLite, ignora silenciosamente os comandos RLS.
    """
    def __init__(self, conn, tenant_id: str):
        self.conn = conn
        self.tenant_id = str(tenant_id)
        self.is_sqlite = "sqlite" in type(conn).__module__.lower() or "sqlite" in type(conn).__name__.lower()

    def __enter__(self):
        if not self.is_sqlite:
            try:
                cursor = self.conn.cursor()
                cursor.execute("SET LOCAL app.current_tenant = %s;", (self.tenant_id,))
            except Exception:
                pass
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self.is_sqlite:
            try:
                cursor = self.conn.cursor()
                cursor.execute("RESET app.current_tenant;")
            except Exception:
                pass

def init_db():
    conn = get_connection()
    try:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY,
                title TEXT,
                company TEXT,
                budget TEXT,
                link TEXT,
                platform TEXT,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        try: c.execute('ALTER TABLE jobs ADD COLUMN job_type TEXT')
        except: pass
        try: c.execute('ALTER TABLE jobs ADD COLUMN profession TEXT')
        except: pass
        try: c.execute('ALTER TABLE jobs ADD COLUMN level TEXT')
        except: pass
        try: c.execute('ALTER TABLE jobs ADD COLUMN requirements TEXT')
        except: pass
        try: c.execute('ALTER TABLE jobs ADD COLUMN location TEXT')
        except: pass
        try: c.execute('ALTER TABLE jobs ADD COLUMN lat REAL')
        except: pass
        try: c.execute('ALTER TABLE jobs ADD COLUMN lon REAL')
        except: pass
        try: c.execute('ALTER TABLE jobs ADD COLUMN lang TEXT')
        except: pass
        # Tabela de vagas onde o usuário já se candidatou
        c.execute('''
            CREATE TABLE IF NOT EXISTS applied_jobs (
                link TEXT PRIMARY KEY,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # Tabela de vagas ignoradas/rejeitadas pelo filtro ou usuário
        c.execute('''
            CREATE TABLE IF NOT EXISTS ignored_jobs (
                link TEXT PRIMARY KEY,
                reason TEXT,
                ignored_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # Tabela de pagamentos processados (Idempotência Persistida)
        c.execute('''
            CREATE TABLE IF NOT EXISTS processed_payments (
                payment_id TEXT PRIMARY KEY,
                user_id TEXT,
                amount REAL,
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        c.execute('CREATE INDEX IF NOT EXISTS idx_jobs_added_at ON jobs(added_at)')
        conn.commit()
    finally:
        conn.close()
    init_career_db()
    init_saas_db()

def register_payment_if_new(payment_id: str, user_id: str, amount: float = 39.90) -> bool:
    """Registra pagamento de forma atômica/idempotente. Retorna True se novo, False se já processado."""
    conn = get_connection()
    try:
        c = conn.cursor()
        c.execute('INSERT INTO processed_payments (payment_id, user_id, amount) VALUES (?, ?, ?)', (str(payment_id), str(user_id), float(amount)))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

import math

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calcula a distância em KM entre duas coordenadas geográficas utilizando a Fórmula de Haversine."""
    if lat1 is None or lon1 is None or lat2 is None or lon2 is None:
        return 999999.0
    R = 6371.0  # Raio da Terra em KM
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def insert_jobs(jobs):
    if not isinstance(jobs, list):
        return 0
    conn = get_connection()
    try:
        c = conn.cursor()
        inserted = 0
        for job in jobs:
            if not isinstance(job, dict):
                continue
            try:
                link = job.get('link') or ''
                title = job.get('title') or ''
                platform = job.get('platform') or ''
                if not link or not title or not platform or link == '#':
                    continue
                raw_prof = job.get('profession') or ''
                if isinstance(raw_prof, (tuple, list)):
                    raw_prof = str(raw_prof[0]) if raw_prof else ''
                else:
                    raw_prof = str(raw_prof)

                from scrapers.ai_filter import classify_profession_fallback
                clean_prof = classify_profession_fallback(title, raw_prof)
                if isinstance(clean_prof, (tuple, list)):
                    clean_profession = str(clean_prof[0]) if clean_prof else 'Outros'
                else:
                    clean_profession = str(clean_prof) if clean_prof else (raw_prof or 'Outros')

                clean_profession = str(clean_profession)

                c.execute('INSERT INTO jobs (id, title, company, budget, link, platform, job_type, profession, level, requirements, location, lat, lon, lang) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                          (link, title, job.get('company') or 'N/A', job.get('budget') or 'A combinar', link, platform, job.get('job_type') or 'CLT', clean_profession, job.get('level') or 'Todos', job.get('requirements') or 'Requisitos descritos no link da vaga.', job.get('location') or 'Remoto/Brasil', job.get('lat'), job.get('lon'), job.get('lang') or 'pt'))
                inserted += 1
            except sqlite3.IntegrityError:
                pass # duplicate
        conn.commit()
        return inserted
    finally:
        conn.close()

def get_jobs(include_all: bool = True, lat: float = None, lon: float = None, radius: float = 50.0):
    conn = get_connection()
    try:
        c = conn.cursor()
        c.execute('''
            SELECT j.title, j.company, j.budget, j.link, j.platform, j.added_at, j.job_type, j.profession, j.level, j.requirements,
                   CASE 
                       WHEN a.link IS NOT NULL THEN 'Aplicado'
                       WHEN i.link IS NOT NULL THEN 'Ignorado'
                       ELSE 'Disponível'
                   END as status,
                   j.location, j.lat, j.lon, j.lang
            FROM jobs j
            LEFT JOIN applied_jobs a ON j.link = a.link
            LEFT JOIN ignored_jobs i ON j.link = i.link
            ORDER BY j.added_at DESC
        ''')
        rows = c.fetchall()
        
        jobs = []
        for r in rows:
            j_lat = r[12]
            j_lon = r[13]
            dist_km = None
            if lat is not None and lon is not None and j_lat is not None and j_lon is not None:
                dist_km = haversine_distance(float(lat), float(lon), float(j_lat), float(j_lon))
                if radius and dist_km > float(radius):
                    continue  # Filtra vagas fora do raio de proximidade solicitado

            jobs.append({
                "title": r[0] if r[0] is not None else "Vaga Sem Título",
                "company": r[1] if r[1] is not None else "Empresa Confidencial",
                "budget": r[2] if r[2] is not None else "A combinar",
                "link": r[3] if r[3] is not None else "#",
                "platform": r[4] if r[4] is not None else "Geral",
                "added_at": r[5] if r[5] is not None else "",
                "job_type": r[6] if r[6] is not None else "CLT",
                "profession": r[7] if r[7] is not None else "Outros",
                "level": r[8] if r[8] is not None else "Todos",
                "requirements": r[9] if r[9] is not None else "Requisitos na página.",
                "status": r[10] if r[10] is not None else "Disponível",
                "location": r[11] if r[11] is not None else "Remoto/Brasil",
                "lat": j_lat,
                "lon": j_lon,
                "lang": r[14] if r[14] is not None else "pt",
                "distance_km": round(dist_km, 1) if dist_km is not None else None
            })
        return jobs
    finally:
        conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized.")

# Alias para compatibilidade
get_all_jobs = get_jobs

def is_applied(link: str) -> bool:
    """Retorna True se o usuário já se candidatou a essa vaga."""
    conn = get_connection()
    try:
        c = conn.cursor()
        c.execute('SELECT 1 FROM applied_jobs WHERE link = ?', (link,))
        return c.fetchone() is not None
    finally:
        conn.close()

def mark_applied(link: str):
    """Marca uma vaga como 'já candidatado'."""
    conn = get_connection()
    try:
        c = conn.cursor()
        c.execute('INSERT OR IGNORE INTO applied_jobs (link) VALUES (?)', (link,))
        conn.commit()
    finally:
        conn.close()

def mark_ignored(link: str, reason: str):
    """Marca uma vaga como 'ignorada' permanentemente."""
    conn = get_connection()
    try:
        c = conn.cursor()
        c.execute('INSERT OR REPLACE INTO ignored_jobs (link, reason) VALUES (?, ?)', (link, reason))
        conn.commit()
    finally:
        conn.close()

def init_career_db():
    """Inicializa a tabela user_career_progress no banco de dados de forma idempotente."""
    conn = get_connection()
    try:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS user_career_progress (
                user_id TEXT NOT NULL,
                profession_id TEXT NOT NULL,
                step_id TEXT NOT NULL,
                status INTEGER DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, profession_id, step_id)
            )
        ''')
        c.execute('''
            CREATE INDEX IF NOT EXISTS idx_user_career_progress_lookup 
            ON user_career_progress (user_id, profession_id)
        ''')
        conn.commit()
    finally:
        conn.close()

def save_user_step_status(user_id, profession_id: str, step_id: str, status: int = 1) -> bool:
    """
    Salva ou atualiza o status de progresso do usuário em uma etapa de carreira.
    Utiliza UPSERT idempotente para evitar duplicação.
    """
    conn = get_connection()
    try:
        c = conn.cursor()
        c.execute('''
            INSERT INTO user_career_progress (user_id, profession_id, step_id, status, updated_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id, profession_id, step_id) DO UPDATE SET
                status = excluded.status,
                updated_at = CURRENT_TIMESTAMP
        ''', (str(user_id), str(profession_id), str(step_id), int(status)))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def get_user_career_progress(user_id, profession_id: str = None) -> dict:
    """
    Recupera o progresso de carreira do usuário.
    Se profession_id for informado: {step_id: {"status": int, "updated_at": str}}
    Se profession_id for None: {profession_id: {step_id: {"status": int, "updated_at": str}}}
    """
    conn = get_connection()
    try:
        c = conn.cursor()
        if profession_id:
            c.execute('''
                SELECT step_id, status, updated_at
                FROM user_career_progress
                WHERE user_id = ? AND profession_id = ?
            ''', (str(user_id), str(profession_id)))
            rows = c.fetchall()
            return {row[0]: {"status": row[1], "updated_at": row[2]} for row in rows}
        else:
            c.execute('''
                SELECT profession_id, step_id, status, updated_at
                FROM user_career_progress
                WHERE user_id = ?
            ''', (str(user_id),))
            rows = c.fetchall()
            result = {}
            for prof, step, stat, updated in rows:
                if prof not in result:
                    result[prof] = {}
                result[prof][step] = {"status": stat, "updated_at": updated}
            return result
    finally:
        conn.close()

def toggle_user_step_status(user_id, profession_id: str, step_id: str) -> int:
    """
    Alterna o status da etapa (0 -> 1 ou 1 -> 0) e salva no banco.
    Retorna o novo status (0 ou 1).
    """
    progress = get_user_career_progress(user_id, profession_id)
    step_info = progress.get(str(step_id), {})
    current_status = step_info.get("status", 0) if isinstance(step_info, dict) else int(step_info)
    new_status = 0 if current_status == 1 else 1
    save_user_step_status(user_id, profession_id, step_id, new_status)
    return new_status

def get_career_step_status(user_id, profession_id: str, step_id: str) -> bool:
    """Retorna True se a etapa específica foi concluída (status=1)."""
    progress = get_user_career_progress(user_id, profession_id)
    step_info = progress.get(str(step_id), {})
    stat = step_info.get("status", 0) if isinstance(step_info, dict) else int(step_info)
    return stat == 1

save_career_step_status = save_user_step_status


# ─────────────────────────────────────────────────────────────
# SaaS PLATFORM — Novas tabelas e funções
# ─────────────────────────────────────────────────────────────

def init_saas_db():
    """Inicializa as tabelas da plataforma SaaS: perfis, candidaturas, planos e stats."""
    conn = get_connection()
    try:
        c = conn.cursor()

        # Perfis de usuário (currículo + plano)
        c.execute('''
            CREATE TABLE IF NOT EXISTS user_profiles (
                user_id     TEXT PRIMARY KEY,
                full_name   TEXT,
                email       TEXT,
                phone       TEXT,
                skills      TEXT,
                experience  TEXT,
                education   TEXT,
                resume_text TEXT,
                plan        TEXT DEFAULT 'free',
                daily_hunts INTEGER DEFAULT 0,
                last_hunt_date TEXT,
                created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Candidaturas registradas (com ou sem autocandidatura)
        c.execute('''
            CREATE TABLE IF NOT EXISTS job_applications (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     TEXT NOT NULL,
                job_url     TEXT NOT NULL,
                job_title   TEXT,
                company     TEXT,
                platform    TEXT,
                applied_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                method      TEXT DEFAULT 'manual',
                status      TEXT DEFAULT 'applied',
                UNIQUE(user_id, job_url)
            )
        ''')

        # Tabela de sessões do copiloto de propostas (histórico de chat por vaga)
        c.execute('''
            CREATE TABLE IF NOT EXISTS proposal_sessions (
                session_id  TEXT PRIMARY KEY,
                user_id     TEXT NOT NULL,
                job_title   TEXT,
                job_requirements TEXT,
                history_json TEXT,
                updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        c.execute('CREATE INDEX IF NOT EXISTS idx_proposal_sessions_user ON proposal_sessions(user_id)')

        # Scores de compatibilidade IA por vaga
        c.execute('''
            CREATE TABLE IF NOT EXISTS ai_compatibility (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     TEXT NOT NULL,
                job_url     TEXT NOT NULL,
                score       INTEGER,
                justification TEXT,
                cover_letter  TEXT,
                created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, job_url)
            )
        ''')

        # Estatísticas de busca por usuário/dia (para dashboard)
        c.execute('''
            CREATE TABLE IF NOT EXISTS search_stats (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     TEXT,
                keyword     TEXT,
                platform    TEXT,
                jobs_found  INTEGER DEFAULT 0,
                searched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
    finally:
        conn.close()

    # Migração: adiciona coluna groq_api_key se não existir
    conn2 = get_connection()
    try:
        c2 = conn2.cursor()
        try:
            c2.execute('ALTER TABLE user_profiles ADD COLUMN groq_api_key TEXT')
            conn2.commit()
        except Exception:
            pass  # Coluna já existe
    finally:
        conn2.close()


# ── Perfis de Usuário ──────────────────────────────────────

def get_user_profile(user_id: str) -> dict:
    """Retorna o perfil completo do usuário ou None se não existir."""
    conn = get_connection()
    try:
        c = conn.cursor()
        c.execute('SELECT * FROM user_profiles WHERE user_id = ?', (str(user_id),))
        row = c.fetchone()
        if not row:
            return {}
        cols = [d[0] for d in c.description]
        return dict(zip(cols, row))
    finally:
        conn.close()

def upsert_user_profile(user_id: str, **kwargs) -> bool:
    """Cria ou atualiza o perfil do usuário com os campos fornecidos."""
    conn = get_connection()
    try:
        c = conn.cursor()
        # Garante que o registro existe
        c.execute('INSERT OR IGNORE INTO user_profiles (user_id) VALUES (?)', (str(user_id),))
        # Atualiza os campos fornecidos
        for field, value in kwargs.items():
            c.execute(f'UPDATE user_profiles SET {field} = ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?',
                      (value, str(user_id)))
        conn.commit()
        return True
    finally:
        conn.close()

def get_user_plan(user_id: str) -> str:
    """Retorna o plano do usuário: 'free' ou 'premium'."""
    profile = get_user_profile(user_id)
    return profile.get('plan', 'free')

def set_user_plan(user_id: str, plan: str) -> bool:
    """Define o plano do usuário ('free' ou 'premium')."""
    return upsert_user_profile(user_id, plan=plan)

def is_premium(user_id: str) -> bool:
    """Retorna True se o usuário tem plano premium."""
    return get_user_plan(str(user_id)) == 'premium'

def check_and_increment_daily_hunts(user_id: str, limit: int = 5) -> bool:
    """
    Verifica se o usuário Free ainda pode fazer buscas hoje.
    Incrementa o contador e retorna True se permitido, False se atingiu o limite.
    """
    if is_premium(user_id):
        return True  # Premium: ilimitado
    conn = get_connection()
    try:
        c = conn.cursor()
        c.execute('SELECT daily_hunts, last_hunt_date FROM user_profiles WHERE user_id = ?', (str(user_id),))
        row = c.fetchone()
        if not row:
            upsert_user_profile(user_id)
            row = (0, None)
        hunts, last_date = row
        import datetime
        today = datetime.date.today().isoformat()
        if last_date != today:
            hunts = 0  # Reinicia contador no novo dia
        if hunts >= limit:
            return False
        c.execute('UPDATE user_profiles SET daily_hunts = ?, last_hunt_date = ? WHERE user_id = ?',
                  (hunts + 1, today, str(user_id)))
        conn.commit()
        return True
    finally:
        conn.close()


# ── Candidaturas ──────────────────────────────────────────

def register_application(user_id: str, job_url: str, job_title: str = '', company: str = '',
                          platform: str = '', method: str = 'manual') -> bool:
    """Registra uma candidatura do usuário a uma vaga."""
    conn = get_connection()
    try:
        c = conn.cursor()
        c.execute('''
            INSERT OR IGNORE INTO job_applications (user_id, job_url, job_title, company, platform, method)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (str(user_id), job_url, job_title, company, platform, method))
        conn.commit()
        return c.rowcount > 0
    finally:
        conn.close()

def get_user_applications(user_id: str) -> list:
    """Retorna todas as candidaturas do usuário."""
    conn = get_connection()
    try:
        c = conn.cursor()
        c.execute('''
            SELECT job_url, job_title, company, platform, applied_at, method, status
            FROM job_applications WHERE user_id = ? ORDER BY applied_at DESC
        ''', (str(user_id),))
        cols = ['job_url', 'job_title', 'company', 'platform', 'applied_at', 'method', 'status']
        return [dict(zip(cols, row)) for row in c.fetchall()]
    finally:
        conn.close()


# ── AI Compatibility & Cover Letters ─────────────────────

def save_ai_score(user_id: str, job_url: str, score: int,
                  justification: str = '', cover_letter: str = '') -> bool:
    """Salva o score de compatibilidade e cover letter gerada pela IA."""
    conn = get_connection()
    try:
        c = conn.cursor()
        c.execute('''
            INSERT INTO ai_compatibility (user_id, job_url, score, justification, cover_letter)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(user_id, job_url) DO UPDATE SET
                score = excluded.score,
                justification = excluded.justification,
                cover_letter = excluded.cover_letter,
                created_at = CURRENT_TIMESTAMP
        ''', (str(user_id), job_url, score, justification, cover_letter))
        conn.commit()
        return True
    finally:
        conn.close()

def get_ai_score(user_id: str, job_url: str) -> dict:
    """Recupera o score de compatibilidade salvo para uma vaga."""
    conn = get_connection()
    try:
        c = conn.cursor()
        c.execute('SELECT score, justification, cover_letter FROM ai_compatibility WHERE user_id = ? AND job_url = ?',
                  (str(user_id), job_url))
        row = c.fetchone()
        if not row:
            return {}
        return {'score': row[0], 'justification': row[1], 'cover_letter': row[2]}
    finally:
        conn.close()


# ── Search Stats (Dashboard) ──────────────────────────────

def log_search_stat(user_id: str, keyword: str, platform: str, jobs_found: int):
    """Registra estatísticas de uma busca para o dashboard."""
    conn = get_connection()
    try:
        c = conn.cursor()
        c.execute('INSERT INTO search_stats (user_id, keyword, platform, jobs_found) VALUES (?, ?, ?, ?)',
                  (str(user_id), keyword, platform, jobs_found))
        conn.commit()
    finally:
        conn.close()

def get_dashboard_stats() -> dict:
    """Retorna estatísticas agregadas para o painel admin."""
    conn = get_connection()
    try:
        c = conn.cursor()
        stats = {}

        # Total de usuários únicos
        c.execute('SELECT COUNT(DISTINCT user_id) FROM user_profiles')
        stats['total_users'] = c.fetchone()[0] or 0

        # Usuários premium
        c.execute("SELECT COUNT(*) FROM user_profiles WHERE plan = 'premium'")
        stats['premium_users'] = c.fetchone()[0] or 0

        # Total de vagas no banco
        c.execute('SELECT COUNT(*) FROM jobs')
        stats['total_jobs'] = c.fetchone()[0] or 0

        # Total de candidaturas
        c.execute('SELECT COUNT(*) FROM job_applications')
        stats['total_applications'] = c.fetchone()[0] or 0

        # Vagas por plataforma (top 10)
        c.execute('''
            SELECT platform, COUNT(*) as cnt FROM jobs
            GROUP BY platform ORDER BY cnt DESC LIMIT 10
        ''')
        stats['jobs_by_platform'] = [{'platform': r[0], 'count': r[1]} for r in c.fetchall()]

        # Buscas por dia (últimos 7 dias)
        c.execute('''
            SELECT DATE(searched_at) as day, SUM(jobs_found) as total
            FROM search_stats
            WHERE searched_at >= DATE('now', '-7 days')
            GROUP BY day ORDER BY day
        ''')
        stats['daily_searches'] = [{'day': r[0], 'jobs_found': r[1]} for r in c.fetchall()]

        return stats
    finally:
        conn.close()


# ─────────────────────────────────────────────────────────────
# CONFORMIDADE LGPD BRASIL (Exportação e Purga de Dados)
# ─────────────────────────────────────────────────────────────

def export_user_data_lgpd(user_id: str) -> dict:
    """Consolida todos os dados pessoais e históricos vinculados ao user_id para portabilidade LGPD."""
    user_str = str(user_id)
    profile = get_user_profile(user_str)
    career = get_user_career_progress(user_str)
    applications = get_user_applications(user_str)
    
    conn = get_connection()
    try:
        c = conn.cursor()
        c.execute('SELECT job_url, score, justification, cover_letter, created_at FROM ai_compatibility WHERE user_id = ?', (user_str,))
        ai_records = [{'job_url': r[0], 'score': r[1], 'justification': r[2], 'cover_letter': r[3], 'created_at': r[4]} for r in c.fetchall()]
    finally:
        conn.close()
        
    return {
        "lgpd_export_timestamp": os.getenv("CURRENT_TIME", "2026-07-27"),
        "user_profile": profile,
        "career_progress": career,
        "applications": applications,
        "ai_evaluations": ai_records
    }

def purge_user_data_lgpd(user_id: str) -> bool:
    """Exclui de forma atômica e irreversível todos os dados pessoais do usuário (Cumprimento LGPD)."""
    user_str = str(user_id)
    conn = get_connection()
    try:
        c = conn.cursor()
        c.execute('DELETE FROM user_profiles WHERE user_id = ?', (user_str,))
        c.execute('DELETE FROM user_career_progress WHERE user_id = ?', (user_str,))
        c.execute('DELETE FROM job_applications WHERE user_id = ?', (user_str,))
        c.execute('DELETE FROM ai_compatibility WHERE user_id = ?', (user_str,))
        c.execute('DELETE FROM search_stats WHERE user_id = ?', (user_str,))
        c.execute('DELETE FROM processed_payments WHERE user_id = ?', (user_str,))
        conn.commit()
        
        # Remover arquivo de currículo TXT se existente
        curriculo_file = os.path.join(os.path.dirname(__file__), f"curriculo_{user_str}.txt")
        if os.path.exists(curriculo_file):
            try:
                os.remove(curriculo_file)
            except Exception:
                pass
                
        return True
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def save_proposal_session(session_id: str, user_id: str, job_title: str, job_requirements: str, history_list: list) -> bool:
    """Salva ou atualiza uma sessão do copiloto de propostas encapsulada por user_id."""
    import json
    conn = get_connection()
    try:
        with PostgresRLSTenantContext(conn, user_id):
            c = conn.cursor()
            c.execute('''
                INSERT INTO proposal_sessions (session_id, user_id, job_title, job_requirements, history_json, updated_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(session_id) DO UPDATE SET
                    history_json = excluded.history_json,
                    updated_at = CURRENT_TIMESTAMP
            ''', (session_id, str(user_id), job_title, job_requirements, json.dumps(history_list, ensure_ascii=False)))
            conn.commit()
            return True
    finally:
        conn.close()

def get_proposal_session(session_id: str, user_id: str) -> dict:
    """Recupera uma sessão do copiloto de propostas sob o escopo RLS do user_id."""
    import json
    conn = get_connection()
    try:
        with PostgresRLSTenantContext(conn, user_id):
            c = conn.cursor()
            c.execute('SELECT session_id, user_id, job_title, job_requirements, history_json FROM proposal_sessions WHERE session_id = ? AND user_id = ?', (session_id, str(user_id)))
            row = c.fetchone()
            if not row:
                return {}
            return {
                "session_id": row[0],
                "user_id": row[1],
                "job_title": row[2],
                "job_requirements": row[3],
                "history": json.loads(row[4]) if row[4] else []
            }
    finally:
        conn.close()


