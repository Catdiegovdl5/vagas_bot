import re, sys

sys.stdout.reconfigure(encoding='utf-8')

with open('static/index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

emoji_pattern = re.compile(
    r'[\U0001F000-\U0001FFFF\u2600-\u27BF\u2300-\u23FF]'
)

for i, line in enumerate(lines, 1):
    matches = emoji_pattern.findall(line)
    if matches:
        print(f"Line {i}: {matches} -> {line.strip()}")
