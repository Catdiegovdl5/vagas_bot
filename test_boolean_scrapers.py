import sys
import os
import urllib.parse
from unittest.mock import patch, MagicMock

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scrapers import linkedin
from scrapers import remotar

def test_boolean_scrapers():
    print("==========================================")
    print("Running Boolean Search & Filter Injection Test")
    print("==========================================")

    # We will patch requests and curl_cffi requests to capture URLs and return dummy data
    captured_urls = []

    # Mock curl_cffi responses
    class MockCurlResponse:
        def __init__(self, url, text):
            self.status_code = 200
            self.text = text
            self.content = text.encode("utf-8")
            self.url = url
        def json(self):
            import json
            return json.loads(self.text)

    # LinkedIn mock response data
    li_search_html = """
    <html>
      <body>
        <li>
          <div data-entity-urn="urn:li:jobPosting:11111111">
            <h3 class="base-search-card__title">Especialista em IA Generativa</h3>
            <h4 class="base-search-card__subtitle">SuperAI Corp</h4>
            <a class="base-card__full-link" href="https://br.linkedin.com/jobs/view/especialista-em-ia-11111111">Link</a>
            <span class="job-search-card__location">Remoto</span>
          </div>
        </li>
      </body>
    </html>
    """
    
    li_desc_html = """
    <div class="show-more-less-html__markup">
      Vaga para Especialista em IA Generativa. Procuramos profissional com experiência em LLM, Python, Generative AI. Contratação PJ.
    </div>
    """

    # Remotar mock response data
    remotar_json = """
    {
      "data": [
        {
          "title": "Especialista em IA",
          "company": {"name": "SuperAI Corp"},
          "externalLink": "https://example.com/job1",
          "jobSalary": {"type": "monthly", "currency": "BRL", "from": 10000, "to": 15000},
          "subtitle": "Especialista em IA",
          "description": "<p>Vaga para Especialista em IA</p>",
          "moreInfos": "Requisitos: IA"
        }
      ]
    }
    """

    def mock_curl_get(url, *args, **kwargs):
        captured_urls.append(url)
        print(f"[Mock Curl GET] URL: {url}")
        if "api.remotar.com.br" in url:
            return MockCurlResponse(url, remotar_json)
        if "jobPosting/11111111" in url:
            return MockCurlResponse(url, li_desc_html)
        return MockCurlResponse(url, li_search_html)

    def mock_requests_get(url, *args, **kwargs):
        captured_urls.append(url)
        print(f"[Mock Requests GET] URL: {url}")
        if "api.remotar.com.br" in url:
            return MockCurlResponse(url, remotar_json)
        return MockCurlResponse(url, "<html></html>")

    # Patch both
    with patch("curl_cffi.requests.get", side_effect=mock_curl_get), \
         patch("requests.get", side_effect=mock_requests_get):
         
        # 1. Test LinkedIn
        print("\n--- Testing LinkedIn Scraper ---")
        li_jobs = linkedin.scrape(
            keyword="especialista em ia",
            level="Todos",
            country="Brasil (Remoto)",
            contract="PJ"
        )
        
        # 2. Test Remotar
        print("\n--- Testing Remotar Scraper ---")
        rem_jobs = remotar.scrape(
            keyword="especialista em ia",
            level="Todos",
            contract="PJ"
        )

    # Verification of LinkedIn URLs
    li_urls = [u for u in captured_urls if "linkedin.com" in u]
    assert len(li_urls) > 0, "LinkedIn URL was not captured!"
    
    # Check that it contains native filters
    # WT=2 (workplace type remote) and JT=C (job type contract/PJ)
    assert "f_WT=2" in li_urls[0], "LinkedIn URL missing workplace type remote filter (&f_WT=2)"
    assert "f_JT=C" in li_urls[0], "LinkedIn URL missing contract job type filter (&f_JT=C)"
    
    # Check that boolean query is encoded correctly
    decoded_url = urllib.parse.unquote(li_urls[0])
    print(f"\nDecoded LinkedIn URL: {decoded_url}")
    
    # Assert operators are present in decoded URL
    assert "AND" in decoded_url, "Boolean 'AND' operator missing in query string"
    assert "OR" in decoded_url, "Boolean 'OR' operator missing in query string"
    assert "Inteligência Artificial" in decoded_url
    assert "LLM" in decoded_url
    assert "Remoto" in decoded_url
    assert "PJ" in decoded_url
    
    # Verification of Remotar URLs
    rem_urls = [u for u in captured_urls if "remotar.com.br" in u]
    assert len(rem_urls) > 0, "Remotar URL was not captured!"
    
    decoded_rem_url = urllib.parse.unquote(rem_urls[0])
    print(f"Decoded Remotar URL: {decoded_rem_url}")
    # Remotar keyword mapping: "especialista em ia" -> "IA" + contract "PJ" -> "IA PJ"
    assert "search=IA PJ" in decoded_rem_url, "Remotar URL missing correct search parameters ('IA PJ')"

    # Check assertions on results
    all_jobs = li_jobs + rem_jobs
    assert len(all_jobs) > 0, "No jobs scraped!"
    
    for job in all_jobs:
        title = job.get("title", "")
        desc = job.get("requirements", "")
        # Run a basic assertion that any scraped job title/description does not contain "FP&A"
        assert "FP&A" not in title, f"Found FP&A false positive in title: {title}"
        assert "FP&A" not in desc, f"Found FP&A false positive in description: {desc}"
        
        # Verify job type returned for LinkedIn/Remotar is PJ
        if job["platform"] == "LinkedIn":
            assert job["job_type"] == "PJ", f"Job type should be PJ, got {job['job_type']}"

    print("\n==========================================")
    print("All Boolean Scrapers Verification Tests Passed!")
    print("==========================================")

if __name__ == "__main__":
    test_boolean_scrapers()
