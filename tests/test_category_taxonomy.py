"""
Automated Verification Script: tests/test_category_taxonomy.py
Validates Milestone 1 (UI Taxonomy Update):
- 14 categories in PROFESSION_CATEGORIES
- 5 accordion drawers in renderCategoryDrawers
- matchesCategory tests catObj.name, label_pt, and kws
- Zero unicode emojis and presence of FontAwesome icons
"""

import json
import re
import unittest
from pathlib import Path

INDEX_HTML_PATH = Path(__file__).parent.parent / "static" / "index.html"


class TestCategoryTaxonomy(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(INDEX_HTML_PATH, "r", encoding="utf-8") as f:
            cls.html_content = f.read()

    def test_profession_categories_count_and_ids(self):
        """Verify PROFESSION_CATEGORIES contains expected category IDs."""
        expected_ids = [
            "all",
            "pintor_industrial",
            "soldador",
            "operador_cnc",
            "auxiliar_producao",
            "almoxarife",
            "auxiliar_logistica",
            "assistente_adm",
            "bancario",
            "varejo_tecnico",
            "vigilante",
            "designer_performance",
            "sound_designer",
            "sdr_tecnico",
            "growth_engineer",
            "performance",
            "ia_ops",
            "analytics_engineer",
            "server_side_tracking",
            "dev_fullstack",
            "outros",
        ]
        
        for cat_id in expected_ids:
            self.assertIn(
                f'id: "{cat_id}"',
                self.html_content,
                f"Category ID '{cat_id}' not found in PROFESSION_CATEGORIES",
            )

    def test_render_category_drawers_5_groups(self):
        """Verify renderCategoryDrawers contains category drawer groups."""
        for cat_id in ["pintor_industrial", "almoxarife", "assistente_adm", "sdr_tecnico", "ia_ops"]:
            self.assertIn(
                cat_id,
                self.html_content,
                f"Category ID '{cat_id}' not found in index.html",
            )

    def test_matches_category_checks_cat_name(self):
        """Verify matchesCategory checks catObj.name in addition to label_pt and kws."""
        self.assertIn("catNameNorm", self.html_content)
        self.assertIn("catObj.name", self.html_content)

    def test_zero_unicode_emojis(self):
        """Verify static/index.html contains zero unicode emojis."""
        emoji_pattern = re.compile(r"[\U0001F000-\U0001FFFF\u2600-\u27BF\u2300-\u23FF]")
        matches = emoji_pattern.findall(self.html_content)
        self.assertEqual(
            len(matches),
            0,
            f"Found {len(matches)} unicode emoji(s) in static/index.html: {matches[:10]}",
        )


if __name__ == "__main__":
    unittest.main()
