import re

with open('bot.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace(
    'FREELANCE_PLATFORMS = ["workana"]',
    'FREELANCE_PLATFORMS = ["workana", "freelancer", "novenove"]'
)

text = text.replace(
    'EMPREGO_PLATFORMS = ["jsearch", "jooble", "remotar", "github_vagas", "indeed", "linkedin", "glassdoor", "infojobs", "gupy", "catho", "vagas_com", "programathor", "coodesh", "geekhunter"]',
    'EMPREGO_PLATFORMS = ["jsearch", "jooble", "remotar", "github_vagas", "indeed", "linkedin", "glassdoor", "infojobs", "gupy", "catho", "vagas_com", "programathor", "coodesh", "geekhunter", "gmail"]'
)

with open('bot.py', 'w', encoding='utf-8') as f:
    f.write(text)

print('Updated bot.py')
