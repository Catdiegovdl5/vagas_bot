import os

log_path = r"C:\Users\99196\OneDrive\Documentos\vagas_bot\erros_robo.log"
scrapers = ["jsearch", "workana", "remotar", "glassdoor", "gupy", "vagas", "programathor", "coodesh", "geekhunter"]

if not os.path.exists(log_path):
    print("Log file not found at", log_path)
else:
    with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    print(f"Total lines: {len(lines)}")
    
    counts = {s: 0 for s in scrapers}
    for line in lines:
        for s in scrapers:
            if s in line.lower():
                counts[s] += 1
    
    print("Occurrences of scrapers in log:")
    for s, c in counts.items():
        print(f"  {s}: {c}")
        
    print("\n--- Detailed errors by Scraper ---")
    for s in scrapers:
        print(f"\n>>> Scraper: {s.upper()} <<<")
        matching_lines = []
        for line in lines:
            if s in line.lower() and ("error" in line.lower() or "exception" in line.lower() or "fail" in line.lower() or "traceback" in line.lower() or "erro" in line.lower()):
                matching_lines.append(line.strip())
        print(f"Found {len(matching_lines)} error lines.")
        # print the last 15 matching lines
        for m_line in matching_lines[-15:]:
            print("  ", m_line)
