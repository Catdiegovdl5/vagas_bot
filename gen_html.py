platforms = [
    ('linkedin', 'LinkedIn', '#0077B5', 'fa-brands fa-linkedin'),
    ('indeed', 'Indeed', '#2164f4', 'fa-solid fa-magnifying-glass'),
    ('gupy', 'Gupy', '#0073b1', 'fa-solid fa-briefcase'),
    ('catho', 'Catho', '#e5007f', 'fa-solid fa-briefcase'),
    ('vagas_com', 'Vagas.com', '#00a550', 'fa-solid fa-briefcase'),
    ('coodesh', 'Coodesh', '#ff5722', 'fa-solid fa-code'),
    ('geekhunter', 'GeekHunter', '#673ab7', 'fa-solid fa-laptop-code'),
    ('github_vagas', 'GitHub Vagas', '#333333', 'fa-brands fa-github'),
    ('infojobs', 'Infojobs', '#0055ff', 'fa-solid fa-briefcase'),
    ('novenove', '99Freelas', '#f44336', 'fa-solid fa-bolt'),
    ('glassdoor', 'Glassdoor', '#0caa41', 'fa-solid fa-building'),
    ('freelancer', 'Freelancer', '#29b2fe', 'fa-solid fa-globe'),
    ('gmail', 'Gmail API', '#ea4335', 'fa-brands fa-google')
]

html = ''
for p_id, name, color, icon in platforms:
    html += f'''            <div class="setting-item">
                <div class="setting-info">
                    <div class="setting-icon" style="color:{color};"><i class="{icon}"></i></div> {name}
                </div>
                <label class="toggle"><input type="checkbox" id="toggle-{p_id}" checked><span class="slider"></span></label>
            </div>\n'''

with open('temp_html.txt', 'w', encoding='utf-8') as f:
    f.write(html)
