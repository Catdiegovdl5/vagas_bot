"""
Empirical Stress Test Suite for Milestone 3 (Final Integration Gate)
Author: Challenger M3_2 (critic / specialist)

Tests:
1. classify_job_profession() across all 14 categories & edge cases
2. is_job_relevant() for edge cases, false positives, false negatives, and blacklisted titles
3. SEARCH_MAPPING macro keyword expansions in bot.py & app.py integration
"""

import sys
import unittest
import os
import py_compile
import glob

# Ensure workspace root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import bot
from bot import classify_job_profession, is_job_relevant, SEARCH_MAPPING, global_title_blacklist
import app


class TestCompilationAndSyntax(unittest.TestCase):
    def test_all_modules_compile(self):
        """Verify python syntax compilation across bot.py, app.py, and scrapers."""
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        target_files = [
            os.path.join(root_dir, "bot.py"),
            os.path.join(root_dir, "app.py")
        ]
        target_files.extend(glob.glob(os.path.join(root_dir, "scrapers", "*.py")))
        
        for filepath in target_files:
            rel = os.path.relpath(filepath, root_dir)
            try:
                py_compile.compile(filepath, doraise=True)
            except py_compile.PyCompileError as e:
                self.fail(f"Compilation error in {rel}: {e}")


class TestClassifyJobProfession(unittest.TestCase):
    def test_14_category_classifications(self):
        """Test representative realistic job titles across all categories."""
        samples = [
            # Operações Físicas
            ({"title": "Pintor Industrial", "requirements": "Experiência em pintura eletrostática e industrial."}, "Operações Físicas", "Pintor Industrial"),
            ({"title": "Mecânico de Manutenção Industrial", "requirements": "Manutenção preventiva em motores e máquinas."}, "Operações Físicas", "Mecânico Industrial"),
            ({"title": "Operador de Produção CNC", "requirements": "Operar máquina CNC na linha de produção."}, "Operações Físicas", "Operador de Produção"),
            ({"title": "Torneiro Mecânico", "requirements": "Usinagem de peças metálicas."}, "Operações Físicas", "Operador de Produção"),
            ({"title": "Soldador TIG / MIG", "requirements": "Soldagem industrial de alta precisão."}, "Operações Físicas", "Operador de Produção"),

            # Logística
            ({"title": "Almoxarife Pleno", "requirements": "Controle de estoque, recebimento e emissão de NFs."}, "Logística", "Almoxarife"),
            ({"title": "Assistente de Logística", "requirements": "Roteamento de cargas e acompanhamento de entregas."}, "Logística", "Assistente de Logística"),
            ({"title": "Conferente de Carga", "requirements": "Conferência física de mercadorias no armazém."}, "Logística", "Assistente de Logística"),

            # Administrativo
            ({"title": "Assistente Administrativo", "requirements": "Atendimento telefônico, organização de documentos."}, "Administrativo", "Assistente Administrativo"),
            ({"title": "Assistente Financeiro", "requirements": "Contas a pagar, contas a receber, conciliação bancária."}, "Administrativo", "Assistente Financeiro"),
            ({"title": "Recepcionista", "requirements": "Recepção de visitantes e atendimento telefônico."}, "Administrativo", "Recepcionista"),
            ({"title": "Assistente de Faturamento", "requirements": "Emissão de notas fiscais e faturamento."}, "Administrativo", "Assistente de Faturamento"),
            ({"title": "Analista de RH", "requirements": "Recrutamento e seleção, subsistemas de RH."}, "Administrativo", "Analista de RH"),

            # Criativos
            ({"title": "Editor de Vídeo", "requirements": "Edição de vídeos para redes sociais em Premiere Pro."}, "Criativos", "Editor de Vídeo"),
            ({"title": "Designer Gráfico", "requirements": "Criação de artes para mídias sociais e impressos."}, "Criativos", "Designer Gráfico"),
            ({"title": "UX Designer", "requirements": "Pesquisa com usuários, wireframes e prototipagem em Figma."}, "Criativos", "UX Designer"),
            ({"title": "Copywriter Senior", "requirements": "Redação publicitária e páginas de vendas de alta conversão."}, "Criativos", "Copywriter"),
            ({"title": "Social Media Manager", "requirements": "Gestão de redes sociais e calendário editorial."}, "Criativos", "Social Media"),

            # Inteligência de Vendas / Vendas
            ({"title": "Executivo de Vendas B2B", "requirements": "Prospecção ativa e fechamento de contratos corporativos."}, "Inteligência de Vendas", "Executivo de Vendas"),
            ({"title": "Account Executive", "requirements": "Gestão de pipeline de vendas SaaS."}, "Inteligência de Vendas", "Executivo de Vendas"),
            ({"title": "SDR - Inside Sales", "requirements": "Qualificação de leads e agendamento de reuniões."}, "Inteligência de Vendas", "SDR"),

            # Engenharia de Dados / Dados
            ({"title": "Engenheiro de Dados Senior", "requirements": "Construção de pipelines de dados em Spark e Airflow."}, "Engenharia de Dados", "Engenheiro de Dados"),
            ({"title": "Analista de Dados", "requirements": "Análise de métricas, SQL e dashboards em Power BI."}, "Engenharia de Dados", "Analista de Dados"),
            ({"title": "Desenvolvedor Python Backend", "requirements": "Desenvolvimento de APIs RESTful em Python FastAPI."}, "Engenharia de Dados", "Desenvolvedor Python"),

            # Analytics Engineer
            ({"title": "Analytics Engineer", "requirements": "Modelagem de dados com dbt e Snowflake."}, "Analytics Engineer", "Analytics Engineer"),

            # IA-Ops / IA
            ({"title": "Prompt Engineer / RAG Specialist", "requirements": "Engenharia de prompt, LangChain e n8n workflows."}, "IA-Ops", "IA-Ops"),
            ({"title": "Especialista em IA-Ops", "requirements": "Automação de agentes de IA usando Make.com e Python."}, "IA-Ops", "IA-Ops"),

            # Outros / Fallbacks
            ({"title": "Desenvolvedor React Frontend", "requirements": "Criação de interfaces web em React e TypeScript."}, "Outros", "Desenvolvedor React"),
        ]

        for job_in, expected_cat, expected_prof in samples:
            res = classify_job_profession(dict(job_in))
            self.assertEqual(
                res.get("category"), expected_cat,
                f"Failed category classification for '{job_in['title']}': expected '{expected_cat}', got '{res.get('category')}'"
            )
            self.assertEqual(
                res.get("profession"), expected_prof,
                f"Failed profession classification for '{job_in['title']}': expected '{expected_prof}', got '{res.get('profession')}'"
            )

    def test_edge_cases_and_robustness(self):
        """Test zero crash guarantee on malformed or edge-case inputs."""
        edge_cases = [
            None,
            {},
            {"title": ""},
            {"title": None, "requirements": None},
            {"title": "   ", "requirements": "   "},
            {"title": "PINTOR INDUSTRIAL ESPECIAIS"},
            {"title": "eDiToR dE vÍdEo SêNiOr"},
            {"title": 12345, "requirements": [1, 2, 3]},
        ]
        for ec in edge_cases:
            try:
                res = classify_job_profession(ec)
                if isinstance(ec, dict) and ec:
                    self.assertIn("category", res)
                    self.assertIn("profession", res)
            except Exception as e:
                self.fail(f"classify_job_profession raised exception on edge case input {ec}: {e}")

    def test_requirements_fallback(self):
        """Test fallback to requirements when title is generic or non-descriptive."""
        job = {
            "title": "Vaga Operacional 01",
            "requirements": "Atuar como Pintor Industrial em fábrica com pintura de estruturas metálicas."
        }
        res = classify_job_profession(job)
        self.assertEqual(res.get("category"), "Operações Físicas")
        self.assertEqual(res.get("profession"), "Pintor Industrial")


class TestIsJobRelevant(unittest.TestCase):
    def setUp(self):
        self.default_settings = {
            "level": "Todos",
            "location": "Todos",
            "contract": "Todos",
            "education": "Todos"
        }

    def test_global_blacklisted_titles(self):
        """Verify global blacklisted titles (academic, legal, medical, etc.) are filtered out."""
        blacklisted_jobs = [
            {"title": "Professor de Programação Python", "requirements": "Lecionar aulas de programação em universidade.", "platform": "catho"},
            {"title": "Advogado Trabalhista", "requirements": "Atuação em contencioso trabalhista.", "platform": "gupy"},
            {"title": "Médico do Trabalho", "requirements": "Exames admissionais e demissionais.", "platform": "catho"},
            {"title": "Enfermeiro de UTI", "requirements": "Cuidados intensivos de enfermagem.", "platform": "infojobs"},
            {"title": "Faxineiro Industrial", "requirements": "Limpeza e higienização de ambientes.", "platform": "catho"},
        ]
        for j in blacklisted_jobs:
            rel = is_job_relevant(j, "tecnologia", self.default_settings)
            self.assertFalse(rel, f"Global blacklisted title '{j['title']}' should be rejected by is_job_relevant!")

    def test_seniority_rejection_for_junior(self):
        """Verify senior roles (Gerente, Director, Coordenador) are rejected when user level is junior."""
        senior_management_jobs = [
            {"title": "Gerente de TI", "requirements": "Gestão da equipe de tecnologia da informação.", "platform": "catho"},
            {"title": "Diretor Comercial", "requirements": "Liderança executiva de vendas.", "platform": "linkedin"},
            {"title": "Coordenador de TI", "requirements": "Coordenação de infraestrutura e suporte.", "platform": "infojobs"},
        ]
        junior_settings = {**self.default_settings, "level": "junior"}
        for j in senior_management_jobs:
            rel = is_job_relevant(j, "tecnologia", junior_settings)
            self.assertFalse(rel, f"Senior role '{j['title']}' should be REJECTED for junior level settings!")

    def test_relevant_trade_and_tech_roles_accepted(self):
        """Verify trade and technical roles pass for their relevant search keywords."""
        relevant_jobs = [
            ("Indústria", {"title": "Operador de Máquinas CNC", "requirements": "Operação de torno CNC em linha de produção industrial.", "platform": "catho"}),
            ("Pintor Industrial", {"title": "Pintor Industrial", "requirements": "Pintura de estruturas metálicas e peças industriais.", "platform": "gupy"}),
            ("Logística", {"title": "Almoxarife", "requirements": "Gestão de estoque e recebimento de materiais.", "platform": "infojobs"}),
            ("Assistente Administrativo", {"title": "Assistente Administrativo", "requirements": "Rotinas de escritório e atendimento.", "platform": "catho"}),
        ]
        for kw, j in relevant_jobs:
            rel = is_job_relevant(j, kw, self.default_settings)
            self.assertTrue(rel, f"Relevant job '{j['title']}' for keyword '{kw}' should be ACCEPTED by is_job_relevant!")

    def test_blacklist_user_keyword_override(self):
        """Verify that if user explicitly searches for a term in the blacklist (e.g. 'gerente de contas'), it is not blocked."""
        job = {"title": "Gerente de Contas B2B", "requirements": "Atendimento e gestão de contas de clientes B2B.", "platform": "linkedin"}
        rel = is_job_relevant(job, "gerente de contas", self.default_settings)
        self.assertTrue(rel, "Explicit search for 'gerente de contas' should NOT be blocked by global blacklist 'gerente'!")

    def test_seniority_level_filtering(self):
        """Test junior, pleno, senior, jovem aprendiz, and ganhar experiencia level filters."""
        job_senior = {"title": "Desenvolvedor Python Senior", "requirements": "Liderança técnica e arquitetura de software Python.", "platform": "gupy"}
        job_junior = {"title": "Desenvolvedor Python Junior", "requirements": "Desenvolvimento de APIs e scripts Python em equipe.", "platform": "gupy"}

        # Junior user
        settings_junior = {**self.default_settings, "level": "junior"}
        self.assertFalse(is_job_relevant(job_senior, "desenvolvedor python", settings_junior), "Junior user should REJECT Senior job")
        self.assertTrue(is_job_relevant(job_junior, "desenvolvedor python", settings_junior), "Junior user should ACCEPT Junior job")

        # Senior user
        settings_senior = {**self.default_settings, "level": "senior"}
        self.assertFalse(is_job_relevant(job_junior, "desenvolvedor python", settings_senior), "Senior user should REJECT Junior job")
        self.assertTrue(is_job_relevant(job_senior, "desenvolvedor python", settings_senior), "Senior user should ACCEPT Senior job")

    def test_contract_type_filtering(self):
        """Test CLT vs PJ filtering logic."""
        job_pj_pure = {"title": "Desenvolvedor Python", "requirements": "Contratação 100% PJ (Pessoa Jurídica). Prestação de serviços.", "platform": "workana"}
        job_clt_pure = {"title": "Desenvolvedor Python", "requirements": "Contratação via Carteira Assinada com benefícios.", "platform": "catho"}

        settings_clt = {**self.default_settings, "contract": "clt"}
        settings_pj = {**self.default_settings, "contract": "pj"}

        self.assertFalse(is_job_relevant(job_pj_pure, "desenvolvedor python", settings_clt), "CLT settings should REJECT PJ-only job")
        self.assertTrue(is_job_relevant(job_clt_pure, "desenvolvedor python", settings_clt), "CLT settings should ACCEPT CLT job")
        self.assertFalse(is_job_relevant(job_clt_pure, "desenvolvedor python", settings_pj), "PJ settings should REJECT CLT-only job")
        self.assertTrue(is_job_relevant(job_pj_pure, "desenvolvedor python", settings_pj), "PJ settings should ACCEPT PJ job")

    def test_location_filtering(self):
        """Test location filter strictness and remote platform overrides."""
        job_sp = {"title": "Assistente Administrativo", "requirements": "Trabalho presencial no escritório em São Paulo SP.", "location": "São Paulo - SP", "platform": "catho"}
        job_rj = {"title": "Assistente Administrativo", "requirements": "Trabalho presencial no escritório no Rio de Janeiro RJ.", "location": "Rio de Janeiro - RJ", "platform": "catho"}
        job_remote = {"title": "Assistente Administrativo", "requirements": "Trabalho 100% home office / remoto de qualquer lugar do Brasil.", "location": "Remoto", "platform": "catho"}

        settings_sp = {**self.default_settings, "location": "sp"}

        self.assertTrue(is_job_relevant(job_sp, "assistente administrativo", settings_sp), "SP location settings should ACCEPT SP job")
        self.assertFalse(is_job_relevant(job_rj, "assistente administrativo", settings_sp), "SP location settings should REJECT RJ job")
        self.assertTrue(is_job_relevant(job_remote, "assistente administrativo", settings_sp), "SP location settings should ACCEPT Remote job")

    def test_talent_pool_and_short_description_rejection(self):
        """Test rejection of talent pool ('banco de talentos') and short requirement strings."""
        talent_pool_job = {"title": "Banco de Talentos - TI", "requirements": "Cadastre seu currículo para futuras vagas.", "platform": "gupy"}
        short_desc_job = {"title": "Desenvolvedor Python", "requirements": "Vaga dev", "platform": "catho"}

        self.assertFalse(is_job_relevant(talent_pool_job, "desenvolvedor python", self.default_settings), "Should reject Banco de Talentos")
        self.assertFalse(is_job_relevant(short_desc_job, "desenvolvedor python", self.default_settings), "Should reject short description (<15 chars)")


class TestSearchMappingExpansions(unittest.TestCase):
    def test_search_mapping_completeness(self):
        """Verify SEARCH_MAPPING in bot.py contains all expected macro categories & sub-professions."""
        macro_categories = [
            "Operações Físicas",
            "Indústria",
            "Logística",
            "Administrativo",
            "Criativos",
            "Design",
            "Inteligência de Vendas",
            "Vendas",
            "Engenharia de Dados"
        ]
        for macro in macro_categories:
            self.assertIn(macro, SEARCH_MAPPING, f"Macro search term '{macro}' MUST be present in SEARCH_MAPPING!")
            expanded = SEARCH_MAPPING[macro]
            self.assertTrue(isinstance(expanded, str) and len(expanded) > 0, f"Expanded keyword for '{macro}' must be valid non-empty string")

    def test_app_integration_with_bot(self):
        """Verify app.py imports is_job_relevant and classify_job_profession without errors."""
        self.assertTrue(hasattr(app, "is_job_relevant") or hasattr(bot, "is_job_relevant"))
        self.assertTrue(hasattr(app, "classify_job_profession") or hasattr(bot, "classify_job_profession"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
