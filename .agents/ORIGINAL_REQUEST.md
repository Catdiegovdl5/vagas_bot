# Original User Request

## 2026-08-05T13:51:59Z

# Teamwork Project Prompt

Refatoração completa, eliminação de loop de reinicialização no launcher.py e validação de integridade dos 4 Prompts do Sistema no repositório vagas_bot.

Working directory: C:\Users\99196\OneDrive\Documentos\vagas_bot
Integrity mode: development

## Requirements

### R1. Diagnóstico e Correção de Inicialização (Launcher & Bat)
O inicializador unificado launcher.py e os scripts de lote (iniciar_tudo.bat, start_bot.bat, start.bat) devem rodar sem entrar em loop infinito caso o token do Telegram não esteja configurado no .env, garantindo que o Servidor Web FastAPI suba normalmente na porta 8000.

### R2. Otimização de SEO & Schema.org (Prompt 1)
Manter os endpoints /sitemap.xml e /api/job/{job_id}/schema.json ativos e sincronizados com a marcação JSON-LD JobPosting do Schema.org no static/index.html.

### R3. Integridade de Categorias e Exclusão Estrita (Prompt 2)
Garantir que a busca de vagas respeite 0% de vazamento de categorias irrelevantes (como vagas de Designer dentro de Tráfego Pago) e que a contagem total reflita estritamente o banco SQLite.

### R4. Resiliência do Frontend e Dashboard (Prompt 3)
Garantir que o painel web em http://localhost:8000/ carregue sem erros de console JavaScript, variáveis undefined ou falhas de requisição.

### R5. Módulo de Autocorreção e Diagnóstico de Erros (Prompt 4)
Manter o middleware middleware/error_reporter.py e o auto-healer core/ai_self_healer.py registrando logs estruturados em logs/ e patches em patches/.

## Acceptance Criteria

### Integridade Visual e Operacional
- [x] O comando python launcher.py inicia o servidor FastAPI em http://localhost:8000/ sem loop de reinicialização.
- [x] A requisição HTTP GET para http://localhost:8000/ retorna status 200 OK.
- [x] As buscas por categoria possuem exclusão NOT LIKE para evitar vazamento de cargos incorretos.
- [x] Alterações salvas e enviadas ao repositório GitHub (refactor/organizacao-e-limpeza).
