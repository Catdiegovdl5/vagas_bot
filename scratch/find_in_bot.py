import json

with open("bot.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

results = {
    "escudo_ptbr": [],
    "applied": []
}

for idx, line in enumerate(lines, 1):
    line_lower = line.lower()
    if "escudo" in line_lower or "ptbr" in line_lower or "langdetect" in line_lower:
        results["escudo_ptbr"].append(f"{idx}: {line.strip()}")
    if "applied" in line_lower or "candidatei" in line_lower:
        results["applied"].append(f"{idx}: {line.strip()}")

with open("scratch/search_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print("Done")
