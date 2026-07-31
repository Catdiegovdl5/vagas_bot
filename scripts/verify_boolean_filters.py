import sys
import os
import urllib.parse
from unittest.mock import patch

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scrapers import linkedin
from scrapers import remotar
from bot import is_job_relevant

def verify_boolean_filters():
    print("====================================================")
    print("Verifying Scrapers and Filters (Adversarial Tests)")
    print("====================================================")
    
    # 1. Test different keywords & contract params for LinkedIn
    test_cases = [
        # (Keyword, Level, Country/Location, Contract)
        ("especialista em ia", "Todos", "Brasil (Remoto)", "PJ"),
        ("desenvolvedor python", "Todos", "Brasil (Remoto)", "CLT"),
        ("desenvolvedor backend", "Todos", "Brasil", "Todos"),
        ("desenvolvedor frontend", "Todos", "Brasil (Remoto)", "Freelancer"),
        ("desenvolvedor fullstack", "Todos", "Brasil", "PJ"),
    ]
    
    for kw, lvl, loc, contract in test_cases:
        captured_urls = []
        
        def mock_get(url, *args, **kwargs):
            captured_urls.append(url)
            # return minimalist mock HTML with standard structure
            html = """
            <html>
              <body>
                <li data-entity-urn="urn:li:jobPosting:9999">
                  <h3 class="base-search-card__title">Developer</h3>
                  <h4 class="base-search-card__subtitle">Test Company</h4>
                  <a class="base-card__full-link" href="https://br.linkedin.com/jobs/view/9999">Link</a>
                  <span class="job-search-card__location">Remoto</span>
                </li>
              </body>
            </html>
            """
            class MockResponse:
                def __init__(self, text):
                    self.status_code = 200
                    self.text = text
                    self.content = text.encode("utf-8")
                    self.url = url
            return MockResponse(html)
            
        with patch("curl_cffi.requests.get", side_effect=mock_get):
            # Run LinkedIn scrape
            linkedin.scrape(keyword=kw, level=lvl, country=loc, contract=contract)
            
        # Analyze URL
        url = captured_urls[0]
        decoded = urllib.parse.unquote(url)
        print(f"\n[Test Case] KW: {kw} | Lvl: {lvl} | Loc: {loc} | Contract: {contract}")
        print(f"Captured URL: {url}")
        print(f"Decoded: {decoded}")
        
        # Assertions
        # Check remote filter and &f_WT=2
        if "remoto" in loc.lower() or "remote" in loc.lower():
            assert "f_WT=2" in url, "Expected f_WT=2 in URL for remote job"
            assert "Remoto" in decoded or "Remote" in decoded, "Expected Remote/Remoto filter in keywords"
        else:
            assert "f_WT=2" not in url, "Did not expect f_WT=2 in URL"
            
        # Check contract filters
        if contract == "PJ":
            assert "f_JT=C" in url, "Expected f_JT=C in URL for PJ"
            assert "PJ" in decoded or "Pessoa Jurídica" in decoded, "Expected PJ keywords"
        elif contract == "CLT":
            assert "f_JT=F" in url, "Expected f_JT=F in URL for CLT"
            assert "CLT" in decoded or "Carteira Assinada" in decoded, "Expected CLT keywords"
        else:
            assert "f_JT=" not in url, "Did not expect f_JT parameter in URL"

    print("\n--- Testing Remotar Scraper ---")
    remotar_cases = [
        ("especialista em ia", "Todos", "PJ"),
        ("desenvolvedor python", "Todos", "CLT"),
        ("desenvolvedor backend", "Todos", "Todos"),
    ]
    for kw, lvl, contract in remotar_cases:
        captured_urls = []
        def mock_get_remotar(url, *args, **kwargs):
            captured_urls.append(url)
            class MockResponse:
                def __init__(self):
                    self.status_code = 200
                    self.text = '{"data": []}'
                    self.content = self.text.encode("utf-8")
                def json(self):
                    return {"data": []}
            return MockResponse()
            
        with patch("curl_cffi.requests.get", side_effect=mock_get_remotar), \
             patch("requests.get", side_effect=mock_get_remotar):
            remotar.scrape(keyword=kw, level=lvl, contract=contract)
            
        url = captured_urls[0]
        decoded = urllib.parse.unquote(url)
        print(f"[Remotar Case] KW: {kw} | Contract: {contract}")
        print(f"Captured URL: {url}")
        print(f"Decoded: {decoded}")
        
        # Check encoding
        if contract == "PJ":
            assert "PJ" in decoded, "Expected 'PJ' in Remotar search"
        elif contract == "CLT":
            assert "CLT" in decoded, "Expected 'CLT' in Remotar search"

    print("\n--- Testing is_job_relevant for FP&A / false positives ---")
    
    # Let's test different job titles and descriptions to ensure they do not result in false positives
    test_jobs = [
        # (Job dict, Keyword, expected relevance)
        (
            {"title": "Analista FP&A", "requirements": "Planejamento financeiro, modelagem, consolidação de dados, excel avançado.", "platform": "LinkedIn"},
            "especialista em ia", False
        ),
        (
            {"title": "Analista Financeiro / FP&A", "requirements": "Atuar na área de planejamento e análise financeira, elaboração de reports.", "platform": "LinkedIn"},
            "especialista em ia", False
        ),
        (
            {"title": "Consultor de IA", "requirements": "Experiência com implementação de LLM, RAG e agentes virtuais em Python.", "platform": "LinkedIn"},
            "especialista em ia", True
        ),
        (
            {"title": "Desenvolvedor Python", "requirements": "Desenvolvimento com Django e FastAPI.", "platform": "LinkedIn"},
            "desenvolvedor python", True
        ),
        (
            {"title": "Professor de Python e Django", "requirements": "Leccionamento e elaboração de aulas online.", "platform": "LinkedIn"},
            "desenvolvedor python", False
        ),
        (
            {"title": "Engenheiro de Tráfego Aéreo", "requirements": "Controle de tráfego de aeronaves.", "platform": "LinkedIn"},
            "gestor de trafego", False
        ),
        (
            {"title": "Gestor de Tráfego Pago / Performance", "requirements": "Gerenciamento de campanhas em Google Ads e Meta Ads.", "platform": "LinkedIn"},
            "gestor de trafego", True
        )
    ]
    
    for job, kw, expected in test_jobs:
        settings = {"level": "Todos", "location": "Brasil (Remoto)", "contract": "Todos"}
        res = is_job_relevant(job, kw, settings)
        print(f"Job: '{job['title']}' | KW: '{kw}' | Got: {res} | Expected: {expected}")
        assert res == expected, f"Relevance check failed for Job: {job['title']} and KW: {kw}! Got {res}, expected {expected}."
        
    print("\nAll tests completed and verification passed!")

if __name__ == "__main__":
    verify_boolean_filters()
