import re, json

with open('static/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

match = re.search(r'const PROFESSION_CATEGORIES = (\[.*?\]);', text, re.DOTALL)
if match:
    raw = match.group(1)
    # Find all { id: "...", name: "..." }
    entries = re.findall(r'id:\s*"([^"]+)",\s*name:\s*"([^"]+)"', raw)
    print(f"Total categories found: {len(entries)}")
    for i, (cid, name) in enumerate(entries, 1):
        print(f"  {i}. ID: {cid} | Name: {name}")

    # Check mega-menu html rendering logic
    print("\n--- Mega-menu / Drawer HTML Rendering Check ---")
    drawers = re.findall(r'class="[^"]*mega-menu[^"]*"|class="[^"]*drawer[^"]*"|id="[^"]*mega[^"]*"|id="[^"]*drawer[^"]*"', text, re.IGNORECASE)
    print(f"Found {len(drawers)} mega-menu/drawer class/id occurrences in HTML/JS")
    
    # Check JS functions for category filtering/rendering
    fns = re.findall(r'function\s+(\w+)', text)
    print(f"Functions in JS: {fns[:15]}")
