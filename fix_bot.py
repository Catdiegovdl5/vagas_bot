import re

with open('bot.py', 'r', encoding='utf-8') as f:
    text = f.read()

match = re.search(r'@dp\.callback_query\(F\.data\.startswith\("mega_loc_"\)\).*?@dp\.callback_query\(F\.data\.startswith\("hunt_"\), F\.data != "hunt_menu"\)', text, re.DOTALL)
if match:
    old_block = match.group(0)
    
    new_block = '''@dp.callback_query(F.data.startswith("mega_loc_"))
async def process_mega_location(callback: CallbackQuery):
    chat_id = callback.message.chat.id
    settings = get_user_settings(chat_id)
    
    if "remoto" in callback.data:
        settings["location"] = "Brasil (Remoto)"
        loc_str = "Remoto"
    else:
        settings["location"] = "Londrina/PR"
        loc_str = "Presencial/Londrina"
        
    settings["level"] = "iniciantes tudo"
    
    for p in ["workana", "freelancer", "novenove"]:
        if p in settings["platforms"]:
            settings["platforms"][p] = False
            
    await callback.answer("Perfil ajustado!", show_alert=False)
    
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛠️ Tecnologia & Suporte", callback_data="mega_cat_ti")],
        [InlineKeyboardButton(text="📈 Comercial & Vendas (SDR)", callback_data="mega_cat_sdr")],
        [InlineKeyboardButton(text="📂 Administrativo (ADM)", callback_data="mega_cat_adm")],
        [InlineKeyboardButton(text="💻 Desenvolvimento de Sistemas", callback_data="mega_cat_dev")],
        [InlineKeyboardButton(text="📦 Logística & Estoque", callback_data="mega_cat_log")]
    ])
    await callback.message.edit_text(f"🎓 *Perfil Iniciante Ativado!*\\n(Vagas Freelance desativadas. Focando em **{loc_str}**).\\n\\n👇 **Selecione a categoria mágica para iniciar a varredura:**", reply_markup=markup, parse_mode="Markdown")

@dp.callback_query(F.data.startswith("mega_cat_"))
async def process_mega_category(callback: CallbackQuery):
    cat_id = callback.data.split("_")[-1]
    
    MAGIC_CATEGORIES = {
        "ti": ["Suporte N1", "Suporte Técnico", "Estágio em TI", "Técnico de Apoio ao Usuário de Informática", "Analista de Suporte Júnior"],
        "sdr": ["SDR Júnior", "SDR", "Inside Sales Júnior", "Assistente de Pré-Vendas", "Assistente de Growth"],
        "adm": ["Assistente Administrativo", "Auxiliar Administrativo", "Digitador", "Data Entry"],
        "dev": ["Desenvolvedor Júnior", "Estágio de Desenvolvimento", "Programador Júnior", "Desenvolvedor Node.JS Júnior"],
        "log": ["Auxiliar de Almoxarifado", "Auxiliar de Expedição", "Auxiliar de Estoque", "Assistente de Logística"]
    }
    
    terms = MAGIC_CATEGORIES.get(cat_id, [])
    await callback.answer(f"Iniciando varredura em {len(terms)} termos!")
    msg = await callback.message.edit_text(f"🎓 *Iniciando varredura automatizada em {len(terms)} termos...*", parse_mode="Markdown")
    
    for i, term in enumerate(terms):
        try:
            await msg.edit_text(f"🎓 *Buscando {i+1}/{len(terms)}: {term}...*", parse_mode="Markdown")
        except:
            pass
        await _do_hunt(term, callback.message)
        
    try:
        await msg.edit_text(f"✅ *Varredura mágica concluída com sucesso!*", parse_mode="Markdown")
    except:
        pass

@dp.callback_query(F.data.startswith("hunt_"), F.data != "hunt_menu")'''
    
    text = text.replace(old_block, new_block)
    
    with open('bot.py', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Successfully fixed bot.py")
else:
    print("Could not find the block to replace!")
