import re

with open('bot.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Update group text
text = text.replace(
    'Freelance (Workana)',
    'Freelance (Workana, 99Freelas...)'
)

# Update groups dict
old_groups = '''    groups = {
        "freelance": ["workana"],
        "globais": ["linkedin", "indeed", "glassdoor"],
        "nacionais": ["gupy", "catho", "infojobs", "vagas_com"],
        "ti": ["coodesh", "geekhunter", "programathor", "github_vagas"],
        "remotos": ["remotar", "jooble", "jsearch"]
    }'''

new_groups = '''    groups = {
        "freelance": ["workana", "freelancer", "novenove"],
        "globais": ["linkedin", "indeed", "glassdoor"],
        "nacionais": ["gupy", "catho", "infojobs", "vagas_com"],
        "ti": ["coodesh", "geekhunter", "programathor", "github_vagas"],
        "remotos": ["remotar", "jooble", "jsearch"]
    }'''

text = text.replace(old_groups, new_groups)

with open('bot.py', 'w', encoding='utf-8') as f:
    f.write(text)

print('Updated bot.py keyboard groups')
