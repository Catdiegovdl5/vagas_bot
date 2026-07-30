with open('static/index.html', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

for i, line in enumerate(lines, 1):
    if 'PROFESSION_CATEGORIES' in line or 'function selectCategory' in line or 'function triggerSearch' in line or 'id="category-drawers"' in line:
        print(f"Line {i}: {line.strip()[:100]}")
