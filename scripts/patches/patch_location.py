import re

with open('bot.py', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update mega_iniciantes block
match = re.search(r'@dp\.callback_query\(F\.data == "mega_iniciantes"\)\nasync def process_mega_iniciantes.*?parse_mode="Markdown"\)', text, re.DOTALL)
if match:
    old_handler = match.group(0)
    
    new_handler = '''@dp.callback_query(F.data == "mega_iniciantes")
async def process_mega_iniciantes(callback: CallbackQuery):
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🌍 Apenas Remoto", callback_data="mega_loc_remoto")],
        [InlineKeyboardButton(text="🏢 Presencial (Londrina e Região)", callback_data="mega_loc_londrina")]
    ])
    await callback.message.edit_text("🎓 *Onde você prefere buscar essas vagas de Iniciante?*", reply_markup=markup, parse_mode="Markdown")

@dp.callback_query(F.data.startswith("mega_loc_"))
async def process_mega_location(callback: CallbackQuery):
    chat_id = callback.message.chat.id
    settings = get_user_settings(chat_id)
    
    # Definir localização baseada na escolha
    if "remoto" in callback.data:
        settings["location"] = "Brasil (Remoto)"
        loc_str = "Remoto"
    else:
        settings["location"] = "Londrina/PR"
        loc_str = "Presencial/Londrina"
        
    # Configurar perfil para iniciante
    settings["level"] = "iniciantes tudo"
    
    # Desligar freelance
    for p in ["workana", "freelancer", "novenove"]:
        if p in settings["platforms"]:
            settings["platforms"][p] = False
            
    # Ligar flag
    settings["mega_iniciantes_active"] = True
    
    await callback.answer("Perfil ajustado!", show_alert=False)
    await callback.message.edit_text(f"🎓 *Perfil ajustado para Iniciantes!*\\n(Vagas Freelance desativadas. Focando em Estágio e Aprendiz em formato **{loc_str}**).\\n\\n👇 **Digite a área que você quer buscar agora (ex: marketing, suporte, desenvolvedor):**", parse_mode="Markdown")'''
    text = text.replace(old_handler, new_handler)
    
    with open('bot.py', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Sucesso patch location")
else:
    print("Could not find mega_iniciantes to replace")
