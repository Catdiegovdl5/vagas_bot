import sys
import os

new_dict_str = '''CO_OCCURRENCE_RULES = {
    "especialista em ia": [
        ["ia", "ai", "inteligencia artificial", "artificial intelligence", "llm", "llms", "generativa", "generative ai", "genai", "chatgpt", "gemini", "claude", "copilot", "openai", "prompt", "rag", "fine tuning"],
        ["especialista", "consultor", "consultora", "analista", "gestor", "gestora", "lead", "lider", "especialista em ia", "coordenador", "coordenadora", "implementacao", "implementar", "implementado", "configuracao", "configurar", "criacao", "criador", "criadora", "criacao de conteudo", "automacao", "automatizar", "otimizacao", "otimizar", "integracao", "integrar", "desenvolvimento", "desenvolver", "desenvolvedor", "desenvolvedora", "treinamento", "treinar", "estrategia", "chatbot", "agente", "agentes", "solucao", "sistema", "plataforma", "ferramenta", "conteudo"]
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
        ["sdr", "bdr", "sales development", "business development", "prospectar", "prospeccao", "leads", "outbound", "inbound", "cold call", "cold email", "vendas", "comercial"],
        ["sdr", "bdr", "representante", "vendedor", "vendedora", "sales", "assessor", "assessora"]
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
    ]
}'''

with open('C:/Users/99196/OneDrive/Documentos/vagas_bot/bot.py', 'r', encoding='utf-8') as f:
    content = f.read()

import re

# Find the start and end of CO_OCCURRENCE_RULES
start_match = re.search(r'CO_OCCURRENCE_RULES\s*=\s*\{', content)
if not start_match:
    print("Could not find CO_OCCURRENCE_RULES")
    sys.exit(1)

start_idx = start_match.start()

# find the closing brace of CO_OCCURRENCE_RULES
# we need to count braces to handle nested braces
brace_count = 0
end_idx = -1
in_string = False
escape = False
quote_char = ''

for i in range(start_idx, len(content)):
    char = content[i]
    
    if escape:
        escape = False
        continue
        
    if char == '\\':
        escape = True
        continue
        
    if in_string:
        if char == quote_char:
            in_string = False
        continue
        
    if char in ['"', "'"]:
        in_string = True
        quote_char = char
        continue
        
    if char == '{':
        brace_count += 1
    elif char == '}':
        brace_count -= 1
        if brace_count == 0:
            end_idx = i + 1
            break

if end_idx == -1:
    print("Could not find end of CO_OCCURRENCE_RULES")
    sys.exit(1)

new_content = content[:start_idx] + new_dict_str + content[end_idx:]

with open('C:/Users/99196/OneDrive/Documentos/vagas_bot/bot.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("CO_OCCURRENCE_RULES successfully updated!")
