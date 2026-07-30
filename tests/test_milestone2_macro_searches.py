"""
Unit test suite for Milestone 2: Scraper Configuration & Macro-Searches
Validates:
- Macro keyword searches for all 6 broad categories
- Sub-profession classification and relevance matching
- "Pintor Industrial" and "Mecânico Industrial" pass global title blacklist
- Invalid cross-domain jobs are correctly rejected by blacklist rules
"""

import unittest
from bot import is_job_relevant, classify_job_profession, SEARCH_MAPPING, global_title_blacklist


class TestMilestone2MacroSearches(unittest.TestCase):

    def setUp(self):
        self.default_settings = {
            "level": "Todos",
            "location": "Todos",
            "contract": "Todos",
            "education": "Todos"
        }

    def test_search_mapping_contains_macro_keywords(self):
        """Verify SEARCH_MAPPING includes all broad category macro terms and sub-professions."""
        macro_terms = [
            "Operações Físicas", "Indústria", "Logística", "Administrativo",
            "Criativos", "Design", "Inteligência de Vendas", "Vendas", "Engenharia de Dados"
        ]
        for term in macro_terms:
            self.assertIn(term, SEARCH_MAPPING, f"Macro keyword '{term}' missing from SEARCH_MAPPING")

    def test_pintor_industrial_not_rejected_by_global_blacklist(self):
        """Verify 'Pintor Industrial' and 'Mecânico Industrial' pass global_title_blacklist."""
        self.assertNotIn("pintor", global_title_blacklist)
        self.assertNotIn("mecanico", global_title_blacklist)

        job_pintor = {
            "title": "Pintor Industrial",
            "requirements": "Executar pintura industrial em estruturas metálicas na fábrica e linha de produção.",
            "platform": "catho"
        }
        self.assertTrue(
            is_job_relevant(job_pintor, "Indústria", self.default_settings),
            "Pintor Industrial should be relevant for 'Indústria' search"
        )

        job_mecanico = {
            "title": "Mecânico Industrial",
            "requirements": "Manutenção mecânica industrial preventiva e corretiva de máquinas na fábrica.",
            "platform": "infojobs"
        }
        self.assertTrue(
            is_job_relevant(job_mecanico, "Indústria", self.default_settings),
            "Mecânico Industrial should be relevant for 'Indústria' search"
        )

    def test_macro_keyword_searches_6_categories(self):
        """Test macro keyword searches across all 6 broad categories."""
        cases = [
            ("Indústria", {
                "title": "Técnico de Manutenção Industrial",
                "requirements": "Manutenção em linha de produção e máquinas industriais de fábrica.",
                "platform": "catho"
            }),
            ("Logística", {
                "title": "Assistente de Logística e Estoque",
                "requirements": "Controle de estoque, expedição, armazenagem e inventário em depósito.",
                "platform": "gupy"
            }),
            ("Administrativo", {
                "title": "Assistente Administrativo Financeiro",
                "requirements": "Rotinas de escritório, contas a pagar, contas a receber e faturamento.",
                "platform": "infojobs"
            }),
            ("Design", {
                "title": "Designer Gráfico Criativo",
                "requirements": "Criação de identidade visual, artes para mídias sociais e projetos de design.",
                "platform": "workana"
            }),
            ("Vendas", {
                "title": "Executivo de Vendas B2B",
                "requirements": "Prospecção de clientes, negociação comercial e gestão de contas de vendas.",
                "platform": "catho"
            }),
            ("Engenharia de Dados", {
                "title": "Engenheiro de Dados Sr",
                "requirements": "Construção de pipelines de dados ETL utilizando Spark, PySpark, Airflow e SQL.",
                "platform": "gupy"
            }),
        ]

        for macro_kw, job in cases:
            self.assertTrue(
                is_job_relevant(job, macro_kw, self.default_settings),
                f"Job '{job['title']}' should be relevant for macro search '{macro_kw}'"
            )

    def test_sub_profession_classification(self):
        """Test sub-profession classification logic via classify_job_profession."""
        sub_professions = [
            ({"title": "Pintor Industrial Jr", "requirements": "Pintura industrial em fábrica."}, "Pintor Industrial", "Operações Físicas"),
            ({"title": "Almoxarife Sênior", "requirements": "Gestão de almoxarifado e recebimento de materiais."}, "Almoxarife", "Logística"),
            ({"title": "Assistente Financeiro Pleno", "requirements": "Fluxo de caixa e conciliação bancária."}, "Assistente Financeiro", "Administrativo"),
            ({"title": "Editor de Vídeo e Motion", "requirements": "Edição de vídeos no Premiere e After Effects."}, "Editor de Vídeo", "Criativos"),
            ({"title": "Executivo de Vendas B2B", "requirements": "Fechamento de contratos comerciais e prospecção."}, "Executivo de Vendas", "Inteligência de Vendas"),
            ({"title": "Engenheiro de Dados", "requirements": "Arquitetura de data lake e pipelines ETL Spark."}, "Engenheiro de Dados", "Engenharia de Dados"),
        ]

        for raw_job, expected_prof, expected_cat in sub_professions:
            classified = classify_job_profession(raw_job)
            self.assertEqual(
                classified.get("profession"),
                expected_prof,
                f"Expected profession '{expected_prof}' for title '{raw_job['title']}', got '{classified.get('profession')}'"
            )
            self.assertTrue(
                classified.get("category") in (expected_cat, "Criativos de Performance", "Engenharia de IA/Dados"),
                f"Expected category '{expected_cat}' for title '{raw_job['title']}', got '{classified.get('category')}'"
            )

    def test_invalid_cross_domain_jobs_rejected(self):
        """Test that invalid cross-domain jobs are correctly rejected by blacklist rules."""
        invalid_cases = [
            ("Indústria", {
                "title": "Advogado Trabalhista",
                "requirements": "Atuação jurídica em direito do trabalho para indústrias.",
                "platform": "catho"
            }),
            ("Logística", {
                "title": "Gestor de Tráfego Pago",
                "requirements": "Gestão de tráfego pago em Meta Ads e Google Ads para e-commerce.",
                "platform": "gupy"
            }),
            ("Administrativo", {
                "title": "Desenvolvedor Backend Python",
                "requirements": "Desenvolvimento de APIs RESTful em FastAPI e Django.",
                "platform": "infojobs"
            }),
            ("Criativos", {
                "title": "Mecânico de Manutenção",
                "requirements": "Manutenção mecânica de motores e máquinas pesadas.",
                "platform": "catho"
            }),
            ("Vendas", {
                "title": "Engenheiro de Dados",
                "requirements": "Construção de pipelines ETL com Apache Spark e Hadoop.",
                "platform": "gupy"
            }),
        ]

        for macro_kw, job in invalid_cases:
            self.assertFalse(
                is_job_relevant(job, macro_kw, self.default_settings),
                f"Cross-domain job '{job['title']}' should be rejected for macro search '{macro_kw}'"
            )


if __name__ == "__main__":
    unittest.main()
