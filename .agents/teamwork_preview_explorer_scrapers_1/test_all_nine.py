import sys
import os
import asyncio
import traceback

sys.path.append("C:/Users/99196/OneDrive/Documentos/vagas_bot")

from scrapers import jsearch, workana, remotar, glassdoor, gupy, vagas_com, programathor, coodesh, geekhunter

async def test_scrapers():
    scrapers_dict = {
        "Jsearch": (jsearch.scrape, {"keyword": "Python", "level": "Todos", "country": "Brasil"}),
        "Workana": (workana.scrape, {"keyword": "Python", "level": "Todos"}),
        "Remotar": (remotar.scrape, {"keyword": "Python", "level": "Todos"}),
        "Glassdoor": (glassdoor.scrape, {"keyword": "Python", "level": "Todos", "country": "Brasil"}),
        "Gupy": (gupy.scrape, {"keyword": "Python", "level": "Todos", "country": "Brasil"}),
        "Vagas.com": (vagas_com.scrape, {"keyword": "Python", "level": "Todos", "country": "Brasil"}),
        "Programathor": (programathor.scrape, {"keyword": "Python", "level": "Todos", "country": "Brasil"}),
        "Coodesh": (coodesh.scrape, {"keyword": "Python", "level": "Todos", "country": "Brasil"}),
        "Geekhunter": (geekhunter.scrape, {"keyword": "Python", "level": "Todos", "country": "Brasil"}),
    }
    
    for name, (func, kwargs) in scrapers_dict.items():
        print(f"\n==========================================")
        print(f"TESTING SCRAPER: {name}")
        print(f"==========================================")
        try:
            res = await asyncio.to_thread(func, **kwargs)
            print(f"STATUS: SUCCESS")
            print(f"RESULTS RETURNED: {len(res)}")
            for idx, job in enumerate(res[:3]):
                print(f"  Job #{idx+1}:")
                print(f"    Title: {job.get('title')}")
                print(f"    Company: {job.get('company')}")
                print(f"    Link: {job.get('link')}")
                print(f"    Requirements: {job.get('requirements')[:100]}...")
        except Exception as e:
            print(f"STATUS: FAILED")
            print(f"ERROR: {e}")
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_scrapers())
