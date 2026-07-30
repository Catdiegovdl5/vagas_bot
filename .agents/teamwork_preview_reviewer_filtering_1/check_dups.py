import re
from collections import Counter

with open(r"C:\Users\99196\OneDrive\Documentos\vagas_bot\static\index.html", "r", encoding="utf-8") as f:
    content = f.read()

ids = re.findall(r'id=["\']([^"\']+)["\']', content)
counts = Counter(ids)
dups = {k: v for k, v in counts.items() if v > 1}
print("Duplicate IDs found:")
for id_name, count in dups.items():
    print(f"  - {id_name}: {count} times")
