import urllib.request
import json
import sys
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from prioriti.database import get_connection

def run_qa_category_integrity_test():
    print("========================================================================")
    print("      TESTE DE INTEGRIDADE DE CATEGORIAS & EXCLUSÕES DE DESIGNER (QA)    ")
    print("========================================================================")

    # 1. Total DB Count
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM jobs")
    total_db_jobs = c.fetchone()[0]
    conn.close()
    print(f"\n[1] TOTAL DE VAGAS NO BANCO: {total_db_jobs}")

    # 2. Test Filters and Precision Percentage
    test_categories = [
        ("Gestor de Tráfego Geral", "http://localhost:8000/api/vagas?categoria=gestor_trafego"),
        ("Meta Ads / Social Ads", "http://localhost:8000/api/vagas?subcategoria=meta_ads"),
        ("Google Ads / Search", "http://localhost:8000/api/vagas?subcategoria=google_ads"),
        ("Media Buyer / Mídia Paga", "http://localhost:8000/api/vagas?subcategoria=media_buyer"),
        ("Growth & Performance", "http://localhost:8000/api/vagas?subcategoria=growth_performance"),
    ]

    print("\n[2] VERIFICAÇÃO DE PRECISÃO E LEAKS DE DESIGNER:")
    for label, url in test_categories:
        try:
            req = urllib.request.urlopen(url)
            data = json.loads(req.read().decode("utf-8"))
            jobs = data.get("jobs", [])
            total_matching = data.get("total", len(jobs))
            
            designer_leaks = [j["title"] for j in jobs if any(k in j["title"].lower() for k in ["designer", "design", "ui/ux", "videomaker"])]
            leak_count = len(designer_leaks)
            precision = 100.0 if len(jobs) == 0 else ((len(jobs) - leak_count) / len(jobs)) * 100.0
            
            print(f"  - [{label}]: {total_matching} vagas no banco | Retornadas: {len(jobs)} | Leaks: {leak_count} | Precisão: {precision:.1f}%")
        except Exception as e:
            print(f"  - [{label}]: Falha na requisição -> {e}")

    print("\n========================================================================")
    print("           VALIDAÇÃO DE INTEGRIDADE DE CATEGORIAS CONCLUÍDA             ")
    print("========================================================================")

if __name__ == "__main__":
    run_qa_category_integrity_test()
