import os
import ast
import sqlite3
import pytest
from unittest.mock import MagicMock, AsyncMock

import database
import bot

# --- 1. TESTES DE SINTAXE E CARREGAMENTO DE MENU NO BOT.PY ---

def test_bot_imports_and_syntax():
    """Garante que bot.py não possui erros de sintaxe e é analisável via AST."""
    bot_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bot.py")
    with open(bot_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read())
    assert tree is not None, "Falha ao analisar sintaxe do bot.py"

def test_main_menu_includes_carreiras_button():
    """Verifica se o menu inline principal inclui o botão '🎓 Trilha de Carreiras'."""
    markup = bot.get_main_menu_markup()
    callback_datas = [btn.callback_data for row in markup.inline_keyboard for btn in row]
    btn_texts = [btn.text for row in markup.inline_keyboard for btn in row]
    
    assert "car:main" in callback_datas, "callback_data 'car:main' deve estar presente no get_main_menu_markup()"
    assert any("Trilha de Carreiras" in t for t in btn_texts), "Botão 'Trilha de Carreiras' deve estar presente no menu principal"

def test_carreiras_main_markup_button_limit_and_callbacks():
    """Garante que o menu principal de carreiras tem <= 15 botões e callbacks válidos."""
    markup = bot.get_carreiras_main_markup()
    total_buttons = sum(len(row) for row in markup.inline_keyboard)
    assert total_buttons <= 15, f"Menu de carreiras possui {total_buttons} botões (máximo permitido: 15)"
    
    for row in markup.inline_keyboard:
        for btn in row:
            if btn.callback_data:
                assert len(btn.callback_data.encode("utf-8")) < 64, f"Callback '{btn.callback_data}' excede 64 bytes"

# --- 2. TESTES DE CONTEÚDO DAS 5 PROFISSÕES ELITES ---

def test_content_availability_all_5_professions():
    """Verifica se todas as 5 profissões estão registradas com dados completos e URLs válidas."""
    expected_professions = [
        "server_side_tracking",
        "growth_engineer",
        "analytics_engineer",
        "ia_ops",
        "sdr_tecnico"
    ]
    
    data = bot.CAREER_GUIDANCE_DATA
    assert isinstance(data, dict), "CAREER_GUIDANCE_DATA deve ser um dicionário"
    
    for prof_id in expected_professions:
        assert prof_id in data, f"Profissão '{prof_id}' não encontrada em CAREER_GUIDANCE_DATA"
        prof = data[prof_id]
        
        # Validar campos obrigatórios de R1
        assert prof.get("title"), f"Profissão '{prof_id}' sem título"
        assert prof.get("description") or prof.get("summary"), f"Profissão '{prof_id}' sem descrição/resumo"
        assert prof.get("market_demand"), f"Profissão '{prof_id}' sem informação de mercado"
        
        skills = prof.get("skills", [])
        tools = prof.get("tools", [])
        assert len(skills) >= 3 or len(tools) >= 3, f"Profissão '{prof_id}' deve listar ferramentas/skills"
        
        # Validar etapas de certificação (entre 3 e 5 etapas por profissão)
        steps = prof.get("specialization_steps", prof.get("steps", []))
        assert 3 <= len(steps) <= 5, f"Profissão '{prof_id}' deve conter de 3 a 5 etapas (encontrado: {len(steps)})"
        
        for idx, step in enumerate(steps):
            assert isinstance(step, dict), f"Etapa {idx} de '{prof_id}' deve ser um dicionário"
            assert step.get("step_id"), f"Etapa {idx} de '{prof_id}' sem step_id"
            assert step.get("title"), f"Etapa {idx} de '{prof_id}' sem título"
            assert step.get("cert_url"), f"Etapa {idx} de '{prof_id}' sem cert_url"
            assert step["cert_url"].startswith("http"), f"Etapa {idx} em '{prof_id}' possui URL inválida: {step['cert_url']}"

# --- 3. TESTES DE PERSISTÊNCIA NO BANCO E ISOLAMENTO DE VAGAS ---

def test_career_db_read_write_and_toggle_persistence(tmp_path):
    """Testa salvar, ler e alternar (toggle) o progresso do usuário no SQLite."""
    test_db = os.path.join(tmp_path, "test_career_progress.db")
    original_db = database.DB_PATH
    database.DB_PATH = test_db
    
    try:
        database.init_db()
        
        user_id = "user_test_999"
        prof_id = "server_side_tracking"
        step_id = "step_1"
        
        # Inicialmente deve estar 0 / uncompleted
        prog = database.get_user_career_progress(user_id, prof_id)
        assert step_id not in prog or prog[step_id].get("status") == 0
        
        # Marcar como concluído (status = 1)
        ok = database.save_user_step_status(user_id, prof_id, step_id, 1)
        assert ok is True
        
        prog = database.get_user_career_progress(user_id, prof_id)
        assert step_id in prog
        assert prog[step_id]["status"] == 1
        assert database.get_career_step_status(user_id, prof_id, step_id) is True
        
        # Alternar (toggle) status: 1 -> 0
        new_status = database.toggle_user_step_status(user_id, prof_id, step_id)
        assert new_status == 0
        assert database.get_career_step_status(user_id, prof_id, step_id) is False
        
        # Alternar novamente: 0 -> 1
        new_status = database.toggle_user_step_status(user_id, prof_id, step_id)
        assert new_status == 1
        assert database.get_career_step_status(user_id, prof_id, step_id) is True
        
    finally:
        database.DB_PATH = original_db

def test_career_persistence_does_not_overwrite_job_search_data(tmp_path):
    """Garante isolamento absoluto: dados de carreira não afetam 'jobs', 'applied_jobs' ou 'ignored_jobs'."""
    test_db = os.path.join(tmp_path, "test_jobs_isolation.db")
    original_db = database.DB_PATH
    database.DB_PATH = test_db
    
    try:
        database.init_db()
        
        # Inserir vagas normais de busca
        sample_jobs = [
            {"title": "Dev Server-Side", "company": "Tech Corp", "budget": "R$ 10000", "link": "https://vaga1.com", "platform": "linkedin"},
            {"title": "Growth Engineer", "company": "ScaleUp Inc", "budget": "R$ 12000", "link": "https://vaga2.com", "platform": "indeed"}
        ]
        inserted = database.insert_jobs(sample_jobs)
        assert inserted == 2
        
        # Marcar vaga 1 como candidatada e vaga 2 com acao
        database.mark_applied("https://vaga1.com")
        database.mark_ignored("https://vaga2.com", "fora do perfil")
        
        # Inserir e alterar múltiplos registros de progresso de carreira
        for i in range(1, 5):
            database.save_user_step_status("user_888", "growth_engineer", f"step_{i}", 1)
            database.save_user_step_status("user_888", "ia_ops", f"step_{i}", 1)
            
        # Verificar que tabelas de vagas permanecem completamente inalteradas
        assert database.is_applied("https://vaga1.com") is True
        
        conn = database.get_connection()
        try:
            c = conn.cursor()
            c.execute("SELECT count(*) FROM jobs")
            total_jobs = c.fetchone()[0]
            assert total_jobs == 2
            
            c.execute("SELECT count(*) FROM applied_jobs")
            total_applied = c.fetchone()[0]
            assert total_applied == 1
            
            c.execute("SELECT count(*) FROM ignored_jobs")
            total_ignored = c.fetchone()[0]
            assert total_ignored == 1
        finally:
            conn.close()
            
    finally:
        database.DB_PATH = original_db

# --- 4. TESTES DE VALIDAÇÃO DE CALLBACK_DATA DA TELEGRAM API ---

def test_all_callback_data_under_64_bytes():
    """Valida se TODOS os callback_data gerados em menus e roadmaps respeitam o limite de 64 bytes."""
    # 1. Main menu
    main_markup = bot.get_main_menu_markup()
    for row in main_markup.inline_keyboard:
        for btn in row:
            if btn.callback_data:
                b_len = len(btn.callback_data.encode("utf-8"))
                assert b_len < 64, f"Callback '{btn.callback_data}' tem {b_len} bytes (> 64B)"
                
    # 2. Carreiras main menu
    car_markup = bot.get_carreiras_main_markup()
    for row in car_markup.inline_keyboard:
        for btn in row:
            if btn.callback_data:
                b_len = len(btn.callback_data.encode("utf-8"))
                assert b_len < 64, f"Callback '{btn.callback_data}' tem {b_len} bytes (> 64B)"
                
    # 3. Profession details & roadmap para cada profissão
    for prof_id in bot.CAREER_GUIDANCE_DATA.keys():
        detail_markup = bot.get_profession_detail_markup(prof_id)
        for row in detail_markup.inline_keyboard:
            for btn in row:
                if btn.callback_data:
                    b_len = len(btn.callback_data.encode("utf-8"))
                    assert b_len < 64, f"Detail callback '{btn.callback_data}' tem {b_len} bytes"
                    
        roadmap_markup = bot.get_profession_roadmap_markup("user_test", prof_id)
        for row in roadmap_markup.inline_keyboard:
            for btn in row:
                if btn.callback_data:
                    b_len = len(btn.callback_data.encode("utf-8"))
                    assert b_len < 64, f"Roadmap callback '{btn.callback_data}' tem {b_len} bytes"

# --- 5. TESTES DE INTEGRACÃO E HANDLERS DO TELEGRAM ---

@pytest.mark.asyncio
async def test_cmd_carreiras_handler():
    """Testa a invocação do handler /carreiras."""
    mock_msg = AsyncMock()
    mock_msg.answer = AsyncMock()
    
    await bot.cmd_carreiras(mock_msg)
    
    mock_msg.answer.assert_called_once()
    args, kwargs = mock_msg.answer.call_args
    assert "Guia de Profissionalização" in args[0]
    assert kwargs.get("reply_markup") is not None
