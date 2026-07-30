import re

with open('bot.py', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Add button to main menu
old_menu = '''def get_main_menu_markup():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎯 Caçar Vagas", callback_data="hunt_menu")],
        [InlineKeyboardButton(text="🛠 Configurações", callback_data="settings_menu")]
    ])'''

new_menu = '''def get_main_menu_markup():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎯 Caçar Vagas", callback_data="hunt_menu")],
        [InlineKeyboardButton(text="🎓 Caçar Tudo para Iniciantes", callback_data="hunt_iniciantes_bot")],
        [InlineKeyboardButton(text="🛠 Configurações", callback_data="settings_menu")]
    ])'''

text = text.replace(old_menu, new_menu)

# 2. Add the handler
handler = '''@dp.callback_query(F.data == "hunt_iniciantes_bot")
async def process_hunt_iniciantes(callback: CallbackQuery):
    chat_id = callback.message.chat.id
    settings = get_user_settings(chat_id)
    active_plats = [k for k, v in settings["platforms"].items() if v]
    if not active_plats:
        try:
            await callback.answer("Ative pelo menos uma plataforma em Configurações!", show_alert=True)
        except Exception:
            await callback.message.answer("Ative pelo menos uma plataforma em Configurações!")
        return
        
    await callback.answer()
    
    old_level = settings["level"]
    settings["level"] = "iniciantes tudo"
    
    keywords = ['desenvolvedor', 'designer', 'marketing', 'editor de video', 'social media', 'suporte tecnico', 'administracao', 'logistica', 'financeiro']
    msg = await callback.message.answer("🎓 *Iniciando mega caçada para iniciantes em 9 áreas...*", parse_mode="Markdown")
    
    for i, kw in enumerate(keywords):
        try:
            await msg.edit_text(f"🎓 *Buscando {i+1}/9: {kw}...*", parse_mode="Markdown")
        except:
            pass
        await _do_hunt(kw, callback.message, callback=callback)
        
    try:
        await msg.edit_text(f"✅ *Mega caçada para iniciantes concluída!*", parse_mode="Markdown")
    except:
        pass
        
    settings["level"] = old_level

'''

# Insert handler before `import unicodedata` which is below process_hunt
text = text.replace('import unicodedata', handler + 'import unicodedata')

with open('bot.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Updated bot.py with hunt_iniciantes_bot")
