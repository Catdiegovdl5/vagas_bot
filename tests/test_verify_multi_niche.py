import sys
import os

# Ensure the correct folder is in sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bot import is_job_relevant, DEFAULT_SETTINGS

def test_developer_niche():
    print("Testing Developer Niche...")
    keyword = "Desenvolvedor Python"
    settings = DEFAULT_SETTINGS.copy()
    settings["location"] = "Todos"
    settings["level"] = "Todos"
    settings["contract"] = "Todos"

    # Valid Case: "Vaga de Desenvolvedor Python Backend"
    # Expected: True
    job_valid = {
        "title": "Vaga de Desenvolvedor Python Backend",
        "requirements": "Requisitos: Experiência com Python, Flask ou Django, banco de dados.",
        "location": "remoto",
        "platform": "linkedin"
    }
    assert is_job_relevant(job_valid, keyword, settings), "Failed: Valid Python Developer job should be approved"

    # Invalid Case: Blacklist "Professor de Python"
    # Expected: False
    job_professor = {
        "title": "Professor de Python e Desenvolvedor",
        "requirements": "Lecionar aulas de Python para iniciantes.",
        "location": "remoto",
        "platform": "linkedin"
    }
    assert not is_job_relevant(job_professor, keyword, settings), "Failed: Professor de Python should be rejected"

    # Invalid Case: Co-occurrence (Missing python backend technologies)
    # Expected: False
    job_missing_tech = {
        "title": "Desenvolvedor de Software",
        "requirements": "Trabalhar com Java e Spring Boot.",
        "location": "remoto",
        "platform": "linkedin"
    }
    assert not is_job_relevant(job_missing_tech, keyword, settings), "Failed: Job with missing Python tech should be rejected"
    print("Developer Niche tests passed!")

def test_marketing_niche():
    print("Testing Marketing Niche...")
    keyword = "Gestor de Tráfego"
    settings = DEFAULT_SETTINGS.copy()
    settings["location"] = "Todos"
    settings["level"] = "Todos"
    settings["contract"] = "Todos"

    # Valid Case: "Procura-se Gestor de Tráfego Pago"
    # Expected: True
    job_valid = {
        "title": "Procura-se Gestor de Tráfego Pago",
        "requirements": "Gerenciar campanhas no Facebook Ads e Google Ads.",
        "location": "remoto",
        "platform": "linkedin"
    }
    assert is_job_relevant(job_valid, keyword, settings), "Failed: Valid traffic manager job should be approved"

    # Invalid Case: Blacklist "Controlador de Tráfego Aéreo"
    # Expected: False
    job_aereo = {
        "title": "Controlador de Tráfego Aéreo",
        "requirements": "Controlar tráfego aéreo no aeroporto da cidade.",
        "location": "Londrina/PR",
        "platform": "linkedin"
    }
    assert not is_job_relevant(job_aereo, keyword, settings), "Failed: Controlador de Tráfego Aéreo should be rejected"
    print("Marketing Niche tests passed!")

def test_designer_niche():
    print("Testing Designer Niche...")
    keyword = "Designer Gráfico"
    settings = DEFAULT_SETTINGS.copy()
    settings["location"] = "Todos"
    settings["level"] = "Todos"
    settings["contract"] = "Todos"

    # Valid Case: "Designer Gráfico Pleno"
    # Expected: True
    job_valid = {
        "title": "Designer Gráfico Pleno",
        "requirements": "Criação de identidade visual e criativos no Figma/Photoshop.",
        "location": "remoto",
        "platform": "linkedin"
    }
    assert is_job_relevant(job_valid, keyword, settings), "Failed: Valid designer job should be approved"

    # Invalid Case: Blacklist "Programador e Designer Gráfico"
    # Expected: False
    job_programador = {
        "title": "Programador e Designer Gráfico",
        "requirements": "Desenvolvimento de sites WordPress e design de logotipos.",
        "location": "remoto",
        "platform": "linkedin"
    }
    assert not is_job_relevant(job_programador, keyword, settings), "Failed: Programador e Designer Gráfico should be rejected"
    print("Designer Niche tests passed!")

def test_settings_filters():
    print("Testing Settings Filters (Location, Contract, Level)...")
    keyword = "Desenvolvedor Python"
    
    # 1. Location constraint: Remoto
    settings_remote = DEFAULT_SETTINGS.copy()
    settings_remote["location"] = "Brasil (Remoto)"
    
    job_presential = {
        "title": "Desenvolvedor Python Presencial",
        "requirements": "Atuação 100% presencial no escritório de São Paulo.",
        "location": "São Paulo, SP",
        "platform": "linkedin"
    }
    assert not is_job_relevant(job_presential, keyword, settings_remote), "Failed: Presential job should be rejected for remote setting"

    # 2. Contract constraint: CLT
    settings_clt = DEFAULT_SETTINGS.copy()
    settings_clt["contract"] = "CLT"
    
    job_pj = {
        "title": "Desenvolvedor Python PJ",
        "requirements": "Contratação estritamente como Pessoa Jurídica (PJ).",
        "location": "remoto",
        "platform": "linkedin"
    }
    assert not is_job_relevant(job_pj, keyword, settings_clt), "Failed: PJ-only job should be rejected for CLT setting"

    # 3. Level constraint: Júnior
    settings_jr = DEFAULT_SETTINGS.copy()
    settings_jr["level"] = "Júnior"
    
    job_senior = {
        "title": "Desenvolvedor Python Sênior",
        "requirements": "Requisitos: Experiência de +5 anos liderando equipes de Python.",
        "location": "remoto",
        "platform": "linkedin"
    }
    assert not is_job_relevant(job_senior, keyword, settings_jr), "Failed: Sênior job should be rejected for Júnior setting"
    print("Settings filters tests passed!")

if __name__ == "__main__":
    test_developer_niche()
    test_marketing_niche()
    test_designer_niche()
    test_settings_filters()
    print("All multi-niche and settings tests passed successfully!")
