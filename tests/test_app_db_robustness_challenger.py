import pytest
import html
import hashlib
import sqlite3
import os
import sys
import time
from unittest.mock import patch, AsyncMock

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from fastapi.testclient import TestClient
from prioriti.app import app
import prioriti.app as app_module
import prioriti.database as db_module
from prioriti.normalizer import normalizar_banco_dados

client = TestClient(app, raise_server_exceptions=False)

@pytest.fixture
def temp_db(tmp_path):
    """Fixture providing an isolated temporary database for testing database integrity, with normalizer applied."""
    db_file = tmp_path / "challenger_test_jobs.db"
    db_path_str = str(db_file)
    with patch("prioriti.database.DB_PATH", db_path_str):
        db_module.init_db()
        normalizar_banco_dados()
        yield db_path_str


# =====================================================================
# TEST SUITE 1: Telegram Notification Exception Escaping
# =====================================================================

class TestTelegramNotificationEscaping:
    
    def test_telegram_escaping_malformed_html_script_and_special_chars(self):
        """
        Empirically test that when an unhandled exception occurs, malformed HTML/Markdown characters
        (<script>, _, *, &, ", ') in the URL path and exception message are safely escaped using html.escape.
        """
        posted_payloads = []

        async def mock_post(url, json=None, **kwargs):
            posted_payloads.append({"url": url, "json": json})
            mock_resp = AsyncMock()
            mock_resp.status_code = 200
            return mock_resp

        # Inject route that raises an exception with malformed HTML/Markdown characters
        @app.get("/test/malformed_escape")
        def route_with_malformed_exc(query: str = ""):
            raise ValueError(f"Malformed exc error: <script>alert('xss&\"1\"')</script> _bold_ *italic* & foo='bar'")

        # Reset rate limiter timestamp in prioriti.app
        app_module._last_alert_time = 0

        with patch.dict(os.environ, {"TELEGRAM_BOT_TOKEN": "123456:TEST_BOT_TOKEN", "ADMIN_TELEGRAM_ID": "99999"}), \
             patch("httpx.AsyncClient.post", side_effect=mock_post):

            response = client.get("/test/malformed_escape?query=<script>bad_query</script>&sym=*_&'")
            
            assert response.status_code == 500
            assert response.json() == {"status": "error", "message": "Ocorreu um erro interno de servidor."}

            assert len(posted_payloads) == 1
            telegram_msg = posted_payloads[0]["json"]["text"]
            parse_mode = posted_payloads[0]["json"]["parse_mode"]
            assert parse_mode == "HTML"

            # Check that raw unescaped <script> tag is NOT present in Telegram payload
            assert "<script>" not in telegram_msg
            assert "&lt;script&gt;" in telegram_msg
            
            # Check that & is escaped as &amp;
            assert "&amp;" in telegram_msg

            # Verify HTML tag structure of the critical error message is intact
            assert telegram_msg.startswith("🚨 <b>CRITICAL UNHANDLED ERROR</b>")
            assert "📍 <b>Rota:</b> <code>" in telegram_msg
            assert "❌ <b>Exceção:</b> <code>" in telegram_msg

    def test_telegram_escaping_unclosed_html_tags_in_path_and_exc(self):
        """
        Verify that unclosed HTML tags (<b>, <code>, <a>, <div>) in path and exception string
        do not corrupt the Telegram HTML payload structure.
        """
        posted_payloads = []

        async def mock_post(url, json=None, **kwargs):
            posted_payloads.append({"url": url, "json": json})
            mock_resp = AsyncMock()
            mock_resp.status_code = 200
            return mock_resp

        @app.get("/test/unclosed_tags/{path_val}")
        def route_unclosed(path_val: str):
            raise RuntimeError("Unclosed tags crash test: <b>unclosed bold <code>unclosed code <a href='http://bad'>link")

        app_module._last_alert_time = 0

        with patch.dict(os.environ, {"TELEGRAM_BOT_TOKEN": "123456:TEST_BOT_TOKEN"}), \
             patch("httpx.AsyncClient.post", side_effect=mock_post):

            response = client.get("/test/unclosed_tags/unclosed_path_tag")
            
            assert response.status_code == 500
            assert len(posted_payloads) == 1
            msg = posted_payloads[0]["json"]["text"]

            # Confirm raw <b> inside code block from input exc was escaped
            assert "&lt;b&gt;" in msg
            assert "&lt;a href=" in msg or "&lt;a" in msg

    def test_telegram_rate_limiting_behavior(self):
        """
        Verify the 5-minute (300s) rate limit on Telegram error alerts.
        """
        posted_payloads = []

        async def mock_post(url, json=None, **kwargs):
            posted_payloads.append({"url": url, "json": json})
            mock_resp = AsyncMock()
            mock_resp.status_code = 200
            return mock_resp

        @app.get("/test/rate_limit_trigger")
        def route_rate_limit():
            raise Exception("Rate limit exception test")

        app_module._last_alert_time = 0

        with patch.dict(os.environ, {"TELEGRAM_BOT_TOKEN": "123456:TEST_BOT_TOKEN"}), \
             patch("httpx.AsyncClient.post", side_effect=mock_post):

            # First call triggers notification
            r1 = client.get("/test/rate_limit_trigger")
            assert r1.status_code == 500
            assert len(posted_payloads) == 1

            # Second call within 300s should NOT post to Telegram, but still return 500
            r2 = client.get("/test/rate_limit_trigger")
            assert r2.status_code == 500
            assert len(posted_payloads) == 1


# =====================================================================
# TEST SUITE 2: /api/vagas Endpoint Robustness
# =====================================================================

class TestApiVagasRobustness:

    def test_api_vagas_default_query(self, temp_db):
        """Verify default /api/vagas call returns HTTP 200 and valid JSON schema."""
        with patch("prioriti.database.DB_PATH", temp_db):
            response = client.get("/api/vagas")
            assert response.status_code == 200
            data = response.json()
            assert "total" in data
            assert "count" in data
            assert "jobs" in data
            assert isinstance(data["jobs"], list)

    def test_api_vagas_empty_strings(self, temp_db):
        """Verify passing empty string parameters for all query params returns HTTP 200."""
        with patch("prioriti.database.DB_PATH", temp_db):
            params = {
                "estado": "",
                "cidade": "",
                "senioridade": "",
                "nivel": "",
                "modalidade": "",
                "categoria": "",
                "subcategoria": "",
                "profession": "",
                "q": ""
            }
            response = client.get("/api/vagas", params=params)
            assert response.status_code == 200
            data = response.json()
            assert "total" in data
            assert "jobs" in data

    def test_api_vagas_sql_injection_and_xss_special_characters(self, temp_db):
        """Stress-test /api/vagas with SQL injection payloads and XSS special characters."""
        with patch("prioriti.database.DB_PATH", temp_db):
            malformed_inputs = [
                "'; DROP TABLE jobs; --",
                "<script>alert('xss')</script>",
                "SP' OR '1'='1",
                "gestor_trafego'; SELECT * FROM jobs; --",
                "%%' AND 1=1 UNION SELECT 1,2,3--",
                "!@#$%^&*()_+-=[]{}|;:'\",.<>?/\\",
                "São Paulo & <script> 🚀"
            ]

            for bad_input in malformed_inputs:
                params = {
                    "estado": bad_input,
                    "cidade": bad_input,
                    "senioridade": bad_input,
                    "modalidade": bad_input,
                    "categoria": bad_input,
                    "subcategoria": bad_input,
                    "profession": bad_input,
                    "q": bad_input
                }
                response = client.get("/api/vagas", params=params)
                assert response.status_code == 200, f"Failed on input: {bad_input}"
                data = response.json()
                assert "total" in data
                assert "count" in data
                assert "jobs" in data
                assert isinstance(data["jobs"], list)

    def test_api_vagas_non_existent_categories_and_locations(self, temp_db):
        """Verify queries with non-existent categories/locations gracefully return 0 matching jobs."""
        with patch("prioriti.database.DB_PATH", temp_db):
            params = {
                "categoria": "category_does_not_exist_999",
                "subcategoria": "subcat_phantom_123",
                "profession": "fake_profession_404",
                "estado": "XX",
                "cidade": "CidadeInexistenteNoMundoReal"
            }
            response = client.get("/api/vagas", params=params)
            assert response.status_code == 200
            data = response.json()
            assert data["total"] == 0
            assert data["count"] == 0
            assert data["jobs"] == []

    def test_api_jobs_alias_route(self, temp_db):
        """Verify /api/jobs works as a functional alias for /api/vagas."""
        with patch("prioriti.database.DB_PATH", temp_db):
            response = client.get("/api/jobs")
            assert response.status_code == 200
            data = response.json()
            assert "jobs" in data

    def test_api_vagas_traffic_category_and_designer_exclusions(self, temp_db):
        """Test specific traffic categories and designer exclusion logic in /api/vagas."""
        with patch("prioriti.database.DB_PATH", temp_db):
            # Seed test jobs into temp_db
            jobs = [
                {"title": "Gestor de Trafego Meta Ads", "company": "Empresa A", "link": "http://job1.com", "platform": "workana"},
                {"title": "Designer Grafico Criativo", "company": "Empresa B", "link": "http://job2.com", "platform": "gupy"},
                {"title": "Media Buyer Google Ads", "company": "Empresa C", "link": "http://job3.com", "platform": "infojobs"}
            ]
            db_module.insert_jobs(jobs)
            normalizar_banco_dados()

            response = client.get("/api/vagas?categoria=gestor_trafego")
            assert response.status_code == 200
            data = response.json()
            assert data["total"] >= 1
            titles = [j["title"] for j in data["jobs"]]
            assert "Gestor de Trafego Meta Ads" in titles
            # Designer Grafico should be excluded
            assert "Designer Grafico Criativo" not in titles

    def test_api_vagas_schema_mismatch_without_normalizer_bug(self, tmp_path):
        """
        EMPIRICAL BUG DETECTION:
        If database is initialized via init_db() alone without normalizar_banco_dados(),
        the 'senioridade_norm' column is missing, causing /api/vagas to return an error dictionary.
        """
        db_file = tmp_path / "raw_init_jobs.db"
        db_path_str = str(db_file)
        with patch("prioriti.database.DB_PATH", db_path_str):
            db_module.init_db() # Raw init_db without normalizer
            response = client.get("/api/vagas")
            assert response.status_code == 200
            data = response.json()
            # Empirical proof: when senioridade_norm column is absent, 'error' key is returned
            assert "error" in data
            assert "no such column: j.senioridade_norm" in data["error"]


# =====================================================================
# TEST SUITE 3: Database Insertion Integrity with MD5 Job IDs
# =====================================================================

class TestDatabaseMD5InsertionIntegrity:

    def test_md5_job_id_generation_format_and_determinism(self, temp_db):
        """
        Verify that MD5 job IDs generated by insert_jobs:
        1. Are exactly 16 hexadecimal characters long.
        2. Are deterministic (same link yields exact same MD5 16-char prefix).
        3. Yield unique hashes for distinct links.
        """
        with patch("prioriti.database.DB_PATH", temp_db):
            link = "https://workana.com/job/desenvolvedor-python-123"
            expected_md5 = hashlib.md5(link.encode('utf-8')).hexdigest()[:16]

            job = {
                "title": "Desenvolvedor Python",
                "company": "Tech Corp",
                "link": link,
                "platform": "workana"
            }

            inserted = db_module.insert_jobs([job])
            assert inserted == 1

            conn = db_module.get_connection()
            c = conn.cursor()
            c.execute("SELECT id, title, link FROM jobs WHERE link = ?", (link,))
            row = c.fetchone()
            conn.close()

            assert row is not None
            inserted_id, inserted_title, inserted_link = row

            assert len(inserted_id) == 16
            assert inserted_id == expected_md5
            assert inserted_title == "Desenvolvedor Python"
            assert inserted_link == link

    def test_explicit_id_preservation(self, temp_db):
        """Verify that when an explicit job 'id' is provided, it is preserved instead of auto-generating MD5."""
        with patch("prioriti.database.DB_PATH", temp_db):
            explicit_id = "CUSTOM_JOB_ID_99"
            job = {
                "id": explicit_id,
                "title": "Dev React",
                "company": "Startup X",
                "link": "https://gupy.io/job/react-99",
                "platform": "gupy"
            }

            inserted = db_module.insert_jobs([job])
            assert inserted == 1

            conn = db_module.get_connection()
            c = conn.cursor()
            c.execute("SELECT id FROM jobs WHERE link = ?", ("https://gupy.io/job/react-99",))
            row = c.fetchone()
            conn.close()

            assert row[0] == explicit_id

    def test_unicode_and_utf8_link_encoding_integrity(self, temp_db):
        """Test that links containing non-ASCII, accents, special characters, and emojis encode cleanly without error."""
        with patch("prioriti.database.DB_PATH", temp_db):
            unicode_links = [
                "https://vagas.com.br/vaga-de-engenheiro-de-dados-são-paulo?ref=tráfego",
                "https://example.com/job?title=Desenvolvedor%20Full%20Stack&city=Florianópolis🔥",
                "https://site.org/vagas/ñandú-especialista-áéíóú-123"
            ]

            jobs = [
                {"title": f"Vaga Unicode {idx}", "company": "Company Unicode", "link": url, "platform": "vagas_com"}
                for idx, url in enumerate(unicode_links)
            ]

            inserted = db_module.insert_jobs(jobs)
            assert inserted == len(unicode_links)

            for url in unicode_links:
                expected_id = hashlib.md5(url.encode('utf-8')).hexdigest()[:16]
                conn = db_module.get_connection()
                c = conn.cursor()
                c.execute("SELECT id FROM jobs WHERE link = ?", (url,))
                row = c.fetchone()
                conn.close()
                assert row is not None
                assert row[0] == expected_id

    def test_duplicate_job_insertion_idempotency(self, temp_db):
        """
        Verify that duplicate job insertions (same link/MD5 ID) trigger sqlite3.IntegrityError,
        which is safely ignored, returning 0 inserted jobs on duplicate run.
        """
        with patch("prioriti.database.DB_PATH", temp_db):
            job = {
                "title": "Data Scientist",
                "company": "AI Labs",
                "link": "https://linkedin.com/jobs/view/1000",
                "platform": "linkedin"
            }

            # First insertion
            count1 = db_module.insert_jobs([job])
            assert count1 == 1

            # Duplicate insertion
            count2 = db_module.insert_jobs([job])
            assert count2 == 0

    def test_malformed_job_objects_resilience(self, temp_db):
        """
        Verify insert_jobs resilience against malformed job objects:
        - None in list
        - Non-dict items (ints, strings, lists)
        - Dicts missing required fields ('link', 'title', 'platform')
        - Dict with link="#"
        - Non-string profession values (lists, tuples, numbers)
        """
        with patch("prioriti.database.DB_PATH", temp_db):
            malformed_batch = [
                None,
                12345,
                "not a dict",
                {},
                {"title": "No Link", "platform": "gupy"}, # Missing link
                {"link": "http://valid.com/1", "platform": "gupy"}, # Missing title
                {"title": "Valid Title", "link": "http://valid.com/2"}, # Missing platform
                {"title": "Hash Link", "link": "#", "platform": "gupy"}, # Invalid link '#'
                {
                    "title": "Job With Tuple Profession",
                    "company": "Corp",
                    "link": "http://valid.com/3",
                    "platform": "workana",
                    "profession": ("Tecnologia", "Engenharia"),
                    "lat": "invalid_lat"
                }
            ]

            inserted = db_module.insert_jobs(malformed_batch)
            assert inserted == 1 # Only valid.com/3 should be inserted

            conn = db_module.get_connection()
            c = conn.cursor()
            c.execute("SELECT title, profession FROM jobs WHERE link = ?", ("http://valid.com/3",))
            row = c.fetchone()
            conn.close()

            assert row is not None
            assert row[0] == "Job With Tuple Profession"
            assert isinstance(row[1], str)

    def test_md5_batch_collision_resistance(self, temp_db):
        """Verify zero collisions for a batch of 500 distinct job links."""
        with patch("prioriti.database.DB_PATH", temp_db):
            batch_size = 500
            jobs = [
                {
                    "title": f"Dev Job {i}",
                    "company": f"Company {i}",
                    "link": f"https://example.com/jobs/dev-{i}?session={i*77}",
                    "platform": "workana"
                }
                for i in range(batch_size)
            ]

            inserted = db_module.insert_jobs(jobs)
            assert inserted == batch_size

            conn = db_module.get_connection()
            c = conn.cursor()
            c.execute("SELECT COUNT(DISTINCT id) FROM jobs")
            count_ids = c.fetchone()[0]
            conn.close()

            assert count_ids == batch_size
