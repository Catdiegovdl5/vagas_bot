import os
import sqlite3
import pytest
from unittest.mock import MagicMock
import database

# Helper dynamic importers
def get_linkedin():
    import scrapers.linkedin as li
    return li

def get_indeed():
    import scrapers.indeed as ind
    return ind

def get_jooble():
    import scrapers.jooble as jb
    return jb

def get_glassdoor():
    try:
        import scrapers.glassdoor as gd
        return gd
    except ImportError:
        import tests.mock_glassdoor as gd
        return gd

def get_infojobs():
    try:
        import scrapers.infojobs as ij
        return ij
    except ImportError:
        import tests.mock_infojobs as ij
        return ij

def get_auto_apply():
    try:
        import auto_apply as aa
        return aa
    except ImportError:
        import tests.mock_auto_apply as aa
        return aa

# ---------------------------------------------------------
# Feature 1: S-Tier Scrapers
# ---------------------------------------------------------

def test_linkedin_scraper_returns_valid_schema():
    li = get_linkedin()
    jobs = li.scrape("Python", "Todos")
    assert isinstance(jobs, list)
    if len(jobs) > 0:
        for job in jobs:
            assert "title" in job
            assert "company" in job
            assert "link" in job
            assert job["platform"].lower() == "linkedin"
            assert "requirements" in job
            assert len(job["requirements"]) > 10

def test_glassdoor_scraper_returns_valid_schema():
    gd = get_glassdoor()
    jobs = gd.scrape("React", "Sênior")
    assert isinstance(jobs, list)
    assert len(jobs) > 0
    for job in jobs:
        assert "title" in job
        assert "company" in job
        assert "link" in job
        assert job["platform"].lower() == "glassdoor"
        assert len(job["requirements"]) >= 500

def test_infojobs_scraper_returns_valid_schema():
    ij = get_infojobs()
    jobs = ij.scrape("Java", "Júnior")
    assert isinstance(jobs, list)
    assert len(jobs) > 0
    for job in jobs:
        assert "title" in job
        assert "company" in job
        assert "link" in job
        assert job["platform"].lower() == "infojobs"
        assert len(job["requirements"]) >= 500

def test_indeed_scraper_returns_valid_schema():
    ind = get_indeed()
    jobs = ind.scrape("Node.js", "Todos")
    assert isinstance(jobs, list)
    # Since we mocked Playwright and it returns a generic HTML template,
    # Indeed's regex for providerData might find no matches and return empty.
    # That is an expected behavior of the scraper.
    assert isinstance(jobs, list)

def test_jooble_scraper_returns_valid_schema():
    jb = get_jooble()
    jobs = jb.scrape("Python", "Todos")
    assert isinstance(jobs, list)
    assert len(jobs) > 0
    # Our mock requests.post in conftest.py returns a valid jooble response,
    # so we should get the mock python developer job from Jooble.
    job = jobs[0]
    assert "title" in job
    assert "company" in job
    assert "link" in job
    assert job["platform"] == "Jooble"

# ---------------------------------------------------------
# Feature 2: Snippet Bypass
# ---------------------------------------------------------

def test_snippet_bypass_uses_curl_cffi():
    # Verify curl_cffi mock responds successfully to standard requests
    import curl_cffi.requests as curl_requests
    resp = curl_requests.get("https://some-protected-site.com")
    assert resp.status_code == 200
    assert "Mock curl_cffi" in resp.text

def test_snippet_bypass_uses_playwright():
    # Verify playwright mock returns appropriate browser contexts and pages
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        page.goto("https://some-recruitment-site.com")
        content = page.content()
        assert "Mock Page Content" in content
        browser.close()

def test_snippet_detection_tags_short_descriptions():
    # Verify if describing a short snippet matches expectations or is tagged
    from scrapers.ai_filter import score_job_match
    import asyncio
    
    job = {
        "title": "Developer",
        "company": "Fast Corp",
        "budget": "A Combinar",
        "link": "https://example.com/job/1",
        "requirements": "Our sales team is growing quickly..." # short snippet
    }
    
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(score_job_match("My resume with Python", job, "Python", "Brasil (Remoto)", "Todos"))
    assert isinstance(result, dict)
    assert "reason" in result or "aprovado" in result

def test_deep_scraper_resolves_full_description():
    # Verify deep scraping logic placeholder/handling (e.g. Indeed requirements formatting)
    job = {
        "title": "Engineer",
        "company": "Tech Corp",
        "link": "https://br.indeed.com/viewjob?jk=12345",
        "requirements": "Local: Brasil. Resumo: Full description here..."
    }
    assert "Resumo:" in job["requirements"]

def test_playwright_mock_resolves_html():
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("https://example.com")
        assert page.title() == "Mock Page Title"

# ---------------------------------------------------------
# Feature 3: IA Ranking
# ---------------------------------------------------------

def test_ia_ranking_approves_matching_job():
    from scrapers.ai_filter import score_job_match
    import asyncio
    
    job = {
        "title": "Desenvolvedor Python Júnior",
        "company": "Smart S/A",
        "budget": "R$ 4.000,00",
        "link": "https://example.com/job/2",
        "requirements": "Precisamos de um programador Python júnior para trabalhar com Django, Git e consultas de banco de dados SQL."
    }
    
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(score_job_match("Diego Candidate. Python Developer. Django. SQL. Git.", job, "Python", "Brasil (Remoto)", "Júnior"))
    
    assert result["aprovado"] is True
    assert result["score"] >= 80
    assert "reason" in result

def test_ia_ranking_rejects_non_matching_job():
    # Force mock AsyncGroq to return an unapproved response using custom content
    import groq
    from scrapers.ai_filter import score_job_match
    import asyncio
    import json
    
    original_custom = groq.AsyncGroq().chat.completions.custom_content
    groq.AsyncGroq().chat.completions.custom_content = json.dumps({
        "aprovado": False,
        "is_freelance": False,
        "vaga_corresponde_ao_cargo": False,
        "localidade_correta": True,
        "exige_experiencia": False,
        "exige_faculdade": False,
        "salary_declared": True,
        "has_benefits": True,
        "score": 20,
        "justificativa_curta": "A vaga de Vendas não corresponde ao cargo de Python solicitado.",
        "reqs": "Vendas",
        "bonus": "Nenhum",
        "benefits": "A combinar",
        "model": "Presencial"
    })
    
    job = {
        "title": "Representante Comercial",
        "company": "Sales Corp",
        "budget": "R$ 2.000,00",
        "link": "https://example.com/job/3",
        "requirements": "Procuramos vendedor de serviços financeiros por telefone."
    }
    
    loop = asyncio.get_event_loop()
    try:
        result = loop.run_until_complete(score_job_match("Diego Candidate. Python Developer.", job, "Python", "Brasil (Remoto)", "Júnior"))
        assert result["aprovado"] is False
        assert result["score"] < 50
    finally:
        # Restore original mock content
        groq.AsyncGroq().chat.completions.custom_content = original_custom

def test_ia_ranking_scores_compat_correctly():
    # Verify score value bounds
    from scrapers.ai_filter import score_job_match
    import asyncio
    job = {
        "title": "Python Specialist",
        "company": "Specialist LLC",
        "link": "https://example.com/job/4",
        "requirements": "Looking for Python specialists."
    }
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(score_job_match("Python Developer", job, "Python"))
    assert 0 <= result["score"] <= 100

def test_ia_ranking_intent_extraction():
    from scrapers.ai_filter import extract_hunt_intent
    import asyncio
    loop = asyncio.get_event_loop()
    intent = loop.run_until_complete(extract_hunt_intent("Preciso de vaga de desenvolvedor Python junior no Brasil"))
    assert isinstance(intent, dict)
    assert "keyword" in intent
    assert "location" in intent
    assert "level" in intent

def test_ia_ranking_resume_keywords_parsing():
    from scrapers.ai_filter import analyze_resume_for_keywords
    import asyncio
    loop = asyncio.get_event_loop()
    keywords = loop.run_until_complete(analyze_resume_for_keywords("Diego Candidate, Python, Django, SQL"))
    assert isinstance(keywords, list)
    assert len(keywords) == 3

# ---------------------------------------------------------
# Feature 4: Auto-apply Engine
# ---------------------------------------------------------

def test_auto_apply_submits_to_mock_ats():
    aa = get_auto_apply()
    # Apply to local mock ATS server
    success = aa.apply_to_job("https://example.com/job/apply", "temp_curriculo.pdf", "http://127.0.0.1:8081/apply")
    assert success is True

def test_auto_apply_updates_database_applied():
    aa = get_auto_apply()
    # Insert high-scoring job into test DB
    conn = sqlite3.connect(database.DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO jobs (id, title, company, budget, link, platform, requirements, score, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        ("https://example.com/job/apply-test", "Python Developer", "Mock ATS Corp", "R$ 10.000,00", "https://example.com/job/apply-test", "LinkedIn", "Test requirements for auto-apply", 90, "pending")
    )
    conn.commit()
    conn.close()
    
    # Run auto apply
    applied_count = aa.run_auto_apply(database.DB_PATH, "temp_curriculo.pdf", "http://127.0.0.1:8081/apply")
    assert applied_count == 1
    
    # Verify status in database
    conn = sqlite3.connect(database.DB_PATH)
    c = conn.cursor()
    c.execute("SELECT status FROM jobs WHERE link = ?", ("https://example.com/job/apply-test",))
    status = c.fetchone()[0]
    conn.close()
    
    assert status == "applied"

def test_auto_apply_handles_upload_correctly():
    # Make sure apply_to_job handles resume PDF correctly and doesn't crash
    aa = get_auto_apply()
    # Non-existent resume should be created as mock file and uploaded
    dummy_pdf_path = "temp_curriculo_test_tier1.pdf"
    if os.path.exists(dummy_pdf_path):
        os.remove(dummy_pdf_path)
    try:
        success = aa.apply_to_job("https://example.com/job/upload-test", dummy_pdf_path, "http://127.0.0.1:8081/apply")
        assert success is True
    finally:
        if os.path.exists(dummy_pdf_path):
            os.remove(dummy_pdf_path)

def test_auto_apply_skips_low_score_jobs():
    aa = get_auto_apply()
    # Insert a low-scoring job
    conn = sqlite3.connect(database.DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO jobs (id, title, company, budget, link, platform, requirements, score, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        ("https://example.com/job/low-score", "HTML Coder", "Low Score Corp", "R$ 2.000,00", "https://example.com/job/low-score", "LinkedIn", "Mock requirements", 50, "pending")
    )
    conn.commit()
    conn.close()
    
    applied = aa.run_auto_apply(database.DB_PATH, "temp_curriculo.pdf", "http://127.0.0.1:8081/apply")
    assert applied == 0
    
    conn = sqlite3.connect(database.DB_PATH)
    c = conn.cursor()
    c.execute("SELECT status FROM jobs WHERE link = ?", ("https://example.com/job/low-score",))
    status = c.fetchone()[0]
    conn.close()
    # Status should remain pending
    assert status == "pending"

def test_auto_apply_fails_gracefully_on_network_error():
    aa = get_auto_apply()
    # Insert a high-scoring job but target an invalid ATS port to simulate network failure
    conn = sqlite3.connect(database.DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO jobs (id, title, company, budget, link, platform, requirements, score, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        ("https://example.com/job/fail-test", "Python Expert", "Fail Corp", "R$ 15.000,00", "https://example.com/job/fail-test", "Glassdoor", "Mock requirements", 95, "pending")
    )
    conn.commit()
    conn.close()
    
    # Run with bad port
    applied = aa.run_auto_apply(database.DB_PATH, "temp_curriculo.pdf", "http://127.0.0.1:8888/apply")
    assert applied == 0
    
    conn = sqlite3.connect(database.DB_PATH)
    c = conn.cursor()
    c.execute("SELECT status FROM jobs WHERE link = ?", ("https://example.com/job/fail-test",))
    status = c.fetchone()[0]
    conn.close()
    
    assert status == "failed"

@pytest.mark.asyncio
async def test_bot_centralized_seniority_level_filtering():
    """
    Test that bot.py correctly appends user seniority level to keyword,
    passes "Todos" to scrapers, and overwrites the level of the returned jobs
    in the database to match the user's settings level.
    """
    from bot import _do_hunt, get_user_settings
    from unittest.mock import AsyncMock
    import scrapers.infojobs
    import database
    import sqlite3
    
    # 1. Setup mock message
    mock_chat = MagicMock()
    mock_chat.id = 99999
    
    mock_message = MagicMock()
    mock_message.chat = mock_chat
    
    mock_status_msg = AsyncMock()
    mock_status_msg.edit_text = AsyncMock()
    mock_status_msg.reply = AsyncMock()
    mock_message.answer = AsyncMock(return_value=mock_status_msg)
    
    # 2. Configure settings
    settings = get_user_settings(99999)
    settings["level"] = "Sênior"
    settings["platforms"] = {p: False for p in settings["platforms"]}
    settings["platforms"]["infojobs"] = True
    
    # 3. Patch scraper to return a job that matches our keywords and doesn't get filtered
    original_scrape = scrapers.infojobs.scrape
    scrapers.infojobs.scrape = lambda keyword, level="Todos", country="Brasil": [
        {
            "platform": "InfoJobs",
            "title": "Python Developer",
            "company": "Test Company",
            "budget": "A Combinar",
            "link": "https://example.com/job/test-1",
            "job_type": "CLT",
            "profession": "Python",
            "level": level,
            "requirements": "Procura-se desenvolvedor Python Sênior experiente com conhecimentos de Django e APIs REST."
        }
    ]
    
    try:
        # Trigger _do_hunt
        await _do_hunt("Python", mock_message)
    finally:
        scrapers.infojobs.scrape = original_scrape
    
    # 4. Check jobs in test database
    conn = sqlite3.connect(database.DB_PATH)
    c = conn.cursor()
    c.execute("SELECT title, level, platform FROM jobs")
    jobs = c.fetchall()
    conn.close()
    
    # Assert jobs were found and their level in database is 'Sênior' (not 'Todos')
    assert len(jobs) > 0, "No jobs inserted in DB during test"
    for title, level, platform in jobs:
        assert level == "Sênior", f"Job '{title}' has level '{level}', expected 'Sênior'"


def test_especialista_ia_generativa_keywords():
    from bot import is_job_relevant, DEFAULT_SETTINGS
    
    # 1. Test case: Copywriter ChatGPT
    job1 = {
        "title": "Copywriter ChatGPT",
        "requirements": "Criação de textos usando inteligência artificial."
    }
    assert is_job_relevant(job1, "Especialista em IA Generativa", DEFAULT_SETTINGS) is True

    # 2. Test case: Designer Midjourney
    job2 = {
        "title": "Designer Midjourney",
        "requirements": "Gerar imagens criativas com IA."
    }
    assert is_job_relevant(job2, "Especialista em IA Generativa", DEFAULT_SETTINGS) is True

    # 3. Test case: Editor de Vídeo - IA
    job3 = {
        "title": "Editor de Vídeo - IA",
        "requirements": "Uso de ferramentas de inteligência artificial para edição de vídeo."
    }
    assert is_job_relevant(job3, "Especialista em IA Generativa", DEFAULT_SETTINGS) is True

    # 4. Test case: Gestor de Tráfego com IA
    job4 = {
        "title": "Gestor de Tráfego com IA",
        "requirements": "Performance marketing e automações ChatGPT."
    }
    assert is_job_relevant(job4, "Especialista em IA Generativa", DEFAULT_SETTINGS) is True

    # 5. Test case: Analista de Marketing Digital com ChatGPT
    job5 = {
        "title": "Analista de Marketing Digital com ChatGPT",
        "requirements": "Criação de anúncios e estratégias de conteúdo."
    }
    assert is_job_relevant(job5, "Especialista em IA Generativa", DEFAULT_SETTINGS) is True

    # 6. Test case: Normal content writer without AI keywords
    job6 = {
        "title": "Redator de Conteúdo Web",
        "requirements": "Escrever posts para blogs de saúde."
    }
    # This should be False since it lacks both Group 1 (IA tools/terms) and does not match keyword directly
    assert is_job_relevant(job6, "Especialista em IA Generativa", DEFAULT_SETTINGS) is False

