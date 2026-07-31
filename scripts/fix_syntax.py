import codecs

with open('bot.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
inside_broken_string = False
broken_str = ''

for line in lines:
    if 'await callback.message.answer("🎓 *Perfil ajustado para Iniciantes!*' in line:
        inside_broken_string = True
        broken_str += line.rstrip('\\n')
    elif inside_broken_string:
        if 'parse_mode="Markdown")' in line:
            broken_str += '\\n' + line
            new_lines.append(broken_str)
            inside_broken_string = False
        else:
            broken_str += '\\n' + line.rstrip('\\n')
    else:
        new_lines.append(line)

with open('bot.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
    
print('Fixed syntax error')
