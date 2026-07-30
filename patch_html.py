import re

with open('static/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

with open('temp_html.txt', 'r', encoding='utf-8') as f:
    new_toggles = f.read()

old_end = '''            <div class="setting-item">
                <div class="setting-info">
                    <div class="setting-icon" style="color:#f97316;"><i class="fa-solid fa-rocket"></i></div> Remotar (Scraper)
                </div>
                <label class="toggle"><input type="checkbox" id="toggle-remotar"><span class="slider"></span></label>
            </div>
        </div>'''

new_end = '''            <div class="setting-item">
                <div class="setting-info">
                    <div class="setting-icon" style="color:#f97316;"><i class="fa-solid fa-rocket"></i></div> Remotar (Scraper)
                </div>
                <label class="toggle"><input type="checkbox" id="toggle-remotar"><span class="slider"></span></label>
            </div>\n''' + new_toggles + '        </div>'

text = text.replace(old_end, new_end)

with open('static/index.html', 'w', encoding='utf-8') as f:
    f.write(text)

print('HTML toggles inserted successfully!')
