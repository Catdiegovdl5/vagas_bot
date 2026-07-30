"""
test_all_platforms.py
Testa os scrapers: coodesh, geekhunter, programathor, indeed, glassdoor, infojobs
com keyword='gestor de trafego' e exibe placar final.
"""

import sys
import os
import asyncio
import time

# Garante que o diretório raiz do projeto está no path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scrapers import coodesh, geekhunter, programathor, indeed, glassdoor, infojobs

# Importa is_job_relevant do bot.py
try:
    from bot import is_job_relevant
    HAS_BOT = True
except Exception as e:
    print(f"[AVISO] Não foi possível importar is_job_relevant de bot.py: {e}")
    HAS_BOT = False

KEYWORD = "gestor de trafego"
SETTINGS = {
    "level": "Todos",
    "location": "Remoto",
    "contract": "Todos",
}

TIMEOUT_PER_SCRAPER = 90  # segundos


def run_sync_scraper(name, fn, *args, **kwargs):
    """Executa um scraper síncrono com timeout via thread."""
    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(fn, *args, **kwargs)
        try:
            result = future.result(timeout=TIMEOUT_PER_SCRAPER)
            return result
        except concurrent.futures.TimeoutError:
            print(f"  [{name}] TIMEOUT após {TIMEOUT_PER_SCRAPER}s")
            return []
        except Exception as e:
            print(f"  [{name}] ERRO: {e}")
            return []


async def run_async_scraper(name, fn, *args, **kwargs):
    """Executa um scraper assíncrono com timeout."""
    try:
        result = await asyncio.wait_for(fn(*args, **kwargs), timeout=TIMEOUT_PER_SCRAPER)
        return result
    except asyncio.TimeoutError:
        print(f"  [{name}] TIMEOUT após {TIMEOUT_PER_SCRAPER}s")
        return []
    except Exception as e:
        print(f"  [{name}] ERRO: {e}")
        return []


def count_relevant(jobs):
    if not HAS_BOT:
        return "N/A"
    return sum(1 for j in jobs if is_job_relevant(j, KEYWORD, SETTINGS))


def print_separator():
    print("-" * 70)


async def main():
    print("=" * 70)
    print(f"  TESTE DE PLATAFORMAS — keyword: '{KEYWORD}'")
    print("=" * 70)
    print()

    results = {}

    # ── 1. Coodesh (síncrono) ────────────────────────────────────────────
    print("[1/6] Coodesh (API JSON) ...")
    t0 = time.time()
    jobs_coodesh = run_sync_scraper("Coodesh", coodesh.scrape, KEYWORD, level="Todos", country="Brasil")
    elapsed = time.time() - t0
    print(f"  Vagas brutas: {len(jobs_coodesh)} | Tempo: {elapsed:.1f}s")
    if jobs_coodesh:
        print(f"  Primeiro resultado: {jobs_coodesh[0].get('title', '?')} — {jobs_coodesh[0].get('company', '?')}")
    rel = count_relevant(jobs_coodesh)
    results["Coodesh"] = {"raw": len(jobs_coodesh), "relevant": rel, "elapsed": elapsed}
    print_separator()

    # ── 2. GeekHunter (síncrono / HTML) ──────────────────────────────────
    print("[2/6] GeekHunter (HTML scraper) ...")
    t0 = time.time()
    jobs_gh = run_sync_scraper("GeekHunter", geekhunter.scrape, KEYWORD, level="Todos", country="Brasil")
    elapsed = time.time() - t0
    print(f"  Vagas brutas: {len(jobs_gh)} | Tempo: {elapsed:.1f}s")
    if jobs_gh:
        print(f"  Primeiro resultado: {jobs_gh[0].get('title', '?')} — {jobs_gh[0].get('company', '?')}")
    rel = count_relevant(jobs_gh)
    results["GeekHunter"] = {"raw": len(jobs_gh), "relevant": rel, "elapsed": elapsed}
    print_separator()

    # ── 3. ProgramaThor (síncrono / HTML) ────────────────────────────────
    print("[3/6] ProgramaThor (HTML scraper) ...")
    t0 = time.time()
    jobs_pt = run_sync_scraper("ProgramaThor", programathor.scrape, KEYWORD, level="Todos", country="Brasil")
    elapsed = time.time() - t0
    print(f"  Vagas brutas: {len(jobs_pt)} | Tempo: {elapsed:.1f}s")
    if jobs_pt:
        print(f"  Primeiro resultado: {jobs_pt[0].get('title', '?')} — {jobs_pt[0].get('company', '?')}")
    rel = count_relevant(jobs_pt)
    results["ProgramaThor"] = {"raw": len(jobs_pt), "relevant": rel, "elapsed": elapsed}
    print_separator()

    # ── 4. Indeed (síncrono / Playwright) ────────────────────────────────
    print("[4/6] Indeed (Playwright) ...")
    t0 = time.time()
    jobs_indeed = run_sync_scraper("Indeed", indeed.scrape, KEYWORD, level="Todos", country="Brasil")
    elapsed = time.time() - t0
    print(f"  Vagas brutas: {len(jobs_indeed)} | Tempo: {elapsed:.1f}s")
    if jobs_indeed:
        print(f"  Primeiro resultado: {jobs_indeed[0].get('title', '?')} — {jobs_indeed[0].get('company', '?')}")
    rel = count_relevant(jobs_indeed)
    results["Indeed"] = {"raw": len(jobs_indeed), "relevant": rel, "elapsed": elapsed}
    print_separator()

    # ── 5. Glassdoor (síncrono / Playwright) ─────────────────────────────
    print("[5/6] Glassdoor (Playwright) ...")
    t0 = time.time()
    jobs_gd = run_sync_scraper("Glassdoor", glassdoor.scrape, KEYWORD, level="Todos", country="Brasil")
    elapsed = time.time() - t0
    print(f"  Vagas brutas: {len(jobs_gd)} | Tempo: {elapsed:.1f}s")
    if jobs_gd:
        print(f"  Primeiro resultado: {jobs_gd[0].get('title', '?')} — {jobs_gd[0].get('company', '?')}")
    rel = count_relevant(jobs_gd)
    results["Glassdoor"] = {"raw": len(jobs_gd), "relevant": rel, "elapsed": elapsed}
    print_separator()

    # ── 6. InfoJobs (assíncrono / Playwright) ────────────────────────────
    print("[6/6] InfoJobs (async Playwright) ...")
    t0 = time.time()
    jobs_ij = await run_async_scraper("InfoJobs", infojobs.scrape, KEYWORD, level="Todos", country="Brasil")
    elapsed = time.time() - t0
    print(f"  Vagas brutas: {len(jobs_ij)} | Tempo: {elapsed:.1f}s")
    if jobs_ij:
        print(f"  Primeiro resultado: {jobs_ij[0].get('title', '?')} — {jobs_ij[0].get('company', '?')}")
    rel = count_relevant(jobs_ij)
    results["InfoJobs"] = {"raw": len(jobs_ij), "relevant": rel, "elapsed": elapsed}
    print_separator()

    # ── PLACAR FINAL ──────────────────────────────────────────────────────
    print()
    print("=" * 70)
    print(f"  PLACAR FINAL — keyword: '{KEYWORD}'")
    print("=" * 70)
    header = f"{'Plataforma':<15} {'Vagas Brutas':>13} {'Relevantes':>12} {'Tempo':>8}"
    print(header)
    print("-" * 52)
    total_raw = 0
    total_rel = 0
    for name, data in results.items():
        raw = data["raw"]
        rel = data["relevant"]
        elapsed = data["elapsed"]
        rel_str = str(rel) if rel != "N/A" else "N/A"
        print(f"  {name:<13} {raw:>13} {rel_str:>12} {elapsed:>7.1f}s")
        total_raw += raw
        if rel != "N/A":
            total_rel += rel
    print("-" * 52)
    print(f"  {'TOTAL':<13} {total_raw:>13} {total_rel:>12}")
    print("=" * 70)
    print()

    if total_raw == 0:
        print("[AVISO] Nenhuma vaga encontrada em nenhuma plataforma.")
        print("  Possíveis causas: sem conexão à internet, Playwright não instalado,")
        print("  ou as plataformas bloquearam o scraper.")
    else:
        print(f"[OK] Teste concluído. Total de {total_raw} vagas brutas coletadas.")


if __name__ == "__main__":
    asyncio.run(main())
