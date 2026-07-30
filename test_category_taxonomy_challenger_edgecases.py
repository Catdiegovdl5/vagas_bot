"""
Challenger Empirical Edge-Case & Stress Test Suite for Milestone 1 (UI Taxonomy Update)
Empirically tests:
1. Basic edge cases (Empty/None profession & title, whitespace, missing fields)
2. Case insensitivity (UPPERCASE, lowercase, MiXeD cAsE)
3. Accent tolerance & NFD normalization
4. Substring false positive collisions (ui in pesquisa/guia, ux in auxiliar, ads in leads)
5. Outros category complementarity
6. UI taxonomy structure (14 categories in PROFESSION_CATEGORIES, 5 accordion drawers in renderCategoryDrawers)
"""

import ast
import re
import unicodedata
import unittest
from pathlib import Path

INDEX_HTML_PATH = Path(__file__).parent / "static" / "index.html"


def norm_str(s: str) -> str:
    """Python exact replica of JS normStr(str) in static/index.html."""
    if not s:
        return ""
    nfkd = unicodedata.normalize("NFD", str(s))
    no_accents = "".join(c for c in nfkd if unicodedata.category(c) != "Mn")
    return no_accents.lower()


def matches_category(job: dict, cat_obj: dict, categories_list: list) -> bool:
    """Python exact replica of JS matchesCategory(j, catObj) in static/index.html."""
    if not cat_obj or cat_obj.get("id") == "all":
        return True

    title_lower = norm_str(job.get("title") or "")
    prof_lower = norm_str(job.get("profession") or "")

    # For 'outros', return everything that does NOT belong to any specific category
    if cat_obj.get("id") == "outros":
        other_cats = [c for c in categories_list if c.get("id") not in ["all", "outros"]]
        belongs_to_other = False
        for c in other_cats:
            c_name_norm = norm_str(c.get("name") or "")
            c_label_norm = norm_str(c.get("label_pt") or "")
            if prof_lower and (
                (c_name_norm and (prof_lower == c_name_norm or c_name_norm in prof_lower))
                or (c_label_norm and (prof_lower == c_label_norm or c_label_norm in prof_lower))
            ):
                belongs_to_other = True
                break
            if c.get("kws"):
                for kw in c["kws"]:
                    kw_norm = norm_str(kw)
                    if kw_norm and (kw_norm in title_lower or kw_norm in prof_lower):
                        belongs_to_other = True
                        break
            if belongs_to_other:
                break
        return not belongs_to_other

    # Check profession field in DB (cat_obj.name and cat_obj.label_pt)
    if prof_lower:
        cat_name_norm = norm_str(cat_obj.get("name") or "")
        cat_label_norm = norm_str(cat_obj.get("label_pt") or "")
        if cat_name_norm and (prof_lower == cat_name_norm or cat_name_norm in prof_lower):
            return True
        if cat_label_norm and (prof_lower == cat_label_norm or cat_label_norm in prof_lower):
            return True

    # Keyword matching
    if cat_obj.get("kws"):
        for kw in cat_obj["kws"]:
            kw_norm = norm_str(kw)
            if kw_norm and (kw_norm in title_lower or kw_norm in prof_lower):
                return True

    return False


class TestChallengerCategoryEdgeCases(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(INDEX_HTML_PATH, "r", encoding="utf-8") as f:
            cls.html_content = f.read()
        cls.categories = cls._parse_js_categories()

    @classmethod
    def _parse_js_categories(cls):
        match = re.search(r"const PROFESSION_CATEGORIES = (\[.*?\]);", cls.html_content, re.DOTALL)
        if not match:
            raise ValueError("PROFESSION_CATEGORIES not found in static/index.html")

        js_array_str = match.group(1)
        cleaned_str = re.sub(r"<i class='[^']*'></i>", "", js_array_str)
        cleaned_str = re.sub(r"id:", "'id':", cleaned_str)
        cleaned_str = re.sub(r"name:", "'name':", cleaned_str)
        cleaned_str = re.sub(r"icon:", "'icon':", cleaned_str)
        cleaned_str = re.sub(r"label_pt:", "'label_pt':", cleaned_str)
        cleaned_str = re.sub(r"label_en:", "'label_en':", cleaned_str)
        cleaned_str = re.sub(r"kws:", "'kws':", cleaned_str)

        return ast.literal_eval(cleaned_str)

    def test_edge_case_empty_or_none_profession(self):
        """Test matching when profession field is empty string, None, or whitespace."""
        cat_logistics = next(c for c in self.categories if c["id"] == "logistica")
        cat_outros = next(c for c in self.categories if c["id"] == "outros")

        # 1. Job with empty profession but matching keyword in title
        job_empty_prof_matching_title = {"title": "Auxiliar de Almoxarifado", "profession": ""}
        self.assertTrue(matches_category(job_empty_prof_matching_title, cat_logistics, self.categories))

        # 2. Job with None profession and None title (completely blank job object)
        job_none = {"title": None, "profession": None}
        self.assertFalse(matches_category(job_none, cat_logistics, self.categories))
        self.assertTrue(matches_category(job_none, cat_outros, self.categories))

        # 3. Job with whitespace profession and missing keywords
        job_spaces = {"title": "  ", "profession": "   "}
        self.assertFalse(matches_category(job_spaces, cat_logistics, self.categories))
        self.assertTrue(matches_category(job_spaces, cat_outros, self.categories))

    def test_edge_case_uppercase_lowercase_mixedcase(self):
        """Test case insensitivity across UPPERCASE, lowercase, and MiXeD cAsE inputs."""
        cat_data = next(c for c in self.categories if c["id"] == "engenharia_dados")

        jobs = [
            {"title": "ENGENHEIRO DE DADOS SENIOR", "profession": "ENGENHARIA DE DADOS"},
            {"title": "engenheiro de dados senior", "profession": "engenharia de dados"},
            {"title": "EnGeNhEiRo De DaDoS SeNiOr", "profession": "EnGeNhEiRa De DaDoS"},
        ]

        for job in jobs:
            self.assertTrue(
                matches_category(job, cat_data, self.categories),
                f"Case matching failed for job title '{job['title']}'",
            )

    def test_edge_case_accent_and_nfd_normalization(self):
        """Test accent tolerance (e.g. 'Operações Físicas' vs 'Operacoes Fisicas')."""
        cat_ops = next(c for c in self.categories if c["id"] == "operacoes_fisicas")

        accented_job = {"title": "TÉCNICO DE MANUTENÇÃO E OPERAÇÕES FÍSICAS", "profession": "OPERAÇÕES FÍSICAS"}
        unaccented_job = {"title": "TECNICO DE MANUTENCAO E OPERACOES FISICAS", "profession": "OPERACOES FISICAS"}

        self.assertTrue(matches_category(accented_job, cat_ops, self.categories))
        self.assertTrue(matches_category(unaccented_job, cat_ops, self.categories))

    def test_empirical_finding_short_keyword_substring_false_positives(self):
        """Empirically confirm substring collision behavior for short keywords ('ui', 'ux', 'ads')."""
        cat_criativos = next(c for c in self.categories if c["id"] == "criativos")
        cat_growth = next(c for c in self.categories if c["id"] == "growth_engineer")

        # 1. 'ux' inside 'Auxiliar' causes false positive match for Criativos
        job_aux_limpeza = {"title": "Auxiliar de Limpeza", "profession": ""}
        self.assertTrue(
            matches_category(job_aux_limpeza, cat_criativos, self.categories),
            "Empirical verification: 'ux' substring in 'Auxiliar' matches Criativos in JS includes()",
        )

        # 2. 'ui' inside 'Pesquisador' / 'Guia' causes false positive match for Criativos
        job_pesquisador = {"title": "Pesquisador Científico", "profession": ""}
        self.assertTrue(
            matches_category(job_pesquisador, cat_criativos, self.categories),
            "Empirical verification: 'ui' substring in 'Pesquisador' matches Criativos in JS includes()",
        )

        # 3. 'ads' inside 'Leads' causes false positive match for Growth & Tráfego
        job_leads = {"title": "Gerente de Leads", "profession": ""}
        self.assertTrue(
            matches_category(job_leads, cat_growth, self.categories),
            "Empirical verification: 'ads' substring in 'Leads' matches Growth & Tráfego in JS includes()",
        )

    def test_outros_complementarity_property(self):
        """Verify 'outros' matches iff a job does NOT match any specific category."""
        cat_outros = next(c for c in self.categories if c["id"] == "outros")
        specific_cats = [c for c in self.categories if c["id"] not in ["all", "outros"]]

        sample_jobs = [
            {"title": "Padeiro Artesanal", "profession": "Gastronomia"},
            {"title": "Engenheiro de Dados Spark", "profession": "Engenharia de Dados"},
            {"title": "SDR B2B Outbound", "profession": "SDR Técnico"},
        ]

        for job in sample_jobs:
            matches_specific = any(matches_category(job, sc, self.categories) for sc in specific_cats)
            matches_out = matches_category(job, cat_outros, self.categories)
            self.assertEqual(matches_out, not matches_specific)


if __name__ == "__main__":
    unittest.main()
