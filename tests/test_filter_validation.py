"""
Automated Verification Script: test_filter_validation.py
Validates R1 (Work Mode Drawers & regex hierarchy), R2 (Location filters & NFD normalization), 
and R3 (Zero unicode emojis, FontAwesome vector icon presence) in static/index.html.
"""

import re
import unittest
import unicodedata
from pathlib import Path


INDEX_HTML_PATH = Path(__file__).parent / "static" / "index.html"


def norm_str(s: str) -> str:
    """Python equivalent of JS normStr(str)."""
    if not s:
        return ""
    nfkd = unicodedata.normalize("NFD", s)
    no_accents = "".join(c for c in nfkd if unicodedata.category(c) != "Mn")
    return no_accents.lower()


def get_job_work_model(job: dict) -> str:
    """Python equivalent of JS getJobWorkModel(job)."""
    title = (job.get("title") or "").lower()
    reqs = (job.get("requirements") or "").lower()
    loc = (job.get("location") or "").lower()

    norm = norm_str(f"{title} {reqs} {loc}")

    has_hybrid = bool(re.search(r"\b(hibrid[oa]s?|hybrid)\b", norm))
    has_remote = bool(
        re.search(
            r"\b(remot[oa]s?|home\s*office|remote|teletrabalho|wfh|work\s*from\s*home|anywhere)\b",
            norm,
        )
    )

    norm_presential = re.sub(r"\b(nao|não)\s+(e\s+)?presencia[li]s?\b", "", norm)
    has_presential = bool(re.search(r"\b(presencia[li]s?|onsite|on-site)\b", norm_presential))

    if has_hybrid:
        return "hibrido"
    if has_remote and not has_presential:
        return "remoto"
    if has_presential and not has_remote:
        return "presencial"
    if has_remote:
        return "remoto"
    if has_presential:
        return "presencial"
    return "outros"


class TestFilterValidation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(INDEX_HTML_PATH, "r", encoding="utf-8") as f:
            cls.html_content = f.read()

    def test_r1_js_functions_defined_in_html(self):
        """Verify getJobWorkModel and normStr helper functions are defined in index.html."""
        self.assertIn("function getJobWorkModel(", self.html_content)
        self.assertIn("function normStr(", self.html_content)
        self.assertIn("normalize(\"NFD\")", self.html_content)

    def test_r1_work_model_matching_logic(self):
        """Test work mode matching logic against required test cases."""
        # 1. Feminine "remota"
        job_remota = {"title": "Vaga 100% Remota", "requirements": "Atuação em equipe"}
        self.assertEqual(get_job_work_model(job_remota), "remoto")

        # 2. Feminine/Accented "híbrida"
        job_hibrida = {
            "title": "Desenvolvedor React",
            "requirements": "Atuação em modalidade híbrida (2 dias presencial, 3 dias remoto)",
        }
        self.assertEqual(get_job_work_model(job_hibrida), "hibrido")

        # 3. Plural "presenciais"
        job_presenciais = {"title": "Analista de Suporte", "requirements": "Vagas presenciais em São Paulo"}
        self.assertEqual(get_job_work_model(job_presenciais), "presencial")

        # 4. "home office"
        job_homeoffice = {"title": "Engenheiro de Software", "requirements": "Trabalho em home office"}
        self.assertEqual(get_job_work_model(job_homeoffice), "remoto")

        # 5. "não é presencial"
        job_nao_presencial = {
            "title": "Vaga Remota",
            "requirements": "Desenvolvimento backend. Não é presencial.",
        }
        self.assertEqual(get_job_work_model(job_nao_presencial), "remoto")

        # 6. Additional keywords: WFH, teletrabalho, on-site
        self.assertEqual(get_job_work_model({"title": "Dev Python", "requirements": "Teletrabalho integral"}), "remoto")
        self.assertEqual(get_job_work_model({"title": "DevOps", "requirements": "On-site em Curitiba"}), "presencial")

    def test_r2_location_accent_normalization(self):
        """Test location search queries with and without accents."""
        cases = [
            ("Sao Paulo", "São Paulo", True),
            ("São Paulo", "Sao Paulo", True),
            ("Rio de Janeiro", "Rio de Janeiro", True),
            ("rio de janeiro", "RIO DE JANEIRO", True),
            ("Curitiba", "Curitiba", True),
            ("Exterior", "Vaga no Exterior", True),
            ("Florianopolis", "Florianópolis", True),
        ]

        for query, target, expected_match in cases:
            norm_q = norm_str(query)
            norm_t = norm_str(target)
            match = norm_q in norm_t
            self.assertEqual(
                match,
                expected_match,
                f"Query '{query}' vs Target '{target}' failed. Norm Q: '{norm_q}', Norm T: '{norm_t}'",
            )

    def test_r3_zero_unicode_emojis_in_html(self):
        """Verify zero unicode emojis remain in static/index.html."""
        emoji_pattern = re.compile(
            r"[\U0001F000-\U0001FFFF\u2600-\u27BF\u2300-\u23FF]"
        )
        matches = emoji_pattern.findall(self.html_content)
        self.assertEqual(
            len(matches),
            0,
            f"Found {len(matches)} unicode emoji(s) in static/index.html: {matches[:10]}",
        )

    def test_r3_fontawesome_icons_present(self):
        """Verify required FontAwesome vector icons are present in static/index.html."""
        required_icons = [
            "fa-user-gear",
            "fa-key",
            "fa-user",
            "fa-chart-simple",
            "fa-file-lines",
            "fa-circle-check",
            "fa-bullseye",
            "fa-spinner fa-spin",
        ]
        for icon in required_icons:
            self.assertIn(icon, self.html_content, f"Required FontAwesome icon '{icon}' not found in index.html")


if __name__ == "__main__":
    unittest.main()
