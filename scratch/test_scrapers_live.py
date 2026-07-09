import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scrapers import jsearch, jooble, remotar, github_vagas, meta_ads

keyword = "Gestor de Tráfego"
level = "Todos"

print("--- TESTING JSEARCH ---")
try:
    res = jsearch.scrape(keyword, level)
    print("JSearch returned:", len(res), "jobs")
    for r in res[:2]:
        print("  -", r["title"], "at", r["company"], "link:", r["link"][:50])
except Exception as e:
    print("JSearch Failed:", e)

print("\n--- TESTING JOOBLE ---")
try:
    res = jooble.scrape(keyword, level)
    print("Jooble returned:", len(res), "jobs")
    for r in res[:2]:
        print("  -", r["title"], "at", r["company"], "link:", r["link"][:50])
except Exception as e:
    print("Jooble Failed:", e)

print("\n--- TESTING REMOTAR ---")
try:
    res = remotar.scrape(keyword, level)
    print("Remotar returned:", len(res), "jobs")
    for r in res[:2]:
        print("  -", r["title"], "at", r["company"], "link:", r["link"][:50])
except Exception as e:
    print("Remotar Failed:", e)

print("\n--- TESTING GITHUB VAGAS ---")
try:
    res = github_vagas.scrape(keyword, level)
    print("Github Vagas returned:", len(res), "jobs")
    for r in res[:2]:
        print("  -", r["title"], "at", r["company"], "link:", r["link"][:50])
except Exception as e:
    print("Github Vagas Failed:", e)
