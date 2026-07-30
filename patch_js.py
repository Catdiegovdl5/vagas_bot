import re

with open('static/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Dynamic platform gathering logic
dynamic_logic = '''            let platforms = [];
            const allToggles = ['jsearch', 'jooble', 'workana', 'remotar', 'linkedin', 'indeed', 'gupy', 'catho', 'vagas_com', 'coodesh', 'geekhunter', 'github_vagas', 'infojobs', 'novenove', 'glassdoor', 'freelancer', 'gmail'];
            allToggles.forEach(plat => {
                if(document.getElementById('toggle-' + plat) && document.getElementById('toggle-' + plat).checked) {
                    platforms.push(plat);
                }
            });'''

old_logic_pattern = r'''\s*let platforms = \[\];
\s*if\(document\.getElementById\('toggle-jsearch'\) && document\.getElementById\('toggle-jsearch'\)\.checked\) platforms\.push\('jsearch'\);
\s*if\(document\.getElementById\('toggle-jooble'\) && document\.getElementById\('toggle-jooble'\)\.checked\) platforms\.push\('jooble'\);
\s*if\(document\.getElementById\('toggle-workana'\) && document\.getElementById\('toggle-workana'\)\.checked\) platforms\.push\('workana'\);
\s*if\(document\.getElementById\('toggle-remotar'\) && document\.getElementById\('toggle-remotar'\)\.checked\) platforms\.push\('remotar'\);'''

text = re.sub(old_logic_pattern, '\n' + dynamic_logic, text)

with open('static/index.html', 'w', encoding='utf-8') as f:
    f.write(text)

print('Replaced platforms logic in index.html')
