import os
import ast
import asyncio
from unittest.mock import AsyncMock, MagicMock
import pytest

# Helper to extract the local menus dict using AST
def get_menus_dict():
    bot_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bot.py")
    with open(bot_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read())
        
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == 'show_niche_jobs':
            for body_node in node.body:
                if isinstance(body_node, ast.Assign):
                    for target in body_node.targets:
                        if isinstance(target, ast.Name) and target.id == 'menus':
                            return ast.literal_eval(body_node.value)
    raise ValueError("Could not find 'menus' assignment inside 'show_niche_jobs' in bot.py")

# Test 1: All areas are present as top-level keys in menus
def test_all_areas_present():
    menus = get_menus_dict()
    expected_areas = {"ai", "dev", "dados", "mkt", "audio", "base", "junior", "pleno"}
    assert set(menus.keys()) == expected_areas, f"Expected areas {expected_areas}, but got {set(menus.keys())}"
    print("Test 1 Passed: All 8 areas are present as top-level keys in menus.")

# Test 2: No single message renders more than 15 buttons
@pytest.mark.asyncio
async def test_no_markup_exceeds_15_buttons():
    from bot import select_mode, show_niche_jobs, get_main_menu_markup, get_settings_markup
    
    # 2.1: Main menu markup
    markup = get_main_menu_markup()
    button_count = sum(len(row) for row in markup.inline_keyboard)
    assert button_count <= 15, f"Main menu markup has {button_count} buttons"
    
    # 2.2: Settings menu markup
    markup = get_settings_markup(12345)
    button_count = sum(len(row) for row in markup.inline_keyboard)
    assert button_count <= 15, f"Settings markup has {button_count} buttons"
    
    # helper for mock callback
    def make_mock_callback(data):
        cb = MagicMock()
        cb.data = data
        cb.answer = AsyncMock()
        cb.message = AsyncMock()
        cb.message.edit_text = AsyncMock()
        cb.message.chat = MagicMock()
        cb.message.chat.id = 12345
        return cb

    # 2.3: Select mode niche menu markup
    cb = make_mock_callback("modo_emprego")
    await select_mode(cb)
    args, kwargs = cb.message.edit_text.call_args
    markup = kwargs.get("reply_markup") or args[0]
    assert markup is not None, "select_mode did not provide reply_markup"
    button_count = sum(len(row) for row in markup.inline_keyboard)
    assert button_count <= 15, f"Select mode niche menu has {button_count} buttons"
    
    # 2.4: Niche sub-menus
    menus = get_menus_dict()
    for niche in menus.keys():
        cb = make_mock_callback(f"nicho_{niche}")
        await show_niche_jobs(cb)
        args, kwargs = cb.message.edit_text.call_args
        markup = kwargs.get("reply_markup")
        assert markup is not None, f"show_niche_jobs did not provide reply_markup for niche {niche}"
        button_count = sum(len(row) for row in markup.inline_keyboard)
        assert button_count <= 15, f"Niche sub-menu for '{niche}' has {button_count} buttons"
        
    print("Test 2 Passed: No markup renders more than 15 buttons.")

# Test 3: Search rules, keywords, and blacklists exist for every single profession
def test_all_professions_have_rules():
    from bot import CO_OCCURRENCE_RULES, blacklist, normalize_str
    
    # Extract search_mapping dynamically by importing or reading
    bot_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bot.py")
    with open(bot_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read())
        
    search_mapping = None
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == '_do_hunt':
            for body_node in node.body:
                if isinstance(body_node, ast.Assign):
                    for target in body_node.targets:
                        if isinstance(target, ast.Name) and target.id == 'search_mapping':
                            search_mapping = ast.literal_eval(body_node.value)
                            break
    
    assert search_mapping is not None, "Could not find 'search_mapping' assignment in _do_hunt"
    
    menus = get_menus_dict()
    all_professions = []
    for niche, profs in menus.items():
        all_professions.extend(profs)
        
    # Check count: we expect 49 professions
    assert len(all_professions) == 49, f"Expected 49 professions in menus, but found {len(all_professions)}"
    
    for prof in all_professions:
        # 1. Search mapping must exist
        assert prof in search_mapping, f"Profession '{prof}' missing from search_mapping"
        
        # 2. Normalized key
        norm_key = normalize_str(prof)
        
        # 3. Co-occurrence rules must exist
        assert norm_key in CO_OCCURRENCE_RULES, f"Normalized key '{norm_key}' (for '{prof}') missing from CO_OCCURRENCE_RULES"
        
        # 4. Blacklist must exist
        assert norm_key in blacklist, f"Normalized key '{norm_key}' (for '{prof}') missing from blacklist"
        
    print(f"Test 3 Passed: Verified search rules, keywords, and blacklists exist for all {len(all_professions)} professions.")

if __name__ == "__main__":
    test_all_areas_present()
    test_all_professions_have_rules()
    asyncio.run(test_no_markup_exceeds_15_buttons())
    print("All custom validation tests passed perfectly!")
