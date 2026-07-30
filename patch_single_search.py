import re

with open('bot.py', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Patch mega_iniciantes block
match = re.search(r'@dp\.callback_query\(F\.data == "mega_iniciantes"\).*?settings\["platforms"\] = old_platforms\n', text, re.DOTALL)
if not match:
    # If the previous patch failed, let's try broader match
    match = re.search(r'@dp\.callback_query\(F\.data == "mega_iniciantes"\).*?@dp\.callback_query\(F\.data\.startswith\("hunt_"\)', text, re.DOTALL)

if match:
    old_handler = match.group(0).replace('@dp.callback_query(F.data.startswith("hunt_")', '')
    
    new_handler = '''@dp.callback_query(F.data == "mega_iniciantes")
async def process_mega_iniciantes(callback: CallbackQuery):
    chat_id = callback.message.chat.id
    settings = get_user_settings(chat_id)
    
    # Configurar perfil para iniciante
    settings["level"] = "iniciantes tudo"
    settings["location"] = "Londrina, Remoto" # Ou "Brasil (Remoto)" dependendo da base, a string exata usada  "Brasil (Remoto)"
    
    # Desligar freelance
    for p in ["workana", "freelancer", "novenove"]:
        if p in settings["platforms"]:
            settings["platforms"][p] = False
            
    # Ligar flag
    settings["mega_iniciantes_active"] = True
    
    await callback.answer("Perfil ajustado para Iniciantes!", show_alert=False)
    await callback.message.answer("🎓 *Perfil ajustado para Iniciantes!*\n(Vagas Freelance desativadas. Focando em Estágio e Aprendiz em formato Remoto/Londrina).\n\n👇 **Digite a área que você quer buscar agora (ex: marketing, suporte, desenvolvedor):**", parse_mode="Markdown")

'''
    # We replace the matched block (excluding the start of the next handler if it matched it)
    text = text.replace(old_handler, new_handler)
else:
    print("Could not find mega_iniciantes block")


# 2. Patch handle_free_text
old_free_text = '''@dp.message(F.text)
async def handle_free_text(message: types.Message):
    if message.text.startswith("/"):
        return
        
    await message.answer("🔍 *Processando seu pedido...*", parse_mode="Markdown")'''

new_free_text = '''@dp.message(F.text)
async def handle_free_text(message: types.Message):
    if message.text.startswith("/"):
        return
        
    chat_id = message.chat.id
    settings = get_user_settings(chat_id)
    
    if settings.get("mega_iniciantes_active"):
        settings["mega_iniciantes_active"] = False
        keyword = message.text.strip()[:50]
        await message.answer(f"🔍 *Buscando vagas de iniciante para: {keyword}...*", parse_mode="Markdown")
        await _do_hunt(keyword, message)
        return
        
    await message.answer("🔍 *Processando seu pedido...*", parse_mode="Markdown")'''

text = text.replace(old_free_text, new_free_text)

with open('bot.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Patched Mega Iniciantes single-search behavior")
