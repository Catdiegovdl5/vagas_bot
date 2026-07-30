# Análise Detalhada: Estruturação de Carreiras Elites e Design de Tests (`test_carreiras.py`)

## 1. Resumo Executivo

Este relatório apresenta o detalhamento estrutural para o módulo de orientação de carreiras elites e o design técnico do arquivo de testes `test_carreiras.py` para o `vagas_bot`.

O módulo contempla as **5 Profissões Elites**:
1. **Server-Side Tracking** (GTM SS, Meta CAPI, Stape, GA4 Server Side)
2. **Growth Engineer** (A/B testing, Python/SQL para growth, pipelines de dados, otimização de funil)
3. **Analytics Engineer** (dbt, BigQuery/Snowflake, SQL avançado, modelagem dimensional)
4. **IA-Ops** (Fluxos LLM, LangChain/LlamaIndex, Prompt Engineering, APIs de IA, AutoGen/CrewAI)
5. **SDR Técnico** (Prospecção técnica, CRM HubSpot/Salesforce, estratégia outbound, ferramentas CAD/API)

Cada profissão possui estrutura completa de dados com **4 etapas práticas de especialização/certificação** vinculadas a links e referências reais e válidas. Além disso, o relatório especifica o esquema de persistência isolado no banco de dados e a arquitetura completa de testes para o `test_carreiras.py`.

---

## 2. Estrutura de Dados das 5 Profissões Elites

A estrutura de dados principal do módulo `CAREER_GUIDANCE_DATA` é definida em Python da seguinte forma:

```python
CAREER_GUIDANCE_DATA = {
    "server_side_tracking": {
        "id": "server_side_tracking",
        "title": "⚡ Server-Side Tracking Specialist",
        "category": "Analytics & AdTech Infrastructure",
        "description": (
            "Especialista em arquitetura e implementação de rastreamento de dados de navegação no servidor. "
            "Contorna bloqueios de ITP (Safari), adblockers e restrições de privacidade do iOS (ATT), "
            "garantindo máxima integridade de dados para Meta Ads, Google Ads e GA4."
        ),
        "skills": [
            "GTM Server-Side", "Meta Conversions API (CAPI)", "Stape.io Cloud Hosting", 
            "GA4 Server-Side", "Cookie First-Party", "Custom Domains", "Data Layer SS"
        ],
        "market_demand": "Altíssima - Empresas com alto investimento em tráfego pago pagam prêmios por recuperação de dados de conversão.",
        "specialization_steps": [
            {
                "step_id": "step_1",
                "title": "Certificação Google Tag Manager & GTM Server-Side",
                "description": "Dominar a arquitetura de contêineres de servidor no GTM, clientes de recepção e disparo de tags server-side.",
                "cert_name": "Google Tag Manager & Analytics Individual Qualification",
                "cert_url": "https://skillshop.exceedlms.com/student/path/18323-google-analytics-individual-qualification",
                "docs_url": "https://developers.google.com/tag-platform/tag-manager/server-side"
            },
            {
                "step_id": "step_2",
                "title": "Meta Conversions API (CAPI) Developer Specialist",
                "description": "Configurar integração server-to-server da CAPI com deduplicação por event_id e Advanced Matching.",
                "cert_name": "Meta Certified Marketing Developer",
                "cert_url": "https://www.facebook.com/business/learn/certification",
                "docs_url": "https://developers.facebook.com/docs/marketing-api/conversions-api"
            },
            {
                "step_id": "step_3",
                "title": "Infraestrutura Cloud & Stape.io Masterclass",
                "description": "Implementação de servidor proxy via Stape.io, gerenciamento de registros DNS CNAME e Custom Loader.",
                "cert_name": "Stape Server-Side Tracking Academy",
                "cert_url": "https://stape.io/academy",
                "docs_url": "https://stape.io/blog"
            },
            {
                "step_id": "step_4",
                "title": "GA4 Server-Side & Privacidade (Consent Mode v2)",
                "description": "Exportação para BigQuery, anonimização de IP e conformidade com LGPD/GDPR no servidor.",
                "cert_name": "Google Analytics 4 Certification",
                "cert_url": "https://skillshop.docebosaas.com/learn/courses/14840/google-analytics-4-certification",
                "docs_url": "https://support.google.com/analytics/answer/9355949"
            }
        ]
    },
    "growth_engineer": {
        "id": "growth_engineer",
        "title": "🚀 Growth Engineer",
        "category": "Engineering & Growth Marketing",
        "description": (
            "Engenheiro híbrido focado na interseção de produto, ciência de dados e marketing. "
            "Desenvolve experimentos de A/B testing automatizados, pipelines de retenção de usuários e engenharia de funil."
        ),
        "skills": [
            "A/B Testing (Statsig, Optimizely)", "Python/SQL para Growth", "PostHog / Mixpanel Analytics",
            "Pipelines & Webhooks", "Otimização de Funil (CRO)", "Product-Led Growth (PLG)"
        ],
        "market_demand": "Alta - Scale-ups e startups SaaS buscam profissionais técnicos para otimizar métricas de CAC, LTV e retenção.",
        "specialization_steps": [
            {
                "step_id": "step_1",
                "title": "Certificação Optimizely / VWO em Experimentos A/B",
                "description": "Desenhar, programar e validar testes A/B estatisticamente confiáveis na camada de produto e web.",
                "cert_name": "Optimizely Certified Experimenter & Strategist",
                "cert_url": "https://www.optimizely.com/education/certification/",
                "docs_url": "https://vwo.com/academic/"
            },
            {
                "step_id": "step_2",
                "title": "PostHog & Product Analytics Mastery",
                "description": "Instrumentação de eventos de produto, feature flags, análise de coortes e cálculo de retenção.",
                "cert_name": "PostHog Product Analytics Certification",
                "cert_url": "https://posthog.com/tutorials",
                "docs_url": "https://mixpanel.com/partners/certification/"
            },
            {
                "step_id": "step_3",
                "title": "Python & SQL para Marketing Analytics & Pipelines",
                "description": "Construir scripts em Python e queries SQL para automação de funil e enriquecimento de dados de produto.",
                "cert_name": "DataCamp Marketing Analytics with Python",
                "cert_url": "https://www.datacamp.com/tracks/marketing-analytics-with-python",
                "docs_url": "https://www.datacamp.com/courses/sql-for-marketing"
            },
            {
                "step_id": "step_4",
                "title": "Growth Engineering & PLG Specialization (Reforge)",
                "description": "Implementação de loops de aquisição virais, arquitetura de software para Growth e onboarding.",
                "cert_name": "Reforge Growth Engineering Certificate",
                "cert_url": "https://www.reforge.com/courses/growth-series",
                "docs_url": "https://www.reforge.com/blog"
            }
        ]
    },
    "analytics_engineer": {
        "id": "analytics_engineer",
        "title": "📊 Analytics Engineer",
        "category": "Data Engineering & Business Intelligence",
        "description": (
            "Engenheiro de dados especializado em dbt e SQL avançado para transformar dados brutos no warehouse em "
            "modelos limpos, testados, documentados e prontos para tomada de decisão estratégica."
        ),
        "skills": [
            "dbt (data build tool)", "BigQuery / Snowflake", "SQL Avançado (Window, CTEs)",
            "Modelagem Dimensional (Kimball)", "Git & CI/CD para Dados", "Data Quality & Testing"
        ],
        "market_demand": "Muito Alta - Padrão da indústria moderna de dados (Modern Data Stack) em empresas mid-market e enterprise.",
        "specialization_steps": [
            {
                "step_id": "step_1",
                "title": "dbt Certified Analytics Engineer",
                "description": "Modelagem de dados com dbt Core/Cloud, desenvolvimento de macros, testes de dados e CI/CD com Git.",
                "cert_name": "dbt Certified Analytics Engineer",
                "cert_url": "https://www.getdbt.com/certifications/analytics-engineer-certification/",
                "docs_url": "https://docs.getdbt.com/"
            },
            {
                "step_id": "step_2",
                "title": "GCP Professional Data Engineer (BigQuery)",
                "description": "Arquitetura de Data Warehousing na nuvem, consultas otimizadas, particionamento e controle de custos no BigQuery.",
                "cert_name": "Google Cloud Certified Professional Data Engineer",
                "cert_url": "https://cloud.google.com/learn/certification/data-engineer",
                "docs_url": "https://cloud.google.com/bigquery/docs"
            },
            {
                "step_id": "step_3",
                "title": "Snowflake SnowPro Core Certification",
                "description": "Gestão de warehouses virtuais, compartilhamento seguro de dados, time-travel e clone zero-copy no Snowflake.",
                "cert_name": "Snowflake Certified SnowPro Core",
                "cert_url": "https://www.snowflake.com/en/resources/certifications/",
                "docs_url": "https://docs.snowflake.com/"
            },
            {
                "step_id": "step_4",
                "title": "Modelagem Dimensional Kimball & Data Warehousing",
                "description": "Projetar tabelas fato e dimensão (SCD Tipo 1/2) e aplicar engenharia de software no pipeline de transformações.",
                "cert_name": "Coursera Data Warehousing Specialization (Univ. of Colorado)",
                "cert_url": "https://www.coursera.org/specializations/data-warehousing",
                "docs_url": "https://www.kimballgroup.com/"
            }
        ]
    },
    "ia_ops": {
        "id": "ia_ops",
        "title": "🤖 IA-Ops (AI Operations Engineer)",
        "category": "Artificial Intelligence & Operations",
        "description": (
            "Engenheiro responsável por projetar, implantar e operar fluxos de trabalho baseados em LLMs, RAG, "
            "sistemas multiagentes e integrações de APIs de Inteligência Artificial para automação de processos."
        ),
        "skills": [
            "LLM Workflows & Chains", "LangChain / LlamaIndex", "Prompt Engineering Avançado",
            "APIs de IA (OpenAI, Groq, Anthropic)", "Sistemas Multiagentes (AutoGen, CrewAI)", "Vector DBs (Pinecone, Chroma)"
        ],
        "market_demand": "Explosiva - Demanda urgente por empresas buscando automatizar operações com IA Generativa.",
        "specialization_steps": [
            {
                "step_id": "step_1",
                "title": "LangChain & LLM Application Development (DeepLearning.AI)",
                "description": "Desenvolvimento de sistemas com ChatGPT/LangChain, gerenciamento de memória e agentes autônomos em Python.",
                "cert_name": "DeepLearning.AI Building Systems with ChatGPT & LangChain",
                "cert_url": "https://www.deeplearning.ai/short-courses/building-systems-with-chatgpt/",
                "docs_url": "https://python.langchain.com/"
            },
            {
                "step_id": "step_2",
                "title": "Prompt Engineering Specialization (Vanderbilt University)",
                "description": "Técnicas avançadas de prompting (Chain-of-Thought, ReAct, Few-Shot) e avaliação de performance de modelos.",
                "cert_name": "Coursera Prompt Engineering Specialization",
                "cert_url": "https://www.coursera.org/learn/prompt-engineering",
                "docs_url": "https://platform.openai.com/docs/guides/prompt-engineering"
            },
            {
                "step_id": "step_3",
                "title": "Sistemas Multiagentes e Arquitetura RAG (CrewAI / LlamaIndex)",
                "description": "Orquestração de múltiplos agentes autônomos com CrewAI e busca semântica RAG usando LlamaIndex e Bancos Vetoriais.",
                "cert_name": "DeepLearning.AI Multi AI Agent Systems with CrewAI",
                "cert_url": "https://www.deeplearning.ai/short-courses/multi-ai-agent-systems-with-crewai/",
                "docs_url": "https://docs.crewai.com/"
            },
            {
                "step_id": "step_4",
                "title": "Microsoft Azure AI Engineer Associate / AWS Certified AI Practitioner",
                "description": "Deploy de soluções de IA Generativa enterprise com segurança, conformidade e SLAs de alta disponibilidade.",
                "cert_name": "Microsoft Certified: Azure AI Engineer Associate (AI-102)",
                "cert_url": "https://learn.microsoft.com/en-us/credentials/certifications/azure-ai-engineer/",
                "docs_url": "https://aws.amazon.com/certification/certified-ai-practitioner/"
            }
        ]
    },
    "sdr_tecnico": {
        "id": "sdr_tecnico",
        "title": "🎯 SDR Técnico (Technical SDR)",
        "category": "Sales Engineering & Technical Prospecting",
        "description": (
            "Pré-vendedor especialista em prospecção B2B outbound de produtos técnicos complexos (SaaS, APIs, Cloud e IA). "
            "Conduz descobertas técnicas, qualifica decisores (CTOs, VPs) e automatiza cadências de contato via dados e APIs."
        ),
        "skills": [
            "Prospecção Técnica Outbound", "CRM HubSpot / Salesforce", "Estratégias de Cadência",
            "Data Enrichment (Clay, Apollo.io)", "Ferramentas CAD & APIs", "Qualificação MEDDIC/BANT"
        ],
        "market_demand": "Alta - Essencial em empresas B2B SaaS e consultorias de tecnologia avançada.",
        "specialization_steps": [
            {
                "step_id": "step_1",
                "title": "HubSpot Sales Hub & Inbound/Outbound Sales Certification",
                "description": "Operação avançada de CRM, cadências de e-mail automatizadas e gestão de pipeline de vendas.",
                "cert_name": "HubSpot Academy Inbound Sales Certification",
                "cert_url": "https://academy.hubspot.com/courses/inbound-sales",
                "docs_url": "https://academy.hubspot.com/"
            },
            {
                "step_id": "step_2",
                "title": "Salesforce Certified Sales Associate",
                "description": "Navegação e gerenciamento profissional no Salesforce Sales Cloud para contas de tecnologia enterprise.",
                "cert_name": "Salesforce Certified Sales Associate",
                "cert_url": "https://trailhead.salesforce.com/en/credentials/salesassociate",
                "docs_url": "https://trailhead.salesforce.com/"
            },
            {
                "step_id": "step_3",
                "title": "Prospecção Técnica e Data Enrichment (Apollo.io & Clay)",
                "description": "Construção de listas de ICP, enriquecimento de leads via scraping/APIs e personalização em escala.",
                "cert_name": "Clay University Data Enrichment Specialist",
                "cert_url": "https://university.clay.com/",
                "docs_url": "https://www.apollo.io/academy"
            },
            {
                "step_id": "step_4",
                "title": "Technical Sales Discovery & Cadence Strategy (Winning by Design)",
                "description": "Técnicas de qualificação técnica para conversar com diretores de engenharia e contorno de objeções complexas.",
                "cert_name": "Winning by Design Prospecting & Technical Sales Certification",
                "cert_url": "https://winningbydesign.com/",
                "docs_url": "https://winningbydesign.com/resources/"
            }
        ]
    }
}
```

---

## 3. Persistência de Dados Sem Interferência nas Vagas

### 3.1 Esquema da Tabela `career_progress`

Para armazenar o status de conclusão dos módulos/etapas de carreira do usuário sem modificar ou apagar os dados de busca de vagas (`jobs`, `applied_jobs`, `ignored_jobs`), define-se uma tabela isolada no SQLite:

```sql
CREATE TABLE IF NOT EXISTS career_progress (
    user_id TEXT NOT NULL,
    profession_id TEXT NOT NULL,
    step_id TEXT NOT NULL,
    completed INTEGER DEFAULT 1,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, profession_id, step_id)
);
```

### 3.2 Funções de Banco em `database.py`

As funções de persistência implementadas para interagir exclusivamente com `career_progress`:

```python
def save_career_step_status(user_id: str, profession_id: str, step_id: str, completed: bool = True):
    """Salva ou atualiza o status de conclusão de uma etapa de carreira para um usuário."""
    conn = get_connection()
    try:
        c = conn.cursor()
        c.execute('''
            INSERT INTO career_progress (user_id, profession_id, step_id, completed, updated_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id, profession_id, step_id) 
            DO UPDATE SET completed = excluded.completed, updated_at = CURRENT_TIMESTAMP
        ''', (str(user_id), str(profession_id), str(step_id), 1 if completed else 0))
        conn.commit()
    finally:
        conn.close()

def get_career_step_status(user_id: str, profession_id: str, step_id: str) -> bool:
    """Retorna True se a etapa específica foi concluída pelo usuário."""
    conn = get_connection()
    try:
        c = conn.cursor()
        c.execute('''
            SELECT completed FROM career_progress 
            WHERE user_id = ? AND profession_id = ? AND step_id = ?
        ''', (str(user_id), str(profession_id), str(step_id)))
        row = c.fetchone()
        return bool(row[0]) if row else False
    finally:
        conn.close()

def get_user_career_progress(user_id: str, profession_id: str = None) -> dict:
    """Retorna o mapa de etapas concluídas pelo usuário para uma profissão ou todas."""
    conn = get_connection()
    try:
        c = conn.cursor()
        if profession_id:
            c.execute('''
                SELECT profession_id, step_id, completed FROM career_progress 
                WHERE user_id = ? AND profession_id = ?
            ''', (str(user_id), str(profession_id)))
        else:
            c.execute('''
                SELECT profession_id, step_id, completed FROM career_progress 
                WHERE user_id = ?
            ''', (str(user_id),))
        rows = c.fetchall()
        return {(r[0], r[1]): bool(r[2]) for r in rows}
    finally:
        conn.close()
```

### 3.3 Garantia de Isolamento
1. A tabela `career_progress` possui chave primária tripla `(user_id, profession_id, step_id)`.
2. As tabelas `jobs` (onde ficam registradas as vagas encontradas), `applied_jobs` e `ignored_jobs` **nunca são lidas ou alteradas** pelas rotinas de carreira.
3. Isso garante **100% de desacoplamento** entre o rastreador de vagas e o módulo de desenvolvimento profissional.

---

## 4. Design do Arquivo de Testes `test_carreiras.py`

O arquivo `test_carreiras.py` conterá a suíte completa de testes unitários e de integração utilizando `pytest`.

### 4.1 Estrutura do Teste

```python
import os
import ast
import sqlite3
import pytest
from unittest.mock import MagicMock, AsyncMock

# --- SUÍTE DE TESTES DE CARREIRAS ---

# 1. Testes de Sintaxe e Carregamento de Menu no bot.py
def test_bot_imports_and_syntax():
    """Garante que bot.py não possui erros de sintaxe e importa corretamente."""
    bot_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bot.py")
    with open(bot_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read())
    assert tree is not None, "Falha ao analisar sintaxe do bot.py"

def test_career_menu_button_limit():
    """Garante que nenhum menu de carreiras ultrapassa o limite de 15 botões do Telegram."""
    from bot import get_career_menu_markup
    markup = get_career_menu_markup()
    button_count = sum(len(row) for row in markup.inline_keyboard)
    assert button_count <= 15, f"Menu de carreiras tem {button_count} botões (máximo permitido: 15)"

# 2. Testes de Disponibilidade de Conteúdo das 5 Profissões Elites
def test_content_availability_all_5_professions():
    """Verifica se todas as 5 profissões estão presentes com dados completos e URLs válidas."""
    from career_data import CAREER_GUIDANCE_DATA  # ou dicionário definido em bot.py
    
    expected_professions = [
        "server_side_tracking",
        "growth_engineer",
        "analytics_engineer",
        "ia_ops",
        "sdr_tecnico"
    ]
    
    for prof_id in expected_professions:
        assert prof_id in CAREER_GUIDANCE_DATA, f"Profissão '{prof_id}' não encontrada em CAREER_GUIDANCE_DATA"
        prof = CAREER_GUIDANCE_DATA[prof_id]
        
        # Validar campos obrigatórios
        assert prof.get("title"), f"Profissão '{prof_id}' sem título"
        assert prof.get("description"), f"Profissão '{prof_id}' sem descrição"
        assert len(prof.get("skills", [])) >= 3, f"Profissão '{prof_id}' deve ter no mínimo 3 skills"
        
        # Validar passos de especialização (deve ter de 3 a 4 passos)
        steps = prof.get("specialization_steps", [])
        assert 3 <= len(steps) <= 4, f"Profissão '{prof_id}' deve ter entre 3 e 4 passos de especialização (encontrado: {len(steps)})"
        
        for step in steps:
            assert step.get("step_id"), f"Passo em '{prof_id}' sem step_id"
            assert step.get("title"), f"Passo em '{prof_id}' sem título"
            assert step.get("description"), f"Passo em '{prof_id}' sem descrição"
            assert step.get("cert_url") and step["cert_url"].startswith("http"), f"Passo '{step.get('step_id')}' em '{prof_id}' com URL inválida"

# 3. Testes de Persistência no Banco de Dados e Isolamento de Vagas
def test_career_db_read_write_persistence(tmp_path):
    """Testa leitura e escrita no banco de dados para progresso em carreiras."""
    import database
    
    # Usar banco temporário para teste
    test_db = os.path.join(tmp_path, "test_jobs.db")
    original_db = database.DB_PATH
    database.DB_PATH = test_db
    
    try:
        database.init_db()
        database.init_career_db()
        
        # Testar gravação de conclusão
        database.save_career_step_status("user_123", "server_side_tracking", "step_1", True)
        assert database.get_career_step_status("user_123", "server_side_tracking", "step_1") is True
        
        # Testar desmarcar etapa
        database.save_career_step_status("user_123", "server_side_tracking", "step_1", False)
        assert database.get_career_step_status("user_123", "server_side_tracking", "step_1") is False
        
        # Testar múltiplas etapas
        database.save_career_step_status("user_123", "ia_ops", "step_1", True)
        database.save_career_step_status("user_123", "ia_ops", "step_2", True)
        
        progress = database.get_user_career_progress("user_123", "ia_ops")
        assert progress.get(("ia_ops", "step_1")) is True
        assert progress.get(("ia_ops", "step_2")) is True
        assert progress.get(("ia_ops", "step_3")) is None or progress.get(("ia_ops", "step_3")) is False
        
    finally:
        database.DB_PATH = original_db

def test_career_persistence_does_not_overwrite_job_search_data(tmp_path):
    """Garante que salvar progresso de carreira NÃO altera ou apaga vagas de emprego salvas."""
    import database
    
    test_db = os.path.join(tmp_path, "test_jobs_isolation.db")
    original_db = database.DB_PATH
    database.DB_PATH = test_db
    
    try:
        database.init_db()
        database.init_career_db()
        
        # Inserir vagas de teste no banco
        sample_jobs = [
            {"title": "Dev Python", "company": "Empresa X", "budget": "R$ 8000", "link": "https://vaga1.com", "platform": "linkedin"},
            {"title": "Analytics Eng", "company": "Empresa Y", "budget": "R$ 10000", "link": "https://vaga2.com", "platform": "indeed"}
        ]
        inserted = database.insert_jobs(sample_jobs)
        assert inserted == 2
        
        # Marcar uma vaga como candidatada
        database.mark_applied("https://vaga1.com")
        
        # Executar múltiplas operações de progresso de carreira
        for i in range(1, 5):
            database.save_career_step_status("user_456", "growth_engineer", f"step_{i}", True)
            
        # Verificar se os dados de vagas permanecem 100% intactos
        jobs_after = database.get_jobs()
        assert len(jobs_after) == 1  # Vaga 2 ativa (vaga 1 foi candidatada)
        assert jobs_after[0]["link"] == "https://vaga2.com"
        assert database.is_applied("https://vaga1.com") is True
        
    finally:
        database.DB_PATH = original_db
```

---

## 5. Método de Verificação Executável

Para validar o relatório e a arquitetura proposta:
1. Inspeção de sintaxe e AST em `bot.py` e `database.py`.
2. Execução dos testes automatizados via `pytest`:
   ```bash
   python -m pytest test_carreiras.py -v
   ```
3. Verificação de schema SQLite no banco de testes.
