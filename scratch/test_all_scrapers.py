import sys
import os
import asyncio

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scrapers import linkedin, indeed, glassdoor, infojobs, jooble, jsearch, remotar, github_vagas, meta_ads

async def run_in_thread(func, *args, **kwargs):
    return await asyncio.to_thread(func, *args, **kwargs)

async def test_scrapers():
    plats = {
        "linkedin": linkedin.scrape,
        "indeed": indeed.scrape,
        "glassdoor": glassdoor.scrape,
        "infojobs": infojobs.scrape,
        "jooble": jooble.scrape,
        "jsearch": jsearch.scrape,
        "remotar": remotar.scrape,
        "github_vagas": github_vagas.scrape,
        "meta_ads": meta_ads.scrape
    }
    
    keyword = "Gestor de Tráfego"
    level = "Todos"
    
    for name, func in plats.items():
        print(f"\n=== TESTING {name.upper()} ===")
        try:
            import inspect
            sig = inspect.signature(func)
            if "country" in sig.parameters:
                jobs = await run_in_thread(func, keyword, level=level, country="Brasil (Remoto)")
            else:
                jobs = await run_in_thread(func, keyword, level=level)
                
            real_jobs = [j for j in jobs if "Sem vagas" not in j['title'] and "Não houve" not in j['requirements']]
            print(f"Total jobs: {len(jobs)} | Real jobs: {len(real_jobs)}")
            if real_jobs:
                print(f"Sample 1: {real_jobs[0]['title']} at {real_jobs[0]['company']} (link: {real_jobs[0]['link'][:60]})")
                if len(real_jobs) > 1:
                    print(f"Sample 2: {real_jobs[1]['title']} at {real_jobs[1]['company']} (link: {real_jobs[1]['link'][:60]})")
        except Exception as e:
            print(f"FAILED {name}: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_scrapers())
