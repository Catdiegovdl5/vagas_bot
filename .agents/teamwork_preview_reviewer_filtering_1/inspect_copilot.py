with open(r"C:\Users\99196\OneDrive\Documentos\vagas_bot\static\index.html", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, l in enumerate(lines[2240:2400], 2241):
    print(f"{i}: {l.strip()}".encode('ascii', errors='replace').decode('ascii'))
