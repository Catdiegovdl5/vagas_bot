import re

with open('bot.py', 'r', encoding='utf-8') as f:
    text = f.read()

match = re.search(r'@dp\.callback_query\(F\.data == "mega_iniciantes"\).*?settings\["level"\] = old_level\n', text, re.DOTALL)

if match:
    old_handler = match.group(0)
    
    new_handler = '''@dp.callback_query(F.data == "mega_iniciantes")
async def process_mega_iniciantes_menu(callback: CallbackQuery):
    await callback.answer()
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Sim, incluir Freelance", callback_data="start_mega_ini_yes")],
        [InlineKeyboardButton(text="❌ Não, apenas Empregos", callback_data="start_mega_ini_no")]
    ])
    await callback.message.edit_text("🎓 *Deseja incluir plataformas Freelance (Workana, 99Freelas) nesta busca?*", reply_markup=markup, parse_mode="Markdown")

@dp.callback_query(F.data.startswith("start_mega_ini_"))
async def process_mega_iniciantes_start(callback: CallbackQuery):
    chat_id = callback.message.chat.id
    settings = get_user_settings(chat_id)
    
    include_freela = callback.data.endswith("yes")
    
    active_plats = [k for k, v in settings["platforms"].items() if v]
    
    if not include_freela:
        # Remover plataformas freelance da lista de ativas desta busca temporariamente
        freela_list = ["workana", "freelancer", "novenove"]
        active_plats = [p for p in active_plats if p not in freela_list]
        
    if not active_plats:
        try:
            await callback.answer("Nenhuma plataforma restou para buscar!", show_alert=True)
        except:
            pass
        return
        
    await callback.answer()
    
    # Salvar temporariamente as plataformas ativas reais para o `_do_hunt` usar
    old_platforms = settings["platforms"].copy()
    if not include_freela:
        for p in ["workana", "freelancer", "novenove"]:
            if p in settings["platforms"]:
                settings["platforms"][p] = False
    
    old_level = settings["level"]
    settings["level"] = "iniciantes tudo"
    
    keywords = ['desenvolvedor', 'designer', 'marketing', 'editor de video', 'social media', 'suporte tecnico', 'administracao', 'logistica', 'financeiro']
    msg = await callback.message.edit_text("🎓 *Iniciando mega caçada para iniciantes em 9 áreas...*", parse_mode="Markdown")
    
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
        
    # Restaurar settings
    settings["level"] = old_level
    settings["platforms"] = old_platforms
'''
    text = text.replace(old_handler, new_handler)
    
    with open('bot.py', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Sucesso!")
else:
    print("Nao achou o bloco mega_iniciantes")
