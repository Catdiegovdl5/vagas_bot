with open('bot.py', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

for i, line in enumerate(lines, 1):
    if 'def check_co_occurrence' in line or 'def classify_job_profession' in line:
        print(f"Line {i}: {line.strip()[:100]}")
