# Original User Request

## Initial Request — 2026-07-16T14:50:29-03:00

You are the project orchestrator for the 'precision' phase.
Identity: orchestrator_precision
Working Directory: C:\Users\99196\OneDrive\Documentos\vagas_bot\.agents\orchestrator_precision

Your task is to plan, dispatch, and coordinate the team to fulfill the following requirements in the workspace C:/Users/99196/OneDrive/Documentos/vagas_bot:

### Context / Goal
Refatorar e corrigir o bot de busca de vagas do Telegram (Vagas Sniper Bot) para eliminar erros de execução e implementar um motor de busca de alta precisão. O novo motor deve manter a busca exata de palavras-chave, mas cruzar dados com listas estritas de "títulos permitidos" e "títulos bloqueados" para evitar falsos-positivos de outras áreas.

Integrity mode: demo

### Requirements
R1. Eliminação de Erros em Tempo de Execução: O bot do Telegram deve inicializar e realizar buscas completas de ponta-a-ponta sem lançar exceções.
R2. Motor de Busca Altamente Preciso: Implementar um sistema de filtragem de vagas que utilize correspondência exata de palavras-chave como base, mas incorpore um sistema robusto de listas de inclusão (allowlists) e bloqueio (blocklists) de títulos de cargo para eliminar falsos-positivos de indústrias não-relacionadas (ex: descartar "Enfermeira que sabe Python" quando buscar por "Python").

### Acceptance Criteria
- Um script de teste automatizado (test_motor.py) foi criado.
- O script contém um conjunto de vagas simuladas (mock jobs) que incluem verdadeiros-positivos e pelo menos 10 falsos-positivos difíceis de áreas de trabalho conflitantes.
- Ao rodar 'python test_motor.py', o script valida que 100% dos falsos-positivos são bloqueados pelo novo motor, sem intervenção humana.
- O bot roda ('python bot.py') e pode processar solicitações sem apresentar nenhum crash no console.

### Key Instructions for you:
1. Initialize your plan.md, progress.md and other files in your working directory C:\Users\99196\OneDrive\Documentos\vagas_bot\.agents\orchestrator_precision.
2. Continually update progress.md as the Sentinel scans this file to report progress to the user.
3. Spawn subagents (e.g. workers/specialists) as needed to perform the analysis, implementation, and verification.
4. When all requirements and acceptance criteria are completed, send a message to me (the Sentinel) claiming completion. Do not announce victory to the user directly, as I must run a mandatory victory audit first.
