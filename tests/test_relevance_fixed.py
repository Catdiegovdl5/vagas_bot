import sys
import os

# Ensure the correct folder is in sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bot import is_job_relevant, DEFAULT_SETTINGS

def test_relevance():
    keyword = "Especialista em IA"
    settings = DEFAULT_SETTINGS.copy()
    settings["location"] = "Todos"
    settings["level"] = "Todos"
    settings["contract"] = "Todos"

    # Case 1: "Vendedor Especialista..." (with keyword "Especialista em IA")
    # Expected: Rejected (False) due to "Vendedor" in commercial_sales blacklist
    job_vendedor = {
        "title": "Vendedor Especialista em Soluções",
        "requirements": "Procuramos profissional com experiência em vendas de tecnologia e IA.",
        "location": "remoto",
        "platform": "linkedin"
    }
    assert not is_job_relevant(job_vendedor, keyword, settings), "Failed: Vendedor Especialista should be rejected"

    # Case 2: "Especialista Em Anúncios Mercado Livre" (with keyword "Especialista em IA")
    # Expected: Rejected (False) due to "Anúncios" / "Mercado Livre" in marketing_ads blacklist,
    # and "ia" Portuguese verb lookaround conflict.
    job_anuncios = {
        "title": "Especialista Em Anúncios Mercado Livre",
        "requirements": "Procuramos um profissional qualificado que ia gerenciar campanhas de tráfego pago.",
        "location": "remoto",
        "platform": "linkedin"
    }
    assert not is_job_relevant(job_anuncios, keyword, settings), "Failed: Especialista Em Anúncios Mercado Livre should be rejected"

    # Case 3: "Editor de Vsl com especialista Ia" (with keyword "Especialista em IA")
    # Expected: Rejected (False) due to "Editor" / "Vsl" in creative_video blacklist
    job_editor = {
        "title": "Editor de Vsl com especialista Ia",
        "requirements": "Desejável domínio de Premiere Pro, After Effects e ferramentas de Ia.",
        "location": "remoto",
        "platform": "linkedin"
    }
    assert not is_job_relevant(job_editor, keyword, settings), "Failed: Editor de Vsl com especialista Ia should be rejected"

    # Valid Case: "Buscamos um Especialista em IA para treinar LLMs..." (with keyword "Especialista em IA")
    # Expected: Approved (True)
    job_valid = {
        "title": "Buscamos um Especialista em IA para treinar LLMs",
        "requirements": "Atuar na criação e treinamento de LLMs, engenharia de prompt e IA generativa.",
        "location": "remoto",
        "platform": "linkedin"
    }
    assert is_job_relevant(job_valid, keyword, settings), "Failed: Valid Specialist in AI job should be approved"

    print("All relevance tests passed successfully!")

if __name__ == "__main__":
    test_relevance()
