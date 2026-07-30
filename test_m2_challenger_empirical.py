"""
Empirical Challenger Test Suite for Milestone 2: Scraper Configuration & Macro-Searches
Author: Challenger Agent (critic / specialist)

Verifies:
1. py_compile clean pass for bot.py, app.py, and scrapers/*.py
2. Macro search terms ("Indústria", "Logística", "Administrativo", "Design", "Vendas", "Engenharia de Dados", etc.)
3. Sub-profession classification for "Pintor Industrial", "Almoxarife", and other key roles
4. Global blacklist behavior (inclusion of academic/legal/intern terms, non-exclusion of industrial trade roles)
5. Edge cases: missing fields, case/accent insensitivity, cross-domain rejection
"""

import os
import glob
import py_compile
import unittest

import bot
from bot import is_job_relevant, classify_job_profession, SEARCH_MAPPING, global_title_blacklist


class TestPyCompileCleanPass(unittest.TestCase):

    def test_all_python_files_compile(self):
        """Verify py_compile clean pass across bot.py, app.py, and all scrapers/*.py."""
        root_dir = os.path.dirname(os.path.abspath(__file__))
        target_files = [
            os.path.join(root_dir, "bot.py"),
            os.path.join(root_dir, "app.py")
        ]
        scraper_files = glob.glob(os.path.join(root_dir, "scrapers", "*.py"))
        target_files.extend(scraper_files)

        self.assertGreater(len(target_files), 5, "Should find at least bot.py, app.py, and scrapers")

        compiled_count = 0
        for filepath in target_files:
            rel_path = os.path.relpath(filepath, root_dir)
            try:
                py_compile.compile(filepath, doraise=True)
                compiled_count += 1
            except py_compile.PyCompileError as e:
                self.fail(f"Syntax/Compilation error in file {rel_path}: {e}")

        print(f"\n[PASS] Successfully compiled {compiled_count} python files clean.")


class TestMacroSearches(unittest.TestCase):

    def setUp(self):
        self.default_settings = {
            "level": "Todos",
            "location": "Todos",
            "contract": "Todos",
            "education": "Todos"
        }

    def test_search_mapping_coverage(self):
        """Verify SEARCH_MAPPING includes all 6 macro categories and additional macro keywords."""
        required_macro_categories = [
            "Indústria",
            "Logística",
            "Administrativo",
            "Design",
            "Vendas",
            "Engenharia de Dados"
        ]
        additional_macro_categories = [
            "Operações Físicas",
            "Criativos",
            "Inteligência de Vendas"
        ]

        for macro in required_macro_categories:
            self.assertIn(macro, SEARCH_MAPPING, f"Required macro category '{macro}' missing from SEARCH_MAPPING")

        for macro in additional_macro_categories:
            self.assertIn(macro, SEARCH_MAPPING, f"Macro term '{macro}' missing from SEARCH_MAPPING")

    def test_macro_searches_empirical_relevance(self):
        """Test empirical relevance matching for jobs under all 6 broad macro categories."""
        test_cases = [
            ("Indústria", {
                "title": "Técnico de Manutenção Industrial",
                "requirements": "Atuar na manutenção preventiva e corretiva de equipamentos em linha de produção fabril.",
                "platform": "catho"
            }),
            ("Logística", {
                "title": "Analista de Logística e Armazenagem",
                "requirements": "Gestão de estoque, inventário, conferência de materiais e expedição em centro de distribuição.",
                "platform": "gupy"
            }),
            ("Administrativo", {
                "title": "Assistente Administrativo Financeiro",
                "requirements": "Rotinas de escritório, lançamento de notas fiscais, contas a pagar e faturamento.",
                "platform": "infojobs"
            }),
            ("Design", {
                "title": "Designer Gráfico e Visual",
                "requirements": "Criação de materiais publicitários, mídias digitais, peças gráficas e identidade visual.",
                "platform": "workana"
            }),
            ("Vendas", {
                "title": "Executivo de Vendas B2B",
                "requirements": "Prospecção de novos clientes corporativos, negociação comercial e fechamento de contratos.",
                "platform": "catho"
            }),
            ("Engenharia de Dados", {
                "title": "Engenheiro de Dados Pleno",
                "requirements": "Desenvolvimento de pipelines ETL/ELT em PySpark, SQL, Airflow e manutenção de Data Lake.",
                "platform": "gupy"
            }),
        ]

        for macro_kw, job in test_cases:
            result = is_job_relevant(job, macro_kw, self.default_settings)
            self.assertTrue(result, f"Job '{job['title']}' failed relevance check for macro category '{macro_kw}'")

    def test_macro_keywords_casing_and_accents(self):
        """Test macro keywords with variations in case and normalization."""
        macro_variations = [
            ("INDUSTRIA", {"title": "Operador Industrial", "requirements": "Operação de máquinas industriais na fábrica.", "platform": "catho"}),
            ("industria", {"title": "Mecânico Industrial", "requirements": "Manutenção em equipamentos de fábrica.", "platform": "catho"}),
            ("LOGISTICA", {"title": "Auxiliar de Logística", "requirements": "Separação de pedidos e movimentação de estoque.", "platform": "gupy"}),
            ("vendas", {"title": "Consultor de Vendas", "requirements": "Atendimento ao cliente e vendas presenciais/remotas.", "platform": "infojobs"}),
        ]

        for kw, job in macro_variations:
            result = is_job_relevant(job, kw, self.default_settings)
            self.assertTrue(result, f"Macro keyword variation '{kw}' failed to match relevant job '{job['title']}'")


class TestSubProfessionClassification(unittest.TestCase):

    def test_pintor_industrial_classification(self):
        """Test exact classification of 'Pintor Industrial' titles."""
        cases = [
            {"title": "Pintor Industrial", "requirements": "Pintura de estruturas metálicas e jateamento."},
            {"title": "Pintor Industrial Jr", "requirements": "Aplicação de tintas industriais e acabamento."},
            {"title": "Pintor de Estruturas Metálicas", "requirements": "Preparo de superfícies e pintura em fábrica."},
        ]
        for job_in in cases:
            classified = classify_job_profession(dict(job_in))
            self.assertEqual(classified.get("profession"), "Pintor Industrial", f"Failed profession for {job_in['title']}")
            self.assertEqual(classified.get("category"), "Operações Físicas", f"Failed category for {job_in['title']}")

    def test_almoxarife_classification(self):
        """Test exact classification of 'Almoxarife' titles."""
        cases = [
            {"title": "Almoxarife", "requirements": "Organização de almoxarifado, controle de entrada e saída de ferramentas."},
            {"title": "Almoxarife Sênior", "requirements": "Gestão de almoxarifado e recebimento de insumos industriais."},
            {"title": "Auxiliar de Almoxarifado", "requirements": "Auxílio na recepção, conferência e estocagem de peças."},
        ]
        for job_in in cases:
            classified = classify_job_profession(dict(job_in))
            self.assertEqual(classified.get("profession"), "Almoxarife", f"Failed profession for {job_in['title']}")
            self.assertEqual(classified.get("category"), "Logística", f"Failed category for {job_in['title']}")

    def test_other_key_sub_professions_classification(self):
        """Test classification for other core sub-professions across categories."""
        cases = [
            ({"title": "Mecânico Industrial", "requirements": "Manutenção mecânica fabril."}, "Mecânico Industrial", "Operações Físicas"),
            ({"title": "Assistente Financeiro", "requirements": "Contas a pagar e conciliação."}, "Assistente Financeiro", "Administrativo"),
            ({"title": "Editor de Vídeo", "requirements": "Edição Premiere e After Effects."}, "Editor de Vídeo", "Criativos"),
            ({"title": "Executivo de Vendas", "requirements": "Vendas B2B de software."}, "Executivo de Vendas", "Inteligência de Vendas"),
            ({"title": "Engenheiro de Dados", "requirements": "ETL Spark e Databricks."}, "Engenheiro de Dados", "Engenharia de Dados"),
        ]

        for job_in, expected_prof, expected_cat in cases:
            classified = classify_job_profession(dict(job_in))
            self.assertEqual(classified.get("profession"), expected_prof, f"Mismatch in profession for {job_in['title']}")
            self.assertEqual(classified.get("category"), expected_cat, f"Mismatch in category for {job_in['title']}")


class TestGlobalBlacklistBehavior(unittest.TestCase):

    def setUp(self):
        self.default_settings = {
            "level": "Todos",
            "location": "Todos",
            "contract": "Todos",
            "education": "Todos"
        }

    def test_industrial_trade_roles_pass_blacklist(self):
        """Verify Pintor Industrial, Mecânico Industrial, and Almoxarife are not blocked by global blacklist."""
        blacklisted_lower = [term.lower() for term in global_title_blacklist]
        
        self.assertNotIn("pintor", blacklisted_lower, "'pintor' should not be in global_title_blacklist")
        self.assertNotIn("mecanico", blacklisted_lower, "'mecanico' should not be in global_title_blacklist")
        self.assertNotIn("almoxarife", blacklisted_lower, "'almoxarife' should not be in global_title_blacklist")

        trade_jobs = [
            ("Indústria", {"title": "Pintor Industrial", "requirements": "Pintura em fábrica de estruturas.", "platform": "catho"}),
            ("Indústria", {"title": "Mecânico Industrial", "requirements": "Manutenção mecânica de máquinas.", "platform": "infojobs"}),
            ("Logística", {"title": "Almoxarife", "requirements": "Controle de peças em estoque.", "platform": "gupy"}),
        ]

        for kw, job in trade_jobs:
            self.assertTrue(is_job_relevant(job, kw, self.default_settings), f"Trade role '{job['title']}' was incorrectly rejected by relevance/blacklist check")

    def test_blacklisted_titles_are_rejected(self):
        """Verify titles containing blacklisted keywords (academic, legal, intern, etc.) are strictly rejected."""
        rejected_jobs = [
            ("Indústria", {"title": "Professor de Automação Industrial", "requirements": "Aulas para curso técnico em indústria.", "platform": "catho"}),
            ("Administrativo", {"title": "Advogado Trabalhista", "requirements": "Atuação jurídica em contencioso trabalhista.", "platform": "infojobs"}),
            ("Logística", {"title": "Estagiário de Almoxarifado", "requirements": "Estágio em suporte ao almoxarifado.", "platform": "gupy"}),
            ("Design", {"title": "Docente de Design Gráfico", "requirements": "Dar aulas na graduação de design.", "platform": "workana"}),
            ("Engenharia de Dados", {"title": "Promotor de Justiça - TI", "requirements": "Cargo público concursado.", "platform": "gupy"}),
        ]

        for kw, job in rejected_jobs:
            self.assertFalse(is_job_relevant(job, kw, self.default_settings), f"Blacklisted job '{job['title']}' was NOT rejected!")


class TestEdgeCasesAndRobustness(unittest.TestCase):

    def setUp(self):
        self.default_settings = {
            "level": "Todos",
            "location": "Todos",
            "contract": "Todos",
            "education": "Todos"
        }

    def test_null_or_empty_fields(self):
        """Test resilience against None or empty strings in title and requirements."""
        empty_job = {"title": None, "requirements": None, "platform": "catho"}
        # Should not raise exception and should return False
        self.assertFalse(is_job_relevant(empty_job, "Indústria", self.default_settings))

        classified = classify_job_profession(empty_job)
        self.assertIsInstance(classified, dict)

    def test_cross_domain_rejection(self):
        """Test that cross-domain mismatches (e.g. backend dev under 'Administrativo') are rejected."""
        mismatched_jobs = [
            ("Administrativo", {"title": "Desenvolvedor Backend Python", "requirements": "Criar microserviços em FastAPI.", "platform": "catho"}),
            ("Logística", {"title": "Gestor de Tráfego Pago", "requirements": "Meta Ads e Google Ads.", "platform": "gupy"}),
            ("Criativos", {"title": "Torneiro Mecânico", "requirements": "Usinagem de peças de aço.", "platform": "infojobs"}),
        ]

        for kw, job in mismatched_jobs:
            self.assertFalse(is_job_relevant(job, kw, self.default_settings), f"Cross-domain job '{job['title']}' should be rejected for '{kw}' search")


if __name__ == "__main__":
    unittest.main()
