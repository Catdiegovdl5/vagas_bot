with open('bot.py', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

for i, line in enumerate(lines, 1):
    if 'CO_OCCURRENCE_RULES =' in line or 'def is_job_relevant' in line or 'MACRO_' in line:
        print(f"Line {i}: {line.strip()[:100]}")
