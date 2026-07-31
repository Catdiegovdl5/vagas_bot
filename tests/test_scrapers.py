import sys
import os
import json
import asyncio
import inspect

# 1. Setup Playwright Mock before importing glassdoor
class MockGlassdoorElement:
    def __init__(self, el_type='card'):
        self.el_type = el_type
    def query_selector(self, selector, *args, **kwargs):
        sel_lower = selector.lower()
        if 'title' in sel_lower or 'link' in sel_lower:
            return MockGlassdoorElement('title')
        elif 'employer' in sel_lower or 'company' in sel_lower:
            return MockGlassdoorElement('company')
        elif 'salary' in sel_lower:
            return MockGlassdoorElement('salary')
        elif 'desc' in sel_lower or 'container' in sel_lower:
            return MockGlassdoorElement('desc')
        return MockGlassdoorElement('any')
    def query_selector_all(self, selector, *args, **kwargs):
        return [MockGlassdoorElement('card')]
    def text_content(self, *args, **kwargs):
        if self.el_type == 'title':
            return "Desenvolvedor Glassdoor"
        elif self.el_type == 'company':
            return "Empresa Glassdoor"
        elif self.el_type == 'salary':
            return "R$ 8.000"
        elif self.el_type == 'desc':
            return "Requisitos para a vaga de desenvolvedor na Glassdoor: Experiencia com Python, Django e FastAPI. " * 10
        return "Generic Content"
    def get_attribute(self, name, *args, **kwargs):
        return "https://example.com/glassdoor-job"
    def click(self, *args, **kwargs):
        pass

class MockPage:
    def __init__(self):
        self.url = ""
    def goto(self, url, *args, **kwargs):
        self.url = url
    def wait_for_timeout(self, timeout):
        pass
    def wait_for_selector(self, selector, *args, **kwargs):
        pass
    def content(self):
        return "<html>glassdoor mock page</html>"
    def query_selector_all(self, selector, *args, **kwargs):
        return [MockGlassdoorElement('card')]
    def query_selector(self, selector, *args, **kwargs):
        return MockGlassdoorElement('desc')
    def close(self):
        pass

class MockBrowserContext:
    def new_page(self, *args, **kwargs):
        return MockPage()
    def close(self):
        pass

class MockBrowser:
    def new_context(self, *args, **kwargs):
        return MockBrowserContext()
    def close(self):
        pass

class MockBrowserType:
    def launch(self, *args, **kwargs):
        return MockBrowser()

class MockSyncPlaywright:
    def __init__(self):
        self.chromium = MockBrowserType()
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

class PlaywrightSyncApiMock:
    @staticmethod
    def sync_playwright():
        return MockSyncPlaywright()

sys.modules['playwright.sync_api'] = PlaywrightSyncApiMock

# 2. Setup requests and curl_cffi mock before importing scrapers
import requests
from requests.models import Response

class MockResponse:
    def __init__(self, text, status_code=200):
        self.text = text
        self.content = text.encode('utf-8')
        self.status_code = status_code
    def json(self):
        return json.loads(self.text)

def mock_get(url, *args, **kwargs):
    url_str = str(url)
    
    # JSearch
    if "jsearch.p.rapidapi.com" in url_str:
        return MockResponse(
            '{"data": [{"job_title": "Desenvolvedor Python", "employer_name": "Empresa JSearch", "job_description": "Vaga para desenvolvedor. Requisitos: Python, Django.", "job_apply_link": "https://example.com/jsearch-job"}]}'
        )
    # Workana
    elif "workana.com" in url_str:
        return MockResponse(
            '<html><body><search :results-initials=\'{"results": [{"title": "Desenvolvedor Vue", "slug": "desenvolvedor-vue-123", "description": "Desenvolvimento frontend com Vue.js.", "budget": "USD 500"}]}\'></search></body></html>'
        )
    # Remotar
    elif "api.remotar.com.br" in url_str:
        return MockResponse(
            '{"data": [{"title": "Desenvolvedor React", "company": {"name": "Empresa Remotar"}, "externalLink": "https://example.com/remotar-job", "jobSalary": {"type": "monthly", "currency": "BRL", "from": 5000, "to": 7000}, "subtitle": "React Frontend Developer", "description": "<p>Vaga para React</p>", "moreInfos": ""}]}'
        )
    # Gupy
    elif "employability-portal.gupy.io" in url_str or "portal.gupy.io" in url_str:
        return MockResponse(
            '{"data": [{"id": 1, "name": "Desenvolvedor Gupy", "careerPageName": "Empresa Gupy", "jobUrl": "https://example.com/gupy-job", "type": "vacancy_type_effective", "description": "Vaga de desenvolvedor na Gupy.", "city": "S\u00e3o Paulo", "state": "SP"}]}'
        )
    # Vagas.com
    elif "vagas.com.br" in url_str:
        return MockResponse(
            '<html><body><ul><li class="vaga"><h2><a href="/vagas/v123">Desenvolvedor Vagas.com</a></h2><span class="empresa">Empresa Vagas</span><div class="detalhes">Requisitos: Python e SQL.</div></li></ul></body></html>'
        )
    # Programathor
    elif "programathor.com.br" in url_str:
        return MockResponse(
            '<html><body><div class="cell-list"><a href="/jobs/123"><h3>Desenvolvedor Programathor</h3></a><div class="logo" title="Empresa Programathor"></div><span class="tag">Python</span><span class="tag">Django</span></div></body></html>'
        )
    # Coodesh
    elif "api.coodesh.com" in url_str:
        return MockResponse(
            '{"docs": [{"title": "Desenvolvedor Coodesh", "slug": "desenvolvedor-coodesh-123", "company": {"company_name": "Empresa Coodesh"}, "salary_range_formatted": "R$ 6.000 - R$ 8.000", "skills": [{"name": "Python"}, {"name": "React"}]}]}'
        )
    # Geekhunter
    elif "geekhunter.com" in url_str:
        return MockResponse(
            '<html><body><a href="https://www.geekhunter.com/pt/empresa-geek/jobs/vaga-123"><p class="chakra-text css-q4uo1b">Desenvolvedor Geekhunter</p><p class="chakra-text css-o118sj">R$ 10.000</p><p class="chakra-text css-2fkfcz">CLT</p><div class="css-dqhvn">Python</div><div class="css-dqhvn">AWS</div></a></body></html>'
        )
        
    return MockResponse("<html>Mock HTML Content</html>")

requests.get = mock_get

class MockCurlRequests:
    @staticmethod
    def get(url, *args, **kwargs):
        return mock_get(url, *args, **kwargs)
    @staticmethod
    def post(url, *args, **kwargs):
        return MockResponse('{"status": "success"}')

class MockCurlCffi:
    requests = MockCurlRequests

sys.modules['curl_cffi'] = MockCurlCffi
sys.modules['curl_cffi.requests'] = MockCurlRequests

# Import scrapers after mocking
from scrapers import jsearch, workana, remotar, glassdoor, gupy, vagas_com, programathor, coodesh, geekhunter

def test_scrapers():
    scrapers = {
        "Jsearch": jsearch,
        "Workana": workana,
        "Remotar": remotar,
        "Glassdoor": glassdoor,
        "Gupy": gupy,
        "Vagas Com": vagas_com,
        "Programathor": programathor,
        "Coodesh": coodesh,
        "Geekhunter": geekhunter
    }
    
    failed = False
    
    for name, module in scrapers.items():
        print(f"--- Running {name} Scraper ---")
        try:
            if name in ["Workana", "Remotar"]:
                res = module.scrape(keyword="Desenvolvedor", level="Todos")
            else:
                res = module.scrape(keyword="Desenvolvedor", level="Todos", country="Brasil")
                
            if inspect.isawaitable(res):
                vagas = asyncio.run(res)
            else:
                vagas = res
                
            print(f"[{name}] Found {len(vagas)} jobs.")
            
            # Print first job safely
            if vagas:
                job_desc = str(vagas[0]).encode('ascii', 'ignore').decode('ascii')
                print(f"[{name}] Sample Job: {job_desc}")
            
            # Verify requirement: len(vagas) > 0
            assert len(vagas) > 0, f"Error: {name} returned 0 jobs!"
            print(f"[{name}] PASS\n")
            
        except Exception as e:
            print(f"[{name}] FAIL with exception: {e}")
            import traceback
            traceback.print_exc()
            failed = True
            
    if failed:
        print("Verification finished with failures.")
        sys.exit(1)
    else:
        print("All scrapers verified successfully! Verification finished without errors.")
        sys.exit(0)

if __name__ == "__main__":
    test_scrapers()
