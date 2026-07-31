import unicodedata
import re
import ast

with open('static/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

match = re.search(r'const PROFESSION_CATEGORIES = (\[.*?\]);', html, re.DOTALL)
js_array_str = match.group(1)
cleaned_str = re.sub(r"<i class='[^']*'></i>", "", js_array_str)
cleaned_str = re.sub(r"id:", "'id':", cleaned_str)
cleaned_str = re.sub(r"name:", "'name':", cleaned_str)
cleaned_str = re.sub(r"icon:", "'icon':", cleaned_str)
cleaned_str = re.sub(r"label_pt:", "'label_pt':", cleaned_str)
cleaned_str = re.sub(r"label_en:", "'label_en':", cleaned_str)
cleaned_str = re.sub(r"kws:", "'kws':", cleaned_str)
cats = ast.literal_eval(cleaned_str)

def norm_str(s):
    if not s: return ''
    nfkd = unicodedata.normalize('NFD', str(s))
    return ''.join(c for c in nfkd if unicodedata.category(c) != 'Mn').lower()

test_titles = [
    'Auxiliar de Limpeza',
    'Auxiliar Administrativo',
    'Auxiliar de Estoque',
    'Pesquisador Científico',
    'Guia de Turismo',
    'Técnico em Química',
    'Gerente de Leads',
    'Operador de Guincho',
    'Cuidador de Idosos',
    'Engenheiro de Fluidos',
    'Analista de Requisitos',
    'Distribuição de Materiais',
]

print("=== SUBSTRING COLLISION AUDIT ===")
for title in test_titles:
    t_norm = norm_str(title)
    matched = []
    for c in cats:
        if c['id'] in ['all', 'outros']: continue
        for kw in c.get('kws', []):
            kw_norm = norm_str(kw)
            if kw_norm in t_norm:
                matched.append((c['id'], kw))
    print(f"Title: '{title}' -> Matches: {matched}")
