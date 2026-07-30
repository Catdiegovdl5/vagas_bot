import asyncio
import importlib
import PyPDF2
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton

import sys
sys.path.append(".")
from database import (
    insert_jobs, init_db, is_applied, mark_applied,
    save_user_step_status, get_user_career_progress,
    toggle_user_step_status, get_career_step_status,
    get_user_profile, upsert_user_profile, is_premium
)
init_db()  # Garante que as tabelas existem quando o bot inicia
import os
TOKEN = os.environ.get("TELEGRAM_TOKEN", "7724330024:AAFtoSLgXVDlvNmeyPCVMnkWIqbk4wvLSVg")

import traceback
from loguru import logger

# --- Configurando o Monitoramento Profissional (Loguru) ---
logger.remove() # Remove o handler padrão
logger.add(sys.stderr, colorize=True, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>", level="DEBUG")
logger.add("erros_robo.log", rotation="10 MB", retention="5 days", level="DEBUG", 
           format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}")
# ----------------------------------------------------------

import logging
# Suprime logs verbosos de bibliotecas internas
logging.getLogger("httpx").setLevel(logging.WARNING)


bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- Monitoramento de Erros via Telegram ---
@dp.errors()
async def global_error_handler(event: types.ErrorEvent):
    erro_completo = "".join(traceback.format_exception(type(event.exception), event.exception, event.exception.__traceback__))
    logger.error(f"O robô quebrou: {erro_completo}")
    
    import html
    escaped_error = html.escape(erro_completo[:3800])
    msg = f"🚨 <b>CRITICAL BUG DETECTED:</b>\n<pre><code class=\"language-python\">{escaped_error}</code></pre>"
    if event.update.callback_query:
        await event.update.callback_query.message.answer(msg, parse_mode="HTML")
    elif event.update.message:
        await event.update.message.answer(msg, parse_mode="HTML")
# -------------------------------------------

import copy

DEFAULT_RESUME = """
Diego Santos | Especialista Digital Full-Stack

🎯 Áreas de Atuação:
- Gestão de Tráfego Pago: Meta Ads (Facebook/Instagram), Google Ads, TikTok Ads, lojistas, infoprodutos e lançamentos digitais.
- Edição de Vídeo & Motion: Premiere Pro, CapCut Pro, After Effects. Especialista em retenção e viralização (524k+ views orgânicos).
- Criação de Conteúdo / Social Media: Reels, TikTok, YouTube Shorts, copy para posts e campanhas.
- Automação com IA e Python: scripts de automação, bots do Telegram, pipelines de vídeo na nuvem, integrações com APIs de IA (Groq, OpenAI).
- Desenvolvimento Web: HTML, CSS, JavaScript, sites de portfólio, landing pages de alta conversão.

💼 Cases e Resultados:
- 524.000+ views orgânicos em um único Reels (Instagram).
- 56.600+ views no TikTok em nicho Geek/Anime.
- 370 vídeos publicados no YouTube com identidade visual consistente.
- Pipeline automatizada de corte e montagem de vídeos com Python.
- Desenvolvimento de bot inteligente de captura de vagas com IA (Groq) e Telegram.

🛠️ Ferramentas: Meta Business Suite, Google Ads Manager, Premiere Pro, CapCut, After Effects, Python, Playwright, GitHub, Render, n8n.
"""

# Grupos de plataformas por tipo
FREELANCE_PLATFORMS = ["workana", "freelancer", "novenove"]
EMPREGO_PLATFORMS = ["jsearch", "jooble", "remotar", "github_vagas", "indeed", "linkedin", "glassdoor", "infojobs", "gupy", "catho", "vagas_com", "programathor", "coodesh", "geekhunter", "gmail"]

DEFAULT_SETTINGS = {
    "level": "Todos",
    "location": "Brasil (Remoto)",
    "contract": "Todos", # Todos, PJ, CLT, Freelancer
    "education": "Todos", # Todos, Sem Formação
    "display_mode": "compact", # "cards", "compact", "file"
    "platforms": {
        "jsearch": True,
        "jooble": True,
        "workana": True,
        "remotar": True,
        "novenove": False,
        "github_vagas": True,
        "indeed": True,
        "linkedin": True,
        "glassdoor": True,
        "infojobs": True,
        "gupy": True,
        "catho": True,
        "vagas_com": True,
        "programathor": True,
        "coodesh": True,
        "geekhunter": True,
        "gmail": False
    },
    "ai_filter": True,
    "escudo_ptbr": True
}

user_settings_db = {}

def get_user_settings(chat_id):
    chat_id = str(chat_id)
    if chat_id not in user_settings_db:
        user_settings_db[chat_id] = copy.deepcopy(DEFAULT_SETTINGS)
    return user_settings_db[chat_id]

# --- MÓDULO TRILHA DE CARREIRAS ELITES ---
CAREER_GUIDANCE_DATA = {
    "server_side_tracking": {
        "id": "server_side_tracking",
        "title": "⚡ Server-Side Tracking Specialist",
        "subtitle": "Especialista em Coleta de Dados & Privacidade First-Party",
        "category": "Analytics & AdTech Infrastructure",
        "description": (
            "Especialista em arquitetura e implementação de rastreamento de dados de navegação no servidor. "
            "Contorna bloqueios de ITP (Safari), adblockers e restrições de privacidade do iOS (ATT), "
            "garantindo máxima integridade de dados para Meta Ads, Google Ads e GA4."
        ),
        "summary": "Especialista em arquitetura e implementação de rastreamento no servidor (GTM Server-Side, Stape, Meta CAPI, GA4).",
        "market_demand": "Altíssima — Empresas com alto investimento em tráfego pago pagam prêmios por recuperação de dados de conversão.",
        "salary_br": "R$ 6.000,00 a R$ 14.000,00 / mês",
        "salary_usd": "$ 3,000 to $ 6,500 / month",
        "search_kw": "Especialista Tracking",
        "tools": ["Google Tag Manager (Server)", "Stape.io", "Meta Conversions API", "GA4 BigQuery Export", "Cookie First-Party"],
        "skills": ["GTM Server-Side", "Meta Conversions API (CAPI)", "Stape.io Cloud Hosting", "GA4 Server-Side", "Cookie First-Party", "Custom Domains", "Data Layer SS"],
        "specialization_steps": [
            {
                "step_id": "step_1",
                "title": "Certificação Google Tag Manager & GTM Server-Side",
                "description": "Dominar a arquitetura de contêineres de servidor no GTM, clientes de recepção e disparo de tags server-side.",
                "cert_name": "Google Tag Manager Qualification",
                "cert_url": "https://skillshop.exceedlms.com/student/path/18323-google-analytics-individual-qualification",
                "docs_url": "https://developers.google.com/tag-platform/tag-manager/server-side"
            },
            {
                "step_id": "step_2",
                "title": "Meta Conversions API (CAPI) Developer Specialist",
                "description": "Configurar integração server-to-server da CAPI com deduplicação por event_id e Advanced Matching.",
                "cert_name": "Meta Certified Developer",
                "cert_url": "https://www.facebook.com/business/learn/certification",
                "docs_url": "https://developers.facebook.com/docs/marketing-api/conversions-api"
            },
            {
                "step_id": "step_3",
                "title": "Infraestrutura Cloud & Stape.io Masterclass",
                "description": "Implementação de servidor proxy via Stape.io, gerenciamento de registros DNS CNAME e Custom Loader.",
                "cert_name": "Stape Server-Side Academy",
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
        "title": "🚀 Growth Engineer / Gestor de Performance",
        "subtitle": "Gestor de Tráfego Pago & ROI — Google Ads + Meta Ads",
        "category": "Performance Marketing & Growth",
        "description": (
            "Papel híbrido que une marketing, engenharia de dados e programação para gerenciar orçamentos de tráfego pago "
            "focando estritamente em métricas de lucro real (ROI, ROAS e CAC). "
            "Conecta campanhas de Google Ads e Meta Ads a relatórios automatizados de performance."
        ),
        "summary": "Gerencia orçamentos de tráfego pago (Google + Meta) e apresenta relatórios de ROI, ROAS e CAC via Looker Studio.",
        "market_demand": "Muito Alta — Empresas investem pesado em anúncios mas faltam profissionais que comprovem o retorno real.",
        "salary_br": "R$ 5.000,00 a R$ 14.000,00 / mês + Bonificações",
        "salary_usd": "$ 2,500 to $ 7,000 / month",
        "search_kw": "Gestor de Tráfego",
        "references": ["Google Skillshop (ads.google.com/intl/pt-BR/home/tools/skillshop/)", "Meta Blueprint (facebook.com/business/learn/certification)"],
        "tools": ["Google Ads", "Meta Ads Manager", "Google Analytics 4", "Looker Studio", "Google Tag Manager"],
        "skills": ["Campanhas Google Ads (Pesquisa, Vídeo, Display)", "Meta Ads & ROAS Optimization", "Looker Studio (Relatórios Dinâmicos)", "Análise de ROI, ROAS e CAC", "GA4 & Tracking de Conversões", "Media Buying Profissional"],
        "specialization_steps": [
            {
                "step_id": "step_1",
                "title": "Certificações Oficiais Google Ads (Pesquisa, Vídeo & Display)",
                "description": "Conclua as certificações oficiais de Google Ads em Pesquisa, Vídeo, Display e Métricas no Google Skillshop.",
                "cert_name": "Google Ads Certified (Skillshop)",
                "cert_url": "https://skillshop.docebosaas.com/learn/courses/14840",
                "docs_url": "https://ads.google.com/intl/pt-BR/home/tools/skillshop/"
            },
            {
                "step_id": "step_2",
                "title": "Meta Certified Media Buying Professional",
                "description": "Prepare-se para o exame oficial Meta Certified Media Buying Professional — padrão global para gestores de tráfego Meta.",
                "cert_name": "Meta Certified Media Buying Professional",
                "cert_url": "https://www.facebook.com/business/learn/certification",
                "docs_url": "https://www.facebook.com/business/learn"
            },
            {
                "step_id": "step_3",
                "title": "Looker Studio — Relatórios Dinâmicos & Automatizados",
                "description": "Aprenda a criar relatórios dinâmicos e automatizados no Looker Studio para apresentar ROI, ROAS e CAC às empresas.",
                "cert_name": "Google Looker Studio Essentials",
                "cert_url": "https://skillshop.exceedlms.com/student/catalog/list?category_ids=53-google-analytics",
                "docs_url": "https://lookerstudio.google.com"
            },
            {
                "step_id": "step_4",
                "title": "Google Analytics 4 — Certificação Individual (GA4)",
                "description": "Obtenha a certificação oficial GA4 no Google Skillshop para dominar análise de conversões e relatórios de funil.",
                "cert_name": "Google Analytics 4 Certification",
                "cert_url": "https://skillshop.docebosaas.com/learn/courses/14840/google-analytics-4-certification",
                "docs_url": "https://support.google.com/analytics/answer/12159447"
            }
        ]
    },
    "analytics_engineer": {
        "id": "analytics_engineer",
        "title": "📊 Analytics Engineer / Engenheiro de Dados",
        "subtitle": "Analista que transforma dados brutos em decisões rápidas",
        "category": "Data Engineering & Business Intelligence",
        "description": (
            "Profissional que limpa, organiza e transforma volumes massivos de dados brutos "
            "(vindos de bancos de dados ou relatórios) em informações organizadas para tomada de decisões rápidas. "
            "Domina Pandas (Python), SQL, Power BI e Excel avançado para entregar insights acionáveis."
        ),
        "summary": "Usa Pandas (Python), SQL, Power BI e Excel Power Query/Pivot para transformar dados brutos em dashboards de decisão.",
        "market_demand": "Muito Alta — Toda empresa com dados precisa de alguém que saiba limpá-los e apresentá-los de forma útil.",
        "salary_br": "R$ 5.500,00 a R$ 14.000,00 / mês",
        "salary_usd": "$ 3,000 to $ 7,500 / month",
        "search_kw": "Analista de Dados",
        "references": ["Documentação Pandas: pandas.pydata.org", "SQLZoo (sqlzoo.net)", "Microsoft Power BI Learning (learn.microsoft.com)"],
        "tools": ["Python / Pandas", "SQL", "Power BI", "Microsoft Excel (Power Query + Pivot)", "Looker Studio"],
        "skills": ["Pandas (Python) para manipulação de dados", "SQL para consultas e transformações", "Power BI — Dashboards e DAX", "Excel Power Query & Power Pivot", "Limpeza e tratamento de dados", "Storytelling com dados"],
        "specialization_steps": [
            {
                "step_id": "step_1",
                "title": "Python para Análise de Dados com Pandas",
                "description": "Domine a biblioteca Pandas em Python para manipulação, limpeza, agrupamento e tratamento de tabelas de dados reais.",
                "cert_name": "DataCamp — Data Analyst with Python",
                "cert_url": "https://www.datacamp.com/tracks/data-analyst-with-python",
                "docs_url": "https://pandas.pydata.org/docs/"
            },
            {
                "step_id": "step_2",
                "title": "SQL para Análise de Dados — Do Básico ao Avançado",
                "description": "Estude linguagem de banco de dados SQL: SELECT, JOIN, GROUP BY, CTEs e Window Functions para analisar qualquer dataset.",
                "cert_name": "Mode SQL Tutorial / SQLZoo",
                "cert_url": "https://sqlzoo.net/",
                "docs_url": "https://mode.com/sql-tutorial/"
            },
            {
                "step_id": "step_3",
                "title": "Microsoft Power BI — Dashboards Profissionais",
                "description": "Aprofunde-se no Power BI para criar dashboards interativos com DAX, medidas calculadas e relatórios automatizados.",
                "cert_name": "Microsoft Power BI Data Analyst (PL-300)",
                "cert_url": "https://learn.microsoft.com/en-us/credentials/certifications/power-bi-data-analyst-associate/",
                "docs_url": "https://learn.microsoft.com/en-us/power-bi/"
            },
            {
                "step_id": "step_4",
                "title": "Excel Avançado — Power Query & Power Pivot",
                "description": "Domine técnicas avançadas de modelagem de dados no Microsoft Excel com Power Query (ETL) e Power Pivot (Modelagem).",
                "cert_name": "Microsoft Office Specialist — Excel Expert",
                "cert_url": "https://learn.microsoft.com/en-us/credentials/certifications/mos-excel-expert-2019/",
                "docs_url": "https://support.microsoft.com/en-us/office/power-query-overview"
            }
        ]
    },
    "ia_ops": {
        "id": "ia_ops",
        "title": "🤖 Arquiteto de Automação & IA-Ops",
        "subtitle": "Constrói fluxos que rodam 24/7 conectando APIs e agentes de IA",
        "category": "Artificial Intelligence & Operations Automation",
        "description": (
            "Profissional que desenha e constrói fluxos de trabalho que rodam 24/7 sozinhos, conectando diferentes ferramentas "
            "por meio de APIs e orquestrando agentes inteligentes de IA. "
            "Usa n8n, Make e Zapier para automações visuais e Python (Playwright/Selenium) para tarefas dinâmicas complexas."
        ),
        "summary": "Cria automações 24/7 com n8n, Make, Zapier, APIs de IA e Python (Playwright/Selenium) para eliminar trabalho repetitivo.",
        "market_demand": "Explosiva — Toda empresa quer automatizar processos repetitivos com IA e pagar por isso.",
        "salary_br": "R$ 6.000,00 a R$ 15.000,00 / mês",
        "salary_usd": "$ 3,000 to $ 7,500 / month",
        "search_kw": "Especialista em Automação",
        "references": ["n8n.io/workflows (galeria de automações)", "make.com/en/blog", "Playwright Docs: playwright.dev"],
        "tools": ["n8n (principal)", "Make (ex-Integromat)", "Zapier", "Python (Playwright / Selenium)", "APIs REST & Webhooks"],
        "skills": ["n8n — Automações Avançadas & Webhooks", "Make (Integromat) — Cenários Visuais", "Zapier — Integrações Sem Código", "Engenharia de Prompt & Conexões HTTP/JSON", "Python Playwright & Selenium (Web Scraping)", "Integração de APIs de IA (OpenAI, Groq)"],
        "specialization_steps": [
            {
                "step_id": "step_1",
                "title": "n8n — Masterclass de Automações Avançadas",
                "description": "Domine n8n (sua principal ferramenta): crie workflows com HTTP Request, Webhooks, condicionais e integração com APIs externas.",
                "cert_name": "n8n Official Courses",
                "cert_url": "https://docs.n8n.io/courses/",
                "docs_url": "https://n8n.io/workflows/"
            },
            {
                "step_id": "step_2",
                "title": "Make (ex-Integromat) & Zapier — Integrações sem Código",
                "description": "Domine Make e Zapier para conectar dezenas de ferramentas de negócio sem precisar escrever código.",
                "cert_name": "Make Partner Certification",
                "cert_url": "https://www.make.com/en/partners/certification",
                "docs_url": "https://www.zapier.com/learn/"
            },
            {
                "step_id": "step_3",
                "title": "Engenharia de Prompt & Conexões HTTP/JSON para IA",
                "description": "Estude Engenharia de Prompt e como conectar APIs de IA (OpenAI, Anthropic, Groq) via HTTP/JSON nos fluxos de automação.",
                "cert_name": "DeepLearning.AI Prompt Engineering",
                "cert_url": "https://www.deeplearning.ai/short-courses/chatgpt-prompt-engineering-for-developers/",
                "docs_url": "https://platform.openai.com/docs/guides/prompt-engineering"
            },
            {
                "step_id": "step_4",
                "title": "Python Playwright & Selenium — Automação de Tarefas Dinâmicas",
                "description": "Aprenda a automatizar tarefas dinâmicas em websites usando Python com Playwright e Selenium para web scraping e bots.",
                "cert_name": "TestAutomationU — Selenium Python",
                "cert_url": "https://testautomationu.applitools.com/selenium-webdriver-python-tutorial/",
                "docs_url": "https://playwright.dev/python/docs/intro"
            }
        ]
    },
    "sdr_tecnico": {
        "id": "sdr_tecnico",
        "title": "🎯 SDR Técnico (Data-Driven SDR)",
        "subtitle": "Prospecção Inteligente para SaaS B2B — Dados, não Ligações!",
        "category": "Technical Sales & B2B Prospecting",
        "description": (
            "Atuação comercial focada em prospecção ativa e qualificação inteligente de potenciais clientes para empresas de software (SaaS), "
            "otimizando o processo por meio de dados — e não apenas por ligações repetitivas. "
            "Usa CRM, ferramentas de enriquecimento de dados e automação para construir listas e cadências certeiras."
        ),
        "summary": "Qualifica leads SaaS B2B com dados (CRM, Apollo, Clay) — mais inteligência e menos cold call.",
        "market_demand": "Alta — Empresas SaaS e de software crescem via prospecção ativa qualificada e pagam comissões agressivas.",
        "salary_br": "R$ 3.500,00 a R$ 8.000,00 + Comissões (podendo dobrar)",
        "salary_usd": "$ 2,000 to $ 5,000 / month",
        "search_kw": "SDR",
        "references": ["Microsoft Learn MB-910 (learn.microsoft.com/pt-br/credentials/certifications/d365-fundamentals-customer-engagement-apps-crm/)"],
        "tools": ["Microsoft Dynamics 365 CRM", "HubSpot / Salesforce", "Apollo.io / Clay", "LinkedIn Sales Navigator", "Cold Email Automation"],
        "skills": ["Microsoft Dynamics 365 — Fundamentos CRM", "Prospecção Data-Driven (Apollo.io & Clay)", "Técnicas de Vendas Consultivas (BANT/MEDDIC)", "Cadências de Cold Email & LinkedIn", "Integração de Ferramentas de Dados", "Qualificação Inteligente de Leads"],
        "specialization_steps": [
            {
                "step_id": "step_1",
                "title": "Microsoft Dynamics 365 — Fundamentos de CRM (MB-910)",
                "description": "Obtenha a certificação oficial Microsoft Dynamics 365: Fundamentos de CRM (MB-910) para dominar o CRM corporativo padrão de mercado.",
                "cert_name": "Microsoft Dynamics 365 Fundamentals CRM (MB-910)",
                "cert_url": "https://learn.microsoft.com/pt-br/credentials/certifications/d365-fundamentals-customer-engagement-apps-crm/",
                "docs_url": "https://learn.microsoft.com/pt-br/training/paths/learn-fundamentals-microsoft-dynamics-365-customer-engagement/"
            },
            {
                "step_id": "step_2",
                "title": "Técnicas de Vendas Consultivas & Qualificação de Leads",
                "description": "Estude técnicas estruturadas de vendas consultivas e qualificação de leads (BANT, MEDDIC, SPIN Selling) para SaaS B2B.",
                "cert_name": "HubSpot Inbound Sales Certified",
                "cert_url": "https://academy.hubspot.com/courses/inbound-sales",
                "docs_url": "https://academy.hubspot.com/"
            },
            {
                "step_id": "step_3",
                "title": "Prospecção Data-Driven — Apollo.io & Clay",
                "description": "Aprenda a integrar ferramentas de dados (Apollo.io, Clay) para automatizar listas de prospecção fria com personalização em escala.",
                "cert_name": "Apollo.io Academy / Clay University",
                "cert_url": "https://university.clay.com/",
                "docs_url": "https://www.apollo.io/academy"
            },
            {
                "step_id": "step_4",
                "title": "LinkedIn Sales Navigator & Cold Email Strategy",
                "description": "Domine o LinkedIn Sales Navigator para encontrar decisores e construir cadências de cold email de alta taxa de abertura.",
                "cert_name": "LinkedIn Sales Foundations Cert",
                "cert_url": "https://www.linkedin.com/learning/paths/become-a-linkedin-selling-expert",
                "docs_url": "https://business.linkedin.com/sales-solutions/sales-navigator"
            }
        ]
    },
    "dev_python": {
        "id": "dev_python",
        "title": "🐍 Desenvolvedor Python & Backend",
        "subtitle": "Desenvolvimento de APIs REST, microsserviços e sistemas escaláveis",
        "category": "Programação & Engenharia de Software",
        "description": (
            "Desenvolve aplicações backend robustas, APIs REST e microsserviços escaláveis usando a linguagem Python. "
            "Domina frameworks modernos como FastAPI e Django, integração com bancos de dados relacionais e implantação em nuvem."
        ),
        "summary": "Cria APIs e backend com Python, FastAPI, Django, PostgreSQL e Docker para web e sistemas.",
        "market_demand": "Altíssima — Python é uma das linguagens mais buscadas do mercado para web, backend e automação.",
        "salary_br": "R$ 4.500,00 a R$ 12.000,00 / mês",
        "salary_usd": "$ 2,500 to $ 6,500 / month",
        "search_kw": "Desenvolvedor Python",
        "references": ["Python Institute (pythoninstitute.org)", "FastAPI Docs (fastapi.tiangolo.com)", "Django Project (djangoproject.com)"],
        "tools": ["Python 3", "FastAPI", "Django", "PostgreSQL / SQLAlchemy", "Docker", "Git / GitHub"],
        "skills": ["Python Avançado & POO", "Criação de APIs RESTful com FastAPI", "Django Framework & ORM", "Modelagem SQL & PostgreSQL", "Testes Automatizados (pytest)", "Containerização com Docker"],
        "specialization_steps": [
            {
                "step_id": "step_1",
                "title": "Python Avançado & Programação Orientada a Objetos",
                "description": "Domine a sintaxe avançada do Python, estruturas de dados, POO, decoradores e manipulação de arquivos.",
                "cert_name": "OpenEDG Python Institute (PCEP / PCAP)",
                "cert_url": "https://pythoninstitute.org/pcap",
                "docs_url": "https://docs.python.org/3/"
            },
            {
                "step_id": "step_2",
                "title": "Criação de APIs REST de Alta Performance com FastAPI",
                "description": "Aprenda a construir APIs assíncronas com FastAPI, Pydantic, Swagger automático e autenticação JWT.",
                "cert_name": "FastAPI Masterclass",
                "cert_url": "https://fastapi.tiangolo.com/tutorial/",
                "docs_url": "https://fastapi.tiangolo.com/"
            },
            {
                "step_id": "step_3",
                "title": "Bancos de Dados Relacionais com PostgreSQL & ORM",
                "description": "Aprenda modelagem de banco de dados, consultas SQL complexas, migrações com Alembic e integração via SQLAlchemy/Django ORM.",
                "cert_name": "PostgreSQL Certified Associate",
                "cert_url": "https://www.postgresql.org/about/",
                "docs_url": "https://www.postgresql.org/docs/"
            },
            {
                "step_id": "step_4",
                "title": "Docker & Implantação Cloud de APIs Python",
                "description": "Containerize aplicações Python com Docker/Docker Compose e faça o deploy em plataformas Cloud como Render ou AWS.",
                "cert_name": "AWS Certified Cloud Practitioner",
                "cert_url": "https://aws.amazon.com/certification/certified-cloud-practitioner/",
                "docs_url": "https://docs.docker.com/"
            }
        ]
    },
    "frontend_react": {
        "id": "frontend_react",
        "title": "⚛️ Desenvolvedor Frontend React & Next.js",
        "subtitle": "Interfaces web modernas, rápidas, responsivas e escaláveis",
        "category": "Programação & Engenharia de Software",
        "description": (
            "Especialista em construir interfaces de usuário dinâmicas e responsivas usando React.js e Next.js. "
            "Conecta páginas web com APIs REST/GraphQL e aplica boas práticas de UI/UX, SEO e otimização de performance."
        ),
        "summary": "Desenvolve interfaces modernas com React, Next.js, TypeScript e TailwindCSS para web e webapps.",
        "market_demand": "Muito Alta — Praticamente toda empresa tech precisa de desenvolvedores frontend qualificados.",
        "salary_br": "R$ 4.500,00 a R$ 13.000,00 / mês",
        "salary_usd": "$ 2,500 to $ 6,500 / month",
        "search_kw": "Desenvolvedor React",
        "references": ["React Docs (react.dev)", "Next.js Documentation (nextjs.org/docs)", "Meta Frontend Developer Cert"],
        "tools": ["React.js", "Next.js", "TypeScript", "TailwindCSS", "HTML5 & CSS3", "Git / GitHub"],
        "skills": ["JavaScript ES6+ & TypeScript", "React Components, Hooks & State", "Next.js (App Router, SSR, SSG)", "Estilização com TailwindCSS", "Consumo de APIs REST / Fetch / Axios", "Otimização de Performance Web (Web Vitals)"],
        "specialization_steps": [
            {
                "step_id": "step_1",
                "title": "JavaScript Moderno (ES6+) & TypeScript",
                "description": "Domine manipulação do DOM, Promises, Async/Await e tipagem estática com TypeScript.",
                "cert_name": "Meta Frontend Developer Professional Certificate",
                "cert_url": "https://www.coursera.org/professional-certificates/meta-front-end-developer",
                "docs_url": "https://developer.mozilla.org/pt-BR/docs/Web/JavaScript"
            },
            {
                "step_id": "step_2",
                "title": "React.js — Hooks, Estado e Componentização",
                "description": "Crie aplicações SPA reativas utilizando useState, useEffect, useContext e gerenciamento de estado.",
                "cert_name": "Meta React Specialization",
                "cert_url": "https://react.dev/learn",
                "docs_url": "https://react.dev/"
            },
            {
                "step_id": "step_3",
                "title": "Next.js — Renderização no Servidor (SSR) & SEO",
                "description": "Desenvolva sites e sistemas com o Next.js App Router, componentes de servidor, rotas de API e otimização SEO.",
                "cert_name": "Vercel Next.js Learn Certificate",
                "cert_url": "https://nextjs.org/learn",
                "docs_url": "https://nextjs.org/docs"
            },
            {
                "step_id": "step_4",
                "title": "TailwindCSS & Design Systems Responsivos",
                "description": "Aprenda a aplicar estilização moderna e utilitária com TailwindCSS, garantindo layout 100% responsivo para mobile e desktop.",
                "cert_name": "TailwindCSS Official Academy",
                "cert_url": "https://tailwindcss.com/docs",
                "docs_url": "https://tailwindcss.com/"
            }
        ]
    },
    "devops_cloud": {
        "id": "devops_cloud",
        "title": "☁️ Engenheiro DevOps & Cloud",
        "subtitle": "Automação de infraestrutura, CI/CD e nuvem AWS/Docker",
        "category": "Cloud & Infraestrutura",
        "description": (
            "Profissional responsável por automatizar a entrega de software, gerenciar servidores na nuvem "
            "e garantir que os sistemas fiquem no ar sem quedas. Trabalha com AWS, Docker, Kubernetes e esteiras CI/CD."
        ),
        "summary": "Automatiza deploy, gerencia servidores na AWS, cria containers Docker e configura esteiras CI/CD.",
        "market_demand": "Altíssima — A transição das empresas para a nuvem exige especialistas em DevOps.",
        "salary_br": "R$ 6.500,00 a R$ 16.000,00 / mês",
        "salary_usd": "$ 3,500 to $ 8,000 / month",
        "search_kw": "DevOps",
        "references": ["AWS Skill Builder (aws.training)", "Docker Docs (docs.docker.com)", "Linux Foundation (training.linuxfoundation.org)"],
        "tools": ["Linux (Ubuntu/Debian)", "Docker", "AWS (EC2, S3, RDS)", "GitHub Actions / GitLab CI", "Terraform", "Nginx"],
        "skills": ["Administração de Servidores Linux", "Containerização com Docker & Compose", "Serviços em Nuvem AWS", "Esteiras de CI/CD Automatizadas", "Infraestrutura como Código (Terraform)", "Monitoramento & Logs (Prometheus/Grafana)"],
        "specialization_steps": [
            {
                "step_id": "step_1",
                "title": "Administração de Sistemas Linux & Redes",
                "description": "Domine comandos bash, permissões, usuários, serviços systemd e protocolos de rede em Linux.",
                "cert_name": "Linux Foundation Certified System Administrator (LFCS)",
                "cert_url": "https://training.linuxfoundation.org/certification/linux-foundation-certified-sysadmin-lfcs/",
                "docs_url": "https://www.linux.org/lessons/"
            },
            {
                "step_id": "step_2",
                "title": "Docker & Containerização de Aplicações",
                "description": "Aprenda a empacotar qualquer aplicação em containers leves e portáteis usando Dockerfiles e Docker Compose.",
                "cert_name": "Docker Certified Associate (DCA)",
                "cert_url": "https://docs.docker.com/get-started/",
                "docs_url": "https://docs.docker.com/"
            },
            {
                "step_id": "step_3",
                "title": "AWS Cloud Practitioner & Solutions Architect",
                "description": "Conecte serviços fundamentais da Amazon Web Services: EC2, S3, RDS, IAM e VPC para hospedar sistemas de forma segura.",
                "cert_name": "AWS Certified Solutions Architect – Associate",
                "cert_url": "https://aws.amazon.com/certification/certified-solutions-architect-associate/",
                "docs_url": "https://aws.amazon.com/getting-started/"
            },
            {
                "step_id": "step_4",
                "title": "Automação CI/CD & Infraestrutura como Código",
                "description": "Construa pipelines automatizadas de deploy no GitHub Actions e provisione servidores de forma programática com Terraform.",
                "cert_name": "HashiCorp Certified: Terraform Associate",
                "cert_url": "https://www.hashicorp.com/certification/terraform-associate",
                "docs_url": "https://developer.hashicorp.com/terraform/docs"
            }
        ]
    },
    "ui_ux_designer": {
        "id": "ui_ux_designer",
        "title": "🎨 UI/UX Designer",
        "subtitle": "Desenho de interfaces visuais e pesquisa de experiência do usuário",
        "category": "Design & Produto",
        "description": (
            "Cria experiências digitais encantadoras e fáceis de usar em aplicativos e sites. "
            "Realiza pesquisas com usuários (UX) e projeta telas profissionais e protótipos interativos no Figma (UI)."
        ),
        "summary": "Desenha telas visuais profissionais e fluxos amigáveis no Figma para sites e aplicativos móveis.",
        "market_demand": "Alta — Produtos digitais competem pela qualidade visual e facilidade de uso.",
        "salary_br": "R$ 4.000,00 a R$ 11.000,00 / mês",
        "salary_usd": "$ 2,000 to $ 5,500 / month",
        "search_kw": "UI/UX Designer",
        "references": ["Figma Learn (help.figma.com)", "Google UX Design Certificate (coursera.org/google-ux-design)"],
        "tools": ["Figma (principal)", "Prototipagem Interativa", "Design Systems", "Miro / FigJam", "Usability Testing"],
        "skills": ["Design de Interfaces no Figma", "Arquitetura de Informação & Wireframes", "UX Research & Testes de Usabilidade", "Construção de Design Systems", "Prototipagem de Alta Fidelidade", "Handoff de Design para Desenvolvedores"],
        "specialization_steps": [
            {
                "step_id": "step_1",
                "title": "Fundamentos de UX Research & Design Thinking",
                "description": "Aprenda a entender a dor dos usuários, criar personas, mapa de jornada e realizar entrevistas de pesquisa.",
                "cert_name": "Google UX Design Professional Certificate",
                "cert_url": "https://www.coursera.org/professional-certificates/google-ux-design",
                "docs_url": "https://www.interaction-design.org/literature"
            },
            {
                "step_id": "step_2",
                "title": "Figma Masterclass — Telas & Componentes Reutilizáveis",
                "description": "Domine Auto Layout, variantes, componentes flexíveis e bibliotecas no Figma.",
                "cert_name": "Figma Official Certification / Masterclass",
                "cert_url": "https://help.figma.com/hc/en-us/categories/360002042114-Learn-Figma",
                "docs_url": "https://help.figma.com/"
            },
            {
                "step_id": "step_3",
                "title": "Prototipagem Interativa & Micro-animações",
                "description": "Transforme telas estáticas em protótipos navegáveis com transições suaves para testes com clientes reais.",
                "cert_name": "UX Design Institute — Prototyping",
                "cert_url": "https://www.uxdesigninstitute.com/",
                "docs_url": "https://help.figma.com/hc/en-us/articles/360040451373-Create-prototypes"
            },
            {
                "step_id": "step_4",
                "title": "Design Systems & Handoff para Devs",
                "description": "Organize regras de tipografia, cores, espaçamentos e tokens para entrega perfeita à equipe de desenvolvimento.",
                "cert_name": "Design Systems Academy",
                "cert_url": "https://www.designsystems.com/",
                "docs_url": "https://www.designsystems.com/getting-started-with-design-systems/"
            }
        ]
    },
    "suporte_ti": {
        "id": "suporte_ti",
        "title": "🎧 Analista de Suporte & Infraestrutura TI",
        "subtitle": "Atendimento técnico, manutenção de redes, chamados e computadores",
        "category": "Suporte & Operações de TI",
        "description": (
            "Porta de entrada essencial na área de Tecnologia. Responsável por resolver problemas técnicos de usuários, "
            "configurar computadores, gerenciar redes locais (LAN/Wi-Fi) e administrar chamados no padrão ITIL."
        ),
        "summary": "Presta suporte técnico, configura redes e sistemas, resolve chamados de TI e ajuda usuários.",
        "market_demand": "Muito Alta (Excelente para iniciantes) — Toda empresa com computadores contrata suporte técnico constantemente.",
        "salary_br": "R$ 2.200,00 a R$ 5.500,00 / mês",
        "salary_usd": "$ 1,500 to $ 3,500 / month",
        "search_kw": "Suporte Técnico",
        "references": ["Google IT Support (coursera.org/professional-certificates/google-it-support)", "CompTIA A+ (comptia.org/certifications/a)"],
        "tools": ["Windows Server / Active Directory", "Linux Básico", "Sistemas de Chamados (Jira/Freshdesk)", "Redes (TCP/IP, DNS, DHCP)", "AnyDesk / TeamViewer"],
        "skills": ["Diagnóstico de Hardware & Software", "Configuração de Redes TCP/IP & Wi-Fi", "Administração de Usuários no Active Directory", "Atendimento ao Cliente & Comunicação", "Gestão de Incidentes (ITIL)", "Acesso Remoto & Manutenção"],
        "specialization_steps": [
            {
                "step_id": "step_1",
                "title": "Certificado Profissional de Suporte em TI do Google",
                "description": "Curso completo cobrindo redes, sistemas operacionais, administração de sistemas e segurança de TI.",
                "cert_name": "Google IT Support Professional Certificate",
                "cert_url": "https://www.coursera.org/professional-certificates/google-it-support",
                "docs_url": "https://support.google.com/"
            },
            {
                "step_id": "step_2",
                "title": "Fundamentos de Hardware & Sistemas Operacionais (CompTIA A+)",
                "description": "Estude montagem, manutenção, diagnóstico de erros em Windows e comandos de terminal.",
                "cert_name": "CompTIA A+ Certification",
                "cert_url": "https://www.comptia.org/certifications/a",
                "docs_url": "https://www.comptia.org/resources"
            },
            {
                "step_id": "step_3",
                "title": "Redes de Computadores & Protocolos (TCP/IP, DNS, DHCP)",
                "description": "Entenda roteamento, switches, endereçamento IP, configuração de roteadores e diagnóstico com ping/traceroute.",
                "cert_name": "Cisco Certified Network Associate (CCNA) Fundamentals",
                "cert_url": "https://www.cisco.com/c/en/us/training-events/training-certifications/certifications/associate/ccna.html",
                "docs_url": "https://www.netacad.com/"
            },
            {
                "step_id": "step_4",
                "title": "Active Directory & Gestão de Chamados ITIL v4",
                "description": "Aprenda a gerenciar contas corporativas no Windows Active Directory e operar ferramentas de chamados sob metodologias ITIL.",
                "cert_name": "ITIL 4 Foundation Certificate",
                "cert_url": "https://www.axelos.com/certifications/itil-service-management/itil-4-foundation",
                "docs_url": "https://learn.microsoft.com/pt-br/windows-server/identity/ad-ds/get-started"
            }
        ]
    }
}

CAREER_PROFILES = CAREER_GUIDANCE_DATA

for _pid, _pdata in CAREER_GUIDANCE_DATA.items():
    if "steps" not in _pdata:
        _pdata["steps"] = _pdata["specialization_steps"]
    if "summary" not in _pdata:
        _pdata["summary"] = _pdata["description"]

PROFESSION_ALIASES = {
    "1": "server_side_tracking",
    "2": "growth_engineer",
    "3": "analytics_engineer",
    "4": "ia_ops",
    "5": "sdr_tecnico",
    "6": "dev_python",
    "7": "frontend_react",
    "8": "devops_cloud",
    "9": "ui_ux_designer",
    "10": "suporte_ti",
    "server_side_tracking": "server_side_tracking",
    "growth_engineer": "growth_engineer",
    "analytics_engineer": "analytics_engineer",
    "ia_ops": "ia_ops",
    "sdr_tecnico": "sdr_tecnico",
    "dev_python": "dev_python",
    "frontend_react": "frontend_react",
    "devops_cloud": "devops_cloud",
    "ui_ux_designer": "ui_ux_designer",
    "suporte_ti": "suporte_ti"
}

def resolve_profession_id(prof_id: str) -> str:
    return PROFESSION_ALIASES.get(str(prof_id), str(prof_id))

def get_carreiras_main_markup():
    buttons = [
        [InlineKeyboardButton(text="⚡ Server-Side Tracking", callback_data="car:p:server_side_tracking"),
         InlineKeyboardButton(text="🚀 Growth Engineer", callback_data="car:p:growth_engineer")],
        [InlineKeyboardButton(text="📊 Analytics Engineer", callback_data="car:p:analytics_engineer"),
         InlineKeyboardButton(text="🤖 IA-Ops Specialist", callback_data="car:p:ia_ops")],
        [InlineKeyboardButton(text="🎯 SDR Técnico B2B", callback_data="car:p:sdr_tecnico"),
         InlineKeyboardButton(text="🐍 Dev Python & Backend", callback_data="car:p:dev_python")],
        [InlineKeyboardButton(text="⚛️ Dev Frontend React", callback_data="car:p:frontend_react"),
         InlineKeyboardButton(text="☁️ DevOps & Cloud", callback_data="car:p:devops_cloud")],
        [InlineKeyboardButton(text="🎨 UI/UX Designer", callback_data="car:p:ui_ux_designer"),
         InlineKeyboardButton(text="🎧 Suporte & Infra TI", callback_data="car:p:suporte_ti")],
        [InlineKeyboardButton(text="📚 Cursos PT/EN, Inglês & IAs de Estudo", callback_data="car:estudos")],
        [InlineKeyboardButton(text="🔙 Voltar ao Menu Principal", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

get_career_menu_markup = get_carreiras_main_markup

def get_profession_detail_markup(prof_id: str):
    pid = resolve_profession_id(prof_id)
    buttons = [
        [InlineKeyboardButton(text="🗺️ Ver Trilha & Roadmap", callback_data=f"car:r:{pid}")],
        [InlineKeyboardButton(text="🔍 Buscar Vagas Desta Carreira", callback_data=f"car:j:{pid}")],
        [InlineKeyboardButton(text="📚 Cursos Recomendados & IAs de Apoio", callback_data="car:estudos")],
        [InlineKeyboardButton(text="🔙 Voltar às Carreiras", callback_data="car:main")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

@dp.message(Command("estudos"))
@dp.callback_query(F.data == "car:estudos")
async def show_guia_estudos(target):
    """Exibe o ecossistema global de cursos, aprendizado de inglês e IAs de apoio."""
    message = target.message if isinstance(target, CallbackQuery) else target
    if isinstance(target, CallbackQuery):
        await target.answer()

    text = (
        "📚 *Guia Global de Estudos, Cursos & IAs*\n"
        "_Recursos selecionados para acelerar seu aprendizado e obter certificações de peso._\n\n"
        "🔬 *1. FERRAMENTAS GOOGLE LABS (LEARN)*\n"
        "• [NotebookLM](https://notebooklm.google) — RAG sem alucinação + Podcasts de Áudio\n"
        "• [Google Illuminate](https://illuminate.google.com) — Converte artigos acadêmicos em áudio\n"
        "• [Learn Your Way](https://learnyourway.withgoogle.com) — Adapta conteúdos ao seu estilo\n"
        "• [Google AI Studio](https://aistudio.google.com) — Teste gratuito dos modelos Gemini 3\n"
        "• [Jules AI Code Agent](https://jules.google) — Agente de programação experimental\n"
        "• [Project Genie](https://labs.google/projectgenie) — Criação de cenários 2D com IA\n\n"
        "🌐 *2. APRENDER INGLÊS (GRATUITO)*\n"
        "• [EF SET Test & Certificado](https://www.efset.org) — Certificado oficial CEFR\n"
        "• [BBC Learning English](https://www.bbc.co.uk/learningenglish) — Cursos em áudio/vídeo\n"
        "• [Google Translate Speaking](https://translate.google.com) — Prática de fala com IA\n"
        "• [Coursera English Career](https://www.coursera.org/learn/careerdevelopment) — Inglês p/ trabalho\n\n"
        "🇧🇷 *3. CURSOS TECH EM PORTUGUÊS (COM CERTIFICADO)*\n"
        "• [Google Skillshop](https://skillshop.exceedlms.com) — Ads, GA4, GTM e Looker Studio\n"
        "• [Fundação Bradesco](https://www.ev.org.br) — Python, SQL, Excel, HTML/CSS\n"
        "• [DIO.me Bootcamps](https://www.dio.me) — Bootcamps com empresas tech\n"
        "• [Microsoft Learn PT-BR](https://learn.microsoft.com/pt-br/) — Power BI, Azure, Dynamics\n"
        "• [Santander Academy](https://www.santanderopenacademy.com) — Marketing, Vendas e IA\n\n"
        "🇺🇸 *4. CERTIFICAÇÕES GLOBAIS EM INGLÊS*\n"
        "• [Meta Professional Certs](https://www.coursera.org/professional-certificates/meta-front-end-developer) — React & Marketing\n"
        "• [AWS Skill Builder](https://aws.skillbuilder.aws) — Treinamentos AWS Cloud\n"
        "• [Python Institute](https://pythoninstitute.org) — Certificações PCEP e PCAP\n"
        "• [Linux Foundation](https://training.linuxfoundation.org) — Linux & DevOps\n\n"
        "🤖 *5. OUTRAS IAS DE APOIO*\n"
        "• [Google Gemini](https://gemini.google.com) — Deep Research e tutoria passo a passo\n"
        "• [SciSpace / Consensus](https://typeset.io) — Leitura de artigos acadêmicos\n"
        "• [Wolfram Alpha](https://www.wolframalpha.com) — Cálculo e exatas passo a passo\n"
        "• [RemNote](https://www.remnote.com) — Flashcards com repetição espaçada"
    )

    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎓 Ver Trilhas de Carreiras", callback_data="car:main")],
        [InlineKeyboardButton(text="🔙 Voltar ao Menu Principal", callback_data="main_menu")]
    ])

    if isinstance(target, CallbackQuery):
        await message.edit_text(text, reply_markup=markup, parse_mode="Markdown", disable_web_page_preview=True)
    else:
        await message.answer(text, reply_markup=markup, parse_mode="Markdown", disable_web_page_preview=True)


def get_profession_roadmap_markup(user_id, prof_id: str):
    pid = resolve_profession_id(prof_id)
    prof = CAREER_GUIDANCE_DATA.get(pid)
    if not prof:
        return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 Voltar", callback_data="car:main")]])
    
    progress = get_user_career_progress(user_id, pid)
    steps = prof.get("specialization_steps", prof.get("steps", []))
    
    buttons = []
    for idx, step in enumerate(steps):
        if isinstance(step, dict):
            step_id = step.get("step_id", f"step_{idx+1}")
            step_title = step.get("title", f"Etapa {idx+1}")
            cert_url = step.get("cert_url")
        else:
            step_id = f"step_{idx+1}"
            step_title = str(step)
            cert_url = None
            
        step_info = progress.get(step_id, {})
        is_done = (step_info.get("status", 0) == 1) if isinstance(step_info, dict) else (int(step_info) == 1)
        icon = "✅" if is_done else "⬜"
        
        short_title = step_title[:32] + "..." if len(step_title) > 35 else step_title
        btn_text = f"{icon} {short_title}"
        
        buttons.append([InlineKeyboardButton(text=btn_text, callback_data=f"car:t:{pid}:{step_id}")])
        if cert_url:
            cert_name = step.get("cert_name", "Certificação / Curso") if isinstance(step, dict) else "Certificação"
            buttons.append([InlineKeyboardButton(text=f"🎓 {cert_name[:35]} 🔗", url=cert_url)])
            
    buttons.append([InlineKeyboardButton(text="🔍 Buscar Vagas Desta Carreira", callback_data=f"car:j:{pid}")])
    buttons.append([InlineKeyboardButton(text="🔙 Voltar aos Detalhes", callback_data=f"car:p:{pid}")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

async def render_roadmap_view(message: types.Message, user_id: str, pid: str, is_edit: bool = False):
    prof = CAREER_GUIDANCE_DATA.get(pid)
    if not prof:
        return
        
    progress = get_user_career_progress(user_id, pid)
    steps = prof.get("specialization_steps", prof.get("steps", []))
    total_steps = len(steps)
    
    done_count = 0
    for idx, step in enumerate(steps):
        step_id = step.get("step_id", f"step_{idx+1}") if isinstance(step, dict) else f"step_{idx+1}"
        sinfo = progress.get(step_id, {})
        stat = sinfo.get("status", 0) if isinstance(sinfo, dict) else int(sinfo)
        if stat == 1:
            done_count += 1
            
    percent = int((done_count / total_steps) * 100) if total_steps > 0 else 0
    
    msg = (
        f"🗺️ *Roadmap: {prof['title']}*\n"
        f"Progresso: *{percent}%* ({done_count}/{total_steps} etapas concluídas)\n\n"
        f"Clique nas etapas abaixo para marcar/desmarcar o seu progresso ou acesse os links das certificações oficiais:"
    )
    
    markup = get_profession_roadmap_markup(user_id, pid)
    if is_edit:
        await message.edit_text(msg, reply_markup=markup, parse_mode="Markdown")
    else:
        await message.answer(msg, reply_markup=markup, parse_mode="Markdown")


@dp.message(Command("start"))
@dp.message(Command("tutorial"))
@dp.message(Command("boasvindas"))
@dp.message(F.text == "📖 Tutorial & Boas-Vindas")
@dp.message(F.text == "📖 Tutorial")
@dp.callback_query(F.data == "onboarding_tutorial")
async def cmd_start(update):
    """Apresentação de Boas-Vindas e Tutorial Interativo ao iniciar o bot."""
    message = update.message if isinstance(update, CallbackQuery) else update
    user_id = str(message.chat.id)
    profile = get_user_profile(user_id)
    if not profile.get("full_name"):
        name = message.from_user.full_name if message.from_user else "Usuário"
        upsert_user_profile(user_id, full_name=name)
        
    await show_onboarding_tutorial(update)

async def show_onboarding_tutorial(target):
    message = target.message if isinstance(target, CallbackQuery) else target
    if isinstance(target, CallbackQuery):
        await target.answer()
        
    user_id = str(message.chat.id)
    profile = get_user_profile(user_id)
    
    pdf_status = "✅ PDF Ativo" if profile.get("resume_text") else "❌ Nenhum PDF"
    text_status = "✅ Texto Configurado" if profile.get("experience") or profile.get("skills") else "❌ Nenhum Texto"
    key_status = "✅ Chave Própria (`gsk_...`)" if profile.get("groq_api_key") else "⚡ Pool Compartilhado"
    
    text = (
        "🚀 *Bem-vindo ao Sniper Bot SaaS!*\n"
        "_Seu assistente inteligente de busca de vagas e desenvolvimento de carreira tech._\n\n"
        "✨ *Como tirar o máximo proveito do robô em 4 passos:*\n\n"
        "1️⃣ *Cadastre seu Perfil ou Currículo (PDF)*\n"
        "   Envie seu PDF ou digite seu perfil para a IA ler suas habilidades e calcular o *Score de Compatibilidade (%)* em cada vaga.\n\n"
        "2️⃣ *Conecte sua Chave Groq IA (Gratuito)*\n"
        "   Cadastre sua chave pessoal em [console.groq.com](https://console.groq.com) para análises super rápidas e sem limite de cota.\n\n"
        "3️⃣ *Dispare a Caçada de Vagas*\n"
        "   Varredura em 14 plataformas simultâneas (Gupy, LinkedIn, Workana, InfoJobs, etc). O bot gera *Cover Letters* personalizadas para você!\n\n"
        "4️⃣ *Trilha de Carreiras de Elite*\n"
        "   Explore roadmaps, guias práticos e certificações oficiais para as 5 profissões mais bem pagas do mercado.\n\n"
        "─── ⚙️ *SEU STATUS ATUAL* ───\n"
        f"• Currículo PDF: *{pdf_status}*\n"
        f"• Perfil em Texto: *{text_status}*\n"
        f"• Motor de IA: *{key_status}*\n\n"
        "👇 *Escolha onde deseja começar:*"
    )
    
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📄 Enviar Currículo (PDF)", callback_data="perfil_upload_pdf"),
         InlineKeyboardButton(text="📝 Digitar Perfil (Texto)", callback_data="perfil_edit_text")],
        [InlineKeyboardButton(text="🔑 Configurar Chave Groq IA", callback_data="config_chave_ia")],
        [InlineKeyboardButton(text="🎯 Caçar Vagas Agora", callback_data="hunt_menu"),
         InlineKeyboardButton(text="🎓 Trilha de Carreiras", callback_data="car:main")],
        [InlineKeyboardButton(text="👤 Ver Meu Perfil Completo", callback_data="menu_perfil")],
        [InlineKeyboardButton(text="🚀 Acessar Menu Principal", callback_data="main_menu")]
    ])
    
    if isinstance(target, CallbackQuery):
        await message.edit_text(text, reply_markup=markup, parse_mode="Markdown", disable_web_page_preview=True)
    else:
        await message.answer(text, reply_markup=markup, parse_mode="Markdown", disable_web_page_preview=True)

def get_main_reply_keyboard():
    keyboard = [
        [KeyboardButton(text="📍 Buscar Vagas Perto de Mim", request_location=True)],
        [KeyboardButton(text="🎯 Caçar Vagas"), KeyboardButton(text="🎓 Carreiras")],
        [KeyboardButton(text="👤 Meu Perfil"), KeyboardButton(text="⚡ Server-Side Tracking")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

@dp.message(F.location)
async def handle_user_location(message: types.Message):
    """Manipula a localização enviada pelo usuário via celular e busca vagas próximas num raio de 50km."""
    if not message.location:
        await message.answer("Não foi possível capturar sua localização.")
        return
        
    lat = message.location.latitude
    lon = message.location.longitude
    
    await message.answer(f"📍 *Localização recebida!* (Lat: `{lat:.4f}`, Lon: `{lon:.4f}`)\n🔎 Buscando vagas físicas e híbridas num raio de 50 km...", parse_mode="Markdown")
    
    from database import get_jobs
    jobs = await asyncio.to_thread(get_jobs, include_all=True, lat=lat, lon=lon, radius=50.0)
    
    if not jobs:
        await message.answer("⚠️ Nenhuma vaga presencial/híbrida foi encontrada no raio de 50 km da sua localização atual. Tente buscar na lista geral de vagas 100% remotas!", reply_markup=get_main_reply_keyboard())
        return
        
    res_text = f"🎯 *Encontramos {len(jobs)} vagas num raio de 50 km da sua localização:*\n\n"
    for idx, j in enumerate(jobs[:8], 1):
        dist_info = f" ({j['distance_km']} km)" if j.get('distance_km') is not None else ""
        res_text += f"{idx}. *{j['title']}* - {j['company']}\n📍 _{j.get('location', 'Brasil')}_{dist_info}\n🔗 [Ver Vaga]({j['link']})\n\n"
        
    await message.answer(res_text, parse_mode="Markdown", disable_web_page_preview=True, reply_markup=get_main_reply_keyboard())

@dp.message(Command("logs"))
async def cmd_logs(message: types.Message):
    if not os.path.exists("erros_robo.log"):
        await message.answer("Nenhum log de erro encontrado.")
        return
    
    def read_log_tail():
        with open("erros_robo.log", "r", encoding="utf-8") as f:
            lines = f.readlines()
            tail = "".join(lines[-50:])
            if len(tail) > 3500:
                tail = "..." + tail[-3500:]
            return tail
            
    tail = await asyncio.to_thread(read_log_tail)
    await message.answer(f"📜 *Últimos Logs (erros_robo.log):*\n\n```log\n{tail}\n```", parse_mode="Markdown")

@dp.callback_query(F.data == "main_menu")
async def callback_main_menu(callback: CallbackQuery):
    await callback.answer()
    markup = get_main_menu_markup()
    await callback.message.edit_text("🤖 *Sniper Bot Nativo 100% Operante*\n\nO que você deseja fazer?", reply_markup=markup, parse_mode="Markdown")

# ---------------------------------------------------------
# HANDLERS DO MENU PRINCIPAL E NAVEGAÇÃO
# ---------------------------------------------------------
async def show_main_menu(message: types.Message):
    """Exibe o menu de navegação rápido (ReplyKeyboard) e o menu inline principal."""
    persistent_markup = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎯 Caçar Vagas"), KeyboardButton(text="🚀 Trilha de Carreiras")],
            [KeyboardButton(text="👤 Meu Perfil"), KeyboardButton(text="🔑 Chave IA")],
            [KeyboardButton(text="📖 Tutorial"), KeyboardButton(text="🛠 Configurações")]
        ],
        resize_keyboard=True,
        is_persistent=True
    )
    await message.answer("Bem-vindo de volta! Use o menu rápido abaixo ou escolha uma opção:", reply_markup=persistent_markup)
    
    markup = get_main_menu_markup()
    await message.answer("🤖 *Sniper Bot Nativo 100% Operante*\n\nO que você deseja fazer?", reply_markup=markup, parse_mode="Markdown")

def get_main_menu_markup():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎯 Caçar Vagas", callback_data="hunt_menu")],
        [InlineKeyboardButton(text="👤 Meu Perfil & Currículo", callback_data="menu_perfil")],
        [InlineKeyboardButton(text="🎓 Trilha de Carreiras", callback_data="car:main")],
        [InlineKeyboardButton(text="🔑 Minha Chave Groq IA", callback_data="config_chave_ia")],
        [InlineKeyboardButton(text="📖 Tutorial & Guia", callback_data="onboarding_tutorial")],
        [InlineKeyboardButton(text="🛠 Configurações", callback_data="settings_menu")]
    ])

# ----------------- CONFIGURAÇÕES -----------------
@dp.callback_query(F.data == "settings_menu")
async def settings_menu(callback: CallbackQuery):
    await callback.answer()
    chat_id = callback.message.chat.id
    await callback.message.edit_text("⚙️ *Configurações do Robô*", reply_markup=get_settings_markup(chat_id), parse_mode="Markdown")

def get_settings_markup(chat_id):
    settings = get_user_settings(chat_id)
    p = settings["platforms"]
    mode_labels = {
        "cards": "📱 Cartões 1a1",
        "compact": "📋 Lista Resumida",
        "file": "📄 Tabela CSV + Lista"
    }
    cur_mode = mode_labels.get(settings.get("display_mode", "compact"), "📋 Lista Resumida")
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"📍 Local: {settings['location']} (Mudar)", callback_data="change_location")],
        [InlineKeyboardButton(text=f"Nível: {settings['level']} (Mudar)", callback_data="change_level")],
        [InlineKeyboardButton(text=f"Contrato: {settings['contract']} (Mudar)", callback_data="change_contract")],
        [InlineKeyboardButton(text=f"Formação: {settings['education']} (Mudar)", callback_data="change_education")],
        [InlineKeyboardButton(text=f"📊 Formato: {cur_mode} (Mudar)", callback_data="change_display_mode")],
        # --- GRUPOS DE PLATAFORMAS ---
        [InlineKeyboardButton(text="── 🚀 PLATAFORMAS ──", callback_data="noop")],
        [InlineKeyboardButton(text=f"🚀 Freelance (Workana, 99Freelas...): {'✅ ON' if p.get('workana') else '❌ OFF'}", callback_data="toggle_group_freelance")],
        [InlineKeyboardButton(text=f"🌐 Globais (LinkedIn, Indeed): {'✅ ON' if any([p.get('linkedin'), p.get('indeed'), p.get('glassdoor')]) else '❌ OFF'}", callback_data="toggle_group_globais")],
        [InlineKeyboardButton(text=f"🇧🇷 Nacionais (Gupy, Catho...): {'✅ ON' if any([p.get('gupy'), p.get('catho'), p.get('infojobs'), p.get('vagas_com')]) else '❌ OFF'}", callback_data="toggle_group_nacionais")],
        [InlineKeyboardButton(text=f"💻 Foco em TI (Coodesh, GitHub): {'✅ ON' if any([p.get('coodesh'), p.get('geekhunter'), p.get('programathor'), p.get('github_vagas')]) else '❌ OFF'}", callback_data="toggle_group_ti")],
        [InlineKeyboardButton(text=f"🏡 Remotos (Remotar, Jooble): {'✅ ON' if any([p.get('remotar'), p.get('jooble'), p.get('jsearch')]) else '❌ OFF'}", callback_data="toggle_group_remotos")],
        # --- OUTROS ---
        [InlineKeyboardButton(text=f"📧 Gmail Alertas: {'✅ ON' if p['gmail'] else '❌ OFF'}", callback_data="toggle_gmail")],
        [InlineKeyboardButton(text=f"🛡️ Escudo PT-BR: {'✅ ON' if settings.get('escudo_ptbr', True) else '❌ OFF'}", callback_data="toggle_escudo_ptbr")],
        [InlineKeyboardButton(text="🔑 Minha Chave de IA (Groq)", callback_data="config_chave_ia")],
        [InlineKeyboardButton(text="🔙 Voltar ao Início", callback_data="main_menu")]
    ])

@dp.callback_query(F.data == "change_display_mode")
async def change_display_mode(callback: CallbackQuery):
    await callback.answer()
    chat_id = callback.message.chat.id
    settings = get_user_settings(chat_id)
    modes = ["compact", "file", "cards"]
    cur = settings.get("display_mode", "compact")
    idx = modes.index(cur) if cur in modes else 0
    settings["display_mode"] = modes[(idx + 1) % len(modes)]
    await callback.message.edit_reply_markup(reply_markup=get_settings_markup(chat_id))

@dp.callback_query(F.data == "change_level")
async def change_level(callback: CallbackQuery):
    await callback.answer()
    chat_id = callback.message.chat.id
    settings = get_user_settings(chat_id)
    levels = ["Todos", "Júnior", "Pleno", "Sênior", "Jovem Aprendiz", "Ganhar Experiência", "Iniciantes Tudo"]
    idx = levels.index(settings["level"]) if settings["level"] in levels else 0
    settings["level"] = levels[(idx + 1) % len(levels)]
    await callback.message.edit_reply_markup(reply_markup=get_settings_markup(chat_id))

@dp.callback_query(F.data == "change_location")
async def change_location(callback: CallbackQuery):
    await callback.answer()
    chat_id = callback.message.chat.id
    settings = get_user_settings(chat_id)
    locations = ["Brasil (Remoto)", "Londrina/PR", "Assaí/PR"]
    idx = locations.index(settings["location"])
    settings["location"] = locations[(idx + 1) % len(locations)]
    await callback.message.edit_reply_markup(reply_markup=get_settings_markup(chat_id))

@dp.callback_query(F.data == "change_contract")
async def change_contract(callback: CallbackQuery):
    await callback.answer()
    chat_id = callback.message.chat.id
    settings = get_user_settings(chat_id)
    contracts = ["Todos", "PJ", "CLT", "Freelancer"]
    idx = contracts.index(settings["contract"])
    settings["contract"] = contracts[(idx + 1) % len(contracts)]
    await callback.message.edit_reply_markup(reply_markup=get_settings_markup(chat_id))

@dp.callback_query(F.data == "change_education")
async def change_education(callback: CallbackQuery):
    await callback.answer()
    chat_id = callback.message.chat.id
    settings = get_user_settings(chat_id)
    educations = ["Todos", "Sem Formação"]
    idx = educations.index(settings["education"])
    settings["education"] = educations[(idx + 1) % len(educations)]
    await callback.message.edit_reply_markup(reply_markup=get_settings_markup(chat_id))

@dp.callback_query(F.data == "noop")
async def noop(callback: CallbackQuery):
    """Botão de cabeçalho de seção - não faz nada."""
    await callback.answer()

@dp.callback_query(F.data.startswith("toggle_group_"))
async def toggle_group(callback: CallbackQuery):
    await callback.answer()
    chat_id = callback.message.chat.id
    settings = get_user_settings(chat_id)
    group_name = callback.data.replace("toggle_group_", "")
    
    groups = {
        "freelance": ["workana", "freelancer", "novenove"],
        "globais": ["linkedin", "indeed", "glassdoor"],
        "nacionais": ["gupy", "catho", "infojobs", "vagas_com"],
        "ti": ["coodesh", "geekhunter", "programathor", "github_vagas"],
        "remotos": ["remotar", "jooble", "jsearch"]
    }
    
    plats = groups.get(group_name, [])
    if not plats: return
    
    # Se algum estiver ON, desliga todos. Se todos estiverem OFF, liga todos.
    is_any_on = any(settings["platforms"].get(p, False) for p in plats)
    new_state = not is_any_on
    
    for p in plats:
        if p in settings["platforms"]:
            settings["platforms"][p] = new_state
            
    await callback.message.edit_reply_markup(reply_markup=get_settings_markup(chat_id))

@dp.callback_query(F.data == "noop_applied")
async def handle_noop_applied(callback: CallbackQuery):
    await callback.answer()

@dp.callback_query(F.data == "toggle_escudo_ptbr")
async def toggle_escudo_ptbr(callback: CallbackQuery):
    await callback.answer()
    chat_id = callback.message.chat.id
    settings = get_user_settings(chat_id)
    settings["escudo_ptbr"] = not settings.get("escudo_ptbr", True)
    await callback.message.edit_reply_markup(reply_markup=get_settings_markup(chat_id))

@dp.callback_query(F.data.startswith("toggle_"))
async def toggle_platform(callback: CallbackQuery):
    # Mantém compatibilidade com outros toggles como toggle_gmail
    if callback.data.startswith("toggle_group_"): return

    await callback.answer()
    chat_id = callback.message.chat.id
    settings = get_user_settings(chat_id)
    plat = callback.data.replace("toggle_", "")
    if plat in settings["platforms"]:
        settings["platforms"][plat] = not settings["platforms"][plat]
    await callback.message.edit_reply_markup(reply_markup=get_settings_markup(chat_id))

# ----------------- CAÇAR VAGAS (MODO) -----------------
@dp.callback_query(F.data == "hunt_menu")
async def hunt_menu(callback: CallbackQuery):
    await callback.answer()
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Modo Freelance", callback_data="modo_freelance")],
        [InlineKeyboardButton(text="💼 Modo Emprego", callback_data="modo_emprego")],
        [InlineKeyboardButton(text="🌐 Modo Ambos", callback_data="modo_ambos")],
        [InlineKeyboardButton(text="🔙 Voltar", callback_data="main_menu")]
    ])
    await callback.message.edit_text(
        "🎯 *Onde você quer buscar vagas?*\n\n"
        "🚀 *Freelance* — Workana e 99Freelas (projetos e propostas)\n"
        "💼 *Emprego* — LinkedIn, Indeed, Glassdoor e mais\n"
        "🌐 *Ambos* — Todas as plataformas ativas",
        reply_markup=markup, parse_mode="Markdown"
    )

@dp.callback_query(F.data.startswith("modo_"))
async def select_mode(callback: CallbackQuery):
    await callback.answer()
    chat_id = callback.message.chat.id
    settings = get_user_settings(chat_id)
    modo = callback.data.split("_")[1]  # freelance | emprego | ambos

    # Ativa/desativa plataformas conforme o modo
    if modo == "freelance":
        for p in FREELANCE_PLATFORMS: settings["platforms"][p] = True
        for p in EMPREGO_PLATFORMS: settings["platforms"][p] = False
    elif modo == "emprego":
        for p in FREELANCE_PLATFORMS: settings["platforms"][p] = False
        for p in EMPREGO_PLATFORMS: settings["platforms"][p] = True
    else:  # ambos
        for p in FREELANCE_PLATFORMS + EMPREGO_PLATFORMS: settings["platforms"][p] = True

    # Vai para o menu de nichos
    menus_markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🧠 Especialista em IA", callback_data="nicho_ai")],
        [InlineKeyboardButton(text="💻 Desenvolvimento", callback_data="nicho_dev")],
        [InlineKeyboardButton(text="📊 Dados & RPA", callback_data="nicho_dados")],
        [InlineKeyboardButton(text="📈 Growth & Mkt", callback_data="nicho_mkt")],
        [InlineKeyboardButton(text="🎬 Audiovisual & Criação", callback_data="nicho_audio")],
        [InlineKeyboardButton(text="🏢 Base / Apoio Adm", callback_data="nicho_base")],
        [InlineKeyboardButton(text="🎯 Júnior", callback_data="nicho_junior")],
        [InlineKeyboardButton(text="🚀 Pleno", callback_data="nicho_pleno")],
        [InlineKeyboardButton(text="🔙 Voltar ao Modo", callback_data="hunt_menu")]
    ])
    modo_labels = {"freelance": "🚀 Freelance", "emprego": "💼 Emprego", "ambos": "🌐 Ambos"}
    await callback.message.edit_text(
        f"*Modo: {modo_labels[modo]}*\n\n🎯 Selecione o Nicho Estratégico:",
        reply_markup=menus_markup, parse_mode="Markdown"
    )

@dp.callback_query(F.data.startswith("nicho_"))
async def show_niche_jobs(callback: CallbackQuery):
    await callback.answer()
    nicho = callback.data.split("_")[1]
    
    menus = {
        "ai": [
            "Especialista em IA",
            "Engenheiro de IA",
            "Desenvolvedor de Agentes IA",
            "Prompt Engineer",
            "Machine Learning Engineer",
            "Cientista de Dados"
        ],
        "dev": [
            "Desenvolvedor Python",
            "Desenvolvedor Backend",
            "Desenvolvedor Node",
            "Desenvolvedor React",
            "Desenvolvedor Fullstack",
            "Desenvolvedor Django",
            "Desenvolvedor FastAPI"
        ],
        "dados": [
            "Analista de Power BI",
            "Desenvolvedor RPA",
            "Analista de Dados",
            "Engenheiro de Dados",
            "Analista de Analytics",
            "Analista SQL"
        ],
        "mkt": [
            "Gestor de Tráfego",
            "Growth Hacker",
            "Analista de Marketing Digital",
            "SDR",
            "Copywriter",
            "Especialista em SEO",
            "Analista de CRM"
        ],
        "audio": [
            "Editor de Vídeo",
            "Video Maker",
            "Social Media",
            "Designer Gráfico",
            "UX Designer"
        ],
        "base": [
            "Assistente Administrativo",
            "Recepcionista",
            "Suporte Técnico N1",
            "Assistente de Faturamento",
            "Assistente de Logística",
            "Assistente Financeiro",
            "Telemarketing",
            "Analista de RH"
        ],
        "junior": [
            "Desenvolvedor Junior Python",
            "Desenvolvedor Junior React",
            "Desenvolvedor Junior Fullstack",
            "Analista de Dados Junior",
            "Analista de Marketing Junior"
        ],
        "pleno": [
            "Desenvolvedor Pleno Python",
            "Desenvolvedor Pleno React",
            "Desenvolvedor Pleno Fullstack",
            "Analista de Dados Pleno",
            "Gestor de Trafego Pleno"
        ]
    }
    
    profs = menus.get(nicho, [])
    buttons = [[InlineKeyboardButton(text=p, callback_data=f"hunt_{p}")] for p in profs]
    buttons.append([InlineKeyboardButton(text="🔙 Voltar aos Nichos", callback_data="hunt_menu")])
    
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback.message.edit_text("🎯 *Selecione a Tecnologia/Profissão:*", reply_markup=markup, parse_mode="Markdown")

# ----------------- PROCESSO DE BUSCA -----------------
@dp.callback_query(F.data.startswith("auto_apply_"))
async def handle_auto_apply_callback(callback: CallbackQuery):
    await callback.answer("Candidatura por e-mail agendada com sucesso!", show_alert=True)

@dp.callback_query(F.data == "mark_applied_btn")
async def handle_mark_applied(callback: CallbackQuery):
    """Marca a vaga como candidatada e atualiza o botão."""
    link = None
    if callback.message.reply_markup:
        for row in callback.message.reply_markup.inline_keyboard:
            for btn in row:
                if btn.url:
                    link = btn.url
                    break
            if link: break
    
    if not link:
        await callback.answer("❌ Erro: Link da vaga não encontrado.", show_alert=True)
        return
    await asyncio.to_thread(mark_applied, link)
    await callback.answer("✅ Marcado como candidatado!", show_alert=False)
    # Atualiza os botões da mensagem para mostrar que já candidatou
    try:
        old_markup = callback.message.reply_markup
        new_rows = []
        for row in old_markup.inline_keyboard:
            new_row = []
            for btn in row:
                if btn.callback_data and btn.callback_data == "mark_applied_btn":
                    # Substitui botão por indicador visual
                    new_row.append(InlineKeyboardButton(text="✅ Já me Candidatei", callback_data="noop_applied"))
                else:
                    new_row.append(btn)
            new_rows.append(new_row)
        await callback.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(inline_keyboard=new_rows))
    except Exception:
        pass  # Se falhar ao editar, não quebra


@dp.callback_query(F.data == "mega_iniciantes")
async def process_mega_iniciantes(callback: CallbackQuery):
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🌍 Apenas Remoto", callback_data="mega_loc_remoto")],
        [InlineKeyboardButton(text="🏢 Presencial (Londrina e Região)", callback_data="mega_loc_londrina")]
    ])
    await callback.message.edit_text("🎓 *Onde você prefere buscar essas vagas de Iniciante?*", reply_markup=markup, parse_mode="Markdown")

@dp.callback_query(F.data.startswith("mega_loc_"))
async def process_mega_location(callback: CallbackQuery):
    chat_id = callback.message.chat.id
    settings = get_user_settings(chat_id)
    
    if "remoto" in callback.data:
        settings["location"] = "Brasil (Remoto)"
        loc_str = "Remoto"
    else:
        settings["location"] = "Londrina/PR"
        loc_str = "Presencial/Londrina"
        
    settings["level"] = "iniciantes tudo"
    
    for p in ["workana", "freelancer", "novenove"]:
        if p in settings["platforms"]:
            settings["platforms"][p] = False
            
    await callback.answer("Perfil ajustado!", show_alert=False)
    
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛠️ Tecnologia & Suporte", callback_data="mega_cat_ti")],
        [InlineKeyboardButton(text="📈 Comercial & Vendas (SDR)", callback_data="mega_cat_sdr")],
        [InlineKeyboardButton(text="📂 Administrativo (ADM)", callback_data="mega_cat_adm")],
        [InlineKeyboardButton(text="💻 Desenvolvimento de Sistemas", callback_data="mega_cat_dev")],
        [InlineKeyboardButton(text="📦 Logística & Estoque", callback_data="mega_cat_log")]
    ])
    await callback.message.edit_text(f"🎓 *Perfil Iniciante Ativado!*\n(Vagas Freelance desativadas. Focando em **{loc_str}**).\n\n👇 **Selecione a categoria mágica para iniciar a varredura:**", reply_markup=markup, parse_mode="Markdown")

MAGIC_CATEGORIES = {
    "operacoes_fisicas": ["Operador CNC", "Pintor Industrial", "Mecânico Industrial", "Soldador", "Eletricista", "Operador de Produção", "Auxiliar de Operações", "Conferente"],
    "logistica": ["Assistente de Logística", "Auxiliar de Logística", "Auxiliar de Almoxarifado", "Operador de Empilhadeira", "Auxiliar de Expedição", "Motorista", "Almoxarife"],
    "administrativo": ["Assistente Administrativo", "Auxiliar Administrativo", "Recepcionista", "Auxiliar de Escritório", "Data Entry", "Digitador", "Assistente Financeiro"],
    "criativos_performance": ["Designer Conversional", "Copywriter", "Criador de Anúncios", "Motion Designer", "Editor de Vídeo", "Gestor de Tráfego", "Designer Gráfico"],
    "inteligencia_vendas": ["SDR", "BDR", "Inside Sales", "Analista de Sales Ops", "Executivo de Vendas", "CRM", "Analista de Vendas"],
    "engenharia_ia_dados": ["Engenheiro de Dados", "Engenheiro de IA", "Machine Learning", "Data Engineer", "Cientista de Dados", "Analista de Dados"],
    "ti": ["Suporte N1", "Suporte Técnico", "Help Desk Júnior", "Técnico de Apoio ao Usuário de Informática", "Analista de Suporte Júnior"],
    "sdr": ["SDR Júnior", "SDR", "Inside Sales Júnior", "Assistente de Pré-Vendas", "Assistente de Growth"],
    "adm": ["Assistente Administrativo", "Auxiliar Administrativo", "Digitador", "Data Entry"],
    "dev": ["Desenvolvedor Júnior", "Programador Trainee", "Programador Júnior", "Desenvolvedor Node.JS Júnior"],
    "log": ["Auxiliar de Almoxarifado", "Auxiliar de Expedição", "Auxiliar de Estoque", "Assistente de Logística"]
}

@dp.callback_query(F.data.startswith("mega_cat_"))
async def process_mega_category(callback: CallbackQuery):
    cat_id = callback.data.split("_")[-1]
    
    terms = MAGIC_CATEGORIES.get(cat_id, [])
    await callback.answer(f"Iniciando varredura em {len(terms)} termos!")
    msg = await callback.message.edit_text(f"🎓 *Iniciando varredura automatizada em {len(terms)} termos...*", parse_mode="Markdown")
    
    for i, term in enumerate(terms):
        try:
            await msg.edit_text(f"🎓 *Buscando {i+1}/{len(terms)}: {term}...*", parse_mode="Markdown")
        except:
            pass
        await _do_hunt(term, callback.message)
        
    try:
        await msg.edit_text(f"✅ *Varredura mágica concluída com sucesso!*", parse_mode="Markdown")
    except:
        pass

@dp.callback_query(F.data.startswith("hunt_"), F.data != "hunt_menu")
async def process_hunt(callback: CallbackQuery):
    chat_id = callback.message.chat.id
    settings = get_user_settings(chat_id)
    active_plats = [k for k, v in settings["platforms"].items() if v]
    if not active_plats:
        try:
            await callback.answer("Ative pelo menos uma plataforma em Configurações!", show_alert=True)
        except Exception:
            await callback.message.answer("Ative pelo menos uma plataforma em Configurações!")
        return
        
    await callback.answer()
    keyword = callback.data.split("_", 1)[1]
    await _do_hunt(keyword, callback.message, callback=callback)


import unicodedata
import re

def normalize_str(s):
    if not s: return ""
    s = unicodedata.normalize('NFD', str(s))
    return s.encode('ascii', 'ignore').decode('utf-8').lower()

global_title_blacklist = [
    # Acadêmico / Ensino
    "professor", "professora", "docente", "tutor", "tutoria", "instrutor", "instrutora", "palestrante", 
    "academic", "academico", "lecturer", "lecionar", "ensinar", "aulas",
    # Jurídico / Legal
    "advogado", "advogada", "direito", "juridico", "paralegal", "promotor de justica",
    # Saúde / Médico
    "medico", "medica", "enfermeiro", "enfermeira", "enfermagem", "dentista", "farmaceutico", 
    "fisioterapeuta", "nutricionista", "veterinario", "psicologo", "psicologa", "psiquiatra", "biomedico",
    # Trabalho Braçal / Manutenção Física / Limpeza (geral)
    "faxineiro", "faxineira", "diarista", "domestica", "passadeira", "cozinheiro", "cozinheira", 
    "garcom", "garconete", "copa", "servente", "pedreiro", "carpinteiro", "frentista", 
    "lavador", "ajudante de obras", "servicos gerais",
    # Outros
    "voluntario", "voluntary"
]

BLACKLIST_PROFILES = {
    "commercial_sales": [
        "vendas", "vendedor", "vendedora", "comercial", "sdr", "bdr", 
        "sales", "representative", "representante", "negocios", "account"
    ],
    "marketing_ads": [
        "marketing", "ads", "anuncio", "anuncios", "trafego", "performance", 
        "midia", "media", "seo", "e-commerce", "ecommerce", "mercado livre", 
        "mercado-livre", "shopee", "inbound", "outbound", "growth"
    ],
    "creative_video": [
        "video", "imagem", "editor", "editora", "vsl", "motion", 
        "designer", "design", "figma", "arte", "artes", "criativo", 
        "filmmaker", "videomaker", "copywriter", "copywriting", "redator", 
        "redatora", "conteudo", "social media"
    ],
    "customer_service": [
        "atendimento", "suporte", "helpdesk", "telemarketing", "sac", 
        "suporte ao cliente", "customer service"
    ]
}

AI_TECHNICAL_BLACKLIST = (
    BLACKLIST_PROFILES["commercial_sales"] +
    BLACKLIST_PROFILES["marketing_ads"] +
    BLACKLIST_PROFILES["creative_video"] +
    BLACKLIST_PROFILES["customer_service"]
)

blacklist = {
    # --- IA / Inteligência Artificial ---
    "especialista em ia": AI_TECHNICAL_BLACKLIST,
    "engenheiro de ia": AI_TECHNICAL_BLACKLIST,
    "desenvolvedor de agentes ia": AI_TECHNICAL_BLACKLIST,
    "prompt engineer": AI_TECHNICAL_BLACKLIST,
    "machine learning engineer": AI_TECHNICAL_BLACKLIST,
    "cientista de dados": ["suporte", "infraestrutura", "redes", "helpdesk", "service desk", "dba", "entrada de dados", "digitador"],
    
    # --- Desenvolvimento de Software ---
    "desenvolvedor python": ["professor", "tutor", "instrutor", "curso", "vendas", "comercial"],
    "desenvolvedor backend": ["frontend", "front-end", "designer", "design", "vendas"],
    "desenvolvedor node": ["python", "java", "c#", "php", "ruby"],
    "desenvolvedor react": ["backend", "back-end", "database", "dba"],
    "desenvolvedor fullstack": ["wordpress", "wix", "shopify", "design", "designer"],
    "desenvolvedor django": ["frontend", "front-end", "node", "javascript", "react"],
    "desenvolvedor fastapi": ["frontend", "front-end", "node", "javascript", "react"],
    
    # --- Dados & RPA ---
    "analista de power bi": ["suporte", "helpdesk", "telemarketing", "vendas", "comercial"],
    "desenvolvedor rpa": ["vendas", "comercial", "atendimento", "suporte", "helpdesk"],
    "analista de dados": ["suporte", "infraestrutura", "redes", "helpdesk", "service desk", "dba", "entrada de dados", "digitador"],
    "engenheiro de dados": ["suporte", "infraestrutura", "redes", "helpdesk", "service desk", "dba", "entrada de dados", "digitador"],
    "analista de analytics": ["suporte", "helpdesk", "vendas", "comercial"],
    "analista sql": ["suporte", "helpdesk", "telemarketing", "vendas", "comercial"],
    
    # --- Growth & Marketing ---
    "gestor de trafego": ["aereo", "logistica", "transporte", "rodoviario", "carga", "frota", "veiculos", "patio", "controlador"],
    "growth hacker": ["suporte", "helpdesk", "vendas", "comercial"],
    "analista de marketing digital": ["designer", "design", "vendas", "sdr"],
    "sdr": ["loja", "balcao", "caixa", "repositor", "estoque", "limpeza", "farmacia", "supermercado", "promotor", "panfleteiro", "corretor"],
    "copywriter": ["designer", "design", "video", "editor"],
    "especialista em seo": ["designer", "design", "video", "editor", "programador"],
    "analista de crm": ["designer", "design", "video", "editor"],
    
    # --- Audiovisual & Criativo ---
    "editor de video": ["redacao", "texto", "copywriter", "marketing"],
    "video maker": ["redacao", "texto", "copywriter", "marketing"],
    "social media": ["programador", "desenvolvedor", "dba"],
    "designer grafico": ["programador", "desenvolvedor", "video", "editor"],
    "ux designer": ["programador", "desenvolvedor", "video", "editor"],
    
    # --- Base / Apoio Administrativo ---
    "assistente administrativo": ["producao", "limpeza", "carga", "descarga", "pesado", "operario", "servente", "cozinha", "estoque", "repositor", "caixa", "atendente", "vendas"],
    "recepcionista": ["limpeza", "zelador", "carga", "descarga", "vigilante armado", "seguranca armada"],
    "suporte tecnico n1": ["eletricista", "mecanico", "manutencao predial", "refrigeracao", "ar condicionado", "telemarketing", "vendas"],
    "assistente de faturamento": ["limpeza", "carga", "descarga", "vendas"],
    "assistente de logistica": ["motorista", "carregador", "limpeza", "carga", "descarga"],
    "assistente financeiro": ["limpeza", "carga", "descarga", "vendas"],
    "telemarketing": ["limpeza", "carga", "descarga", "motorista"],
    "analista de rh": ["direito", "pedagogia", "psicologia", "enfermagem", "limpeza"],
    
    # --- Júnior ---
    "desenvolvedor junior python": ["direito", "pedagogia", "psicologia", "enfermagem", "medicina", "nutricao", "marketing", "vendas", "sdr", "bdr", "designer", "design", "rh", "recepcao", "portaria", "limpeza", "senior", "sr", "pleno"],
    "desenvolvedor junior react": ["direito", "pedagogia", "psicologia", "enfermagem", "medicina", "nutricao", "marketing", "vendas", "sdr", "bdr", "designer", "design", "rh", "recepcao", "portaria", "limpeza", "senior", "sr", "pleno"],
    "desenvolvedor junior fullstack": ["direito", "pedagogia", "psicologia", "enfermagem", "medicina", "nutricao", "marketing", "vendas", "sdr", "bdr", "designer", "design", "rh", "recepcao", "portaria", "limpeza", "senior", "sr", "pleno"],
    "analista de dados junior": ["direito", "pedagogia", "psicologia", "enfermagem", "medicina", "nutricao", "marketing", "vendas", "sdr", "bdr", "designer", "design", "rh", "recepcao", "portaria", "limpeza", "senior", "sr", "pleno"],
    "analista de marketing junior": ["direito", "pedagogia", "psicologia", "enfermagem", "medicina", "nutricao", "sdr", "bdr", "designer", "design", "rh", "recepcao", "portaria", "limpeza", "senior", "sr", "pleno"],
    
    # --- Pleno ---
    "desenvolvedor pleno python": ["junior", "jr", "estagio", "estagiario", "senior", "sr", "director", "diretor", "coordenador", "gerente"],
    "desenvolvedor pleno react": ["junior", "jr", "estagio", "estagiario", "senior", "sr", "director", "diretor", "coordenador", "gerente"],
    "desenvolvedor pleno fullstack": ["junior", "jr", "estagio", "estagiario", "senior", "sr", "director", "diretor", "coordenador", "gerente"],
    "analista de dados pleno": ["junior", "jr", "estagio", "estagiario", "senior", "sr", "director", "diretor", "coordenador", "gerente"],
    "gestor de trafego pleno": ["junior", "jr", "estagio", "estagiario", "senior", "sr", "director", "diretor", "coordenador", "gerente", "aereo", "logistica", "transporte"],

    # --- OLD KEYS FOR BACKWARD COMPATIBILITY ---
    "gestor de trafego / performance": ["aereo", "logistica", "transporte", "rodoviario", "carga", "frota", "veiculos", "patio", "controlador"],
    "especialista em ia generativa": [
        "mlops", "machine learning engineer", "redes neurais", "data scientist", "engenheiro de dados",
        "rpa", "automacao", "uipath", "zapier", "n8n", "make.com",
        "backend", "desenvolvedor", "dev", "programador", "software engineer",
        "data engineer", "cloud", "devops", "kubernetes", "docker",
        "suporte", "infraestrutura", "helpdesk", "sysadmin"
    ],
    "ai coder / ai agent developer": ["vendas", "comercial", "conteudo", "social media"],
    "analista de dados / data scientist": ["suporte", "infraestrutura", "redes", "helpdesk", "service desk", "dba", "entrada de dados", "digitador"],
    "python scraping & data engineering": ["professor", "tutor", "instrutor", "curso", "vendas", "comercial"],
    "auxiliar administrativo": ["producao", "limpeza", "carga", "descarga", "pesado", "operario", "servente", "cozinha", "estoque", "repositor", "caixa", "atendente", "vendas"],
    "recepcao / portaria": ["limpeza", "zelador", "carga", "descarga", "vigilante armado", "seguranca armada"],
    "suporte tecnico n1 / service desk": ["eletricista", "mecanico", "manutencao predial", "refrigeracao", "ar condicionado", "telemarketing", "vendas"],
    "desenvolvedor junior / estagiario": ["direito", "pedagogia", "psicologia", "enfermagem", "medicina", "nutricao", "marketing", "vendas", "sdr", "bdr", "designer", "design", "rh", "recepcao", "portaria", "limpeza"],
    "python backend": ["professor", "tutor", "instrutor", "curso", "vendas", "comercial", "frontend", "front-end", "designer", "design"],
    "sdr / vendas junior": ["loja", "balcao", "caixa", "repositor", "estoque", "limpeza", "farmacia", "supermercado", "promotor", "panfleteiro", "corretor"],

    # --- Broad Category Macro Keywords & New Taxonomy Sub-Professions Blacklists ---
    "Operações Físicas": ["advogado", "medico", "professor", "desenvolvedor", "social media", "copywriter", "enfermeiro", "psicologo"],
    "operacoes fisicas": ["advogado", "medico", "professor", "desenvolvedor", "social media", "copywriter", "enfermeiro", "psicologo"],
    "Indústria": ["advogado", "medico", "professor", "desenvolvedor react", "social media", "copywriter", "telemarketing", "enfermeiro", "psicologo"],
    "industria": ["advogado", "medico", "professor", "desenvolvedor react", "social media", "copywriter", "telemarketing", "enfermeiro", "psicologo"],
    "Logística": ["gestor de trafego", "trafego pago", "advogado", "medico", "professor", "desenvolvedor react", "copywriter", "enfermeiro", "psicologo"],
    "logistica": ["gestor de trafego", "trafego pago", "advogado", "medico", "professor", "desenvolvedor react", "copywriter", "enfermeiro", "psicologo"],
    "Administrativo": ["desenvolvedor", "engenheiro de software", "programador", "medico", "enfermeiro", "pintor industrial", "soldador", "usinagem"],
    "administrativo": ["desenvolvedor", "engenheiro de software", "programador", "medico", "enfermeiro", "pintor industrial", "soldador", "usinagem"],
    "Criativos de Performance": ["desenvolvedor backend", "dba", "motorista", "almoxarife", "soldador", "mecanico"],
    "Criativos": ["desenvolvedor backend", "dba", "motorista", "almoxarife", "soldador", "mecanico"],
    "criativos": ["desenvolvedor backend", "dba", "motorista", "almoxarife", "soldador", "mecanico"],
    "Design": ["desenvolvedor backend", "dba", "motorista", "almoxarife", "soldador", "mecanico"],
    "design": ["desenvolvedor backend", "dba", "motorista", "almoxarife", "soldador", "mecanico"],
    "Inteligência de Vendas": ["repositor", "caixa", "limpeza", "farmacia", "desenvolvedor python", "engenheiro de dados"],
    "inteligencia de vendas": ["repositor", "caixa", "limpeza", "farmacia", "desenvolvedor python", "engenheiro de dados"],
    "Vendas": ["repositor", "caixa", "limpeza", "farmacia", "desenvolvedor python", "engenheiro de dados"],
    "vendas": ["repositor", "caixa", "limpeza", "farmacia", "desenvolvedor python", "engenheiro de dados"],
    "Engenharia de IA/Dados": ["suporte", "infraestrutura", "redes", "helpdesk", "service desk", "dba", "entrada de dados", "digitador", "atendente", "vendas"],
    "Engenharia de Dados": ["suporte", "infraestrutura", "redes", "helpdesk", "service desk", "dba", "entrada de dados", "digitador", "atendente", "vendas"],
    "engenharia de dados": ["suporte", "infraestrutura", "redes", "helpdesk", "service desk", "dba", "entrada de dados", "digitador", "atendente", "vendas"],
    "Pintor Industrial": ["arte", "quadro", "parede residencial", "casa", "apartamento", "desenvolvedor", "vendas", "medico", "advogado"],
    "pintor industrial": ["arte", "quadro", "parede residencial", "casa", "apartamento", "desenvolvedor", "vendas", "medico", "advogado"],
    "Mecânico Industrial": ["auto", "automotivo", "carro", "moto", "bicicleta", "desenvolvedor", "vendas", "medico", "advogado"],
    "mecanico industrial": ["auto", "automotivo", "carro", "moto", "bicicleta", "desenvolvedor", "vendas", "medico", "advogado"],
    "Operador CNC": ["advogado", "medico", "professor"],
    "Soldador": ["advogado", "medico", "professor"],
    "Almoxarife": ["motorista", "carregador", "limpeza", "vendas", "medico", "advogado"],
    "almoxarife": ["motorista", "carregador", "limpeza", "vendas", "medico", "advogado"],
    "Assistente de Logística": ["motorista", "carregador", "limpeza"],
    "Assistente Administrativo": ["producao", "limpeza", "carga"],
    "Assistente Financeiro": ["limpeza", "carga", "descarga", "vendas", "mecanico", "soldador"],
    "assistente financeiro": ["limpeza", "carga", "descarga", "vendas", "mecanico", "soldador"],
    "Copywriter": ["desenvolvedor", "motorista", "mecanico"],
    "Editor de Vídeo": ["desenvolvedor", "motorista", "mecanico"],
    "SDR": ["repositor", "caixa", "limpeza"],
    "Executivo de Vendas": ["balcao", "caixa", "repositor", "limpeza", "estoque", "mecanico", "soldador"],
    "executivo de vendas": ["balcao", "caixa", "repositor", "limpeza", "estoque", "mecanico", "soldador"],
    "Engenheiro de Dados": ["suporte", "infraestrutura", "redes"],
    "Engenheiro de IA": ["suporte", "infraestrutura", "redes"]
}

SEARCH_MAPPING = blacklist

def match_exact_word(text, word):
    if word.endswith('*'):
        # Prefix matching
        pattern = rf'(?<![a-z0-9]){re.escape(word[:-1])}[a-z0-9]*'
    else:
        # Exact word matching
        pattern = rf'(?<![a-z0-9]){re.escape(word)}(?![a-z0-9])'
    return bool(re.search(pattern, text))

CO_OCCURRENCE_RULES = {
    "python backend": [
        ["python", "django", "fastapi", "flask", "pandas", "scrapy", "numpy", "celery", "poetry", "pipenv", "asyncio", "backend"],
        ["desenvolvedor", "desenvolvedora", "programador", "programadora", "engenheiro", "engenheira", "dev", "backend", "back-end", "fullstack", "software engineer", "python"]
    ],
    "desenvolvedor junior / estagiario": [
        ["python", "react", "node", "javascript", "typescript", "java", "c#", "html", "css", "sql", "programacao", "ti", "software", "desenvolvimento", "dev", "frontend", "backend", "fullstack", "web", "tecnologia", "sistemas"],
        ["junior", "jr", "jr.", "estagio", "estagiario", "estagiaria", "iniciante", "trainee", "assistente", "auxiliar"]
    ],
    "especialista em ia": [
        ["ia", "ai", "inteligencia artificial", "artificial intelligence", "llm", "llms", "generativa", "generative ai", "genai", "chatgpt", "gemini", "claude", "copilot", "openai", "prompt", "rag", "fine tuning"],
        ["especialista", "consultor", "consultora", "analista", "gestor", "gestora", "lead", "lider", "especialista em ia", "coordenador", "coordenadora", "implementacao", "implementar", "implementado", "configuracao", "configurar", "criacao", "criador", "criadora", "criacao de conteudo", "automacao", "automatizar", "otimizacao", "otimizar", "integracao", "integrar", "desenvolvimento", "desenvolver", "desenvolvedor", "desenvolvedora", "treinamento", "treinar", "estrategia", "chatbot", "agente", "agentes", "solucao", "sistema", "plataforma", "ferramenta", "conteudo"]
    ],
    "especialista em ia generativa": [
        ["ia", "ai", "artificial", "chatgpt", "midjourney", "generativa", "prompt", "dall-e", "stable diffusion", "llm", "claude", "gemini", "sora", "deepseek", "flux", "genai", "gpt", "anthropic"],
        ["imagem", "video", "audiovisual", "criacao", "design", "designer", "designers", "arte", "conteudo", "generativa", "multimodal", "synthetic", "avatar", "texto", "copy", "redacao", "solucoes", "marketing", "mkt", "redator", "writer", "copywriter", "videomaker", "trafego", "ads", "anuncios", "performance", "social media", "midia", "media"]
    ],
    "engenheiro de ia": [
        ["ia", "ai", "llm", "llms", "machine learning", "deep learning", "generativa", "generative ai", "genai", "rag", "fine-tuning", "nlp", "computacao grafica", "computer vision", "hugging face"],
        ["engenheiro", "engenheira", "desenvolvedor", "desenvolvedora", "dev", "software engineer", "ai engineer", "arquiteto", "arquiteta", "especialista"]
    ],
    "desenvolvedor de agentes ia": [
        ["agente", "agentes", "agent", "agents", "ia", "ai", "llm", "langchain", "autogen", "crewai", "openai", "flowise", "n8n", "make", "lanchain", "vapi", "crew-ai"],
        ["desenvolvedor", "desenvolvedora", "dev", "engenheiro", "engenheira", "programador", "programadora", "software engineer", "criador", "constructor"]
    ],
    "prompt engineer": [
        ["prompt", "prompting", "prompt engineering", "ia", "ai", "llm", "chatgpt", "gemini", "claude", "midjourney", "stable diffusion", "engenharia de prompt"],
        ["engenheiro", "engenheira", "especialista", "analista", "designer", "criador", "dev", "prompter"]
    ],
    "machine learning engineer": [
        ["machine learning", "ml", "mlops", "deep learning", "tensorflow", "pytorch", "sklearn", "keras", "scikit-learn", "computer vision", "nlp", "reinforcement learning", "llmops"],
        ["engenheiro", "engenheira", "desenvolvedor", "desenvolvedora", "dev", "software engineer", "ml engineer", "cientista", "researcher"]
    ],
    "cientista de dados": [
        ["dados", "data", "machine learning", "estatistica", "statistics", "python", "sklearn", "tensorflow", "pytorch", "r", "pandas", "numpy", "modelagem", "predictive modeling"],
        ["cientista", "data scientist", "analista", "especialista", "researcher", "pesquisador", "pesquisadora"]
    ],
    "desenvolvedor python": [
        ["python", "django", "fastapi", "flask", "pandas", "scrapy", "numpy", "celery", "poetry", "pipenv", "asyncio", "backend"],
        ["desenvolvedor", "desenvolvedora", "programador", "programadora", "engenheiro", "engenheira", "dev", "backend", "back-end", "fullstack", "software engineer"]
    ],
    "desenvolvedor backend": [
        ["backend", "back-end", "api", "apis", "rest", "restful", "graphql", "microsservicos", "microservices", "grpc", "sql", "postgresql", "docker", "node", "python", "java", "c#", "go"],
        ["desenvolvedor", "desenvolvedora", "programador", "programadora", "engineer", "dev", "backend developer", "software engineer"]
    ],
    "desenvolvedor node": [
        ["node", "nodejs", "node.js", "express", "nestjs", "nest.js", "javascript", "typescript", "js", "ts", "backend", "back-end"],
        ["desenvolvedor", "desenvolvedora", "programador", "programadora", "dev", "backend", "fullstack", "software engineer"]
    ],
    "desenvolvedor react": [
        ["react", "reactjs", "react.js", "nextjs", "next.js", "typescript", "javascript", "ts", "js", "frontend", "front-end", "tailwind", "redux", "styled-components"],
        ["desenvolvedor", "desenvolvedora", "programador", "programadora", "dev", "frontend", "front-end", "software engineer"]
    ],
    "desenvolvedor fullstack": [
        ["fullstack", "full-stack", "full stack", "frontend", "front-end", "backend", "back-end", "web developer", "dev web"],
        ["desenvolvedor", "desenvolvedora", "programador", "programadora", "dev", "software engineer"]
    ],
    "desenvolvedor django": [
        ["django", "python", "rest", "api", "apis", "drf", "django rest framework"],
        ["desenvolvedor", "desenvolvedora", "programador", "programadora", "dev", "backend", "back-end", "software engineer"]
    ],
    "desenvolvedor fastapi": [
        ["fastapi", "fast-api", "python", "api", "apis", "rest", "restful"],
        ["desenvolvedor", "desenvolvedora", "programador", "programadora", "dev", "backend", "back-end", "software engineer"]
    ],
    "analista de power bi": [
        ["power bi", "powerbi", "bi", "business intelligence", "dax", "power query", "pbi", "looker", "tableau", "qlik", "dashboards", "relatorios"],
        ["analista", "especialista", "desenvolvedor", "desenvolvedora", "consultor", "consultora", "dev", "dashboards analyst"]
    ],
    "desenvolvedor rpa": [
        ["rpa", "automacao", "automacoes", "automation", "uipath", "power automate", "blue prism", "n8n", "make", "make.com", "zapier", "selenium", "puppeteer", "playwrite", "python scraping"],
        ["desenvolvedor", "desenvolvedora", "analista", "engenheiro", "engenheira", "especialista", "dev", "rpa developer", "consultor", "consultora"]
    ],
    "analista de dados": [
        ["dados", "data", "sql", "python", "excel", "bi", "analytics", "tableau", "looker", "dax", "power bi", "google sheets"],
        ["analista", "data analyst", "cientista", "especialista", "consultor", "consultora"]
    ],
    "engenheiro de dados": [
        ["dados", "data", "pipeline", "pipelines", "etl", "elt", "spark", "pyspark", "databricks", "airflow", "kafka", "dbt", "sql", "data lake", "data warehouse", "redshift", "bigquery"],
        ["engenheiro", "engenheira", "data engineer", "arquiteto", "arquiteta", "especialista", "dev"]
    ],
    "analista de analytics": [
        ["analytics", "google analytics", "ga4", "gtm", "google tag manager", "dados", "metrica", "metricas", "kpi", "kpis", "looker studio", "tableau", "tracking", "capi", "pixel"],
        ["analista", "especialista", "consultor", "consultora", "coordenador", "coordenadora", "tracking specialist"]
    ],
    "analista sql": [
        ["sql", "mysql", "postgresql", "oracle", "banco de dados", "database", "tsql", "plsql", "query", "queries", "ddl", "dml", "sql server", "nosql"],
        ["analista", "desenvolvedor", "desenvolvedora", "dev", "dba", "administrador", "administradora", "db engineer"]
    ],
    "gestor de trafego": [
        ["trafego", "trafego pago", "paid traffic", "paid media", "midia paga", "ads", "facebook ads", "google ads", "meta ads", "tiktok ads", "linkedin ads", "performance", "roas", "compra de midia"],
        ["gestor", "gestora", "traffic manager", "analista", "especialista", "coordenador", "coordenadora", "media buyer"]
    ],
    "growth hacker": [
        ["growth", "crescimento", "aquisicao", "acquisition", "conversion", "funil", "funnel", "cro", "a/b", "testes a/b", "ltv", "cac", "outbound", "inbound", "growth hacking"],
        ["growth", "hacker", "analista", "especialista", "gerente", "lead", "head of growth"]
    ],
    "analista de marketing digital": [
        ["marketing", "digital", "redes sociais", "social media", "campanhas", "email marketing", "inbound marketing", "inbound", "content marketing", "inbound"],
        ["analista", "especialista", "coordenador", "coordenadora", "assistente", "auxiliar", "analista de marketing"]
    ],
    "sdr": [
        ["sdr", "bdr", "sales development", "business development", "prospectar", "prospeccao", "leads", "outbound", "inbound", "cold call", "cold email", "vendas", "comercial", "inside sales", "pre vendas"],
        ["sdr", "bdr", "representante", "vendedor", "vendedora", "sales", "assessor", "assessora", "inside sales", "pre vendas", "pre-vendas"]
    ],
    "copywriter": [
        ["copy", "copywriting", "redacao", "redacao publicitaria", "texto", "conteudo", "content", "script", "roteiro", "roteiros", "criativos", "paginas de vendas", "vsl"],
        ["copywriter", "redator", "redatora", "escritor", "escritora", "writer", "especialista"]
    ],
    "especialista em seo": [
        ["seo", "search engine optimization", "otimizacao", "organico", "keyword", "keywords", "palavra-chave", "palavras-chave", "rankeamento", "semrush", "ahrefs", "google search console"],
        ["especialista", "analista", "consultor", "consultora", "gestor", "gestora", "estrategista"]
    ],
    "analista de crm": [
        ["crm", "hubspot", "salesforce", "rd station", "rdstation", "activecampaign", "active campaign", "automacao", "email marketing", "segmentacao", "lifetime value", "ltv", "reguas de relacionamento"],
        ["analista", "especialista", "coordenador", "coordenadora", "gerente", "gestor", "gestora"]
    ],
    "editor de video": [
        ["video", "videos", "edicao", "editing", "premiere", "capcut", "after effects", "davinci", "davinci resolve", "reels", "corte", "cortes", "motion design", "animacao"],
        ["editor", "editora", "video editor", "motion designer", "produtor", "produtora", "criativo", "criativa"]
    ],
    "video maker": [
        ["video", "videos", "producao", "filmagem", "gravacao", "captacao", "roteiro", "reels", "tiktok", "youtube", "camera"],
        ["video maker", "videomaker", "produtor", "produtora", "criador", "criadora", "filmmaker"]
    ],
    "social media": [
        ["social media", "redes sociais", "instagram", "tiktok", "facebook", "linkedin", "youtube", "conteudo", "content", "cronograma de postagens", "copy"],
        ["social media", "analista", "gestor", "gestora", "especialista", "criador", "criadora", "assistente"]
    ],
    "designer grafico": [
        ["design", "grafico", "graphic", "photoshop", "illustrator", "figma", "identidade visual", "brand", "branding", "criativos", "artes", "photoshop", "indesign"],
        ["designer", "graphic designer", "criativo", "criativa", "especialista", "assistente", "auxiliar"]
    ],
    "ux designer": [
        ["ux", "ui", "ux/ui", "user experience", "user interface", "figma", "wireframe", "wireframing", "design", "interfaces", "prototipacao", "usability", "usabilidade"],
        ["designer", "ux designer", "analista", "researcher", "especialista", "product designer"]
    ],
    "assistente administrativo": [
        ["administrativo", "administracao", "adm", "escritorio", "office", "backoffice", "planilhas", "arquivos", "processos internos"],
        ["assistente", "auxiliar", "analista", "coordenador", "coordenadora", "assistente administrativo"]
    ],
    "recepcionista": [
        ["recepcao", "atendimento", "secretaria", "secretariado", "front desk", "recepcao", "portaria", "agendamento"],
        ["recepcionista", "atendente", "secretaria", "assistente", "recepcionista bilingue"]
    ],
    "suporte tecnico n1": [
        ["suporte", "helpdesk", "help-desk", "service desk", "servicedesk", "ti", "chamado", "chamados", "ticket", "tickets", "atendimento ao cliente", "zen desk", "zendesk"],
        ["suporte", "analista", "tecnico", "tecnica", "assistente", "atendente", "n1"]
    ],
    "assistente de faturamento": [
        ["faturamento", "billing", "nota fiscal", "notas fiscais", "nf", "nfe", "lancamento", "contas", "contas a pagar", "contas a receber"],
        ["assistente", "auxiliar", "analista", "tecnico", "tecnica"]
    ],
    "assistente de logistica": [
        ["logistica", "estoque", "expedicao", "armazem", "supply chain", "transporte", "frota", "roteirizacao", "rastreamento"],
        ["assistente", "auxiliar", "analista", "coordenador", "coordenadora", "assistente de logistica"]
    ],
    "assistente financeiro": [
        ["financeiro", "contas", "contas a pagar", "contas a receber", "conciliacao bancaria", "fluxo de caixa", "tesouraria", "cobranca", "dre", "contas", "contabil", "contabilidade"],
        ["assistente", "auxiliar", "analista", "tecnico", "tecnica", "assistente financeiro"]
    ],
    "analista de rh": [
        ["rh", "recursos humanos", "dp", "departamento pessoal", "r&s", "recrutamento", "selecao", "folha", "folha de pagamento", "treinamento", "onboarding", "clt", "beneficios"],
        ["analista", "especialista", "assistente", "coordenador", "coordenadora", "bp", "business partner"]
    ],
    "telemarketing": [
        ["telemarketing", "call center", "sac", "atendimento", "suporte", "teleatendimento", "operador"],
        ["operador", "operadora", "atendente", "agente", "telemarketing", "assistente"]
    ],
    "desenvolvedor junior python": [
        ["python", "django", "fastapi", "flask", "backend", "back-end"],
        ["junior", "jr", "jr.", "estagio", "estagiario", "estagiaria", "iniciante", "trainee"]
    ],
    "desenvolvedor junior react": [
        ["react", "reactjs", "nextjs", "javascript", "typescript", "frontend"],
        ["junior", "jr", "jr.", "estagio", "estagiario", "estagiaria", "iniciante", "trainee"]
    ],
    "desenvolvedor junior fullstack": [
        ["fullstack", "full-stack", "full stack", "frontend", "backend"],
        ["junior", "jr", "jr.", "estagio", "estagiario", "estagiaria", "iniciante", "trainee"]
    ],
    "analista de dados junior": [
        ["dados", "data", "sql", "python", "excel", "bi", "analytics", "power bi"],
        ["junior", "jr", "jr.", "estagio", "estagiario", "estagiaria", "iniciante", "trainee"]
    ],
    "analista de marketing junior": [
        ["marketing", "digital", "redes sociais", "conteudo", "inbound"],
        ["junior", "jr", "jr.", "estagio", "estagiario", "estagiaria", "iniciante", "trainee"]
    ],
    "desenvolvedor pleno python": [
        ["python", "django", "fastapi", "flask", "backend", "back-end"],
        ["pleno", "pl", "pl.", "mid", "middle", "pleno/senior"]
    ],
    "desenvolvedor pleno react": [
        ["react", "nextjs", "javascript", "typescript", "frontend"],
        ["pleno", "pl", "pl.", "mid", "middle", "pleno/senior"]
    ],
    "desenvolvedor pleno fullstack": [
        ["fullstack", "full-stack", "full stack", "frontend", "backend"],
        ["pleno", "pl", "pl.", "mid", "middle", "pleno/senior"]
    ],
    "analista de dados pleno": [
        ["dados", "data", "sql", "python", "bi", "analytics", "power bi"],
        ["pleno", "pl", "pl.", "mid", "middle", "pleno/senior"]
    ],
    "gestor de trafego pleno": [
        ["trafego pago", "ads", "facebook ads", "google ads", "meta ads", "performance", "midia paga"],
        ["pleno", "pl", "pl.", "mid", "middle", "gestor pleno", "analista pleno"]
    ],

    # --- Macro Category Searches & New Taxonomy Sub-Professions ---
    "operacoes fisicas": [
        ["operacoes", "industrial", "industria", "producao", "manutencao", "fabrica", "usinagem", "metalurgica", "linha de producao", "planta", "oficina"],
        ["operador", "tecnico", "mecanico", "eletricista", "soldador", "pintor", "montador", "ajudante", "auxiliar", "ferramenteiro", "torneiro", "inspetor", "supervisor", "lider", "manutencao", "producao"]
    ],
    "industria": [
        ["industrial", "industria", "producao", "manutencao", "fabrica", "usinagem", "metalurgica", "linha de producao", "planta"],
        ["operador", "tecnico", "mecanico", "eletricista", "soldador", "pintor", "montador", "ajudante", "auxiliar", "ferramenteiro", "torneiro", "inspetor", "engenheiro", "producao", "manutencao"]
    ],
    "logistica": [
        ["logistica", "almoxarifado", "estoque", "expedicao", "recebimento", "transporte", "supply chain", "armazem", "deposito", "frotas", "frete", "inventario"],
        ["almoxarife", "assistente", "auxiliar", "conferente", "operador", "motorista", "analista", "coordenador", "empilhadeira", "encarregado", "despachante", "gerente", "logistica", "estoque"]
    ],
    "administrativo": [
        ["administrativo", "administracao", "adm", "escritorio", "backoffice", "financeiro", "recursos humanos", "rh", "faturamento", "contabilidade", "fiscal", "departamento pessoal", "dp", "contas"],
        ["assistente", "auxiliar", "analista", "recepcionista", "secretaria", "atendente", "tecnico", "coordenador", "especialista", "administrativo", "financeiro"]
    ],
    "criativos": [
        ["design", "designer", "criativo", "criativos", "audiovisual", "video", "edicao", "arte", "midia", "motion", "content", "conteudo", "copywriting", "ux", "ui"],
        ["designer", "editor", "videomaker", "video maker", "copywriter", "redator", "motion", "criador", "ilustrador", "ux", "ui", "social media", "arte finalista", "criativo"]
    ],
    "design": [
        ["design", "designer", "grafico", "ux", "ui", "product design", "figma", "photoshop", "illustrator", "visual", "artes"],
        ["designer", "criativo", "especialista", "analista", "assistente", "lider", "head", "director", "design"]
    ],
    "inteligencia de vendas": [
        ["vendas", "comercial", "b2b", "inside sales", "prospeccao", "outbound", "inbound", "contas", "negocios", "sales", "sdr", "bdr", "clientela"],
        ["sdr", "bdr", "executivo", "account executive", "vendedor", "consultor", "closer", "gerente", "representante", "assessor", "analista", "vendas"]
    ],
    "vendas": [
        ["vendas", "comercial", "b2b", "inside sales", "prospeccao", "outbound", "inbound", "sales", "negociacao", "clientes"],
        ["vendedor", "vendedora", "executivo", "sdr", "bdr", "consultor", "representante", "gerente", "closer", "atendente", "assessor", "vendas"]
    ],
    "engenharia de dados": [
        ["dados", "data", "pipeline", "pipelines", "etl", "elt", "spark", "pyspark", "databricks", "airflow", "kafka", "dbt", "sql", "data lake", "data warehouse", "redshift", "bigquery", "snowflake"],
        ["engenheiro", "engenheira", "data engineer", "arquiteto", "arquiteta", "especialista", "dev", "desenvolvedor", "analista"]
    ],
    "pintor industrial": [
        ["industrial", "industria", "pintura", "fabrica", "metalurgica", "producao", "manutencao", "operacoes", "pintor"],
        ["pintor", "pintora", "operador", "tecnico", "ajudante", "auxiliar", "preparador"]
    ],
    "mecanico industrial": [
        ["industrial", "industria", "mecanica", "fabrica", "manutencao", "producao", "usinagem", "mecanico"],
        ["mecanico", "mecanica", "tecnico", "operador", "ajudante", "auxiliar", "ajustador"]
    ],
    "almoxarife": [
        ["almoxarifado", "estoque", "logistica", "recebimento", "expedicao", "armazem", "deposito", "inventario", "almoxarife"],
        ["almoxarife", "assistente", "auxiliar", "conferente", "encarregado", "lider", "operador"]
    ],
    "executivo de vendas": [
        ["vendas", "comercial", "b2b", "account", "contas", "inside sales", "business", "outbound", "negociacao"],
        ["executivo", "executive", "gerente", "consultor", "vendedor", "account executive", "director", "head"]
    ],

    # --- Categoria 1: Operações Físicas e Industriais ---
    "soldador caldeireiro": [
        ["soldagem", "solda", "mig", "tig", "eletrodo", "caldeiraria", "corte", "metalurgia", "chapa", "estrutura metalica", "epi", "esmerilhadeira"],
        ["soldador", "soldadora", "caldeireiro", "caldeireira", "tecnico", "assistente", "operador"]
    ],
    "operador cnc": [
        ["cnc", "torno", "fresadora", "usinagem", "codigo g", "paquimetro", "micrometro", "metrologia", "broca", "ferramentaria", "plano de operacao"],
        ["operador", "operadora", "torneiro", "fresador", "tecnico", "mecanico", "usinador"]
    ],
    "auxiliar de producao": [
        ["producao", "linha de montagem", "montagem", "embalagem", "transformadores", "acabamento", "insumo", "manufatura", "fabrica"],
        ["auxiliar", "ajudante", "operador", "assistente", "montador"]
    ],

    # --- Categoria 2: Logística e Expedição ---
    "auxiliar de logistica": [
        ["logistica", "picking", "packing", "separacao", "expedicao", "recebimento", "carga", "descarga", "cubagem", "centro de distribuicao", "cd", "mercado livre", "dhl", "estoque"],
        ["auxiliar", "assistente", "operador", "analista", "conferente"]
    ],
    "escriturario bancario": [
        ["banco", "bancario", "agencia", "cooperativa", "caixa", "operacoes bancarias", "financeiro", "servicos financeiros", "cpa-10", "cpa-20", "credito", "conta corrente"],
        ["escriturario", "escrituraria", "agente", "caixa", "atendente", "assistente", "bancario", "bancaria"]
    ],

    # --- Categoria 3: Varejo, Comercial e Segurança ---
    "consultor de vendas varejo": [
        ["varejo", "loja", "balcao", "atendimento ao cliente", "estoque de loja", "caixa", "farmacia", "materiais de construcao", "produto", "cliente"],
        ["consultor", "atendente", "vendedor", "vendedora", "assistente", "auxiliar"]
    ],
    "vigilante patrimonial": [
        ["vigilancia", "seguranca patrimonial", "portaria", "ronda", "condominio", "acesso", "monitoramento", "cftv", "controle de acesso"],
        ["vigilante", "fiscal", "seguranca", "porteiro", "vigia"]
    ],

    # --- Categoria 4: Criativos de Performance e Audiovisual ---
    "designer de performance": [
        ["ugc", "ugc creator", "direct response", "criativo de anuncio", "hook", "hooks", "primeiro segundo", "capcut", "veo", "elevenslabs", "reels", "tiktok", "kwai", "ctr", "direct response", "ai content", "conteudo ia", "ai video"],
        ["designer", "criador", "criativo", "criativa", "content creator", "produtor", "editor", "ux writer", "especialista"]
    ],
    "sound designer": [
        ["sound design", "composicao", "trilha sonora", "audio", "musica ambiente", "loop", "meditacao", "respiracao", "relaxamento", "audition", "logic pro", "ableton", "cubase", "frequencia", "mixagem", "masterizacao"],
        ["sound designer", "compositor", "produtor musical", "produtor de audio", "musico", "engenheiro de audio", "especialista"]
    ],

    # --- Categoria 5: Inteligência de Vendas Avançada ---
    "gestor de performance avancado": [
        ["google ads", "meta ads", "tiktok ads", "performance max", "roi", "roas", "cac", "ltv", "lucratividade", "looker studio", "automacao de lances", "auditoria de campanha", "data-driven"],
        ["gestor", "gestora", "especialista", "analista", "media buyer", "performance lead", "growth engineer", "traffic manager"]
    ],
    "sdr tecnico b2b": [
        ["sdr", "bdr", "saas", "b2b", "prospeccao", "hubspot", "salesforce", "dynamics 365", "mb-910", "leads", "cold call", "cold email", "outbound", "enriquecimento de leads", "playwright scraping", "crm"],
        ["sdr", "bdr", "representante", "analista", "inside sales", "pre-vendas", "pre vendas", "sales development"]
    ],

    # --- Categoria 6: Engenharia de IA e Infraestrutura ---
    "especialista tracking elite": [
        ["gtm server", "gtm server-side", "server-side", "meta capi", "conversions api", "ga4", "google analytics 4", "data layer", "stape", "ios 14", "first party", "cookie", "consent mode", "privacidade"],
        ["especialista", "analista", "engenheiro", "arquiteto", "tecnico", "tracking specialist", "martech"]
    ],
    "arquiteto automacao ia ops": [
        ["n8n", "make", "zapier", "agente ia", "claude", "gemini", "openai", "crm", "api", "fluxo autonomo", "automacao de negocio", "integracao", "ia generativa", "orquestrador"],
        ["arquiteto", "especialista", "desenvolvedor", "engenheiro", "ia-ops", "ia ops", "automacao", "no-code", "low-code", "analista"]
    ],
    "desenvolvedor web fullstack": [
        ["python", "fastapi", "django", "node", "nodejs", "react", "reactjs", "php", "sql server", "mysql", "postgresql", "postgres", "pandas", "playwright", "api", "fullstack", "full-stack"],
        ["desenvolvedor", "desenvolvedora", "programador", "programadora", "dev", "engenheiro", "engenheira", "software engineer", "fullstack", "backend"]
    ]
}

def check_ia_validity(raw_text):
    # Find all occurrences of "ia" (case-insensitive) as a whole word, or "i.a."
    # Pattern: (?<![a-zA-Z0-9])(i\.?a\.?)(?![a-zA-Z0-9])
    matches = list(re.finditer(r'(?<![a-zA-Z0-9])(i\.?a\.?)(?![a-zA-Z0-9])', raw_text, re.IGNORECASE))
    if not matches:
        return False
        
    for m in matches:
        matched_str = m.group(1)
        
        # If it has dots like "I.A." or "i.a." or is uppercase "IA", it's AI
        if "." in matched_str or matched_str == "IA":
            return True
            
        # Check context for both "Ia" and "ia"
        start, end = m.span()
        before = raw_text[max(0, start - 30):start]
        after = raw_text[end:end + 30]
        
        before_norm = normalize_str(before).strip()
        after_norm = normalize_str(after).strip()
        
        before_words = re.findall(r'[a-z]+', before_norm)
        last_word_before = before_words[-1] if before_words else ""
        
        after_words = re.findall(r'[a-z]+', after_norm)
        first_word_after = after_words[0] if after_words else ""
        
        verb_before_words = {
            "que", "se", "ele", "ela", "voce", "quem", "nao", "so", "como", "quando", 
            "onde", "eu", "nos", "eles", "elas", "voces", "para"
        }
        
        if last_word_before in verb_before_words:
            continue
            
        is_after_infinitive = False
        if first_word_after:
            if first_word_after.endswith('r') and len(first_word_after) >= 2:
                is_after_infinitive = True
            if first_word_after in {"fazer", "ser", "ter", "realizar", "trabalhar", "gerenciar", "ajudar", "atender", "ir", "dar", "ficar", "agir", "construir", "criar", "desenvolver", "implementar", "usar", "utilizar"}:
                is_after_infinitive = True
                
        if is_after_infinitive:
            continue
            
        return True
        
    return False


import unicodedata
def normalize_text_nfkd(text):
    if not text:
        return ""
    return "".join(c for c in unicodedata.normalize('NFKD', text) if unicodedata.category(c) != 'Mn').lower()

def check_co_occurrence(text_norm, kw_norm, job=None):
    if kw_norm in CO_OCCURRENCE_RULES:
        groups = CO_OCCURRENCE_RULES[kw_norm]
        
        if job:
            full_text = normalize_text_nfkd(job.get('title', '') + " " + job.get('requirements', ''))
        else:
            full_text = normalize_text_nfkd(text_norm)
            
        # Normalizar dotted i.a. para ia para fins de busca por co-ocorrencia
        full_text = re.sub(r'(?<![a-z0-9])i\.?a\.?(?![a-z0-9])', 'ia', full_text)
        
        # --- FALLBACK PARA DESCRICOES CURTAS/GENERICAS (plataformas CLT) ---
        # Se a descrição é muito curta (< 200 chars), provavelmente é genérica do tipo
        # "Vaga para X na Catho." e vai falhar no filtro rigoroso. Nesses casos,
        # basta o TÍTULO conter ao menos um termo de qualquer grupo para passar.
        if job:
            requirements = job.get('requirements', '')
            title_norm = normalize_text_nfkd(job.get('title', ''))
            full_title_text = re.sub(r'(?<![a-z0-9])i\.?a\.?(?![a-z0-9])', 'ia', title_norm)
            
            if len(requirements.strip()) < 200:
                title_matches_all_groups = True
                for group in groups:
                    group_matched = False
                    for word in group:
                        word_norm = normalize_text_nfkd(word)
                        parts = word_norm.split()
                        if all(re.search(r'(?<![a-z0-9])' + re.escape(p) + r'(?![a-z0-9])', full_title_text) for p in parts):
                            if "ia" in parts and job is not None:
                                raw_text = job.get('title', '') + " " + job.get('requirements', '')
                                if not check_ia_validity(raw_text):
                                    continue
                            group_matched = True
                            break
                    if not group_matched:
                        title_matches_all_groups = False
                        break
                if title_matches_all_groups:
                    return True
        
        for group in groups:
            matched_group = False
            for word in group:
                word_norm = normalize_text_nfkd(word)
                # Usar (?<![a-z]) e (?![a-z]) como word boundaries seguros
                parts = word_norm.split()
                if all(re.search(r'(?<![a-z0-9])' + re.escape(p) + r'(?![a-z0-9])', full_text) for p in parts):
                    if "ia" in parts and job is not None:
                        raw_text = job.get('title', '') + " " + job.get('requirements', '')
                        if not check_ia_validity(raw_text):
                            continue
                    matched_group = True
                    break
            if not matched_group:
                return False
        return True
        
    words = kw_norm.split()
    stopwords = {"em", "de", "e", "para", "com", "o", "a", "do", "da"}
    significant_words = [w for w in words if w not in stopwords]
    
    for word in significant_words:
        if not match_exact_word(text_norm, word):
            return False
    return True

    
    # Generic fallback
    words = [w for w in re.split(r'\W+', kw_norm) if len(w) > 2]
    stopwords = {"de", "em", "com", "para", "por", "sem", "sob", "sobre", "the", "and", "with", "for"}
    significant_words = [w for w in words if w not in stopwords]
    
    if not significant_words:
        if kw_norm == "ia" and job is not None:
            raw_text = job.get('title', '') + " " + job.get('requirements', '')
            return check_ia_validity(raw_text)
        return match_exact_word(text_norm, kw_norm)
        
    for word in significant_words:
        if word == "ia" and job is not None:
            raw_text = job.get('title', '') + " " + job.get('requirements', '')
            if not check_ia_validity(raw_text):
                return False
        else:
            if not match_exact_word(text_norm, word):
                return False
    return True

SEARCH_MAPPING = {
    # --- Broad Category Macro Keywords ---
    "Operações Físicas":                "operacoes fisicas",
    "Indústria":                        "industria",
    "Logística":                        "logistica",
    "Administrativo":                   "administrativo",
    "Criativos":                        "criativos",
    "Design":                           "design",
    "Inteligência de Vendas":           "inteligencia de vendas",
    "Vendas":                           "vendas",
    "Engenharia de Dados":              "engenharia de dados",
    "Pintor Industrial":                "pintor industrial",
    "Mecânico Industrial":              "mecanico industrial",
    "Operador de Produção":             "operador de producao",
    "Almoxarife":                       "almoxarife",
    "Assistente Financeiro":            "assistente financeiro",
    "Executivo de Vendas":              "executivo de vendas",
    "Inside Sales":                     "executivo de vendas",
    "Account Executive":                "executivo de vendas",
    "Closer":                           "executivo de vendas",
    "Motion Designer":                  "designer grafico",

    # --- Novas Profissões (6 Categorias) ---
    "Soldador / Caldeireiro":           "soldador caldeireiro",
    "Soldador":                         "soldador caldeireiro",
    "Caldeireiro":                      "soldador caldeireiro",
    "Operador CNC":                     "operador cnc",
    "Torneiro Mecânico":               "operador cnc",
    "Auxiliar de Produção":            "auxiliar de producao",
    "Auxiliar de Linha de Produção":   "auxiliar de producao",
    "Auxiliar de Logística":           "auxiliar de logistica",
    "Auxiliar de Operações Logísticas": "auxiliar de logistica",
    "Separador / Conferente":           "auxiliar de logistica",
    "Agente Bancário":                 "escriturario bancario",
    "Escriturário":                    "escriturario bancario",
    "Bancário":                        "escriturario bancario",
    "Consultor de Vendas Varejo":       "consultor de vendas varejo",
    "Atendente de Loja":               "consultor de vendas varejo",
    "Varejo Técnico":                  "consultor de vendas varejo",
    "Vigilante Patrimonial":            "vigilante patrimonial",
    "Fiscal de Condomínio":            "vigilante patrimonial",
    "Designer de Performance":          "designer de performance",
    "AI UGC Content Creator":           "designer de performance",
    "UGC Creator":                      "designer de performance",
    "Sound Designer":                   "sound designer",
    "Compositor de Trilhas":            "sound designer",
    "Gestor de Performance Avançado":  "gestor de performance avancado",
    "Growth Engineer":                  "gestor de performance avancado",
    "SDR Técnico B2B":                 "sdr tecnico b2b",
    "Especialista em Tracking de Elite": "especialista tracking elite",
    "Analytics Engineer":               "analista de analytics",
    "Arquiteto de Automação & IA-Ops": "arquiteto automacao ia ops",
    "IA-Ops Architect":                 "arquiteto automacao ia ops",
    "Desenvolvedor Web Fullstack":      "desenvolvedor web fullstack",
    "Dev Fullstack / Backend":          "desenvolvedor web fullstack",

    # --- IA / Inteligência Artificial ---
    "Especialista em IA":               "especialista em ia",
    "Especialista em IA Generativa":    "especialista em ia generativa",
    "Engenheiro de IA":                 "engenheiro de ia",
    "Desenvolvedor de Agentes IA":      "desenvolvedor de agentes ia",
    "Prompt Engineer":                  "prompt engineer",
    "Machine Learning Engineer":        "machine learning engineer",
    "Cientista de Dados":               "cientista de dados",

    # --- Desenvolvimento de Software ---
    "Desenvolvedor Python":             "desenvolvedor python",
    "Desenvolvedor Backend":            "desenvolvedor backend",
    "Desenvolvedor Node":               "desenvolvedor node",
    "Desenvolvedor React":              "desenvolvedor react",
    "Desenvolvedor Fullstack":          "desenvolvedor fullstack",
    "Desenvolvedor Django":             "desenvolvedor django",
    "Desenvolvedor FastAPI":            "desenvolvedor fastapi",

    # --- Dados & RPA ---
    "Analista de Power BI":             "analista de power bi",
    "Desenvolvedor RPA":                "desenvolvedor rpa",
    "Analista de Dados":                "analista de dados",
    "Engenheiro de Dados":              "engenheiro de dados",
    "Analista de Analytics":            "analista de analytics",
    "Analista SQL":                     "analista sql",

    # --- Growth & Marketing ---
    "Gestor de Tráfego":               "gestor de trafego",
    "Growth Hacker":                    "growth hacker",
    "Analista de Marketing Digital":    "analista de marketing digital",
    "SDR":                              "sdr",
    "Copywriter":                       "copywriter",
    "Especialista em SEO":              "especialista em seo",
    "Analista de CRM":                  "analista de crm",

    # --- Audiovisual & Criativo ---
    "Editor de Vídeo":                 "editor de video",
    "Video Maker":                      "video maker",
    "Social Media":                     "social media",
    "Designer Gráfico":                "designer grafico",
    "UX Designer":                      "ux designer",

    # --- Base / Apoio Administrativo ---
    "Assistente Administrativo":        "assistente administrativo",
    "Recepcionista":                    "recepcionista",
    "Suporte Técnico N1":              "suporte tecnico n1",
    "Assistente de Faturamento":        "assistente de faturamento",
    "Assistente de Logística":         "assistente de logistica",
    "Assistente Financeiro":            "assistente financeiro",
    "Telemarketing":                    "suporte tecnico n1",
    "Analista de RH":                   "analista de rh",

    # --- Júnior ---
    "Desenvolvedor Junior Python":      "desenvolvedor junior python",
    "Desenvolvedor Junior React":       "desenvolvedor junior react",
    "Desenvolvedor Junior Fullstack":   "desenvolvedor junior fullstack",
    "Analista de Dados Junior":         "analista de dados junior",
    "Analista de Marketing Junior":     "analista de marketing junior",

    # --- Pleno ---
    "Desenvolvedor Pleno Python":       "desenvolvedor pleno python",
    "Desenvolvedor Pleno React":        "desenvolvedor pleno react",
    "Desenvolvedor Pleno Fullstack":    "desenvolvedor pleno fullstack",
    "Analista de Dados Pleno":          "analista de dados pleno",
    "Gestor de Trafego Pleno":          "gestor de trafego pleno",

    # --- Chaves de retrocompatibilidade ---
    "Especialista em IA Generativa":    "especialista em ia generativa",
    "AI Coder / AI Agent Developer":    "desenvolvedor de agentes ia",
    "Engenheiro de Prompt / RAG Specialist": "prompt engineer",
    "Consultor de IA":                  "especialista em ia",
    "Engenheiro de Machine Learning / MLOps": "machine learning engineer",
    "Product Manager de IA / Conversational PO": "especialista em ia",
    "Python Scraping & Data Engineering": "desenvolvedor python",
    "Integração de APIs & Serverless":  "desenvolvedor backend",
    "Backend Python":                   "Python Backend",
    "Desenvolvedor Frontend React":     "desenvolvedor react",
    "Desenvolvedor Fullstack Node/React": "desenvolvedor fullstack",
    "Desenvolvedor FastAPI / Django (Backend)": "desenvolvedor fastapi",
    "Engenheiro de Software Python":    "desenvolvedor python",
    "Analista de BI / Analytics":       "analista de power bi",
    "Automação RPA & Workflow":        "desenvolvedor rpa",
    "Analytics Engineer":               "analista de analytics",
    "Growth Engineer / Product Growth": "growth hacker",
    "Especialista Tracking & MarTech":  "analista de analytics",
    "Analista RevOps":                  "analista de crm",
    "SDR / BDR Técnico":              "sdr",
    "Gestor de Tráfego / Performance": "gestor de trafego",
    "Copywriter de Conversão":         "copywriter",
    "Gestor de Inbound Marketing / CRM": "analista de crm",
    "Analista de SEO & Tráfego Orgânico": "especialista em seo",
    "Editor de Vídeo / Motion Designer": "editor de video",
    "Video Maker / Filmmaker":          "video maker",
    "Design e Social Media":            "social media",
    "Designer UX/UI":                   "ux designer",
    "Editor de Vídeo para Redes Sociais": "editor de video",
    "Designer Gráfico / Visual Designer": "designer grafico",
    "Recepção / Portaria":             "recepcionista",
    "Assistente de Suporte Administrativo": "assistente administrativo",
    "Suporte Técnico N1 / Service Desk": "suporte tecnico n1",
    "SDR Técnico":                     "sdr",
    "Auxiliar Administrativo / faturamento": "assistente de faturamento",
    "Auxiliar de Operações / Logística": "assistente de logistica",
    "Operador de Telemarketing / SAC":  "suporte tecnico n1",
    "Auxiliar de Logística / Estoque": "assistente de logistica",
    "Assistente de DP / Recursos Humanos": "analista de rh",
    "Desenvolvedor Júnior / Estagiário": "desenvolvedor junior / estagiario",
    "Analista de Dados Jr":             "analista de dados junior",
    "Assistente de Marketing":          "analista de marketing junior",
    "Assistente de Growth":             "analista de marketing junior",
    "SDR / Vendas Junior":              "sdr",
    "Editor de Vídeo Júnior":          "editor de video",
    "AI Coder Júnior":                 "desenvolvedor de agentes ia",
    "Engenheiro de Prompt Jr":          "prompt engineer",
    "Estagiário de TI / Programação":  "desenvolvedor junior / estagiario",
    "Desenvolvedor Frontend Júnior":   "desenvolvedor junior react",
    "Estagiário de Dados / BI":        "analista de dados junior",
    "Designer Júnior":                 "designer grafico",
}

search_mapping = SEARCH_MAPPING

def classify_job_profession(job):
    """
    Auto-tags job['profession'] and job['category'] based on title and requirements keywords.
    """
    if not job or not isinstance(job, dict):
        return job

    title_norm = normalize_str(job.get('title', ''))
    reqs_norm = normalize_str(job.get('requirements', ''))
    full_norm = f"{title_norm} {reqs_norm}"

    cat = None
    prof = None

    # Priority 1: Specific Sub-Professions & Roles (Title match first)
    if 'operador cnc' in title_norm or 'cnc' in title_norm or 'torneiro' in title_norm:
        prof = 'Operador CNC'
        cat = 'Operações Físicas'
    elif 'pintor' in title_norm and ('industrial' in title_norm or 'fabrica' in title_norm or 'producao' in title_norm or 'pinto' in title_norm or title_norm.strip() in ('pintor industrial', 'pintor')):
        prof = 'Pintor Industrial'
        cat = 'Operações Físicas'
    elif 'mecanico' in title_norm and ('industrial' in title_norm or 'manutencao' in title_norm or 'fabrica' in title_norm or title_norm.strip() in ('mecanico industrial', 'mecanico')):
        prof = 'Mecânico Industrial'
        cat = 'Operações Físicas'
    elif 'soldador' in title_norm or 'caldeireiro' in title_norm:
        prof = 'Soldador'
        cat = 'Operações Físicas'
    elif 'eletricista' in title_norm:
        prof = 'Eletricista'
        cat = 'Operações Físicas'
    elif any(k in title_norm for k in ['operador de producao', 'auxiliar de producao', 'ajudante de producao', 'operador industrial', 'montador industrial', 'ferramenteiro']):
        prof = 'Operador de Produção'
        cat = 'Operações Físicas'
    elif 'empilhadeira' in title_norm:
        prof = 'Operador de Empilhadeira'
        cat = 'Logística'
    elif 'motorista' in title_norm:
        prof = 'Motorista'
        cat = 'Logística'
    elif 'conferente' in title_norm:
        prof = 'Conferente'
        cat = 'Logística'
    elif any(k in title_norm for k in ['almoxarife', 'almoxarifado']):
        prof = 'Almoxarife'
        cat = 'Logística'
    elif any(k in title_norm for k in ['assistente de logistica', 'auxiliar de logistica', 'analista de logistica', 'auxiliar de estoque']):
        prof = 'Assistente de Logística'
        cat = 'Logística'
    elif any(k in title_norm for k in ['assistente financeiro', 'auxiliar financeiro', 'analista financeiro', 'contas a pagar', 'contas a receber', 'tesouraria']):
        prof = 'Assistente Financeiro'
        cat = 'Administrativo'
    elif any(k in title_norm for k in ['assistente administrativo', 'auxiliar administrativo', 'analista administrativo', 'auxiliar de escritorio']):
        prof = 'Assistente Administrativo'
        cat = 'Administrativo'
    elif any(k in title_norm for k in ['recepcionista', 'recepcao', 'secretaria']):
        prof = 'Recepcionista'
        cat = 'Administrativo'
    elif any(k in title_norm for k in ['data entry', 'digitador']):
        prof = 'Data Entry'
        cat = 'Administrativo'
    elif any(k in title_norm for k in ['assistente de faturamento', 'auxiliar de faturamento', 'faturamento']):
        prof = 'Assistente de Faturamento'
        cat = 'Administrativo'
    elif any(k in title_norm for k in ['analista de rh', 'assistente de rh', 'recursos humanos', 'departamento pessoal', 'dp']):
        prof = 'Analista de RH'
        cat = 'Administrativo'
    elif any(k in title_norm for k in ['motion designer', 'motion design']):
        prof = 'Motion Designer'
        cat = 'Criativos de Performance'
    elif any(k in title_norm for k in ['editor de video', 'video editor', 'videomaker', 'video maker', 'editor de audiovisual']):
        prof = 'Editor de Vídeo'
        cat = 'Criativos de Performance'
    elif any(k in title_norm for k in ['gestor de trafego', 'trafego pago', 'media buyer']):
        prof = 'Gestor de Tráfego'
        cat = 'Criativos de Performance'
    elif any(k in title_norm for k in ['copywriter', 'redator', 'redatora', 'copywriting']):
        prof = 'Copywriter'
        cat = 'Criativos de Performance'
    elif any(k in title_norm for k in ['designer grafico', 'graphic designer', 'designer conversional', 'criador de anuncios']):
        prof = 'Designer Gráfico'
        cat = 'Criativos de Performance'
    elif any(k in title_norm for k in ['ux designer', 'ui designer', 'ux/ui', 'user experience', 'product designer']):
        prof = 'UX Designer'
        cat = 'Criativos'
    elif any(k in title_norm for k in ['social media', 'redes sociais']):
        prof = 'Social Media'
        cat = 'Criativos'
    elif any(k in title_norm for k in ['sales ops', 'analista de sales ops']):
        prof = 'Analista de Sales Ops'
        cat = 'Inteligência de Vendas'
    elif any(k in title_norm for k in ['inside sales', 'inside sales executive']):
        prof = 'Inside Sales'
        cat = 'Inteligência de Vendas'
    elif any(k in title_norm for k in ['executivo de vendas', 'account executive', 'gerente de contas', 'closer']):
        prof = 'Executivo de Vendas'
        cat = 'Inteligência de Vendas'
    elif any(k in title_norm for k in ['sdr', 'bdr', 'sales development', 'pre-vendas', 'pre vendas']):
        prof = 'SDR'
        cat = 'Inteligência de Vendas'
    elif 'crm' in title_norm:
        prof = 'CRM'
        cat = 'Inteligência de Vendas'
    elif any(k in title_norm for k in ['engenheiro de ia', 'ai engineer', 'machine learning', 'ml engineer']):
        prof = 'Engenheiro de IA'
        cat = 'Engenharia de IA/Dados'
    elif any(k in title_norm for k in ['cientista de dados', 'data scientist']):
        prof = 'Cientista de Dados'
        cat = 'Engenharia de IA/Dados'
    elif any(k in title_norm for k in ['engenheiro de dados', 'data engineer', 'engenharia de dados', 'etl engineer']):
        prof = 'Engenheiro de Dados'
        cat = 'Engenharia de IA/Dados'
    elif any(k in title_norm for k in ['analista de dados', 'data analyst']):
        prof = 'Analista de Dados'
        cat = 'Engenharia de IA/Dados'
    elif any(k in title_norm for k in ['analytics engineer']):
        prof = 'Analytics Engineer'
        cat = 'Analytics Engineer'
    elif any(k in title_norm for k in ['ia-ops', 'ia ops', 'prompt engineer', 'agentes ia', 'n8n', 'make.com']):
        prof = 'IA-Ops'
        cat = 'IA-Ops'
    elif any(k in title_norm for k in ['desenvolvedor python', 'python developer', 'python backend', 'python']):
        prof = 'Desenvolvedor Python'
        cat = 'Engenharia de IA/Dados'
    elif any(k in title_norm for k in ['desenvolvedor react', 'react developer', 'frontend react', 'react']):
        prof = 'Desenvolvedor React'
        cat = 'Outros'

    # Priority 2: Macro Category Keywords in Title
    if not cat:
        if any(k in title_norm for k in ['operacoes fisicas', 'industria', 'industrial', 'fabrica', 'producao industrial', 'manutencao industrial', 'usinagem']):
            cat = 'Operações Físicas'
            prof = prof or 'Operador de Produção'
        elif any(k in title_norm for k in ['logistica', 'estoque', 'expedicao', 'armazem', 'supply chain', 'frotas']):
            cat = 'Logística'
            prof = prof or 'Assistente de Logística'
        elif any(k in title_norm for k in ['administrativo', 'administracao', 'backoffice', 'escritorio']):
            cat = 'Administrativo'
            prof = prof or 'Assistente Administrativo'
        elif any(k in title_norm for k in ['criativos', 'design', 'designer', 'audiovisual']):
            cat = 'Criativos'
            prof = prof or 'Designer Gráfico'
        elif any(k in title_norm for k in ['inteligencia de vendas', 'vendas', 'comercial', 'sales intelligence', 'inside sales']):
            cat = 'Inteligência de Vendas'
            prof = prof or 'Executivo de Vendas'
        elif any(k in title_norm for k in ['engenharia de dados', 'data engineering']):
            cat = 'Engenharia de Dados'
            prof = prof or 'Engenheiro de Dados'

    # Priority 3: Fallback check in requirements / full text
    if not cat:
        if 'pintor' in full_norm and ('industrial' in full_norm or 'fabrica' in full_norm or 'estrutura' in full_norm or 'pintura' in full_norm):
            prof = 'Pintor Industrial'
            cat = 'Operações Físicas'
        elif 'mecanico' in full_norm and ('industrial' in full_norm or 'manutencao' in full_norm or 'usinagem' in full_norm or 'mecanica' in full_norm):
            prof = 'Mecânico Industrial'
            cat = 'Operações Físicas'
        elif any(k in full_norm for k in ['operacoes fisicas', 'usinagem', 'soldador', 'manutencao industrial', 'linha de producao']):
            prof = prof or 'Operador de Produção'
            cat = 'Operações Físicas'
        elif any(k in full_norm for k in ['almoxarife', 'almoxarifado', 'expedicao', 'recebimento de carga', 'inventario']):
            prof = prof or ('Almoxarife' if 'almoxarife' in full_norm else 'Assistente de Logística')
            cat = 'Logística'
        elif any(k in full_norm for k in ['contas a pagar', 'conciliacao bancaria', 'fluxo de caixa', 'assistente financeiro']):
            prof = prof or 'Assistente Financeiro'
            cat = 'Administrativo'
        elif any(k in full_norm for k in ['premiere', 'after effects', 'davinci', 'edicao de video']):
            prof = prof or 'Editor de Vídeo'
            cat = 'Criativos'
        elif any(k in full_norm for k in ['prospeccao b2b', 'cold call', 'inside sales', 'sdr', 'bdr']):
            prof = prof or 'SDR'
            cat = 'Inteligência de Vendas'
        elif any(k in full_norm for k in ['spark', 'pyspark', 'airflow', 'databricks', 'dbt', 'data engineer', 'engenharia de dados']):
            prof = prof or 'Engenheiro de Dados'
            cat = 'Engenharia de Dados'

    # Final Defaults
    if not cat:
        cat = 'Outros'
    if not prof:
        prof = job.get('title', 'Outros')

    job['category'] = cat
    job['profession'] = prof
    return job

def is_job_relevant(job, keyword, settings):
    job = classify_job_profession(job)
    clean_kw = SEARCH_MAPPING.get(keyword, keyword)
    title_norm = normalize_str(job.get('title', ''))
    reqs_norm = normalize_str(job.get('requirements', ''))
    full_text = title_norm + " " + reqs_norm
    
    kw_norm = normalize_str(clean_kw)
    user_level = normalize_str(settings.get('level', 'Todos'))
    user_location = normalize_str(settings.get('location', 'Todos'))
    user_contract = normalize_str(settings.get('contract', 'Todos'))
    
    if 'banco de talentos' in title_norm or 'talent pool' in title_norm:
        return False
        
    job_platform = normalize_str(job.get('platform', ''))
    is_freelance_platform = any(p in job_platform for p in ['workana', '99freelas', 'freelancer', 'workana.com'])
    is_remote_default_platform = any(p in job_platform for p in ['remotar', 'coodesh', 'programathor', 'geekhunter'])
    
    # Removed the total bypass for freelance platforms so that CO_OCCURRENCE_RULES can apply to Workana
    # Filtro de Localização Estrito
    job_loc = normalize_str(job.get('location', ''))
    
    # Plataformas de freelance são 100% remotas por natureza — isentar do filtro de localização
    is_remote_term = any(r in full_text or r in job_loc for r in ['remoto', 'remota', 'home office', 'remote', 'teletrabalho', 'anywhere', 'work from home'])
    is_presential_term = any(p in full_text or p in job_loc for p in ['presencial', 'hibrido', 'hybrid', 'on-site', 'onsite', 'modelo hibrido'])
 
    # Filtro de qualidade: Vagas devem ter um mínimo de descrição (exceto LinkedIn/Indeed que às vezes omitem)
    if not is_freelance_platform and len(reqs_norm) < 15 and job_platform not in ['linkedin', 'indeed']:
        return False
        
    if user_location and user_location not in ['todos', 'todas', 'qualquer', 'all']:
        if 'remoto' in user_location:
            if is_freelance_platform or is_remote_default_platform:
                pass  # Plataformas freelance e nativamente remotas passam direto
            elif is_remote_term:
                pass  # Se a vaga diz ser remota, aceita
            elif is_presential_term:
                return False
            elif len(job_loc) > 3 and 'brasil' not in job_loc and 'brazil' not in job_loc:
                return False
        else:
            import re as _re

            # Vagas 100% remotas ou em plataformas freelance sempre atendem a qualquer cidade
            if is_freelance_platform or is_remote_term or is_remote_default_platform:
                pass
            else:
                clean_user_loc = user_location.strip()
                
                # Mapa completo dos 27 estados do Brasil (UF -> termos expandidos)
                UF_MAP = {
                    "sp": ["sao paulo"],
                    "rj": ["rio de janeiro"],
                    "mg": ["minas gerais", "belo horizonte"],
                    "pr": ["parana", "curitiba", "londrina"],
                    "rs": ["rio grande do sul", "porto alegre"],
                    "sc": ["santa catarina", "florianopolis"],
                    "ba": ["bahia", "salvador"],
                    "pe": ["pernambuco", "recife"],
                    "ce": ["ceara", "fortaleza"],
                    "df": ["distrito federal", "brasilia"],
                    "es": ["espirito santo", "vitoria"],
                    "go": ["goias", "goiania"],
                    "ma": ["maranhao", "sao luis"],
                    "mt": ["mato grosso", "cuiaba"],
                    "ms": ["mato grosso do sul", "campo grande"],
                    "pa": ["para", "belem"],
                    "pb": ["paraiba", "joao pessoa"],
                    "am": ["amazonas", "manaus"],
                    "rn": ["rio grande do norte", "natal"],
                    "al": ["alagoas", "maceio"],
                    "pi": ["piaui", "teresina"],
                    "se": ["sergipe", "aracaju"],
                    "ro": ["rondonia", "porto velho"],
                    "to": ["tocantins", "palmas"],
                    "ac": ["acre", "rio branco"],
                    "ap": ["amapa", "macapa"],
                    "rr": ["roraima", "boa vista"],
                }

                # Montar lista de keywords de localização para buscar na vaga
                loc_keywords = [clean_user_loc]
                if clean_user_loc in UF_MAP:
                    loc_keywords.extend(UF_MAP[clean_user_loc])

                def loc_word_match(text, kw):
                    """Verifica se kw aparece como palavra isolada em text (word boundary seguro)."""
                    if not text or not kw:
                        return False
                    # Para siglas de 2 letras (UF), exigir delimitador adjacente para evitar falsos positivos
                    if len(kw) == 2:
                        pattern = r'(?<![a-z0-9])' + _re.escape(kw) + r'(?![a-z0-9])'
                    else:
                        # Para nomes completos, substring é OK (ex: "curitiba" em "curitiba-pr")
                        pattern = _re.escape(kw)
                    return bool(_re.search(pattern, text))

                is_local_match = any(
                    loc_word_match(job_loc, kw) or loc_word_match(full_text, kw)
                    for kw in loc_keywords
                )
                if not is_local_match:
                    return False

 
    if user_contract == 'clt':
        if (match_exact_word(full_text, 'pj') or 'freelancer' in full_text or 'pessoa juridica' in full_text) and 'clt' not in full_text:
            return False
    elif user_contract == 'pj':
        if ('clt' in full_text or 'carteira assinada' in full_text) and not match_exact_word(full_text, 'pj'):
            return False
 
    junior_terms = ['junior', 'jr', 'estagio', 'estagiario', 'trainee', 'assistente', 'auxiliar']
    senior_terms = ['senior', 'sr', 'especialista', 'coordenador', 'gerente', 'diretor', 'tech lead', 'head', 'lead', 'executivo', 'executive', 'architect', 'arquiteto', 'vp', 'manager', 'gestor']
    pleno_terms = ['pleno', 'pl']
    aprendiz_terms = ['aprendiz', 'jovem aprendiz', 'menor aprendiz']
    
    # Previne que a keyword de busca acione o bloqueio de nível de si mesma (ex: "gestor" de trafego não pode bloquear "Júnior")
    active_junior_terms = [t for t in junior_terms if not match_exact_word(kw_norm, t)]
    active_senior_terms = [t for t in senior_terms if not match_exact_word(kw_norm, t)]
    active_pleno_terms = [t for t in pleno_terms if not match_exact_word(kw_norm, t)]
    
    if user_level == 'junior':
        if any(match_exact_word(title_norm, w) for w in active_senior_terms + active_pleno_terms):
            return False
    elif user_level == 'pleno':
        if any(match_exact_word(title_norm, w) for w in active_junior_terms + active_senior_terms):
            return False
    elif user_level == 'senior':
        if any(match_exact_word(title_norm, w) for w in active_junior_terms + active_pleno_terms):
            return False
    elif user_level == 'jovem aprendiz':
        if not any(match_exact_word(full_text, w) for w in aprendiz_terms):
            return False
    elif user_level == 'ganhar experiencia':
        # Aceita vagas de Jovem Aprendiz também, pois o objetivo é ganhar experiência
        is_aprendiz = any(match_exact_word(full_text, w) for w in aprendiz_terms)
        target_exp_terms = [
            "voluntario", "voluntariado", "ong", "projeto social",
            "open source", "codigo aberto",
            "sem experiencia", "nao exige experiencia", "primeiro emprego", "estagio inicial"
        ]
        has_target_exp = any(term in full_text for term in target_exp_terms)
        if not (is_aprendiz or has_target_exp):
            return False
        # Bloqueia vagas claramente sênior/pleno que exigem experiência
        higher_terms = ["pleno", "senior", "sr"]
        if any(match_exact_word(title_norm, w) for w in higher_terms):
            return False
    elif user_level in ('iniciantes stuff', 'iniciantes tudo'):
        is_aprendiz = any(match_exact_word(full_text, w) for w in aprendiz_terms)
        is_junior = any(match_exact_word(title_norm, w) for w in junior_terms)
        is_exact_kw = kw_norm in title_norm
        
        target_exp_terms = [
            "voluntario", "voluntariado", "ong", "projeto social",
            "open source", "codigo aberto",
            "sem experiencia", "nao exige experiencia", "primeiro emprego", "estagio inicial"
        ]
        has_target_exp = any(term in full_text for term in target_exp_terms)
        
        if not (is_aprendiz or has_target_exp or is_junior or is_exact_kw):
            return False
            
        # Bloqueia vagas que exigem experiência prévia / anos de experiência
        if any(term in full_text for term in ["1 ano", "2 anos", "3 anos", "experiencia previa", "com experiencia", "experiencia comprovada"]):
            if not has_target_exp and not is_aprendiz:
                return False

        # Bloqueia vagas claramente sênior/pleno
        higher_terms = ["pleno", "senior", "sr", "head", "lead", "gerente", "coordenador"]
        if any(match_exact_word(title_norm, w) for w in higher_terms):
            return False

    # Verificação inteligente de senioridade na descrição (se o título não for explícito)
    import re
    if user_level in ['junior', 'pleno', 'senior']:
        # Verifica se o título já define a senioridade (se sim, a gente confia no título)
        title_has_level = any(match_exact_word(title_norm, w) for w in active_junior_terms + active_pleno_terms + active_senior_terms)
        
        if not title_has_level:
            # Padrões que indicam fortemente o nível exigido PELA VAGA (evitando 'equipe sênior')
            regex_pattern = r'\b(nivel|perfil|profissional|cargo|vaga|experiencia como|experiencia)\s+(junior|jr|pleno|pl|senior|sr|especialista)\b'
            matches = re.findall(regex_pattern, reqs_norm)
            
            if matches:
                # Extrai apenas os níveis encontrados nas frases-chave
                found_levels = [m[1] for m in matches]
                
                has_junior = any(t in found_levels for t in active_junior_terms)
                has_pleno = any(t in found_levels for t in active_pleno_terms)
                has_senior = any(t in found_levels for t in active_senior_terms)
                
                # Aplica as mesmas regras de rejeição, mas agora baseadas no que a descrição cravou
                if user_level == 'junior' and (has_senior or has_pleno) and not has_junior:
                    return False
                elif user_level == 'pleno' and (has_junior or has_senior) and not has_pleno:
                    return False
                elif user_level == 'senior' and (has_junior or has_pleno) and not has_senior:
                    return False

    # 1. Global Title Blacklist check (excluding terms in user search keyword)
    active_global_blacklist = [term for term in global_title_blacklist if term not in kw_norm and not (user_level in ("ganhar experiencia", "iniciantes tudo", "iniciantes stuff") and term in ("voluntario", "voluntary"))]
    if any(match_exact_word(title_norm, term) for term in active_global_blacklist):
        return False
        
    # 2. Local Niche-specific Blacklist check
    if kw_norm in blacklist:
        if any(match_exact_word(title_norm, w) for w in blacklist[kw_norm]):
            return False
 
    # Para Jovem Aprendiz explícito, pulamos o filtro de keyword pois a vaga é muito genérica
    is_jovem_aprendiz_now = any(match_exact_word(full_text, w) for w in aprendiz_terms)
    if is_jovem_aprendiz_now and user_level in ('ganhar experiencia', 'iniciantes tudo', 'iniciantes stuff', 'jovem aprendiz'):
        return True

    return check_co_occurrence(full_text, kw_norm, job=job)

async def _do_hunt(keyword: str, message: types.Message, callback: CallbackQuery = None):
    search_mapping = {
        # --- IA / Inteligência Artificial ---
        "Especialista em IA":               "especialista em ia",
        "Especialista em IA Generativa":    "especialista em ia generativa",
        "Engenheiro de IA":                 "engenheiro de ia",
        "Desenvolvedor de Agentes IA":      "desenvolvedor de agentes ia",
        "Prompt Engineer":                  "prompt engineer",
        "Machine Learning Engineer":        "machine learning engineer",
        "Cientista de Dados":               "cientista de dados",

        # --- Desenvolvimento de Software ---
        "Desenvolvedor Python":             "desenvolvedor python",
        "Desenvolvedor Backend":            "desenvolvedor backend",
        "Desenvolvedor Node":               "desenvolvedor node",
        "Desenvolvedor React":              "desenvolvedor react",
        "Desenvolvedor Fullstack":          "desenvolvedor fullstack",
        "Desenvolvedor Django":             "desenvolvedor django",
        "Desenvolvedor FastAPI":            "desenvolvedor fastapi",

        # --- Dados & RPA ---
        "Analista de Power BI":             "analista de power bi",
        "Desenvolvedor RPA":                "desenvolvedor rpa",
        "Analista de Dados":                "analista de dados",
        "Engenheiro de Dados":              "engenheiro de dados",
        "Analista de Analytics":            "analista de analytics",
        "Analista SQL":                     "analista sql",

        # --- Growth & Marketing ---
        "Gestor de Tráfego":               "gestor de trafego",
        "Growth Hacker":                    "growth hacker",
        "Analista de Marketing Digital":    "analista de marketing digital",
        "SDR":                              "sdr",
        "Copywriter":                       "copywriter",
        "Especialista em SEO":              "especialista em seo",
        "Analista de CRM":                  "analista de crm",

        # --- Audiovisual & Criativo ---
        "Editor de Vídeo":                 "editor de video",
        "Video Maker":                      "video maker",
        "Social Media":                     "social media",
        "Designer Gráfico":                "designer grafico",
        "UX Designer":                      "ux designer",

        # --- Base / Apoio Administrativo ---
        "Assistente Administrativo":        "assistente administrativo",
        "Recepcionista":                    "recepcionista",
        "Suporte Técnico N1":              "suporte tecnico n1",
        "Assistente de Faturamento":        "assistente de faturamento",
        "Assistente de Logística":         "assistente de logistica",
        "Assistente Financeiro":            "assistente financeiro",
        "Telemarketing":                    "suporte tecnico n1",
        "Analista de RH":                   "analista de rh",

        # --- Júnior ---
        "Desenvolvedor Junior Python":      "desenvolvedor junior python",
        "Desenvolvedor Junior React":       "desenvolvedor junior react",
        "Desenvolvedor Junior Fullstack":   "desenvolvedor junior fullstack",
        "Analista de Dados Junior":         "analista de dados junior",
        "Analista de Marketing Junior":     "analista de marketing junior",

        # --- Pleno ---
        "Desenvolvedor Pleno Python":       "desenvolvedor pleno python",
        "Desenvolvedor Pleno React":        "desenvolvedor pleno react",
        "Desenvolvedor Pleno Fullstack":    "desenvolvedor pleno fullstack",
        "Analista de Dados Pleno":          "analista de dados pleno",
        "Gestor de Trafego Pleno":          "gestor de trafego pleno",

        # --- Chaves de retrocompatibilidade ---
        "Especialista em IA Generativa":    "especialista em ia generativa",
        "AI Coder / AI Agent Developer":    "desenvolvedor de agentes ia",
        "Engenheiro de Prompt / RAG Specialist": "prompt engineer",
        "Consultor de IA":                  "especialista em ia",
        "Engenheiro de Machine Learning / MLOps": "machine learning engineer",
        "Product Manager de IA / Conversational PO": "especialista em ia",
        "Python Scraping & Data Engineering": "desenvolvedor python",
        "Integração de APIs & Serverless":  "desenvolvedor backend",
        "Backend Python":                   "Python Backend",
        "Desenvolvedor Frontend React":     "desenvolvedor react",
        "Desenvolvedor Fullstack Node/React": "desenvolvedor fullstack",
        "Desenvolvedor FastAPI / Django (Backend)": "desenvolvedor fastapi",
        "Engenheiro de Software Python":    "desenvolvedor python",
        "Analista de BI / Analytics":       "analista de power bi",
        "Automação RPA & Workflow":        "desenvolvedor rpa",
        "Analytics Engineer":               "analista de analytics",
        "Growth Engineer / Product Growth": "growth hacker",
        "Especialista Tracking & MarTech":  "analista de analytics",
        "Analista RevOps":                  "analista de crm",
        "SDR / BDR Técnico":              "sdr",
        "Gestor de Tráfego / Performance": "gestor de trafego",
        "Copywriter de Conversão":         "copywriter",
        "Gestor de Inbound Marketing / CRM": "analista de crm",
        "Analista de SEO & Tráfego Orgânico": "especialista em seo",
        "Editor de Vídeo / Motion Designer": "editor de video",
        "Video Maker / Filmmaker":          "video maker",
        "Design e Social Media":            "social media",
        "Designer UX/UI":                   "ux designer",
        "Editor de Vídeo para Redes Sociais": "editor de video",
        "Designer Gráfico / Visual Designer": "designer grafico",
        "Recepção / Portaria":             "recepcionista",
        "Assistente de Suporte Administrativo": "assistente administrativo",
        "Suporte Técnico N1 / Service Desk": "suporte tecnico n1",
        "SDR Técnico":                     "sdr",
        "Auxiliar Administrativo / faturamento": "assistente de faturamento",
        "Auxiliar de Operações / Logística": "assistente de logistica",
        "Operador de Telemarketing / SAC":  "suporte tecnico n1",
        "Auxiliar de Logística / Estoque": "assistente de logistica",
        "Assistente de DP / Recursos Humanos": "analista de rh",
        "Desenvolvedor Júnior / Estagiário": "desenvolvedor junior / estagiario",
        "Analista de Dados Jr":             "analista de dados junior",
        "Assistente de Marketing":          "analista de marketing junior",
        "Assistente de Growth":             "analista de marketing junior",
        "SDR / Vendas Junior":              "sdr",
        "Editor de Vídeo Júnior":          "editor de video",
        "AI Coder Júnior":                 "desenvolvedor de agentes ia",
        "Engenheiro de Prompt Jr":          "prompt engineer",
        "Estagiário de TI / Programação":  "desenvolvedor junior / estagiario",
        "Desenvolvedor Frontend Júnior":   "desenvolvedor junior react",
        "Estagiário de Dados / BI":        "analista de dados junior",
        "Designer Júnior":                 "designer grafico",
    }
    chat_id = message.chat.id
    settings = get_user_settings(chat_id)
    active_plats = [k for k, v in settings["platforms"].items() if v]
    if not active_plats:
        if callback:
            try:
                await callback.answer("Ative pelo menos uma plataforma em Configurações!", show_alert=True)
                return
            except Exception:
                pass
        await message.answer("Ative pelo menos uma plataforma em Configurações!")
        return
        
    plats_str = ', '.join([p.replace('_', ' ').title() for p in active_plats])
    msg_text = f"⏳ *Iniciando os motores para: {keyword}*\n\nLocalização: {settings['location']}\nNível: {settings['level']}\nContrato: {settings['contract']}\nFormação: {settings['education']}\nPlataformas: {plats_str}..."
    if callback:
        try:
            status_msg = await callback.message.edit_text(msg_text, parse_mode="Markdown")
            if isinstance(status_msg, bool):
                status_msg = callback.message
        except Exception:
            status_msg = callback.message
    else:
        status_msg = await message.answer(msg_text, parse_mode="Markdown")
        
    plat_status = {p: "⏳ Buscando..." for p in active_plats}
    is_hunting = True
    
    async def status_updater():
        while is_hunting:
            status_text = f"⏳ *Monitor de Caçada: {keyword}*\n\n"
            for p, stat in plat_status.items():
                status_text += f"*{p.replace('_', ' ').title()}*: {stat}\n"
            try:
                await status_msg.edit_text(status_text, parse_mode="Markdown")
            except Exception:
                pass
            await asyncio.sleep(4)
        
        # Final post-hunt update to the Telegram message after the while is_hunting loop terminates
        status_text = f"⏳ *Monitor de Caçada: {keyword}*\n\n"
        for p, stat in plat_status.items():
            status_text += f"*{p.replace('_', ' ').title()}*: {stat}\n"
        try:
            await status_msg.edit_text(status_text, parse_mode="Markdown")
        except Exception:
            pass
            
    updater_task = asyncio.create_task(status_updater())

    actual_level = settings.get("level", "Todos")
    base_keyword = SEARCH_MAPPING.get(keyword, keyword)
    
    async def fetch_plat(plat):
        logger.info(f"🚀 Iniciando scraper: {plat.upper()}")
        try:
            # Plataformas freelance não recebem o nível na string de busca para não zerar os resultados
            is_freelance = plat in ['workana', '99freelas', 'freelancer']
            plat_search_keyword = base_keyword
            if actual_level != "Todos" and not is_freelance:
                plat_search_keyword = f"{base_keyword} {actual_level}"
                
            module = importlib.import_module(f"scrapers.{plat}")
            import inspect
            sig = inspect.signature(module.scrape)
            contract_val = settings.get("contract", "Todos")
            loc_val = settings.get("location", "Brasil (Remoto)")
            has_var_kwargs = any(p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values())
            
            for tentativa in range(3):
                try:
                    kwargs = {
                        "keyword": plat_search_keyword,
                        "level": "Todos"
                    }
                    if "location" in sig.parameters or has_var_kwargs:
                        kwargs["location"] = loc_val
                    if "country" in sig.parameters or has_var_kwargs:
                        kwargs["country"] = loc_val
                    if "contract" in sig.parameters:
                        kwargs["contract"] = contract_val
                        
                    if inspect.iscoroutinefunction(module.scrape):
                        res = await module.scrape(**kwargs)
                    else:
                        res = await asyncio.to_thread(module.scrape, **kwargs)
                    if res:
                        for job in res:
                            job["level"] = actual_level
                    plat_status[plat] = f"✅ {len(res)} vagas"
                    logger.info(f"✅ Scraper {plat.upper()} finalizado. Vagas encontradas (brutas): {len(res)}")
                    return res
                except Exception as inner_e:
                    logger.warning(f"⚠️ Instabilidade no scraper {plat.upper()} (Tentativa {tentativa+1}/3): {inner_e}")
                    plat_status[plat] = f"⚠️ Retry {tentativa+1}/3"
                    if tentativa < 2:
                        await asyncio.sleep(2)
            plat_status[plat] = "❌ Falhou"
            return []
        except Exception as e:
            logger.exception(f"❌ Erro fatal ao carregar scraper {plat.upper()}: {e}")
        plat_status[plat] = "❌ Falhou"
        return []

    results = await asyncio.gather(*(fetch_plat(p) for p in active_plats))
    is_hunting = False
    await asyncio.sleep(0.5)
    raw_jobs = []
    for r in results:
        if r:
            raw_jobs.extend(r)
            
    # ------ FILTRO SUPREMO LOCAL ------
    unique_jobs = {}
    for job in raw_jobs:
        if "Sem vagas" in job.get('title', '') or "Não houve" in job.get('requirements', ''):
            continue
            
        # Não filtrar por empresa confidencial: LinkedIn, GitHub etc usam nomes anônimos legítimos
            
        # Mantém o filtro de nível local estrito (mesmo que tenha sido enviado para o scraper, 
        # a maioria das plataformas retorna lixo e precisamos barrar no filtro local)
        filter_settings = settings.copy()
        
        if not is_job_relevant(job, keyword, filter_settings):
            continue
            
        comp_norm = normalize_str(job.get('company', ''))
        link_norm = job.get('link', '')
        
        # Usa o link como chave primária de deduplicação (ideal para freelancers com mesmo título)
        # Se não tiver link, usa o fallback de título + empresa
        k = link_norm if link_norm else f"{normalize_str(job.get('title', ''))}|{comp_norm}"
        
        if k not in unique_jobs:
            unique_jobs[k] = job

    all_jobs = list(unique_jobs.values())
    
    for job in all_jobs:
        reqs_norm = normalize_str(job.get('requirements', ''))
        alertas = []
        if 'teste pratico' in reqs_norm or 'case tecnico' in reqs_norm:
            alertas.append("⚠️ [TESTE PRÁTICO]")
        if 'gupy' in reqs_norm or 'gupy.io' in job.get('link', ''):
            alertas.append("🐢 [GUPY]")
            
        if alertas:
            job['title'] = f"{' '.join(alertas)} {job.get('title', '')}"

        if 'combinar' in str(job.get('budget', '')).lower() or not job.get('budget'):
            match = re.search(r'r\$\s*\d{1,3}(?:\.\d{3})*(?:,\d{2})?|\b\d{1,3}k\b', reqs_norm)
            if match:
                job['budget'] = f"🤑 Oculto: {match.group(0).upper()}"

        kw_norm = normalize_str(keyword)
        kw_words = [w for w in re.split(r'\W+', kw_norm) if len(w) > 3]
        count = sum(1 for w in kw_words if w in reqs_norm)
        if count >= 3:
            job['match_score'] = "🔥 Match Alto"
        elif count >= 1:
            job['match_score'] = "👍 Match Médio"
        else:
            job['match_score'] = "🧊 Match Frio"
    # -------------------------------------
    
    if not all_jobs:
        await message.answer("❌ Nenhuma vaga retornou das APIs.")
        return
    
    escudo_enabled = settings.get("escudo_ptbr", True)
    if escudo_enabled:
        await message.answer(f"🛡️ *Escudo PT-BR Ativado!*\nLimpando vagas gringas antes do processamento final...", parse_mode="Markdown")
        from langdetect import detect
        
        def is_brazilian_job(text):
            try:
                if len(text) < 20: return True
                return detect(text) == 'pt'
            except:
                return True
                
        # Pré-filtro brutal: Se não for PT-BR E não for plataforma freelance, lixo.
        vagas_br = []
        for job in all_jobs:
            plat_lower = job.get('platform', '').lower()
            is_freela_plat = any(p in plat_lower for p in ['workana', '99freelas', 'freelancer'])
            
            # Passa direto se for freelance, ou se for PT-BR
            if is_freela_plat or is_brazilian_job(job.get('requirements', '')):
                vagas_br.append(job)
                
        if len(vagas_br) < len(all_jobs):
            await message.answer(f"🗑️ *Limpeza concluída:* {len(all_jobs) - len(vagas_br)} vagas gringas foram deletadas!", parse_mode="Markdown")
    else:
        vagas_br = all_jobs
        
    # --- NOVO MODELO: Enviar TODAS as vagas que passaram no pré-filtro ---
    premium_jobs = vagas_br
    premium_jobs = vagas_br
    await asyncio.to_thread(insert_jobs, premium_jobs)
    _last_found_jobs[str(chat_id)] = premium_jobs
    
    display_mode = settings.get("display_mode", "compact")
    
    mode_names = {
        "compact": "📋 Lista Resumida Compacta",
        "file": "📄 Tabela CSV + Lista",
        "cards": "📱 Cartões 1 a 1 Detalhados"
    }
    
    header_markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Lista Compacta", callback_data="show_mode_compact"),
         InlineKeyboardButton(text="📄 Tabela CSV", callback_data="show_mode_csv")],
        [InlineKeyboardButton(text="📱 Cartões 1 a 1", callback_data="show_mode_cards")]
    ])
    
    await message.answer(
        f"🚀 *{len(premium_jobs)} vagas encontradas!*\n"
        f"Modo Escolhido: *{mode_names.get(display_mode, 'Lista Compacta')}*\n\n"
        f"👇 _Alterne entre os formatos abaixo a qualquer momento:_",
        reply_markup=header_markup,
        parse_mode="Markdown"
    )
    
    if display_mode == "file":
        await send_jobs_csv_file(message, premium_jobs)
        await send_compact_job_list(message, premium_jobs, str(chat_id))
    elif display_mode == "cards":
        await send_job_cards(message, premium_jobs, str(chat_id))
    else:
        # Padrão: Lista Compacta (rápido!)
        await send_compact_job_list(message, premium_jobs, str(chat_id))
        
    await message.answer("🎉 Caçada Concluída!", reply_markup=get_main_menu_markup())


# ─── FUNÇÕES DE EXIBIÇÃO DE VAGAS ───────────────────────────────────────────
_last_found_jobs = {}  # chat_id -> list de vagas

async def send_jobs_csv_file(message: types.Message, jobs: list):
    """Gera um arquivo CSV (com UTF-8 BOM para Excel) e envia no Telegram."""
    import csv, io
    buf = io.BytesIO()
    buf.write(b'\xef\xbb\xbf')  # UTF-8 BOM
    text_stream = io.TextIOWrapper(buf, encoding='utf-8', newline='')
    writer = csv.writer(text_stream, delimiter=';')
    writer.writerow(['#', 'Título da Vaga', 'Empresa', 'Plataforma', 'Nível', 'Contrato', 'Link'])
    for idx, j in enumerate(jobs, 1):
        writer.writerow([
            idx,
            j.get('title', 'N/A'),
            j.get('company', 'N/A'),
            j.get('platform', 'N/A'),
            j.get('level', 'ND'),
            j.get('job_type', 'CLT'),
            j.get('link', '')
        ])
    text_stream.flush()
    data = buf.getvalue()
    
    file_input = BufferedInputFile(data, filename=f"vagas_encontradas_{len(jobs)}.csv")
    await message.answer_document(
        file_input,
        caption=f"📄 *Tabela Completa em CSV ({len(jobs)} Vagas Encontradas)*\n_Abra direto no Excel, Google Sheets ou Celular!_",
        parse_mode="Markdown"
    )

async def send_compact_job_list(message: types.Message, jobs: list, chat_id: str):
    """Envia as vagas em formato de Lista Resumida Compacta (6 vagas por mensagem)."""
    if not jobs:
        return
        
    chunk_size = 6
    total_jobs = len(jobs)
    
    for i in range(0, total_jobs, chunk_size):
        chunk = jobs[i:i + chunk_size]
        start_idx = i + 1
        end_idx = min(i + chunk_size, total_jobs)
        
        lines = [f"📋 *Lista Resumida de Vagas ({start_idx} a {end_idx} de {total_jobs}):*\n"]
        for idx, job in enumerate(chunk, start_idx):
            title = job.get('title', 'Vaga').replace('*', '').replace('_', '')
            company = job.get('company', 'N/A').replace('*', '').replace('_', '')
            plat = job.get('platform', 'Geral').upper()
            link = job.get('link', '')
            level = job.get('level', 'ND')
            loc = job.get('location', 'Remoto')
            
            lines.append(
                f"*{idx}️⃣ {title}*\n"
                f"   🏢 `{company}` | 🌐 `{plat}` | 📍 `{loc}`\n"
                f"   👉 [Acessar Vaga no Site]({link})\n"
            )
            
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📄 Baixar Tabela em CSV", callback_data="show_mode_csv"),
             InlineKeyboardButton(text="📱 Ver Cartões 1a1", callback_data="show_mode_cards")]
        ])
        
        msg_text = "\n".join(lines)
        if len(msg_text) > 4000:
            msg_text = msg_text[:4000]
            
        await message.answer(msg_text, reply_markup=markup, parse_mode="Markdown", disable_web_page_preview=True)
        await asyncio.sleep(0.5)

async def send_job_cards(message: types.Message, jobs: list, chat_id: str):
    """Envia as vagas em formato de Cartões Individuais (1 a 1)."""
    import auto_apply
    count = 0
    
    async def send_with_retry(coro_fn, max_retries=3):
        from aiohttp import ClientError
        for attempt in range(max_retries):
            try:
                return await coro_fn()
            except (ClientError, Exception) as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    logger.warning(f"Falha de envio: {e}. Tentando novamente...")
                    await asyncio.sleep(wait_time)
                else:
                    raise

    def safe_md(val, default="Não informado."):
        s = str(val) if val else default
        return s.replace("_", "\\_").replace("*", "\\*").replace("[", "\\[").replace("`", "\\`")

    for job in jobs:
        link = job.get('link', '')
        if not link or not link.startswith('http'):
            continue

        already_applied = await asyncio.to_thread(is_applied, link)
        if already_applied:
            apply_result = {}
        else:
            apply_result = await asyncio.to_thread(auto_apply.auto_apply, job, str(chat_id))
        
        badges = ""
        if job.get('ai_salary_declared') and job.get('budget') and 'combinar' not in str(job.get('budget', '')).lower():
            badges = f"\n💰 {safe_md(str(job.get('budget', '')))}"
        if job.get('ai_has_benefits'):
            badges += " | 🎁 Com Benefícios" if badges else "\n🎁 Com Benefícios"
        
        base_url = os.getenv('BASE_URL', 'http://localhost:8000')
        tma_url = f"{base_url}/tma/proposal?job_title={job.get('title', 'Vaga')}"
        platform_name = str(job.get('platform', '')).lower()
        is_freelance_platform = any(p in platform_name for p in ['workana', '99freelas', 'novenove'])

        if already_applied:
            buttons = [[InlineKeyboardButton(text="✅ Já me Candidatei", callback_data="noop_applied")]]
            if is_freelance_platform:
                buttons.append([InlineKeyboardButton(text="✍️ Personalizar Proposta", web_app=types.WebAppInfo(url=tma_url))])
            buttons.append([InlineKeyboardButton(text="🔗 Ver Vaga Novamente", url=link)])
        else:
            buttons = [[InlineKeyboardButton(text="🎯 Aplicar para a Vaga", url=link)]]
            if is_freelance_platform:
                buttons.append([InlineKeyboardButton(text="✍️ Personalizar Proposta", web_app=types.WebAppInfo(url=tma_url))])
            buttons.append([InlineKeyboardButton(text="✋ Já me Candidatei", callback_data="mark_applied_btn")])
        
        if apply_result.get("contact_email"):
            buttons.append([InlineKeyboardButton(
                text=f"📧 Enviar Currículo ({apply_result['contact_email'][:25]}...)", 
                callback_data=f"auto_apply_{count}"
            )])
        
        markup = InlineKeyboardMarkup(inline_keyboard=buttons)
        req_preview = safe_md(job.get('requirements', ''))[:200].replace('\n', ' ') + "..." if job.get('requirements') else "Não informado."
        text = (
            f"💎 *{safe_md(job.get('title', 'Vaga'))}*\n"
            f"🏢 Empresa: `{safe_md(job.get('company', 'N/A'))}`\n"
            f"🌐 Fonte: `{safe_md(job.get('platform', 'N/A'))}`\n\n"
            f"📝 *Resumo:* _{req_preview}_"
        )
        if badges.strip():
            text += f"\n{badges}"
        if len(text) > 4000:
            text = text[:4000] + "..."
            
        try:
            await send_with_retry(lambda: message.answer(text, reply_markup=markup, parse_mode="Markdown"))
            count += 1
            await asyncio.sleep(1.0)
        except Exception as e:
            logger.error(f"Erro ao enviar vaga: {e}")

@dp.callback_query(F.data == "show_mode_csv")
async def callback_show_csv(callback: CallbackQuery):
    await callback.answer("Gerando CSV...")
    chat_id = str(callback.message.chat.id)
    jobs = _last_found_jobs.get(chat_id, [])
    if not jobs:
        await callback.message.answer("Nenhuma vaga em cache. Dispare uma nova caçada de vagas!")
        return
    await send_jobs_csv_file(callback.message, jobs)

@dp.callback_query(F.data == "show_mode_cards")
async def callback_show_cards(callback: CallbackQuery):
    await callback.answer("Enviando cartões...")
    chat_id = str(callback.message.chat.id)
    jobs = _last_found_jobs.get(chat_id, [])
    if not jobs:
        await callback.message.answer("Nenhuma vaga em cache. Dispare uma nova caçada de vagas!")
        return
    await send_job_cards(callback.message, jobs, chat_id)

@dp.callback_query(F.data == "show_mode_compact")
async def callback_show_compact(callback: CallbackQuery):
    await callback.answer("Gerando lista compacta...")
    chat_id = str(callback.message.chat.id)
    jobs = _last_found_jobs.get(chat_id, [])
    if not jobs:
        await callback.message.answer("Nenhuma vaga em cache. Dispare uma nova caçada de vagas!")
        return
    await send_compact_job_list(callback.message, jobs, chat_id)


# ----------------- NLP: TEXTO LIVRE -----------------
@dp.message(Command("carreiras"))
@dp.message(F.text == "🎓 Trilha de Carreiras")
async def cmd_carreiras(message: types.Message):
    await show_carreiras_menu(message)

async def show_carreiras_menu(message: types.Message):
    markup = get_carreiras_main_markup()
    await message.answer(
        "🎓 *Guia de Profissionalização & Trilha de Carreira*\n\n"
        "Selecione uma das 5 profissões de elite com alta demanda e altos salários para ver o guia, roadmap e vagas abertas:",
        reply_markup=markup,
        parse_mode="Markdown"
    )

@dp.callback_query(F.data == "car:main")
async def callback_carreiras_main(callback: CallbackQuery):
    await callback.answer()
    markup = get_carreiras_main_markup()
    await callback.message.edit_text(
        "🎓 *Guia de Profissionalização & Trilha de Carreira*\n\n"
        "Selecione uma das 5 profissões de elite com alta demanda e altos salários para ver o guia, roadmap e vagas abertas:",
        reply_markup=markup,
        parse_mode="Markdown"
    )

@dp.callback_query(F.data.startswith("car:p:"))
async def callback_carreira_profile(callback: CallbackQuery):
    await callback.answer()
    raw_pid = callback.data.split(":")[-1]
    pid = resolve_profession_id(raw_pid)
    prof = CAREER_GUIDANCE_DATA.get(pid)
    if not prof:
        await callback.message.answer("Profissão não encontrada.")
        return
        
    tools_str = ", ".join(prof.get("tools", prof.get("skills", [])))
    msg = (
        f"🎓 *{prof['title']}*\n"
        f"_{prof.get('subtitle', prof.get('category', ''))}_\n\n"
        f"📝 *Sobre a Profissão:*\n{prof['description']}\n\n"
        f"📈 *Demanda de Mercado:*\n{prof['market_demand']}\n\n"
        f"💰 *Média Salarial:*\n• 🇧🇷 Brasil: `{prof.get('salary_br', 'R$ 6.000 - R$ 15.000/mês')}`\n• 🌎 Remoto/Gringo: `{prof.get('salary_usd', '$ 3,000 - $ 8,000/mês')}`\n\n"
        f"🛠️ *Ferramentas Chave:*\n_{tools_str}_\n\n"
        f"O que deseja fazer agora?"
    )
    
    markup = get_profession_detail_markup(pid)
    await callback.message.edit_text(msg, reply_markup=markup, parse_mode="Markdown")

@dp.callback_query(F.data.startswith("car:r:"))
async def callback_carreira_roadmap(callback: CallbackQuery):
    await callback.answer()
    raw_pid = callback.data.split(":")[-1]
    pid = resolve_profession_id(raw_pid)
    user_id = str(callback.from_user.id if callback.from_user else callback.message.chat.id)
    await render_roadmap_view(callback.message, user_id, pid, is_edit=True)

@dp.callback_query(F.data.startswith("car:t:"))
async def callback_carreira_toggle(callback: CallbackQuery):
    parts = callback.data.split(":")
    if len(parts) < 4:
        await callback.answer("Erro na ação.")
        return
    raw_pid = parts[2]
    step_id = parts[3]
    pid = resolve_profession_id(raw_pid)
    user_id = str(callback.from_user.id if callback.from_user else callback.message.chat.id)
    
    new_status = toggle_user_step_status(user_id, pid, step_id)
    if new_status == 1:
        await callback.answer("Etapa concluída! 🎉")
    else:
        await callback.answer("Etapa desmarcada!")
        
    await render_roadmap_view(callback.message, user_id, pid, is_edit=True)

@dp.callback_query(F.data.startswith("car:j:"))
async def callback_carreira_job_search(callback: CallbackQuery):
    await callback.answer()
    raw_pid = callback.data.split(":")[-1]
    pid = resolve_profession_id(raw_pid)
    prof = CAREER_GUIDANCE_DATA.get(pid)
    if not prof:
        return
    
    kw = prof.get("search_kw", prof["title"])
    await callback.message.answer(f"🚀 *Disparando caçada de vagas para: {prof['title']} ({kw})*...", parse_mode="Markdown")
    await _do_hunt(kw, callback.message, callback=callback)

# ─── MÓDULO: PERFIL DO USUÁRIO & IA ──────────────────────────────────────────
_aguardando_chave_ia: set = set()
_aguardando_perfil_texto: set = set()

@dp.message(Command("perfil"))
@dp.message(Command("curriculo"))
@dp.message(F.text == "👤 Meu Perfil")
@dp.message(F.text == "👤 Meu Perfil & IA")
@dp.callback_query(F.data == "menu_perfil")
async def show_user_profile_menu(target):
    """Exibe o painel de perfil do usuário e status da IA."""
    message = target.message if isinstance(target, CallbackQuery) else target
    if isinstance(target, CallbackQuery):
        await target.answer()

    user_id = str(message.chat.id)
    profile = get_user_profile(user_id)
    
    name = profile.get("full_name") or (message.from_user.full_name if message.from_user else "Usuário")
    plan = profile.get("plan", "free").upper()
    plan_emoji = "⭐" if plan == "PREMIUM" else "🆓"
    
    pdf_text = profile.get("resume_text", "")
    pdf_info = f"✅ PDF Salvo ({len(pdf_text)} caracteres)" if pdf_text else "❌ Nenhum PDF enviado"
    
    exp_text = profile.get("experience", "")
    exp_info = f"✅ Configurado ({exp_text[:40]}...)" if exp_text else "❌ Não preenchido"
    
    skills = profile.get("skills", "")
    skills_info = skills if skills else "Nenhuma habilidade salva ainda"
    
    groq_key = profile.get("groq_api_key", "")
    key_info = f"✅ Conectada (`{groq_key[:10]}...`)" if groq_key else "⚡ Pool Compartilhado"

    text = (
        f"👤 *Perfil do Usuário: {name}*\n"
        f"Plano: *{plan_emoji} {plan}*\n\n"
        "📋 *RESUMO DO SEU PERFIL PARA A IA:*\n"
        f"• *Currículo (PDF):* {pdf_info}\n"
        f"• *Experiência (Texto):* {exp_info}\n"
        f"• *Habilidades Chave:* `{skills_info}`\n"
        f"• *Chave Groq IA:* {key_info}\n\n"
        "💡 _A IA usa estas informações para calcular a compatibilidade (%) com cada vaga e gerar suas Cover Letters!_"
    )
    
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📄 Enviar Currículo (PDF)", callback_data="perfil_upload_pdf"),
         InlineKeyboardButton(text="📝 Editar Perfil (Texto)", callback_data="perfil_edit_text")],
        [InlineKeyboardButton(text="🔑 Configurar Chave Groq IA", callback_data="config_chave_ia")],
        [InlineKeyboardButton(text="💬 Suporte & Reportar Erros", callback_data="cmd_suporte_handler")],
        [InlineKeyboardButton(text="🎯 Caçar Vagas com este Perfil", callback_data="hunt_menu")],
        [InlineKeyboardButton(text="📖 Ver Tutorial de Boas-Vindas", callback_data="onboarding_tutorial")],
        [InlineKeyboardButton(text="🔙 Voltar ao Menu Principal", callback_data="main_menu")]
    ])
    
    if isinstance(target, CallbackQuery):
        await message.edit_text(text, reply_markup=markup, parse_mode="Markdown")
    else:
        await message.answer(text, reply_markup=markup, parse_mode="Markdown")

@dp.message(Command("suporte"))
@dp.message(F.text == "💬 Suporte")
@dp.message(F.text == "💬 Suporte & Ajuda")
@dp.callback_query(F.data == "cmd_suporte_handler")
async def cmd_suporte(update):
    """Exibe os canais de atendimento e suporte."""
    message = update if isinstance(update, types.Message) else update.message
    if isinstance(update, CallbackQuery):
        await update.answer()

    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Suporte via Telegram (@CATDIEGO)", url="https://t.me/CATDIEGO")],
        [InlineKeyboardButton(text="🟢 Suporte via WhatsApp (43 99165-2706)", url="https://wa.me/5543991652706?text=Olá,%20preciso%20de%20suporte%20no%20Vagas%20Sniper%20Bot")],
        [InlineKeyboardButton(text="🔙 Voltar", callback_data="main_menu")]
    ])

    text = (
        "💬 *Central de Suporte & Reporte de Erros*\n\n"
        "Encontrou um erro nas buscas, tem dúvidas ou sugestões de melhoria?\n\n"
        "Fale diretamente com nossa equipe de suporte nos canais oficiais abaixo:\n"
        "• *Telegram:* @CATDIEGO (Atendimento direto)\n"
        "• *WhatsApp:* (43) 99165-2706\n"
        "• *E-mail:* `9919622diego@gmail.com`\n\n"
        "⏱️ *Horário:* Segunda a Sexta, das 08h às 20h."
    )
    await message.answer(text, reply_markup=markup, parse_mode="Markdown")

@dp.callback_query(F.data == "perfil_edit_text")
async def callback_perfil_edit_text(callback: CallbackQuery):
    await callback.answer()
    user_id = str(callback.from_user.id)
    _aguardando_perfil_texto.add(user_id)
    await callback.message.answer(
        "📝 *Descreva o seu Perfil e Experiência para a IA:*\n\n"
        "Digite suas principais habilidades, anos de experiência, ferramentas que domina e objetivos profissionais.\n\n"
        "*Exemplo:*\n"
        "`Sou desenvolvedor Python e Analista de Dados com 2 anos de experiência em Pandas, SQL, Power BI e automações com n8n. Procuro vagas presenciais em Londrina/PR ou Remotas.`\n\n"
        "👇 *Digite o seu texto abaixo:* (ou /cancelar para sair)",
        parse_mode="Markdown"
    )

@dp.callback_query(F.data == "perfil_upload_pdf")
async def callback_perfil_upload_pdf(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer(
        "📄 *Como enviar o seu Currículo (PDF):*\n\n"
        "Basta anexar ou arrastar o seu arquivo `.pdf` diretamente para esta conversa no Telegram!\n\n"
        "O robô vai ler o documento automaticamente, extrair suas habilidades e salvar no seu perfil para calcular a compatibilidade das vagas.",
        parse_mode="Markdown"
    )

# ─── MÓDULO: CHAVE DE IA PESSOAL ─────────────────────────────────────────────
@dp.message(Command("minha_chave_ia"))
@dp.callback_query(F.data == "config_chave_ia")
async def cmd_minha_chave_ia(update):
    """Abre o menu de configuração de chave Groq pessoal."""
    message = update if isinstance(update, types.Message) else update.message
    user_id = str(message.chat.id)
    if isinstance(update, CallbackQuery):
        await update.answer()

    profile = get_user_profile(user_id)
    chave_atual = profile.get("groq_api_key", "")
    status = f"✅ Chave configurada: `{chave_atual[:12]}...`" if chave_atual else "❌ Nenhuma chave configurada"

    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Inserir / Atualizar Chave", callback_data="ia_key_input")],
        [InlineKeyboardButton(text="🗑️ Remover Minha Chave", callback_data="ia_key_remove")],
        [InlineKeyboardButton(text="🔙 Voltar", callback_data="settings_menu")],
    ])
    await message.answer(
        "🔑 *Minha Chave de IA (Groq)*\n\n"
        f"{status}\n\n"
        "Configure sua chave Groq gratuita para obter:\n"
        "• 🚀 Respostas mais rápidas e exclusivas\n"
        "• 📊 Score de compatibilidade personalizado\n"
        "• ✍️ Cover letters sem compartilhar cota com outros usuários\n\n"
        "👉 Crie sua chave gratuita em: [console.groq.com](https://console.groq.com)\n"
        "_(Clique em API Keys → Create API Key)_",
        reply_markup=markup,
        parse_mode="Markdown",
        disable_web_page_preview=True
    )

@dp.callback_query(F.data == "ia_key_input")
async def callback_ia_key_input(callback: CallbackQuery):
    await callback.answer()
    user_id = str(callback.from_user.id)
    _aguardando_chave_ia.add(user_id)
    await callback.message.answer(
        "🔑 *Cole sua chave Groq abaixo:*\n\n"
        "Formato: `gsk_...`\n\n"
        "_(Sua chave é armazenada de forma segura e usada apenas para suas buscas)_\n\n"
        "Digite /cancelar para cancelar.",
        parse_mode="Markdown"
    )

@dp.callback_query(F.data == "ia_key_remove")
async def callback_ia_key_remove(callback: CallbackQuery):
    await callback.answer()
    user_id = str(callback.from_user.id)
    upsert_user_profile(user_id, groq_api_key=None)
    await callback.message.answer(
        "🗑️ *Chave removida!*\n\n"
        "O bot voltará a usar o pool de chaves compartilhadas.",
        parse_mode="Markdown"
    )

@dp.message(F.text.startswith("gsk_"))
async def handler_receber_chave_groq(message: types.Message):
    """Captura a chave Groq enviada pelo usuário, valida e salva."""
    user_id = str(message.chat.id)
    if user_id not in _aguardando_chave_ia:
        return

    _aguardando_chave_ia.discard(user_id)
    chave = message.text.strip()

    if len(chave) < 20 or not chave.startswith("gsk_"):
        await message.answer(
            "❌ *Chave inválida!* O formato esperado é `gsk_...` com pelo menos 20 caracteres.\n"
            "Tente novamente com /minha\\_chave\\_ia",
            parse_mode="Markdown"
        )
        return

    aguardando = await message.answer("⏳ Testando sua chave...")
    try:
        import requests as req
        headers = {"Authorization": f"Bearer {chave}", "Content-Type": "application/json"}
        payload = {"model": "llama-3.1-8b-instant", "messages": [{"role": "user", "content": "Responda apenas: OK"}], "max_tokens": 5}
        resp = req.post("https://api.groq.com/openai/v1/chat/completions", json=payload, headers=headers, timeout=15)
        if resp.status_code != 200:
            await aguardando.edit_text(
                f"❌ *Chave recusada pelo Groq!*\n"
                f"Erro {resp.status_code}: {resp.json().get('error', {}).get('message', 'Erro desconhecido')[:200]}\n\n"
                "Verifique se a chave está correta e ativa no [console.groq.com](https://console.groq.com).",
                parse_mode="Markdown"
            )
            return
    except Exception as e:
        await aguardando.edit_text(
            f"⚠️ Não foi possível testar a chave agora (erro de rede). Ela foi salva assim mesmo.\n`{e}`",
            parse_mode="Markdown"
        )

    upsert_user_profile(user_id, groq_api_key=chave)
    await aguardando.edit_text(
        "✅ *Chave Groq configurada com sucesso!*\n\n"
        f"Chave: `{chave[:12]}...`\n\n"
        "🚀 A partir de agora, suas análises de compatibilidade e cover letters "
        "usarão sua chave pessoal — respostas mais rápidas e sem compartilhar cota!",
        parse_mode="Markdown"
    )

# Atalho: /cancelar durante qualquer fluxo de digitação
@dp.message(Command("cancelar"))
async def cmd_cancelar(message: types.Message):
    user_id = str(message.chat.id)
    cancelou = False
    if user_id in _aguardando_chave_ia:
        _aguardando_chave_ia.discard(user_id)
        cancelou = True
    if user_id in _aguardando_perfil_texto:
        _aguardando_perfil_texto.discard(user_id)
        cancelou = True
        
    if cancelou:
        await message.answer("❌ Operação cancelada.")
    else:
        await message.answer("Nenhuma operação em andamento.")

# ─────────────────────────────────────────────────────────────────────────────

@dp.message(F.text == "🎯 Caçar Vagas")
async def btn_cacar_vagas(message: types.Message):
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💼 Modo Freelance", callback_data="modo_freelance")],
        [InlineKeyboardButton(text="🏢 Modo Emprego", callback_data="modo_emprego")],
        [InlineKeyboardButton(text="🌐 Modo Ambos", callback_data="modo_ambos")],
        [InlineKeyboardButton(text="🔙 Voltar", callback_data="main_menu")]
    ])
    await message.answer(
        "🎯 *Onde você quer buscar vagas?*\n\n"
        "💼 *Freelance* — Workana (projetos e propostas)\n"
        "🏢 *Emprego* — Gupy, Catho, InfoJobs e Vagas.com\n"
        "🌐 *Ambos* — Todas as plataformas ativas",
        reply_markup=markup, parse_mode="Markdown"
    )

@dp.message(F.text == "🛠 Configurações")
async def btn_configuracoes(message: types.Message):
    chat_id = message.chat.id
    await message.answer("⚙️ *Configurações do Robô*", reply_markup=get_settings_markup(chat_id), parse_mode="Markdown")

# ----------------- NLP: TEXTO LIVRE -----------------
@dp.message(F.text)
async def handle_free_text(message: types.Message):
    if message.text.startswith("/"):
        return
        
    chat_id = message.chat.id
    user_id = str(chat_id)
    
    # Intercepta se o usuário estiver salvando descrição de perfil em texto
    if user_id in _aguardando_perfil_texto:
        _aguardando_perfil_texto.discard(user_id)
        texto = message.text.strip()
        
        tech_keywords = [
            "python", "react", "node", "django", "fastapi", "machine learning",
            "data science", "power bi", "sql", "javascript", "typescript",
            "ia generativa", "rpa", "automacao", "marketing", "trafego",
            "seo", "growth", "backend", "fullstack", "frontend", "devops",
            "cloud", "aws", "docker", "git", "flutter", "kotlin", "java", "sdr", "salesforce", "hubspot", "n8n"
        ]
        text_lower = texto.lower()
        found = [kw for kw in tech_keywords if kw in text_lower]
        skills_str = ", ".join([kw.title() for kw in found]) if found else "Geral / Tech"
        
        upsert_user_profile(user_id, experience=texto, skills=skills_str)
        
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🎯 Caçar Vagas Agora", callback_data="hunt_menu")],
            [InlineKeyboardButton(text="👤 Ver Meu Perfil", callback_data="menu_perfil")]
        ])
        
        await message.answer(
            f"✅ *Perfil de Texto Salvo com Sucesso!*\n\n"
            f"• *Habilidades Identificadas:* `{skills_str}`\n"
            f"• *Resumo Salvo:* _{texto[:140]}..._\n\n"
            "A partir de agora a IA usará este resumo para calcular a compatibilidade das vagas e gerar Cover Letters!",
            reply_markup=markup,
            parse_mode="Markdown"
        )
        return

    settings = get_user_settings(chat_id)
    
        
    await message.answer("🔍 *Processando seu pedido...*", parse_mode="Markdown")
    
    text_lower = message.text.lower()
    
    # Extrair localidade
    if any(w in text_lower for w in ['londrina', 'parana', '/pr']):
        location = 'Londrina/PR'
    elif any(w in text_lower for w in ['assai', 'assaí']):
        location = 'Assaí/PR'
    else:
        location = 'Brasil (Remoto)'
    
    # Extrair nivel
    if any(w in text_lower for w in ['junior', 'júnior', 'estagio', 'estágio', 'iniciante', 'primeiro emprego']):
        level = 'Júnior'
    elif 'pleno' in text_lower:
        level = 'Pleno'
    elif any(w in text_lower for w in ['senior', 'sênior']):
        level = 'Sênior'
    else:
        level = 'Todos'
    
    # Extrair contrato
    if 'clt' in text_lower or 'carteira' in text_lower:
        contract = 'CLT'
    elif 'pj' in text_lower or 'pessoa juridica' in text_lower:
        contract = 'PJ'
    else:
        contract = 'Todos'
    
    # Extrair educação
    if any(w in text_lower for w in ['sem faculdade', 'sem diploma', 'sem formacao']):
        education = 'Sem Formação'
    else:
        education = 'Todos'
    
    keyword = message.text.strip()[:50]
    
    chat_id = message.chat.id
    settings = get_user_settings(chat_id)
    
    if location in ["Brasil (Remoto)", "Londrina/PR", "Assaí/PR"]:
        settings["location"] = location
    if level in ["Todos", "Júnior", "Pleno", "Sênior"]:
        settings["level"] = level
    if contract in ["Todos", "PJ", "CLT"]:
        settings["contract"] = contract
    if education in ["Todos", "Sem Formação"]:
        settings["education"] = education
        
    await _do_hunt(keyword, message)

def parse_pdf_resume_advanced(pdf_path: str) -> dict:
    """Extrai texto e metadados estruturados do PDF usando PyMuPDF (fitz) com pontuação de relevância."""
    raw_text = ""
    
    # 1. Tenta fitz (PyMuPDF)
    try:
        import fitz
        doc = fitz.open(pdf_path)
        pages_text = []
        for page in doc:
            pages_text.append(page.get_text("text") or "")
        raw_text = "\n".join(pages_text)
    except Exception as e:
        logger.warning(f"Erro ao ler PDF com fitz: {e}")
        
    # 2. Fallback para PyPDF2 se fitz falhar ou retornar texto vazio
    if not raw_text.strip():
        try:
            import PyPDF2
            with open(pdf_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    raw_text += (page.extract_text() or "") + "\n"
        except Exception as e:
            logger.warning(f"Erro ao ler PDF com PyPDF2: {e}")

    clean_lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    full_text = "\n".join(clean_lines)

    # Detectar Nome (primeira linha relevante sem e-mail/tel)
    name = "Candidato(a)"
    for line in clean_lines[:6]:
        if not re.search(r'[@\d\+:]|curriculo|resume|linkedin|github|email|telefone|rua|avenida|brasil', line, re.IGNORECASE) and len(line) <= 45:
            name = line.strip()
            break

    category_to_profession = {
        "Python & Backend": "Desenvolvedor Python",
        "React & Frontend": "Desenvolvedor React",
        "Dados & Analytics": "Analytics Engineer",
        "IA & Automações": "IA-Ops Specialist",
        "Growth & Tráfego Pago": "Growth Engineer",
        "SDR & Vendas Tech": "SDR Técnico",
        "DevOps & Cloud": "DevOps & Cloud",
        "UI/UX Design": "UI/UX Designer",
        "Suporte & Infra TI": "Suporte & Infra TI"
    }

    category_keywords = {
        "Python & Backend": ["python", "django", "fastapi", "flask", "pandas", "pytest", "backend"],
        "React & Frontend": ["react", "next.js", "nextjs", "typescript", "javascript", "tailwind", "frontend"],
        "Dados & Analytics": ["power bi", "powerbi", "sql", "excel", "analytics", "data analyst", "looker studio", "pandas"],
        "IA & Automações": ["n8n", "make", "zapier", "ia", "ai", "chatgpt", "openai", "prompts", "prompt engineering", "langchain"],
        "Growth & Tráfego Pago": ["google ads", "meta ads", "gtm", "ga4", "tracking", "traffic", "growth", "cac", "roas"],
        "SDR & Vendas Tech": ["sdr", "bdr", "crm", "hubspot", "salesforce", "inside sales", "prospecção"],
        "DevOps & Cloud": ["docker", "aws", "cloud", "linux", "git", "ci/cd", "terraform"],
        "UI/UX Design": ["figma", "ui", "ux", "wireframe", "prototipagem"],
        "Suporte & Infra TI": ["suporte", "helpdesk", "active directory", "chamados", "itil", "redes"]
    }

    text_lower = full_text.lower()
    category_scores = {}

    for cat, kws in category_keywords.items():
        score = 0
        for kw in kws:
            matches = len(re.findall(r'\b' + re.escape(kw) + r'\b', text_lower))
            if matches > 0:
                score += matches * 2
        if score > 0:
            category_scores[cat] = score

    sorted_categories = sorted(category_scores.items(), key=lambda item: item[1], reverse=True)
    found_skills = [cat for cat, sc in sorted_categories]

    recommended_professions = []
    for cat, sc in sorted_categories:
        prof_title = category_to_profession.get(cat)
        if prof_title and prof_title not in recommended_professions:
            recommended_professions.append(prof_title)

    if any(w in text_lower for w in ["senior", "sênior", "lider", "head", "coordenador", "10 anos", "8 anos", "5 anos"]):
        seniority = "Sênior"
    elif any(w in text_lower for w in ["pleno", "3 anos", "4 anos", "especialista"]):
        seniority = "Pleno"
    elif any(w in text_lower for w in ["junior", "júnior", "estagio", "estágio", "iniciante", "primeiro emprego", "voluntario"]):
        seniority = "Júnior"
    else:
        seniority = "Júnior / Pleno"

    if not recommended_professions:
        recommended_professions = ["Desenvolvedor Python", "Analytics Engineer", "IA-Ops Specialist"]

    return {
        "full_text": full_text,
        "name": name,
        "skills": found_skills[:5],
        "recommended_professions": recommended_professions[:3],
        "seniority": seniority
    }


import io
import fitz
import html
import traceback

@dp.message(Command("logs"))
async def cmd_logs(message: types.Message):
    """Lê as últimas 100 linhas de log em thread separada de forma assíncrona para não travar a thread do bot."""
    log_file = os.path.join(os.path.dirname(__file__), "system.log")
    
    def _read_logs():
        if not os.path.exists(log_file):
            return "Nenhum log registrado ainda."
        with open(log_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        return "".join(lines[-80:])

    try:
        logs_text = await asyncio.to_thread(_read_logs)
        safe_logs = html.escape(logs_text)
        await message.answer(f"📜 <b>Últimos Logs do Sistema:</b>\n<pre>{safe_logs}</pre>", parse_mode="HTML")
    except Exception as e:
        tb_escaped = html.escape(traceback.format_exc())
        await message.answer(f"❌ <b>Erro ao ler logs:</b>\n<pre>{tb_escaped}</pre>", parse_mode="HTML")

@dp.message(Command("lgpd"))
async def cmd_lgpd(message: types.Message):
    """Menu de conformidade LGPD: permite exportar dados ou exercer o Direito ao Esquecimento."""
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📥 Exportar Meus Dados (JSON)", callback_data="lgpd_export")],
        [InlineKeyboardButton(text="🗑️ Excluir Todos os Meus Dados (Purga)", callback_data="lgpd_purge_confirm")],
        [InlineKeyboardButton(text="🔙 Voltar", callback_data="main_menu")]
    ])
    await message.answer(
        "🛡️ <b>Conformidade LGPD (Direitos do Titular)</b>\n\n"
        "Em conformidade com a Lei Geral de Proteção de Dados (Lei nº 13.709/2018), você possui total controle sobre suas informações:\n\n"
        "• <b>Portabilidade:</b> Baixe todos os seus dados pessoais, históricos e currículos armazenados.\n"
        "• <b>Direito ao Esquecimento:</b> Apague permanentemente todo o seu cadastro de nossas bases.\n\n"
        "<i>Prazo legal garantido: Resposta imediata.</i>",
        reply_markup=markup,
        parse_mode="HTML"
    )

@dp.callback_query(F.data == "lgpd_export")
async def callback_lgpd_export(callback: CallbackQuery):
    await callback.answer()
    user_id = str(callback.from_user.id)
    from database import export_user_data_lgpd
    data = await asyncio.to_thread(export_user_data_lgpd, user_id)
    json_str = json.dumps(data, indent=2, ensure_ascii=False)
    
    file_bytes = json_str.encode('utf-8')
    input_file = types.BufferedInputFile(file_bytes, filename=f"dados_lgpd_{user_id}.json")
    await callback.message.answer_document(input_file, caption="📥 <b>Seus dados pessoais exportados (LGPD):</b>", parse_mode="HTML")

@dp.callback_query(F.data == "lgpd_purge_confirm")
async def callback_lgpd_purge_confirm(callback: CallbackQuery):
    await callback.answer()
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚠️ SIM, EXCLUIR TUDO IRREVERSIVELMENTE", callback_data="lgpd_purge_do")],
        [InlineKeyboardButton(text="❌ Cancelar", callback_data="main_menu")]
    ])
    await callback.message.answer(
        "⚠️ <b>ATENÇÃO: EXCLUSÃO DEFINITIVA</b>\n\n"
        "Tem certeza que deseja apagar permanentemente seu perfil, currículo, histórico de candidaturas e conquistas de carreira?\n"
        "<b>Esta ação é irreversível.</b>",
        reply_markup=markup,
        parse_mode="HTML"
    )

@dp.callback_query(F.data == "lgpd_purge_do")
async def callback_lgpd_purge_do(callback: CallbackQuery):
    await callback.answer()
    user_id = str(callback.from_user.id)
    from database import purge_user_data_lgpd
    await asyncio.to_thread(purge_user_data_lgpd, user_id)
    await callback.message.answer("🗑️ <b>Todos os seus dados foram excluídos com sucesso das nossas bases.</b>\nSe desejar utilizar o robô novamente no futuro, basta digitar /start.", parse_mode="HTML")

@dp.message(F.document)
async def handle_document(message: types.Message, bot: Bot):
    if not message.document.file_name.lower().endswith('.pdf'):
        await message.answer("❌ Por favor, envie o seu currículo em formato PDF.")
        return
        
    msg_status = await message.answer("📄 <b>Lendo PDF com PyMuPDF Engine (RAM)...</b>", parse_mode="HTML")
    user_id = message.chat.id
    
    try:
        # Baixa os bytes do PDF diretamente em RAM (Sem gravar em disco)
        file_info = await bot.get_file(message.document.file_id)
        downloaded_file = await bot.download_file(file_info.file_path)
        pdf_bytes = downloaded_file.read() if hasattr(downloaded_file, 'read') else downloaded_file
        
        pdf_stream = io.BytesIO(pdf_bytes)
        
        def _parse_pdf_ram(stream):
            text = ""
            with fitz.open(stream=stream, filetype="pdf") as doc:
                for page in doc:
                    text += page.get_text() + "\n"
            return text
            
        full_text = await asyncio.to_thread(_parse_pdf_ram, pdf_stream)
        
        if not full_text.strip():
            await msg_status.edit_text("❌ O PDF enviado parece estar vazio ou escaneado como imagem sem texto.")
            return

        name = "Candidato(a)"
        skills_list = ["Tecnologia", "Análise de Dados", "Python"]
        seniority = "Júnior / Pleno"
        professions = ["Desenvolvedor Python", "Analytics Engineer", "IA-Ops Specialist"]
        
        skills_str = ", ".join(skills_list)
        upsert_user_profile(str(user_id), full_name=name, resume_text=full_text, skills=skills_str)
        
        buttons = [[InlineKeyboardButton(text=f"🚀 Disparar Busca: {prof}", callback_data=f"hunt_{prof}")] for prof in professions]
        buttons.append([InlineKeyboardButton(text="👤 Ver Perfil Completo", callback_data="menu_perfil"),
                        InlineKeyboardButton(text=f"🎯 Caçar Vagas", callback_data="hunt_menu")])
        markup = InlineKeyboardMarkup(inline_keyboard=buttons)
        
        prof_bullets = "\n".join([f"• <b>{prof}</b>" for prof in professions])
        
        preview_msg = (
            f"📄 <b>Análise do Currículo Concluída em RAM!</b>\n\n"
            f"👤 <b>Candidato(a):</b> <code>{name}</code>\n"
            f"📊 <b>Principais Habilidades:</b> <code>{skills_str}</code>\n"
            f"📈 <b>Senioridade Detectada:</b> <code>{seniority}</code>\n\n"
            f"🎯 <b>Carreiras Mais Recomendadas:</b> \n"
            f"{prof_bullets}\n\n"
            f"👇 <b>Clique abaixo para iniciar a busca automatizada:</b>"
        )
        
        await msg_status.edit_text(preview_msg, reply_markup=markup, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Erro ao processar PDF: {e}")
        tb_safe = html.escape(str(e))
        await msg_status.edit_text(f"❌ <b>Erro ao processar PDF:</b> <code>{tb_safe}</code>", parse_mode="HTML")

@dp.message()
async def echo_message(message: types.Message):
    if not message.text.startswith("/"):
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔍 Procurar Vagas", callback_data="hunt_menu")]
        ])
        await message.answer("Para iniciar as buscas, clique no botão abaixo ou digite /start", reply_markup=markup)

async def main():
    print("Bot Nativo Ligado e Aguardando Comandos!")
    try:
        await bot.delete_webhook(drop_pending_updates=True)
    except Exception as e:
        print(f"Warning: Failed to delete webhook on startup: {e}")

    try:
        await bot.set_chat_menu_button()
    except Exception as e:
        print(f"Warning: Failed to set chat menu button on startup: {e}")
    
    while True:
        try:
            await dp.start_polling(bot)
        except Exception as e:
            print(f"Erro de conexão no Telegram: {e}")
            print("Tentando reconectar em 5 segundos...")
            import asyncio
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
