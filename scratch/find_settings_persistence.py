with open("bot.py", "r", encoding="utf-8") as f:
    content = f.read()

import re
matches = [m.start() for m in re.finditer("user_settings_db", content)]
for m in matches:
    start = max(0, m - 50)
    end = min(len(content), m + 100)
    print(f"--- MATCH AT {m} ---")
    print(content[start:end])
