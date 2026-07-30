import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import bot
import app

print("=== CHECKING BOT.PY AND APP.PY SCRAPER CONFIGURATION ===")

# Check CO_OCCURRENCE_RULES in bot.py
rules = getattr(bot, 'CO_OCCURRENCE_RULES', {})
print(f"CO_OCCURRENCE_RULES count in bot.py: {len(rules)}")

# Check SEARCH_MAPPING or macro-search term mapping in bot.py / app.py
print(f"SEARCH_MAPPING present in bot.py: {hasattr(bot, 'SEARCH_MAPPING')}")
if hasattr(bot, 'SEARCH_MAPPING'):
    print(f"SEARCH_MAPPING keys: {list(bot.SEARCH_MAPPING.keys())}")

# Check classifying helper function
print(f"classify_job_profession in bot.py: {hasattr(bot, 'classify_job_profession')}")
print(f"is_job_relevant in bot.py: {hasattr(bot, 'is_job_relevant')}")

# Inspect new category keywords in CO_OCCURRENCE_RULES
new_cats_terms = [
    "operacoes fisicas", "logistica", "administrativo", 
    "criativos", "inteligencia de vendas", "engenharia de dados"
]
print("\n--- Checking New Categories in CO_OCCURRENCE_RULES & classify_job_profession ---")
for term in new_cats_terms:
    in_co = term in rules
    print(f"  {term}: in CO_OCCURRENCE_RULES = {in_co}")

print(f"\nSample CO_OCCURRENCE_RULES keys ({len(rules)} total):")
for k in list(rules.keys())[:25]:
    print(f"  - {k}")
