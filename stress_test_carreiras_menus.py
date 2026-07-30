import ast
import os
import sys
from unittest.mock import MagicMock, AsyncMock

# Force UTF-8 output on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import database
import bot

def run_ast_syntax_tests():
    print("--- 1. Testing AST Syntax ---")
    files_to_check = ["bot.py", "database.py"]
    results = {}
    for filename in files_to_check:
        filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
        with open(filepath, "r", encoding="utf-8") as f:
            code = f.read()
        tree = ast.parse(code)
        assert tree is not None, f"AST parsing failed for {filename}"
        results[filename] = "PASS"
        print(f"  [PASS] AST syntax valid for {filename} ({len(code)} bytes)")
    return results

def run_menu_edge_cases_and_button_counts():
    print("\n--- 2. Testing Menu Markup & Button Counts (<= 15 buttons) ---")
    violations = []
    cb_violations = []

    # 1. Main Menu Inline Markup
    mm_markup = bot.get_main_menu_markup()
    mm_count = sum(len(row) for row in mm_markup.inline_keyboard)
    print(f"  Main Menu Inline Markup button count: {mm_count}")
    if mm_count > 15:
        violations.append(f"Main menu markup has {mm_count} buttons (> 15)")

    # Check callback_data byte length for main menu
    for row in mm_markup.inline_keyboard:
        for btn in row:
            if btn.callback_data and len(btn.callback_data.encode('utf-8')) >= 64:
                cb_violations.append(f"Main menu callback '{btn.callback_data}' >= 64 bytes")

    # 2. Main Menu Persistent Reply Keyboard
    persistent_markup = bot.ReplyKeyboardMarkup(
        keyboard=[
            [bot.KeyboardButton(text="🎯 Caçar Vagas"), bot.KeyboardButton(text="🎓 Trilha de Carreiras")],
            [bot.KeyboardButton(text="🛠 Configurações")]
        ],
        resize_keyboard=True,
        is_persistent=True
    )
    pm_count = sum(len(row) for row in persistent_markup.keyboard)
    print(f"  Persistent Reply Keyboard button count: {pm_count}")
    if pm_count > 15:
        violations.append(f"Persistent Reply Keyboard has {pm_count} buttons (> 15)")

    # 3. Settings Menu Markup
    settings_markup = bot.get_settings_markup(123456)
    settings_count = sum(len(row) for row in settings_markup.inline_keyboard)
    print(f"  Settings Menu button count: {settings_count}")
    if settings_count > 15:
        violations.append(f"Settings menu markup has {settings_count} buttons (> 15)")

    # 4. Carreiras Main Markup
    car_markup = bot.get_carreiras_main_markup()
    car_count = sum(len(row) for row in car_markup.inline_keyboard)
    print(f"  Carreiras Main Menu button count: {car_count}")
    if car_count > 15:
        violations.append(f"Carreiras main markup has {car_count} buttons (> 15)")

    # 5. Profession Detail & Roadmap Markups under Edge Cases
    professions = list(bot.CAREER_GUIDANCE_DATA.keys())
    print(f"  Testing {len(professions)} professions for detail & roadmap markups...")

    # Mock DB progress for edge cases: empty progress, full progress, partial progress, invalid user
    test_user_scenarios = [
        ("user_empty_progress", {}),
        ("user_full_progress", "FULL"),
        ("user_partial_progress", "PARTIAL"),
        ("user_nonexistent", None)
    ]

    for pid in professions:
        # Detail markup
        det_markup = bot.get_profession_detail_markup(pid)
        det_count = sum(len(row) for row in det_markup.inline_keyboard)
        if det_count > 15:
            violations.append(f"Profession detail '{pid}' has {det_count} buttons (> 15)")

        # Test roadmap markup across user scenarios
        prof_data = bot.CAREER_GUIDANCE_DATA[pid]
        steps = prof_data.get("specialization_steps", prof_data.get("steps", []))

        for user_id, scenario_type in test_user_scenarios:
            # Mock get_user_career_progress
            original_get_progress = bot.get_user_career_progress
            if scenario_type == "FULL":
                mock_prog = {step.get("step_id", f"step_{idx+1}") if isinstance(step, dict) else f"step_{idx+1}": {"status": 1} for idx, step in enumerate(steps)}
            elif scenario_type == "PARTIAL":
                mock_prog = {step.get("step_id", f"step_{idx+1}") if isinstance(step, dict) else f"step_{idx+1}": {"status": idx % 2} for idx, step in enumerate(steps)}
            else:
                mock_prog = {}

            bot.get_user_career_progress = lambda u, p, _m=mock_prog: _m

            try:
                roadmap_markup = bot.get_profession_roadmap_markup(user_id, pid)
                rd_count = sum(len(row) for row in roadmap_markup.inline_keyboard)
                if rd_count > 15:
                    violations.append(f"Roadmap '{pid}' scenario '{user_id}' has {rd_count} buttons (> 15)")

                # Verify callback data lengths
                for row in roadmap_markup.inline_keyboard:
                    for btn in row:
                        if btn.callback_data and len(btn.callback_data.encode('utf-8')) >= 64:
                            cb_violations.append(f"Roadmap '{pid}' callback '{btn.callback_data}' >= 64B")
            finally:
                bot.get_user_career_progress = original_get_progress

    # 6. Edge case: invalid/nonexistent profession ID
    invalid_pid_roadmap = bot.get_profession_roadmap_markup("user_test", "non_existent_prof_999")
    inv_count = sum(len(row) for row in invalid_pid_roadmap.inline_keyboard)
    print(f"  Invalid profession roadmap button count: {inv_count}")
    if inv_count > 15:
        violations.append(f"Invalid profession roadmap has {inv_count} buttons (> 15)")

    # 7. Niche Sub-Menus
    bot_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bot.py")
    with open(bot_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read())
    
    menus_dict = None
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == 'show_niche_jobs':
            for body_node in node.body:
                if isinstance(body_node, ast.Assign):
                    for target in body_node.targets:
                        if isinstance(target, ast.Name) and target.id == 'menus':
                            menus_dict = ast.literal_eval(body_node.value)
    
    if menus_dict:
        print(f"  Testing {len(menus_dict)} niche menus...")
        for niche, prof_list in menus_dict.items():
            # Build buttons as show_niche_jobs does
            buttons = []
            row = []
            for p in prof_list:
                row.append(bot.InlineKeyboardButton(text=p, callback_data=f"n_{p[:20]}"))
                if len(row) == 2:
                    buttons.append(row)
                    row = []
            if row:
                buttons.append(row)
            buttons.append([bot.InlineKeyboardButton(text="🔙 Voltar ao Menu", callback_data="main_menu")])
            
            niche_markup = bot.InlineKeyboardMarkup(inline_keyboard=buttons)
            n_count = sum(len(row) for row in niche_markup.inline_keyboard)
            if n_count > 15:
                violations.append(f"Niche '{niche}' markup has {n_count} buttons (> 15)")

    print(f"\n  [SUMMARY] Button count violations (> 15): {len(violations)}")
    print(f"  [SUMMARY] Callback data byte violations (>= 64B): {len(cb_violations)}")
    
    assert len(violations) == 0, f"Button count violations found: {violations}"
    assert len(cb_violations) == 0, f"Callback data length violations found: {cb_violations}"
    print("  [PASS] All menu markups strictly <= 15 buttons and callback_data < 64 bytes!")

if __name__ == "__main__":
    run_ast_syntax_tests()
    run_menu_edge_cases_and_button_counts()
    print("\nALL STRESS TESTS PASSED SUCCESSFULLY!")
