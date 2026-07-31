import sqlite3
import unicodedata
import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    from prioriti.database import get_connection
except ImportError:
    from database import get_connection

def remover_acentos(texto: str) -> str:
    """Remove acentos e padroniza para caixa baixa."""
    if not texto:
        return ""
    nfkd = unicodedata.normalize('NFKD', texto)
    return "".join([c for c in nfkd if not unicodedata.combining(c)]).lower().strip()

def classificar_senioridade_precisa(titulo: str, descricao: str = "") -> str:
    """
    Regra de Precedência de Título (Padrão GitHub / Open Source):
    O Título é soberano sobre a Descrição.
    Evita que 'Lead Designer' ou 'Sênior' apareça no filtro Júnior só porque a descrição disse 'iniciante'.
    """
    t = remover_acentos(titulo)
    d = remover_acentos(descricao)

    # 1. VERIFICAÇÃO NO TÍTULO (MÁXIMA PRIORIDADE)
    if any(k in t for k in ['lead', 'especialista', 'head', 'coordenador', 'gerente', 'director', 'diretor', 'principal', 'tech lead']):
        return 'lead'
    elif any(k in t for k in ['senior', 'senr', 'sr', 'snr']):
        return 'sr'
    elif any(k in t for k in ['pleno', 'pl']):
        return 'pl'
    elif any(k in t for k in ['junior', 'jr', 'estagio', 'estag', 'trainee', 'iniciante', 'assistant', 'auxiliar']):
        return 'jr'

    # 2. VERIFICAÇÃO NA DESCRIÇÃO (APENAS SE O TÍTULO FOR NEUTRO)
    if any(k in d for k in ['vaga senior', 'nivel senior', 'senioridade: senior', 'requisitos: senior', 'perfil senior']):
        return 'sr'
    elif any(k in d for k in ['vaga pleno', 'nivel pleno', 'senioridade: pleno', 'perfil pleno']):
        return 'pl'
    elif any(k in d for k in ['vaga junior', 'nivel junior', 'para iniciante', 'sem experiencia', 'primeiro emprego']):
        return 'jr'

    return 'jr'  # Padrão para vagas sem especificação clara

def normalizar_banco_dados():
    """Garante que a tabela jobs em jobs.db tenha a coluna senioridade_norm e atualiza todos os registros."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Adiciona a coluna senioridade_norm se não existir
    try:
        cursor.execute("ALTER TABLE jobs ADD COLUMN senioridade_norm TEXT")
        conn.commit()
        print("Criada nova coluna senioridade_norm na tabela jobs.")
    except sqlite3.OperationalError:
        pass  # Coluna já existe

    # Busca todas as vagas do banco (incluindo as que estão None)
    cursor.execute("SELECT id, title, COALESCE(requirements, '') FROM jobs WHERE senioridade_norm IS NULL OR level IS NULL OR level = 'nao_informado'")
    rows = cursor.fetchall()
    
    if rows:
        updates = []
        for vaga_id, titulo, descricao in rows:
            senioridade_correta = classificar_senioridade_precisa(titulo or "", descricao or "")
            updates.append((senioridade_correta, senioridade_correta, vaga_id))
            
        cursor.executemany("UPDATE jobs SET senioridade_norm = ?, level = ? WHERE id = ?", updates)
        conn.commit()
        print(f"[OK] {len(rows)} novas vagas normalizadas com sucesso no banco de dados!")
    else:
        print("[OK] Todas as vagas no banco de dados já possuem senioridade_norm definida.")

    conn.close()

if __name__ == "__main__":
    normalizar_banco_dados()
