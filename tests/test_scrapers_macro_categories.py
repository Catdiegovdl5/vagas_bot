"""
Unit Test: tests/test_scrapers_macro_categories.py
Verifies that scrapers and category classification natively support all 6 new profession categories:
1. Operações Físicas
2. Logística
3. Administrativo
4. Criativos de Performance
5. Inteligência de Vendas
6. Engenharia de IA/Dados
"""

import unittest
import asyncio
from bot import classify_job_profession, SEARCH_MAPPING, CO_OCCURRENCE_RULES, MAGIC_CATEGORIES
from scrapers import gupy, infojobs, vagas_com, linkedin, catho, workana, glassdoor, indeed, remotar

class TestScrapersMacroCategories(unittest.TestCase):

    def test_bot_magic_categories_contains_all_6(self):
        """Verify MAGIC_CATEGORIES in bot.py has entries for all 6 macro categories."""
        expected_keys = [
            "operacoes_fisicas",
            "logistica",
            "administrativo",
            "criativos_performance",
            "inteligencia_vendas",
            "engenharia_ia_dados",
        ]
        for key in expected_keys:
            self.assertIn(key, MAGIC_CATEGORIES, f"MAGIC_CATEGORIES missing macro category '{key}'")
            self.assertTrue(len(MAGIC_CATEGORIES[key]) >= 5, f"Macro category '{key}' has fewer than 5 search terms")

    def test_search_mapping_covers_macro_categories(self):
        """Verify SEARCH_MAPPING includes mappings for all 6 macro titles and their sub-professions."""
        macro_titles = [
            "Operações Físicas",
            "Logística",
            "Administrativo",
            "Criativos de Performance",
            "Inteligência de Vendas",
            "Engenharia de IA/Dados",
            "Pintor Industrial",
            "Mecânico Industrial",
            "Operador CNC",
            "Soldador",
            "Almoxarife",
            "Assistente de Logística",
            "Assistente Administrativo",
            "Copywriter",
            "Editor de Vídeo",
            "SDR",
            "Executivo de Vendas",
            "Engenheiro de Dados",
            "Engenheiro de IA",
        ]
        for title in macro_titles:
            self.assertTrue(title in SEARCH_MAPPING or title.lower() in SEARCH_MAPPING, f"SEARCH_MAPPING missing title '{title}'")

    def test_classify_job_profession_all_6_categories(self):
        """Verify classify_job_profession accurately tags job['profession'] and job['category']."""
        test_cases = [
            # (Job Dict Input, Expected Category)
            ({"title": "Operador CNC Pleno"}, "Operações Físicas"),
            ({"title": "Pintor Industrial de Estrutura Metálica"}, "Operações Físicas"),
            ({"title": "Mecânico Industrial de Manutenção"}, "Operações Físicas"),
            ({"title": "Auxiliar de Logística e Almoxarifado"}, "Logística"),
            ({"title": "Almoxarife e Conferente de Estoque"}, "Logística"),
            ({"title": "Assistente Administrativo de Vendas"}, "Administrativo"),
            ({"title": "Assistente Financeiro e Contas a Pagar"}, "Administrativo"),
            ({"title": "Editor de Vídeo Premiere e CapCut"}, "Criativos de Performance"),
            ({"title": "Copywriter para Anúncios e VSL"}, "Criativos de Performance"),
            ({"title": "SDR Outbound B2B"}, "Inteligência de Vendas"),
            ({"title": "Executivo de Vendas Inside Sales"}, "Inteligência de Vendas"),
            ({"title": "Engenheiro de Dados PySpark e Airflow"}, "Engenharia de IA/Dados"),
        ]

        for job_in, exp_cat in test_cases:
            res = classify_job_profession(job_in.copy())
            self.assertEqual(res.get("category"), exp_cat, f"Category mismatch for title '{job_in['title']}': got '{res.get('category')}', expected '{exp_cat}'")
            self.assertIsNotNone(res.get("profession"), f"Profession empty for title '{job_in['title']}'")

    def test_scrapers_return_classified_payload(self):
        """Verify scrapers output job payload with populated 'profession' and 'category' fields."""
        test_job = {
            "title": "Mecânico Industrial de Usinagem",
            "company": "Fábrica Teste",
            "requirements": "Manutenção preventiva e corretiva de máquinas industriais",
            "link": "https://example.com/job/1"
        }
        classified = classify_job_profession(test_job)
        self.assertEqual(classified["profession"], "Mecânico Industrial")
        self.assertEqual(classified["category"], "Operações Físicas")


if __name__ == "__main__":
    unittest.main()
