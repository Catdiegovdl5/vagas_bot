import sys
import os
import sqlite3
import json

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from prioriti.database import get_connection
from prioriti.app import listar_vagas, remover_acentos

def verify_qa_category_integrity():
    print("=" * 70)
    print("🧪 INICIANDO BATERIA DE TESTES DE INTEGRIDADE DE CATEGORIAS E DASHBOARD (QA)")
    print("=" * 70)

    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    # 1. Total de vagas no banco
    c.execute("SELECT COUNT(*) FROM jobs")
    total_db = c.fetchone()[0]
    print(f"\n📊 Total de vagas registradas na tabela 'jobs': {total_db}")

    # 2. Testar busca geral da API sem filtro
    res_all = listar_vagas()
    total_api_all = res_all.get("total", 0)
    print(f"📊 Total retornado pela API sem filtros (/api/vagas): {total_api_all}")

    # 3. Teste de Exclusão Not Like (0% Vazamento de Designer em Gestor de Tráfego)
    print("\n🔍 Teste 1: Regras de Exclusão (Gestor de Tráfego vs Designer)")
    res_traffic = listar_vagas(categoria="gestor_trafego")
    jobs_traffic = res_traffic.get("jobs", [])
    
    designer_keywords = [
        "designer", "design", "webdesigner", "ui/ux", "ux/ui", 
        "arte finalista", "grafico", "gráfico", "motion", "videomaker"
    ]
    
    leak_count = 0
    leaked_jobs = []
    for j in jobs_traffic:
        title_lower = remover_acentos(j.get("title", ""))
        for dk in designer_keywords:
            dk_norm = remover_acentos(dk)
            if dk_norm in title_lower:
                leak_count += 1
                leaked_jobs.append((j.get("id"), j.get("title")))
                break

    total_traffic = len(jobs_traffic)
    leak_percentage = (leak_count / total_traffic * 100) if total_traffic > 0 else 0.0
    precision_percentage = 100.0 - leak_percentage

    print(f"  - Total de vagas de Gestor de Tráfego analisadas: {total_traffic}")
    print(f"  - Vazamentos detectados de cargos de Designer/Criativo puro: {leak_count}")
    print(f"  - Taxa de Vazamento: {leak_percentage:.2f}%")
    print(f"  - Precisão do Filtro de Gestão de Tráfego: {precision_percentage:.2f}%")

    if leak_count > 0:
        print("  ⚠️ Vagas vazadas detectadas:")
        for lid, ltitle in leaked_jobs[:5]:
            print(f"    - ID {lid}: {ltitle}")

    # 4. Soma de Contagens por Categorias Principais
    print("\n🔍 Teste 2: Validação de Mapeamento e Soma de Categorias")
    categories_to_check = [
        "gestor_trafego", "meta_ads", "google_ads", "dev_fullstack", 
        "python", "ia_ops", "sdr", "logistica", "administrativo"
    ]
    
    sum_individual = 0
    cat_counts = {}
    for cat in categories_to_check:
        r = listar_vagas(categoria=cat)
        cnt = r.get("total", 0)
        cat_counts[cat] = cnt
        sum_individual += cnt
        print(f"  • Categoria '{cat}': {cnt} vagas")

    print(f"\n  - Soma Total das Categorias Principais: {sum_individual}")

    # 5. Resumo Final de QA
    print("\n" + "=" * 70)
    print("📈 RELATÓRIO FINAL DE INTEGRIDADE E PRECISÃO DE CATEGORIAS")
    print("=" * 70)
    print(f"✅ Precisão do Filtro de Categoria (Sem Leaks): {precision_percentage:.2f}%")
    print(f"✅ Consistência da API de Busca: {'APROVADA' if total_api_all == total_db else 'DIVERGENTE'}")
    print("=" * 70)

if __name__ == "__main__":
    verify_qa_category_integrity()
