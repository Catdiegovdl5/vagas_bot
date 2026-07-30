import re

with open(r"C:\Users\99196\OneDrive\Documentos\vagas_bot\bot.py", "r", encoding="utf-8") as f:
    bot_code = f.read()

cats_in_bot = set(re.findall(r"cat\s*=\s*'([^']+)'", bot_code))
print("Categories assigned in bot.py classify_job_profession:", sorted(cats_in_bot))

with open(r"C:\Users\99196\OneDrive\Documentos\vagas_bot\static\index.html", "r", encoding="utf-8") as f:
    html_code = f.read()

match = re.search(r"const PROFESSION_CATEGORIES = (\[.*?\]);", html_code, re.DOTALL)
if match:
    js_block = match.group(1)
    cats = re.findall(r"id:\s*['\"]([^'\"]+)['\"]", js_block)
    labels = re.findall(r"label_pt:\s*['\"]([^'\"]+)['\"]", js_block)
    print("UI Categories (IDs):", cats)
    print("UI Categories (Labels):", labels)
