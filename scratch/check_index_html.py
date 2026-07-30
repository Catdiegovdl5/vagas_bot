with open('static/index.html', 'r', encoding='utf-8', errors='ignore') as f:
    html = f.read()

print(f"HTML Size: {len(html)} bytes")

# Check for drawer elements or mega menus
import re
drawers = re.findall(r'id=["\']([^"\']*drawer[^"\']*)["\']', html, re.I)
mega_menus = re.findall(r'class=["\']([^"\']*mega[^"\']*)["\']', html, re.I)
js_maps = re.findall(r'const\s+([A-Z_]+)\s*=', html)
fetch_calls = re.findall(r'fetch\([^\)]+\)', html)

print("Drawers found:", drawers)
print("Mega menu classes found:", mega_menus[:10])
print("JS constants found:", js_maps)
print("Fetch API calls count:", len(fetch_calls))
for fc in fetch_calls[:5]:
    print("  Fetch:", fc[:100])
